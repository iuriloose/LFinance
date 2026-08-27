from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

CONTRACT_VERSION = 1
ENTITY_TYPES = {
    "payable", "payment", "receivable", "receipt", "income", "expense"
}


def money_to_cents(value):
    return int(
        (Decimal(str(value or 0)) * 100).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )


def _now():
    return datetime.now(timezone.utc).isoformat()


def prepare_sync_schema(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sync_identities (
            entity_type TEXT NOT NULL,
            local_id TEXT NOT NULL,
            sync_id TEXT NOT NULL UNIQUE,
            content_hash TEXT,
            observed_at TEXT NOT NULL,
            deleted_at TEXT,
            PRIMARY KEY (entity_type, local_id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sync_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _content_hash(data):
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _identity(connection, entity_type, local_id):
    local_id = str(local_id)
    row = connection.execute(
        "SELECT sync_id FROM sync_identities WHERE entity_type = ? AND local_id = ?",
        (entity_type, local_id),
    ).fetchone()
    if row:
        return row[0]
    sync_id = str(uuid.uuid4())
    connection.execute(
        """INSERT INTO sync_identities
           (entity_type, local_id, sync_id, observed_at)
           VALUES (?, ?, ?, ?)""",
        (entity_type, local_id, sync_id, _now()),
    )
    return sync_id


def _record(connection, entity_type, local_id, data, observed_at):
    sync_id = _identity(connection, entity_type, local_id)
    digest = _content_hash(data)
    previous = connection.execute(
        """SELECT content_hash, observed_at FROM sync_identities
           WHERE entity_type = ? AND local_id = ?""",
        (entity_type, str(local_id)),
    ).fetchone()
    changed_at = previous[1] if previous and previous[0] == digest else observed_at
    connection.execute(
        """UPDATE sync_identities
           SET content_hash = ?, observed_at = ?, deleted_at = NULL
           WHERE entity_type = ? AND local_id = ?""",
        (digest, changed_at, entity_type, str(local_id)),
    )
    return {
        "id": sync_id,
        "type": entity_type,
        "updated_at": changed_at,
        "deleted_at": None,
        "data": data,
    }


def _fetch_all(connection, query):
    connection.row_factory = sqlite3.Row
    return connection.execute(query).fetchall()


def build_desktop_snapshot(connection, device_id="desktop-local"):
    prepare_sync_schema(connection)
    observed_at = _now()
    records = []
    seen = set()

    for row in _fetch_all(connection, "SELECT * FROM despesas"):
        data = {
            "description": row["descricao"],
            "planned_amount_cents": money_to_cents(row["valor"]),
            "due_date": row["vencimento"],
            "category": row["categoria"],
            "recurrence_type": row["tipo"],
            "installment_number": row["parcela_atual"],
            "installment_count": row["total_parcelas"],
            "total_amount_cents": None if row["valor_total"] is None else money_to_cents(row["valor_total"]),
            "status": row["status"],
        }
        records.append(_record(connection, "payable", row["id"], data, observed_at))
        seen.add(("payable", str(row["id"])))

    for row in _fetch_all(connection, "SELECT * FROM pagamentos"):
        payable_sync_id = None
        if row["id_despesa"] is not None:
            payable_sync_id = _identity(connection, "payable", row["id_despesa"])
        data = {
            "payable_id": payable_sync_id,
            "description": row["descricao"],
            "actual_amount_cents": money_to_cents(row["valor"]),
            "planned_amount_cents": money_to_cents(row["valor_original"]),
            "paid_date": row["data_pagamento"],
            "category": row["categoria"],
            "payment_method": row["forma_pagamento"],
            "interest_cents": money_to_cents(row["acrescimo"]),
            "discount_cents": money_to_cents(row["desconto"]),
            "note": row["observacao"] or "",
        }
        records.append(_record(connection, "payment", row["id"], data, observed_at))
        seen.add(("payment", str(row["id"])))

    for row in _fetch_all(connection, "SELECT * FROM gastos"):
        data = {
            "description": row["descricao"],
            "amount_cents": money_to_cents(row["valor"]),
            "expense_date": row["data_gasto"],
            "category": row["categoria"],
            "note": row["observacao"] or "",
        }
        records.append(_record(connection, "expense", row["id"], data, observed_at))
        seen.add(("expense", str(row["id"])))

    for row in _fetch_all(connection, "SELECT * FROM receitas"):
        data = {
            "description": row["descricao"],
            "amount_cents": money_to_cents(row["valor"]),
            "received_date": row["data_recebimento"],
            "category": row["categoria"],
            "note": row["observacao"] or "",
        }
        records.append(_record(connection, "income", row["id"], data, observed_at))
        seen.add(("income", str(row["id"])))

    for row in _fetch_all(connection, "SELECT * FROM valores_receber"):
        data = {
            "payer": row["pagador"],
            "description": row["descricao"],
            "planned_amount_cents": money_to_cents(row["valor"]),
            "due_date": row["data_prevista"],
            "category": row["categoria"],
            "frequency": row["frequencia"],
            "status": row["status"],
            "note": row["observacao"] or "",
        }
        records.append(_record(connection, "receivable", row["id"], data, observed_at))
        seen.add(("receivable", str(row["id"])))

    for row in _fetch_all(connection, "SELECT * FROM recebimentos"):
        receivable_id = _identity(connection, "receivable", row["valor_receber_id"])
        income_id = _identity(connection, "income", row["receita_id"])
        data = {
            "receivable_id": receivable_id,
            "income_id": income_id,
            "actual_amount_cents": money_to_cents(row["valor"]),
            "received_date": row["data_recebimento"],
            "note": row["observacao"] or "",
        }
        records.append(_record(connection, "receipt", row["id"], data, observed_at))
        seen.add(("receipt", str(row["id"])))

    identities = connection.execute(
        "SELECT entity_type, local_id, sync_id, deleted_at FROM sync_identities"
    ).fetchall()
    for entity_type, local_id, sync_id, deleted_at in identities:
        if entity_type not in ENTITY_TYPES or (entity_type, local_id) in seen:
            continue
        deleted_at = deleted_at or observed_at
        connection.execute(
            """UPDATE sync_identities SET deleted_at = ?
               WHERE entity_type = ? AND local_id = ?""",
            (deleted_at, entity_type, local_id),
        )
        records.append({
            "id": sync_id,
            "type": entity_type,
            "updated_at": deleted_at,
            "deleted_at": deleted_at,
            "data": {},
        })

    connection.commit()
    return {
        "contract_version": CONTRACT_VERSION,
        "device_id": device_id,
        "exported_at": observed_at,
        "entities": sorted(records, key=lambda item: (item["type"], item["id"])),
    }
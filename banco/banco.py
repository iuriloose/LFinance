import sqlite3
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta


CAMINHO_BANCO = Path("banco") / "lfinance.db"


def conectar():
    return sqlite3.connect(CAMINHO_BANCO)


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            vencimento TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            parcela_atual INTEGER,
            total_parcelas INTEGER,
            valor_total REAL,
            status TEXT NOT NULL DEFAULT 'aberta',
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    colunas = [coluna[1] for coluna in cursor.execute("PRAGMA table_info(despesas)")]

    if "parcela_atual" not in colunas:
        cursor.execute("ALTER TABLE despesas ADD COLUMN parcela_atual INTEGER")

    if "total_parcelas" not in colunas:
        cursor.execute("ALTER TABLE despesas ADD COLUMN total_parcelas INTEGER")

    if "valor_total" not in colunas:
        cursor.execute("ALTER TABLE despesas ADD COLUMN valor_total REAL")

    conexao.commit()
    conexao.close()


def inserir_despesa(
    descricao, valor, vencimento, categoria, tipo,
    parcela_atual=None, total_parcelas=None, valor_total=None
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO despesas (
            descricao, valor, vencimento, categoria, tipo,
            parcela_atual, total_parcelas, valor_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        descricao, valor, vencimento, categoria, tipo,
        parcela_atual, total_parcelas, valor_total
    ))

    conexao.commit()
    conexao.close()


def listar_despesas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, vencimento, categoria, tipo,
               parcela_atual, total_parcelas, valor_total, status
        FROM despesas
        ORDER BY
            CASE
                WHEN status = 'aberta' THEN 0
                WHEN status = 'paga' THEN 1
            END,
            vencimento ASC
    """)

    despesas = cursor.fetchall()
    conexao.close()
    return despesas


def somar_despesas_abertas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM despesas
        WHERE status = 'aberta'
    """)

    total = cursor.fetchone()[0]
    conexao.close()
    return total


def contar_despesas_atrasadas(data_hoje):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM despesas
        WHERE status = 'aberta'
        AND vencimento < ?
    """, (data_hoje,))

    total = cursor.fetchone()[0]
    conexao.close()
    return total


def marcar_despesa_como_paga(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE despesas
        SET status = 'paga'
        WHERE id = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()


def pagar_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT descricao, valor, vencimento, categoria, tipo,
               parcela_atual, total_parcelas, valor_total, status
        FROM despesas
        WHERE id = ?
    """, (id_despesa,))

    despesa = cursor.fetchone()

    if not despesa:
        conexao.close()
        return

    (
        descricao,
        valor,
        vencimento,
        categoria,
        tipo,
        parcela_atual,
        total_parcelas,
        valor_total,
        status,
    ) = despesa

    cursor.execute("""
        UPDATE despesas
        SET status = 'paga'
        WHERE id = ?
    """, (id_despesa,))

    data = datetime.strptime(vencimento, "%Y-%m-%d")
    novo_vencimento = (data + relativedelta(months=1)).strftime("%Y-%m-%d")

    if tipo == "Conta fixa":
        cursor.execute("""
            INSERT INTO despesas (
                descricao, valor, vencimento, categoria, tipo, status
            )
            VALUES (?, ?, ?, ?, ?, 'aberta')
        """, (
            descricao,
            valor,
            novo_vencimento,
            categoria,
            tipo,
        ))

    elif (
        tipo == "Parcelamento"
        and parcela_atual is not None
        and total_parcelas is not None
        and parcela_atual < total_parcelas
    ):
        cursor.execute("""
            INSERT INTO despesas (
                descricao, valor, vencimento, categoria, tipo,
                parcela_atual, total_parcelas, valor_total, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aberta')
        """, (
            descricao,
            valor,
            novo_vencimento,
            categoria,
            tipo,
            parcela_atual + 1,
            total_parcelas,
            valor_total,
        ))

    conexao.commit()
    conexao.close()


def excluir_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM despesas
        WHERE id = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()


def reabrir_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE despesas
        SET status = 'aberta'
        WHERE id = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()


def atualizar_despesa(
    id_despesa, descricao, valor, vencimento, categoria, tipo,
    parcela_atual=None, total_parcelas=None, valor_total=None
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE despesas
        SET descricao = ?,
            valor = ?,
            vencimento = ?,
            categoria = ?,
            tipo = ?,
            parcela_atual = ?,
            total_parcelas = ?,
            valor_total = ?
        WHERE id = ?
    """, (
        descricao, valor, vencimento, categoria, tipo,
        parcela_atual, total_parcelas, valor_total, id_despesa
    ))

    conexao.commit()
    conexao.close()
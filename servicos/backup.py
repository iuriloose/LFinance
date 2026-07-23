import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path


TABELAS_OBRIGATORIAS = {"despesas", "receitas", "gastos", "pagamentos"}
COLUNAS_OBRIGATORIAS = {
    "despesas": {"id", "descricao", "valor", "vencimento", "categoria", "tipo", "status"},
    "receitas": {"id", "descricao", "valor", "data_recebimento", "categoria"},
    "gastos": {"id", "descricao", "valor", "data_gasto", "categoria"},
    "pagamentos": {"id", "descricao", "valor", "data_pagamento", "categoria", "tipo"},
}


def copiar_banco_sqlite(origem, destino):
    origem = Path(origem)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    uri_origem = f"{origem.resolve().as_uri()}?mode=ro"
    with closing(sqlite3.connect(uri_origem, uri=True)) as conexao_origem:
        with closing(sqlite3.connect(str(destino))) as conexao_destino:
            conexao_origem.backup(conexao_destino)
            conexao_destino.commit()


def criar_backup_automatico(banco, prefixo="backup_automatico"):
    banco = Path(banco)
    if not banco.exists():
        return None

    pasta = banco.parent / "backups_automaticos"
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    destino = pasta / f"{prefixo}_{data_hora}.db"
    copiar_banco_sqlite(banco, destino)
    valido, motivo = validar_backup_lfinance(destino)
    if not valido:
        destino.unlink(missing_ok=True)
        raise RuntimeError(f"O backup de segurança não pôde ser validado: {motivo}")
    return destino


def restaurar_banco_sqlite(origem, destino, backup_seguranca=None):
    """Restaura um banco por troca atômica e recupera o original em caso de erro."""
    origem = Path(origem)
    destino = Path(destino)

    valido, motivo = validar_backup_lfinance(origem)
    if not valido:
        raise ValueError(motivo)

    destino.parent.mkdir(parents=True, exist_ok=True)
    backup_seguranca = Path(backup_seguranca) if backup_seguranca else None
    if destino.exists() and backup_seguranca and not backup_seguranca.exists():
        copiar_banco_sqlite(destino, backup_seguranca)

    descritor, caminho_temporario = tempfile.mkstemp(
        prefix=".lfinance-restauracao-", suffix=".db", dir=destino.parent
    )
    os.close(descritor)
    temporario = Path(caminho_temporario)

    try:
        copiar_banco_sqlite(origem, temporario)
        valido, motivo = validar_backup_lfinance(temporario)
        if not valido:
            raise ValueError(motivo)
        os.replace(temporario, destino)
    except Exception:
        temporario.unlink(missing_ok=True)
        if backup_seguranca and backup_seguranca.exists():
            descritor, caminho_rollback = tempfile.mkstemp(
                prefix=".lfinance-rollback-", suffix=".db", dir=destino.parent
            )
            os.close(descritor)
            rollback = Path(caminho_rollback)
            try:
                copiar_banco_sqlite(backup_seguranca, rollback)
                os.replace(rollback, destino)
            finally:
                rollback.unlink(missing_ok=True)
        raise

    return backup_seguranca


def validar_backup_lfinance(arquivo):
    arquivo = Path(arquivo)

    try:
        uri = f"{arquivo.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as conexao:
            resultado = conexao.execute("PRAGMA quick_check").fetchone()
            if not resultado or str(resultado[0]).lower() != "ok":
                return False, "O arquivo selecionado está corrompido."

            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }

            if not TABELAS_OBRIGATORIAS.issubset(tabelas):
                return False, "O arquivo não possui a estrutura de um backup do LFinance."

            for tabela, obrigatorias in COLUNAS_OBRIGATORIAS.items():
                colunas = {
                    linha[1]
                    for linha in conexao.execute(f"PRAGMA table_info({tabela})")
                }
                if not obrigatorias.issubset(colunas):
                    return False, (
                        f"A tabela {tabela} não possui todas as colunas necessárias."
                    )
    except sqlite3.Error as erro:
        return False, f"O arquivo não pôde ser lido como banco de dados.\n\n{erro}"

    return True, ""

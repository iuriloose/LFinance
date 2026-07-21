import sqlite3
from pathlib import Path


TABELAS_OBRIGATORIAS = {"despesas", "receitas", "gastos", "pagamentos"}


def copiar_banco_sqlite(origem, destino):
    origem = Path(origem)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    uri_origem = f"{origem.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri_origem, uri=True) as conexao_origem:
        with sqlite3.connect(str(destino)) as conexao_destino:
            conexao_origem.backup(conexao_destino)


def validar_backup_lfinance(arquivo):
    arquivo = Path(arquivo)

    try:
        uri = f"{arquivo.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conexao:
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
    except sqlite3.Error as erro:
        return False, f"O arquivo não pôde ser lido como banco de dados.\n\n{erro}"

    return True, ""

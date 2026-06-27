import sqlite3
from pathlib import Path


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
            status TEXT NOT NULL DEFAULT 'aberta',
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


def inserir_despesa(descricao, valor, vencimento, categoria, tipo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO despesas (descricao, valor, vencimento, categoria, tipo)
        VALUES (?, ?, ?, ?, ?)
    """, (descricao, valor, vencimento, categoria, tipo))

    conexao.commit()
    conexao.close()


def listar_despesas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, vencimento, categoria, tipo, status
        FROM despesas
        ORDER BY vencimento ASC
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


def excluir_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM despesas
        WHERE id = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()
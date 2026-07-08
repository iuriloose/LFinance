import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

from servicos.configuracoes_app import CAMINHO_BANCO, migrar_banco_antigo_se_necessario


migrar_banco_antigo_se_necessario()


def conectar():
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
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


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_recebimento TEXT NOT NULL,
            categoria TEXT NOT NULL,
            observacao TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    colunas_receitas = [coluna[1] for coluna in cursor.execute("PRAGMA table_info(receitas)")]

    if "observacao" not in colunas_receitas:
        cursor.execute("ALTER TABLE receitas ADD COLUMN observacao TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_gasto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            observacao TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    colunas_gastos = [coluna[1] for coluna in cursor.execute("PRAGMA table_info(gastos)")]

    if "observacao" not in colunas_gastos:
        cursor.execute("ALTER TABLE gastos ADD COLUMN observacao TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_despesa INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_pagamento TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            parcela_atual INTEGER,
            total_parcelas INTEGER,
            forma_pagamento TEXT DEFAULT 'Não informado',
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    colunas_pagamentos = [coluna[1] for coluna in cursor.execute("PRAGMA table_info(pagamentos)")]

    if "forma_pagamento" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN forma_pagamento TEXT DEFAULT 'Não informado'")

    conexao.commit()
    conexao.close()
    limpar_parcelamentos_pagos_duplicados()


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


def buscar_despesa_por_id(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, vencimento, categoria, tipo,
               parcela_atual, total_parcelas, valor_total, status
        FROM despesas
        WHERE id = ?
    """, (id_despesa,))

    despesa = cursor.fetchone()
    conexao.close()
    return despesa


def pagar_despesa(id_despesa, forma_pagamento="Não informado"):
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

    if status == "paga":
        conexao.close()
        return

    data_pagamento = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO pagamentos (
            id_despesa, descricao, valor, data_pagamento, categoria, tipo,
            parcela_atual, total_parcelas, forma_pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_despesa, descricao, valor, data_pagamento, categoria, tipo,
        parcela_atual, total_parcelas, forma_pagamento
    ))

    if tipo == "Conta fixa":
        data = datetime.strptime(vencimento, "%Y-%m-%d")
        novo_vencimento = (data + relativedelta(months=1)).strftime("%Y-%m-%d")

        cursor.execute("""
            UPDATE despesas
            SET vencimento = ?,
                status = 'aberta'
            WHERE id = ?
        """, (novo_vencimento, id_despesa))

    elif (
        tipo == "Parcelamento"
        and parcela_atual is not None
        and total_parcelas is not None
    ):
        if parcela_atual < total_parcelas:
            data = datetime.strptime(vencimento, "%Y-%m-%d")
            novo_vencimento = (data + relativedelta(months=1)).strftime("%Y-%m-%d")

            cursor.execute("""
                UPDATE despesas
                SET vencimento = ?,
                    parcela_atual = ?,
                    status = 'aberta'
                WHERE id = ?
            """, (novo_vencimento, parcela_atual + 1, id_despesa))
        else:
            cursor.execute("""
                UPDATE despesas
                SET status = 'paga'
                WHERE id = ?
            """, (id_despesa,))

    else:
        cursor.execute("""
            UPDATE despesas
            SET status = 'paga'
            WHERE id = ?
        """, (id_despesa,))

    conexao.commit()
    conexao.close()


def limpar_parcelamentos_pagos_duplicados():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM despesas
        WHERE status = 'paga'
          AND tipo = 'Parcelamento'
          AND EXISTS (
              SELECT 1
              FROM despesas AS aberta
              WHERE aberta.status = 'aberta'
                AND aberta.tipo = despesas.tipo
                AND aberta.descricao = despesas.descricao
                AND aberta.total_parcelas = despesas.total_parcelas
                AND aberta.parcela_atual = despesas.parcela_atual + 1
          )
    """)

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


def inserir_receita(descricao, valor, data_recebimento, categoria, observacao=""):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO receitas (descricao, valor, data_recebimento, categoria, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (descricao, valor, data_recebimento, categoria, observacao))

    conexao.commit()
    conexao.close()


def listar_receitas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, data_recebimento, categoria, observacao
        FROM receitas
        ORDER BY data_recebimento DESC, id DESC
    """)

    receitas = cursor.fetchall()
    conexao.close()
    return receitas


def buscar_receita_por_id(id_receita):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, data_recebimento, categoria, observacao
        FROM receitas
        WHERE id = ?
    """, (id_receita,))

    receita = cursor.fetchone()
    conexao.close()
    return receita


def atualizar_receita(id_receita, descricao, valor, data_recebimento, categoria, observacao=""):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE receitas
        SET descricao = ?,
            valor = ?,
            data_recebimento = ?,
            categoria = ?,
            observacao = ?
        WHERE id = ?
    """, (descricao, valor, data_recebimento, categoria, observacao, id_receita))

    conexao.commit()
    conexao.close()


def excluir_receita(id_receita):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM receitas
        WHERE id = ?
    """, (id_receita,))

    conexao.commit()
    conexao.close()


def somar_receitas_mes(inicio_mes, fim_mes):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM receitas
        WHERE data_recebimento BETWEEN ? AND ?
    """, (inicio_mes, fim_mes))

    total = cursor.fetchone()[0]
    conexao.close()
    return total



def inserir_gasto(descricao, valor, data_gasto, categoria, observacao=""):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO gastos (descricao, valor, data_gasto, categoria, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (descricao, valor, data_gasto, categoria, observacao))

    conexao.commit()
    conexao.close()


def listar_gastos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, data_gasto, categoria, observacao
        FROM gastos
        ORDER BY data_gasto DESC, id DESC
    """)

    gastos = cursor.fetchall()
    conexao.close()
    return gastos


def buscar_gasto_por_id(id_gasto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, data_gasto, categoria, observacao
        FROM gastos
        WHERE id = ?
    """, (id_gasto,))

    gasto = cursor.fetchone()
    conexao.close()
    return gasto


def atualizar_gasto(id_gasto, descricao, valor, data_gasto, categoria, observacao=""):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE gastos
        SET descricao = ?,
            valor = ?,
            data_gasto = ?,
            categoria = ?,
            observacao = ?
        WHERE id = ?
    """, (descricao, valor, data_gasto, categoria, observacao, id_gasto))

    conexao.commit()
    conexao.close()


def excluir_gasto(id_gasto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM gastos
        WHERE id = ?
    """, (id_gasto,))

    conexao.commit()
    conexao.close()


def somar_gastos_mes(inicio_mes, fim_mes):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM gastos
        WHERE data_gasto BETWEEN ? AND ?
    """, (inicio_mes, fim_mes))

    total = cursor.fetchone()[0]
    conexao.close()
    return total


def listar_pagamentos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, id_despesa, descricao, valor, data_pagamento, categoria,
               tipo, parcela_atual, total_parcelas,
               COALESCE(forma_pagamento, 'Não informado')
        FROM pagamentos
        ORDER BY data_pagamento DESC, id DESC
    """)

    pagamentos = cursor.fetchall()
    conexao.close()
    return pagamentos


def excluir_pagamentos_da_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM pagamentos
        WHERE id_despesa = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()



def excluir_pagamento(id_pagamento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM pagamentos
        WHERE id = ?
    """, (id_pagamento,))

    conexao.commit()
    conexao.close()


def desfazer_pagamento(id_pagamento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id_despesa
        FROM pagamentos
        WHERE id = ?
    """, (id_pagamento,))

    registro = cursor.fetchone()
    if not registro:
        conexao.close()
        return

    id_despesa = registro[0]

    cursor.execute("""
        DELETE FROM pagamentos
        WHERE id = ?
    """, (id_pagamento,))

    if id_despesa:
        cursor.execute("""
            UPDATE despesas
            SET status = 'aberta'
            WHERE id = ?
        """, (id_despesa,))

    conexao.commit()
    conexao.close()


def excluir_despesa_com_historico(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM pagamentos
        WHERE id_despesa = ?
    """, (id_despesa,))

    cursor.execute("""
        DELETE FROM despesas
        WHERE id = ?
    """, (id_despesa,))

    conexao.commit()
    conexao.close()


def limpar_todos_os_dados():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM pagamentos")
    cursor.execute("DELETE FROM gastos")
    cursor.execute("DELETE FROM receitas")
    cursor.execute("DELETE FROM despesas")

    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('pagamentos', 'gastos', 'receitas', 'despesas')")

    conexao.commit()
    conexao.close()

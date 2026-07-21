import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

from servicos.configuracoes_app import CAMINHO_BANCO, migrar_banco_antigo_se_necessario


def conectar():
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO, timeout=15)
    conexao.execute("PRAGMA busy_timeout = 5000")
    return conexao


def criar_tabelas():
    migrar_banco_antigo_se_necessario()
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
            vencimento_referencia TEXT,
            forma_pagamento TEXT DEFAULT 'Não informado',
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    colunas_pagamentos = [coluna[1] for coluna in cursor.execute("PRAGMA table_info(pagamentos)")]

    if "forma_pagamento" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN forma_pagamento TEXT DEFAULT 'Não informado'")

    if "vencimento_referencia" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN vencimento_referencia TEXT")

    if "valor_original" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN valor_original REAL")

    if "acrescimo" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN acrescimo REAL DEFAULT 0")

    if "desconto" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN desconto REAL DEFAULT 0")

    if "observacao" not in colunas_pagamentos:
        cursor.execute("ALTER TABLE pagamentos ADD COLUMN observacao TEXT")

    cursor.execute("""
        UPDATE pagamentos
        SET valor_original = valor
        WHERE valor_original IS NULL
    """)

    cursor.execute("PRAGMA user_version = 3")
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


def pagar_despesa(
    id_despesa, forma_pagamento="Não informado", valor_pago=None,
    data_pagamento=None, observacao=""
):
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
        return False, "A despesa não foi encontrada."

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
        return False, "Esta despesa já está paga."

    valor_original = round(float(valor), 2)
    valor_pago = valor_original if valor_pago is None else round(float(valor_pago), 2)
    if valor_pago < 0:
        conexao.close()
        return False, "O valor pago não pode ser negativo."

    acrescimo = round(max(valor_pago - valor_original, 0), 2)
    desconto = round(max(valor_original - valor_pago, 0), 2)
    data_pagamento = data_pagamento or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO pagamentos (
            id_despesa, descricao, valor, data_pagamento, categoria, tipo,
            parcela_atual, total_parcelas, vencimento_referencia, forma_pagamento,
            valor_original, acrescimo, desconto, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_despesa, descricao, valor_pago, data_pagamento, categoria, tipo,
        parcela_atual, total_parcelas, vencimento, forma_pagamento,
        valor_original, acrescimo, desconto, observacao.strip()
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
    return True, ""


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
        SELECT id
        FROM pagamentos
        WHERE id_despesa = ?
        ORDER BY id DESC
        LIMIT 1
    """, (id_despesa,))
    pagamento = cursor.fetchone()
    conexao.close()

    if pagamento:
        return desfazer_pagamento(pagamento[0])

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("UPDATE despesas SET status = 'aberta' WHERE id = ?", (id_despesa,))

    conexao.commit()
    conexao.close()
    return True, ""


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


def listar_pagamentos_detalhados():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id, id_despesa, descricao, valor, data_pagamento, categoria,
               tipo, parcela_atual, total_parcelas,
               COALESCE(forma_pagamento, 'Não informado'),
               COALESCE(valor_original, valor),
               COALESCE(acrescimo, 0), COALESCE(desconto, 0),
               COALESCE(observacao, '')
        FROM pagamentos
        ORDER BY data_pagamento DESC, id DESC
    """)
    pagamentos = cursor.fetchall()
    conexao.close()
    return pagamentos


def buscar_ultimo_pagamento_da_despesa(id_despesa):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id, valor, data_pagamento
        FROM pagamentos
        WHERE id_despesa = ?
        ORDER BY id DESC
        LIMIT 1
    """, (id_despesa,))
    pagamento = cursor.fetchone()
    conexao.close()
    return pagamento


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
        SELECT id_despesa, tipo, parcela_atual, total_parcelas,
               vencimento_referencia
        FROM pagamentos
        WHERE id = ?
    """, (id_pagamento,))

    registro = cursor.fetchone()
    if not registro:
        conexao.close()
        return False, "O pagamento não foi encontrado."

    (
        id_despesa,
        tipo_pagamento,
        parcela_pagamento,
        total_parcelas_pagamento,
        vencimento_referencia,
    ) = registro

    if not id_despesa:
        cursor.execute("DELETE FROM pagamentos WHERE id = ?", (id_pagamento,))
        conexao.commit()
        conexao.close()
        return True, ""

    cursor.execute("""
        SELECT id, vencimento, tipo, parcela_atual, status
        FROM despesas
        WHERE id = ?
    """, (id_despesa,))
    despesa = cursor.fetchone()

    if not despesa:
        cursor.execute("DELETE FROM pagamentos WHERE id = ?", (id_pagamento,))
        conexao.commit()
        conexao.close()
        return True, ""

    if tipo_pagamento in ("Conta fixa", "Parcelamento"):
        cursor.execute("""
            SELECT id
            FROM pagamentos
            WHERE id_despesa = ?
            ORDER BY id DESC
            LIMIT 1
        """, (id_despesa,))
        ultimo_pagamento = cursor.fetchone()

        if ultimo_pagamento and ultimo_pagamento[0] != id_pagamento:
            conexao.close()
            return False, (
                "Para proteger o histórico, desfaça primeiro o pagamento mais recente "
                "desta conta ou parcelamento."
            )

    _, vencimento_atual, tipo_atual, _, status_atual = despesa
    vencimento_anterior = vencimento_referencia

    parcela_final_legada = (
        tipo_atual == "Parcelamento"
        and status_atual == "paga"
        and parcela_pagamento is not None
        and total_parcelas_pagamento is not None
        and parcela_pagamento >= total_parcelas_pagamento
    )

    if (
        not vencimento_anterior
        and tipo_atual in ("Conta fixa", "Parcelamento")
        and not parcela_final_legada
    ):
        data_atual = datetime.strptime(vencimento_atual, "%Y-%m-%d")
        vencimento_anterior = (data_atual - relativedelta(months=1)).strftime("%Y-%m-%d")

    if tipo_atual == "Conta fixa":
        cursor.execute("""
            UPDATE despesas
            SET vencimento = ?, status = 'aberta'
            WHERE id = ?
        """, (vencimento_anterior or vencimento_atual, id_despesa))

    elif tipo_atual == "Parcelamento":
        cursor.execute("""
            UPDATE despesas
            SET vencimento = ?, parcela_atual = ?, status = 'aberta'
            WHERE id = ?
        """, (
            vencimento_anterior or vencimento_atual,
            parcela_pagamento,
            id_despesa,
        ))

    else:
        cursor.execute("""
            UPDATE despesas
            SET status = 'aberta'
            WHERE id = ?
        """, (id_despesa,))

    cursor.execute("DELETE FROM pagamentos WHERE id = ?", (id_pagamento,))

    conexao.commit()
    conexao.close()
    return True, ""


def excluir_despesa_com_historico(id_despesa):
    """Exclui a despesa e estorna somente seu pagamento mais recente.

    Pagamentos anteriores de contas recorrentes e parcelamentos permanecem no
    histórico, pois representam saídas que realmente aconteceram.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM pagamentos
        WHERE id = (
            SELECT id
            FROM pagamentos
            WHERE id_despesa = ?
            ORDER BY id DESC
            LIMIT 1
        )
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

from datetime import date, datetime

from dateutil.relativedelta import relativedelta


def _conectar():
    from banco.banco import conectar

    return conectar()


def criar_estrutura_valores_receber(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valores_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pagador TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_prevista TEXT NOT NULL,
            categoria TEXT NOT NULL,
            recorrente INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'aberto',
            observacao TEXT,
            gerado_de_id INTEGER,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_valores_receber_gerado_de
        ON valores_receber (gerado_de_id)
        WHERE gerado_de_id IS NOT NULL
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recebimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor_receber_id INTEGER NOT NULL,
            receita_id INTEGER NOT NULL UNIQUE,
            valor REAL NOT NULL,
            data_recebimento TEXT NOT NULL,
            observacao TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recebimentos_valor_receber
        ON recebimentos (valor_receber_id)
    """)


def limpar_valores_receber(cursor):
    cursor.execute("DELETE FROM recebimentos")
    cursor.execute("DELETE FROM valores_receber")
    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name IN ('recebimentos', 'valores_receber')
    """)


def _validar_data(data_texto):
    try:
        date.fromisoformat(str(data_texto))
    except (TypeError, ValueError) as erro:
        raise ValueError("Informe uma data válida.") from erro


def _situacao(status, data_prevista, recebido, valor):
    if status == "cancelado":
        return "cancelado"
    if status == "recebido" or recebido >= valor - 0.005:
        return "recebido"
    if data_prevista < date.today().isoformat():
        return "atrasado"
    if recebido > 0:
        return "parcial"
    return "em_aberto"


def _montar(linha):
    (
        id_valor,
        pagador,
        descricao,
        valor,
        data_prevista,
        categoria,
        recorrente,
        status,
        observacao,
        recebido,
    ) = linha
    valor = round(float(valor or 0), 2)
    recebido = round(float(recebido or 0), 2)
    restante = max(round(valor - recebido, 2), 0)
    return (
        id_valor,
        pagador,
        descricao,
        valor,
        data_prevista,
        categoria,
        int(recorrente or 0),
        status,
        observacao or "",
        recebido,
        restante,
        _situacao(status, data_prevista, recebido, valor),
    )


def _selecionar(conexao, id_valor=None):
    parametros = ()
    filtro = ""
    if id_valor is not None:
        filtro = "WHERE v.id = ?"
        parametros = (id_valor,)

    return conexao.execute(f"""
        SELECT
            v.id,
            v.pagador,
            v.descricao,
            v.valor,
            v.data_prevista,
            v.categoria,
            v.recorrente,
            v.status,
            v.observacao,
            COALESCE(SUM(r.valor), 0)
        FROM valores_receber v
        LEFT JOIN recebimentos r ON r.valor_receber_id = v.id
        {filtro}
        GROUP BY v.id
    """, parametros).fetchall()


def inserir_valor_receber(
    pagador,
    descricao,
    valor,
    data_prevista,
    categoria,
    recorrente=False,
    observacao="",
):
    pagador = str(pagador or "").strip()
    descricao = str(descricao or "").strip()
    categoria = str(categoria or "").strip()
    valor = round(float(valor), 2)
    _validar_data(data_prevista)

    if not pagador:
        raise ValueError("Informe a pessoa ou empresa que fará o pagamento.")
    if not descricao:
        raise ValueError("Informe a descrição do valor a receber.")
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    if not categoria:
        raise ValueError("Informe a categoria.")

    conexao = _conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO valores_receber (
            pagador, descricao, valor, data_prevista, categoria,
            recorrente, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        pagador,
        descricao,
        valor,
        data_prevista,
        categoria,
        int(bool(recorrente)),
        str(observacao or "").strip(),
    ))
    id_valor = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return id_valor


def listar_valores_receber(filtro="ativos"):
    conexao = _conectar()
    valores = [_montar(linha) for linha in _selecionar(conexao)]
    conexao.close()

    filtros = {
        "ativos": {"em_aberto", "parcial", "atrasado"},
        "atrasados": {"atrasado"},
        "recebidos": {"recebido"},
        "cancelados": {"cancelado"},
    }
    if filtro in filtros:
        valores = [item for item in valores if item[11] in filtros[filtro]]

    prioridade = {
        "atrasado": 0,
        "parcial": 1,
        "em_aberto": 2,
        "recebido": 3,
        "cancelado": 4,
    }
    return sorted(valores, key=lambda item: (prioridade[item[11]], item[4], item[0]))


def buscar_valor_receber_por_id(id_valor):
    conexao = _conectar()
    linhas = _selecionar(conexao, id_valor)
    conexao.close()
    return _montar(linhas[0]) if linhas else None


def atualizar_valor_receber(
    id_valor,
    pagador,
    descricao,
    valor,
    data_prevista,
    categoria,
    recorrente=False,
    observacao="",
):
    atual = buscar_valor_receber_por_id(id_valor)
    if not atual:
        return False, "O valor a receber não foi encontrado."
    if atual[11] in {"recebido", "cancelado"}:
        return False, "Um valor recebido ou cancelado não pode ser editado."

    pagador = str(pagador or "").strip()
    descricao = str(descricao or "").strip()
    categoria = str(categoria or "").strip()
    valor = round(float(valor), 2)
    _validar_data(data_prevista)

    if not pagador or not descricao or not categoria:
        return False, "Preencha pessoa/empresa, descrição e categoria."
    if valor <= 0:
        return False, "O valor deve ser maior que zero."
    if valor < atual[9] - 0.005:
        return False, "O total não pode ser menor que o valor já recebido."

    conexao = _conectar()
    conexao.execute("""
        UPDATE valores_receber
        SET pagador = ?,
            descricao = ?,
            valor = ?,
            data_prevista = ?,
            categoria = ?,
            recorrente = ?,
            observacao = ?
        WHERE id = ?
    """, (
        pagador,
        descricao,
        valor,
        data_prevista,
        categoria,
        int(bool(recorrente)),
        str(observacao or "").strip(),
        id_valor,
    ))
    conexao.commit()
    conexao.close()
    return True, "Valor atualizado."


def registrar_recebimento(id_valor, valor_recebido, data_recebimento, observacao=""):
    valor_recebido = round(float(valor_recebido), 2)
    _validar_data(data_recebimento)
    if valor_recebido <= 0:
        return False, "O valor recebido deve ser maior que zero."

    conexao = _conectar()
    try:
        conexao.execute("BEGIN IMMEDIATE")
        linhas = _selecionar(conexao, id_valor)
        if not linhas:
            conexao.rollback()
            return False, "O valor a receber não foi encontrado."

        atual = _montar(linhas[0])
        if atual[11] in {"recebido", "cancelado"}:
            conexao.rollback()
            return False, "Este valor não está disponível para recebimento."
        if valor_recebido > atual[10] + 0.005:
            conexao.rollback()
            return False, "O recebimento não pode ser maior que o saldo restante."

        observacao = str(observacao or "").strip()
        observacao_receita = f"Recebido de {atual[1]}"
        if observacao:
            observacao_receita += f" • {observacao}"

        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO receitas (
                descricao, valor, data_recebimento, categoria, observacao
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            atual[2],
            valor_recebido,
            data_recebimento,
            atual[5],
            observacao_receita,
        ))
        receita_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO recebimentos (
                valor_receber_id, receita_id, valor,
                data_recebimento, observacao
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_valor,
            receita_id,
            valor_recebido,
            data_recebimento,
            observacao,
        ))

        total_recebido = round(atual[9] + valor_recebido, 2)
        completo = total_recebido >= atual[3] - 0.005
        proxima_competencia = False
        if completo:
            cursor.execute(
                "UPDATE valores_receber SET status = 'recebido' WHERE id = ?",
                (id_valor,),
            )
            if atual[6]:
                proxima_data = (
                    datetime.strptime(atual[4], "%Y-%m-%d") + relativedelta(months=1)
                ).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT OR IGNORE INTO valores_receber (
                        pagador, descricao, valor, data_prevista, categoria,
                        recorrente, status, observacao, gerado_de_id
                    )
                    VALUES (?, ?, ?, ?, ?, 1, 'aberto', ?, ?)
                """, (
                    atual[1],
                    atual[2],
                    atual[3],
                    proxima_data,
                    atual[5],
                    atual[8],
                    id_valor,
                ))
                proxima_competencia = cursor.rowcount > 0
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()

    if completo and proxima_competencia:
        return True, "Recebimento concluído e próximo mês criado."
    if completo:
        return True, "Recebimento concluído."
    return True, "Recebimento parcial registrado."


def listar_recebimentos_valor(id_valor):
    conexao = _conectar()
    linhas = conexao.execute("""
        SELECT id, valor, data_recebimento, observacao, receita_id
        FROM recebimentos
        WHERE valor_receber_id = ?
        ORDER BY data_recebimento DESC, id DESC
    """, (id_valor,)).fetchall()
    conexao.close()
    return linhas


def listar_ids_receitas_vinculadas():
    conexao = _conectar()
    ids = {linha[0] for linha in conexao.execute("SELECT receita_id FROM recebimentos")}
    conexao.close()
    return ids


def receita_vinculada_a_recebimento(id_receita):
    conexao = _conectar()
    vinculada = conexao.execute(
        "SELECT 1 FROM recebimentos WHERE receita_id = ? LIMIT 1",
        (id_receita,),
    ).fetchone() is not None
    conexao.close()
    return vinculada


def desfazer_ultimo_recebimento(id_valor):
    conexao = _conectar()
    try:
        conexao.execute("BEGIN IMMEDIATE")
        recebimento = conexao.execute("""
            SELECT id, receita_id
            FROM recebimentos
            WHERE valor_receber_id = ?
            ORDER BY data_recebimento DESC, id DESC
            LIMIT 1
        """, (id_valor,)).fetchone()
        if not recebimento:
            conexao.rollback()
            return False, "Não há recebimento para desfazer."

        proximo = conexao.execute("""
            SELECT id, status
            FROM valores_receber
            WHERE gerado_de_id = ?
        """, (id_valor,)).fetchone()
        if proximo:
            movimentado = conexao.execute(
                "SELECT 1 FROM recebimentos WHERE valor_receber_id = ? LIMIT 1",
                (proximo[0],),
            ).fetchone()
            if movimentado or proximo[1] != "aberto":
                conexao.rollback()
                return False, (
                    "O próximo mês já possui movimentação. "
                    "Desfaça primeiro os recebimentos mais recentes."
                )
            conexao.execute("DELETE FROM valores_receber WHERE id = ?", (proximo[0],))

        conexao.execute("DELETE FROM recebimentos WHERE id = ?", (recebimento[0],))
        conexao.execute("DELETE FROM receitas WHERE id = ?", (recebimento[1],))
        conexao.execute(
            "UPDATE valores_receber SET status = 'aberto' WHERE id = ?",
            (id_valor,),
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
    return True, "Último recebimento desfeito."


def cancelar_valor_receber(id_valor):
    atual = buscar_valor_receber_por_id(id_valor)
    if not atual:
        return False, "O valor a receber não foi encontrado."
    if atual[11] in {"recebido", "cancelado"}:
        return False, "Este valor já está encerrado."

    conexao = _conectar()
    conexao.execute(
        "UPDATE valores_receber SET status = 'cancelado' WHERE id = ?",
        (id_valor,),
    )
    conexao.commit()
    conexao.close()
    return True, "Saldo restante cancelado."


def excluir_valor_receber(id_valor):
    atual = buscar_valor_receber_por_id(id_valor)
    if not atual:
        return False, "O valor a receber não foi encontrado."
    if atual[9] > 0:
        return False, (
            "Este valor possui recebimentos. Cancele o saldo restante "
            "ou desfaça os recebimentos antes de excluir."
        )

    conexao = _conectar()
    conexao.execute("DELETE FROM valores_receber WHERE id = ?", (id_valor,))
    conexao.commit()
    conexao.close()
    return True, "Valor excluído."

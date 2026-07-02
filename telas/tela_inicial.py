from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt

from componentes.tabela import TabelaFinanceira
from telas.nova_despesa import NovaDespesa
from telas.nova_receita import NovaReceita
from telas.novo_gasto import NovoGasto
from banco.banco import (
    listar_despesas,
    buscar_despesa_por_id,
    listar_receitas,
    listar_gastos,
    listar_pagamentos,
)


class JanelaDetalhesMes(QDialog):
    def __init__(self, titulo, subtitulo, secoes, cor="#3b82f6"):
        super().__init__()
        self.setWindowTitle(titulo)
        self.resize(760, 560)
        self.setMinimumSize(720, 500)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0f1117;
                color: #f8fafc;
                font-family: Segoe UI;
            }}

            QLabel#tituloDetalhe {{
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
            }}

            QLabel#subtituloDetalhe {{
                color: #9aa2b8;
                font-size: 14px;
            }}

            QLabel#secaoTitulo {{
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }}

            QLabel#resumoSecao {{
                color: #cbd5e1;
                font-size: 14px;
            }}

            QTableWidget {{
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #263244;
                border-radius: 10px;
                gridline-color: #263244;
                alternate-background-color: #162033;
                selection-background-color: {cor};
                selection-color: #ffffff;
                font-size: 14px;
            }}

            QTableWidget::item {{
                padding-left: 8px;
                padding-right: 8px;
                border-bottom: 1px solid #263244;
            }}

            QHeaderView::section {{
                background-color: #1f2937;
                color: #f8fafc;
                border: none;
                border-right: 1px solid #253044;
                border-bottom: 1px solid #334155;
                padding: 7px 8px;
                font-weight: bold;
                font-size: 14px;
            }}

            QPushButton#btnFechar {{
                background-color: #202638;
                color: #ffffff;
                padding: 11px 28px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2d3447;
            }}

            QPushButton#btnFechar:hover {{
                background-color: #2d3447;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloDetalhe")

        lbl_subtitulo = QLabel(subtitulo)
        lbl_subtitulo.setObjectName("subtituloDetalhe")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_subtitulo)

        for secao in secoes:
            itens = secao.get("itens", [])
            total = sum(float(item.get("valor", 0) or 0) for item in itens)

            cabecalho = QHBoxLayout()

            lbl_secao = QLabel(secao.get("titulo", ""))
            lbl_secao.setObjectName("secaoTitulo")

            lbl_resumo = QLabel(f"{len(itens)} itens • {self.formatar_moeda(total)}")
            lbl_resumo.setObjectName("resumoSecao")
            lbl_resumo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            cabecalho.addWidget(lbl_secao)
            cabecalho.addStretch()
            cabecalho.addWidget(lbl_resumo)
            layout.addLayout(cabecalho)

            tabela = self.criar_tabela(itens)
            layout.addWidget(tabela, 1)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("btnFechar")
        btn_fechar.clicked.connect(self.accept)

        botoes.addWidget(btn_fechar)
        layout.addLayout(botoes)

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def criar_item(self, texto, alinhamento=Qt.AlignCenter):
        item = QTableWidgetItem(str(texto))
        item.setTextAlignment(alinhamento)
        return item

    def criar_tabela(self, itens):
        tabela = QTableWidget()
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Tipo", "Situação"])
        tabela.verticalHeader().setVisible(False)
        tabela.setShowGrid(False)
        tabela.setAlternatingRowColors(True)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setFocusPolicy(Qt.NoFocus)
        tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabela.horizontalHeader().setStretchLastSection(False)
        tabela.horizontalHeader().setFixedHeight(34)

        larguras = [95, 250, 120, 130, 120]
        for indice, largura in enumerate(larguras):
            tabela.setColumnWidth(indice, largura)
            tabela.horizontalHeader().setSectionResizeMode(indice, QHeaderView.Fixed)

        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        tabela.setRowCount(len(itens))
        for linha, item in enumerate(itens):
            tabela.setRowHeight(linha, 34)
            tabela.setItem(linha, 0, self.criar_item(item.get("data", "")))
            tabela.setItem(linha, 1, self.criar_item(item.get("descricao", ""), Qt.AlignCenter))
            tabela.setItem(linha, 2, self.criar_item(self.formatar_moeda(item.get("valor", 0))))
            tabela.setItem(linha, 3, self.criar_item(item.get("tipo", "")))
            tabela.setItem(linha, 4, self.criar_item(item.get("situacao", "")))

        if not itens:
            tabela.setRowCount(1)
            tabela.setSpan(0, 0, 1, 5)
            tabela.setItem(0, 0, self.criar_item("Nenhum item encontrado para este mês."))
            tabela.setRowHeight(0, 40)

        return tabela


class TelaInicial(QWidget):
    def __init__(self, ao_salvar_despesa=None):
        super().__init__()
        self.ao_salvar_despesa = ao_salvar_despesa
        self.montar_tela()

    def saudacao_atual(self):
        hora = datetime.now().hour

        if 5 <= hora < 12:
            return "Bom dia"

        if 12 <= hora < 18:
            return "Boa tarde"

        return "Boa noite"

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa

        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m")
        except Exception:
            return data

    def converter_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").date()
        except Exception:
            return None

    def status_vencimento(self, data):
        hoje = date.today()

        if data < hoje:
            return "Atrasada"
        if data == hoje:
            return "Hoje"
        if data == hoje + timedelta(days=1):
            return "Amanhã"

        return f"Em {(data - hoje).days} dias"

    def obter_todas_despesas(self):
        despesas = []

        for despesa in listar_despesas():
            (
                id_despesa,
                descricao,
                valor,
                vencimento,
                categoria,
                tipo,
                parcela_atual,
                total_parcelas,
                _,
                status,
            ) = self.separar_despesa(despesa)

            data = self.converter_data(vencimento)

            if data is None:
                continue

            despesas.append({
                "id": id_despesa,
                "descricao": descricao,
                "valor": float(valor or 0),
                "vencimento": vencimento,
                "data": data,
                "tipo": tipo,
                "categoria": categoria,
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
                "status": status,
            })

        return despesas

    def obter_despesas(self):
        return [d for d in self.obter_todas_despesas() if d["status"] != "paga"]

    def obter_receitas(self):
        receitas = []

        for receita in listar_receitas():
            id_receita, descricao, valor, data_recebimento, categoria, observacao = receita
            data = self.converter_data(data_recebimento)

            if data is None:
                continue

            receitas.append({
                "id": id_receita,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_recebimento": data_recebimento,
                "data": data,
                "categoria": categoria,
                "observacao": observacao,
            })

        return receitas

    def obter_gastos(self):
        gastos = []

        for gasto in listar_gastos():
            id_gasto, descricao, valor, data_gasto, categoria, observacao = gasto
            data = self.converter_data(data_gasto)

            if data is None:
                continue

            gastos.append({
                "id": id_gasto,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_gasto": data_gasto,
                "data": data,
                "categoria": categoria,
                "observacao": observacao,
            })

        return gastos

    def obter_pagamentos(self):
        pagamentos = []

        for pagamento in listar_pagamentos():
            id_pagamento, id_despesa, descricao, valor, data_pagamento, categoria, tipo, parcela_atual, total_parcelas = pagamento
            data = self.converter_data(data_pagamento)

            if data is None:
                continue

            pagamentos.append({
                "id": id_pagamento,
                "id_despesa": id_despesa,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_pagamento": data_pagamento,
                "data": data,
                "categoria": categoria,
                "tipo": tipo,
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
            })

        return pagamentos

    def criar_card_resumo(self, objeto, icone, titulo, valor, info="", acao=None):
        card = QFrame()
        card.setObjectName(objeto)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(12)

        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("cardIcone")

        textos = QVBoxLayout()
        textos.setSpacing(0)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitulo")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("cardValorMini")

        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_valor)

        if info:
            lbl_info = QLabel(info)
            lbl_info.setObjectName("cardInfoMini")
            textos.addWidget(lbl_info)

        layout.addWidget(lbl_icone)
        layout.addLayout(textos)
        layout.addStretch()

        if acao:
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda evento: acao()
            card.setToolTip("Clique para ver os detalhes")

        return card

    def ajustar_tabela(self, tabela):
        tabela.horizontalHeader().setStretchLastSection(False)

    def item_detalhe(self, data, descricao, valor, tipo, situacao):
        return {
            "data": self.formatar_data(data),
            "descricao": descricao,
            "valor": float(valor or 0),
            "tipo": tipo,
            "situacao": situacao,
        }

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 16, 36, 12)
        layout.setSpacing(10)

        hoje = date.today()
        inicio_mes = hoje.replace(day=1)

        if hoje.month == 12:
            fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)

        despesas = self.obter_despesas()
        todas_despesas = self.obter_todas_despesas()
        receitas = self.obter_receitas()
        gastos = self.obter_gastos()
        pagamentos = self.obter_pagamentos()

        despesas_pendentes_mes = [d for d in despesas if inicio_mes <= d["data"] <= fim_mes]
        despesas_atrasadas = [d for d in despesas if d["data"] < hoje]
        despesas_pagas_mes_sem_historico = [
            d for d in todas_despesas
            if d["status"] == "paga" and inicio_mes <= d["data"] <= fim_mes
        ]

        receitas_mes = [r for r in receitas if inicio_mes <= r["data"] <= fim_mes]
        gastos_mes = [g for g in gastos if inicio_mes <= g["data"] <= fim_mes]
        pagamentos_mes = [p for p in pagamentos if inicio_mes <= p["data"] <= fim_mes]

        total_receitas_mes = sum(r["valor"] for r in receitas_mes)
        total_gastos_mes = sum(g["valor"] for g in gastos_mes)
        total_pagamentos_mes = sum(p["valor"] for p in pagamentos_mes)
        total_pagas_sem_historico = sum(d["valor"] for d in despesas_pagas_mes_sem_historico)
        total_pago_mes = total_gastos_mes + total_pagamentos_mes + total_pagas_sem_historico
        total_a_pagar_mes = sum(d["valor"] for d in despesas_pendentes_mes)
        total_atrasadas = sum(d["valor"] for d in despesas_atrasadas)
        saldo_mes = total_receitas_mes - total_pago_mes

        itens_pagos_contas = [
            self.item_detalhe(
                p["data_pagamento"],
                p["descricao"],
                p["valor"],
                p["tipo"],
                "Paga",
            )
            for p in pagamentos_mes
        ]

        itens_pagos_contas.extend([
            self.item_detalhe(
                d["vencimento"],
                d["descricao"],
                d["valor"],
                d["tipo"],
                "Paga",
            )
            for d in despesas_pagas_mes_sem_historico
        ])

        itens_gastos = [
            self.item_detalhe(
                g["data_gasto"],
                g["descricao"],
                g["valor"],
                "Gasto",
                "Pago",
            )
            for g in gastos_mes
        ]

        itens_pendentes = [
            self.item_detalhe(
                d["vencimento"],
                d["descricao"],
                d["valor"],
                d["tipo"],
                self.status_vencimento(d["data"]),
            )
            for d in sorted(despesas_pendentes_mes, key=lambda item: item["data"])
        ]

        self.detalhes_pagos = [
            {"titulo": "Contas pagas", "itens": sorted(itens_pagos_contas, key=lambda item: item["data"])},
            {"titulo": "Gastos realizados", "itens": sorted(itens_gastos, key=lambda item: item["data"])},
        ]
        self.detalhes_pendentes = [
            {"titulo": "Contas pendentes do mês", "itens": itens_pendentes},
            {"titulo": "Atrasadas", "itens": [
                self.item_detalhe(
                    d["vencimento"],
                    d["descricao"],
                    d["valor"],
                    d["tipo"],
                    "Atrasada",
                )
                for d in sorted(despesas_atrasadas, key=lambda item: item["data"])
            ]},
        ]

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel(f"{self.saudacao_atual()}, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Resumo financeiro deste mês")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")
        btn_despesa.clicked.connect(self.abrir_nova_despesa)

        btn_gasto = QPushButton("🛒  Novo gasto")
        btn_gasto.setObjectName("btnDespesa")
        btn_gasto.clicked.connect(self.abrir_novo_gasto)

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")
        btn_receita.clicked.connect(self.abrir_nova_receita)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_gasto)
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        resumo = QHBoxLayout()
        resumo.setSpacing(12)

        resumo.addWidget(self.criar_card_resumo("cardSaldo", "💰", "Saldo atual", self.formatar_moeda(saldo_mes)))
        resumo.addWidget(self.criar_card_resumo("cardReceita", "📈", "Receitas do mês", self.formatar_moeda(total_receitas_mes), f"{len(receitas_mes)} entradas"))
        resumo.addWidget(self.criar_card_resumo(
            "cardDespesa",
            "✅",
            "Pago no mês",
            self.formatar_moeda(total_pago_mes),
            f"{len(itens_pagos_contas)} contas + {len(gastos_mes)} gastos",
            self.abrir_detalhes_pagos,
        ))
        resumo.addWidget(self.criar_card_resumo(
            "cardAtrasada",
            "📌",
            "A pagar",
            self.formatar_moeda(total_a_pagar_mes),
            f"{len(despesas_pendentes_mes)} pendentes • {len(despesas_atrasadas)} atrasadas",
            self.abrir_detalhes_pendentes,
        ))

        layout.addLayout(resumo)

        painel = QFrame()
        painel.setObjectName("card")

        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(22, 12, 22, 12)
        painel_layout.setSpacing(8)

        titulo_lista = QLabel("📅 Próximos vencimentos")
        titulo_lista.setObjectName("cardValor")
        titulo_lista.setStyleSheet("font-size: 19px;")

        painel_layout.addWidget(titulo_lista)

        tabela = TabelaFinanceira(["Data", "Descrição", "Valor", "Situação", "Parcela"])
        self.ajustar_tabela(tabela)
        tabela.cellDoubleClicked.connect(lambda linha, coluna, t=tabela: self.editar_despesa_tabela(t, linha))

        proximas = sorted(despesas, key=lambda d: d["data"])

        for despesa in proximas:
            parcela = "-"

            if despesa["tipo"] == "Parcelamento" and despesa["parcela_atual"] and despesa["total_parcelas"]:
                parcela = f"{despesa['parcela_atual']}/{despesa['total_parcelas']}"

            tabela.adicionar_linha([
                self.formatar_data(despesa["vencimento"]),
                despesa["descricao"],
                self.formatar_moeda(despesa["valor"]),
                self.status_vencimento(despesa["data"]),
                parcela
            ], despesa["id"])

        painel_layout.addWidget(tabela, 1)
        layout.addWidget(painel, 1)

    def abrir_detalhes_pagos(self):
        janela = JanelaDetalhesMes(
            "Pago no mês",
            "Contas e gastos que já saíram do seu dinheiro neste mês.",
            self.detalhes_pagos,
            "#22c55e",
        )
        janela.exec()

    def abrir_detalhes_pendentes(self):
        janela = JanelaDetalhesMes(
            "A pagar",
            "Contas do mês que ainda precisam ser pagas.",
            self.detalhes_pendentes,
            "#ef4444",
        )
        janela.exec()

    def editar_despesa_tabela(self, tabela, linha):
        item = tabela.item(linha, 0)

        if item is None:
            return

        id_despesa = item.data(Qt.UserRole)

        if not id_despesa:
            return

        despesa = buscar_despesa_por_id(id_despesa)

        if not despesa:
            return

        janela = NovaDespesa(despesa)

        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_nova_despesa(self):
        janela = NovaDespesa()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_novo_gasto(self):
        janela = NovoGasto()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_nova_receita(self):
        janela = NovaReceita()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

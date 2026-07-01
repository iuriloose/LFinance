from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QHeaderView
)

from componentes.tabela import TabelaFinanceira
from telas.nova_despesa import NovaDespesa
from banco.banco import listar_despesas


class TelaInicial(QWidget):
    def __init__(self, ao_salvar_despesa=None):
        super().__init__()
        self.ao_salvar_despesa = ao_salvar_despesa
        self.montar_tela()

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

    def obter_despesas(self):
        despesas = []

        for despesa in listar_despesas():
            (
                _,
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

            if status == "paga" or data is None:
                continue

            despesas.append({
                "descricao": descricao,
                "valor": float(valor or 0),
                "vencimento": vencimento,
                "data": data,
                "tipo": tipo,
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
            })

        return despesas

    def criar_card_resumo(self, objeto, icone, titulo, valor, info=""):
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

        return card

    def ajustar_tabela(self, tabela):
        tabela.horizontalHeader().setStretchLastSection(False)

        tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)

        tabela.setColumnWidth(0, 95)
        tabela.setColumnWidth(1, 380)
        tabela.setColumnWidth(2, 150)
        tabela.setColumnWidth(3, 170)
        tabela.setColumnWidth(4, 105)

        tabela.setStyleSheet(tabela.styleSheet() + """
            QTableWidget {
                border-radius: 14px;
                background-color: #111827;
                gridline-color: #263247;
            }

            QHeaderView::section {
                background-color: #1f2937;
                color: #ffffff;
                border: none;
                border-bottom: 1px solid #334155;
                padding: 8px;
                font-weight: bold;
            }

            QTableCornerButton::section {
                background-color: #1f2937;
                border: none;
                border-bottom: 1px solid #334155;
            }
        """)

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

        fim_semana = hoje + timedelta(days=7)

        despesas = self.obter_despesas()

        despesas_mes = [d for d in despesas if inicio_mes <= d["data"] <= fim_mes]
        despesas_atrasadas = [d for d in despesas if d["data"] < hoje]
        despesas_hoje = [d for d in despesas if d["data"] == hoje]
        despesas_semana = [d for d in despesas if hoje <= d["data"] <= fim_semana]

        total_mes = sum(d["valor"] for d in despesas_mes)
        total_atrasadas = sum(d["valor"] for d in despesas_atrasadas)
        total_hoje = sum(d["valor"] for d in despesas_hoje)
        total_semana = sum(d["valor"] for d in despesas_semana)

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel("Bom dia, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Resumo financeiro deste mês")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")
        btn_despesa.clicked.connect(self.abrir_nova_despesa)

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        resumo = QHBoxLayout()
        resumo.setSpacing(12)

        resumo.addWidget(self.criar_card_resumo("cardSaldo", "💰", "Saldo atual", "R$ 0,00"))
        resumo.addWidget(self.criar_card_resumo("cardReceita", "📈", "Receitas do mês", "R$ 0,00"))
        resumo.addWidget(self.criar_card_resumo("cardDespesa", "💸", "Despesas do mês", self.formatar_moeda(total_mes), f"{len(despesas_mes)} contas"))
        resumo.addWidget(self.criar_card_resumo("cardAtrasada", "🚨", "Atrasadas", self.formatar_moeda(total_atrasadas), f"{len(despesas_atrasadas)} contas"))

        layout.addLayout(resumo)

        faixa = QFrame()
        faixa.setObjectName("card")
        faixa.setFixedHeight(40)

        faixa_layout = QHBoxLayout(faixa)
        faixa_layout.setContentsMargins(22, 5, 22, 5)
        faixa_layout.setSpacing(18)

        labels_faixa = [
            QLabel(f"📅 Hoje: {self.formatar_moeda(total_hoje)}  ({len(despesas_hoje)})"),
            QLabel(f"📆 Semana: {self.formatar_moeda(total_semana)}  ({len(despesas_semana)})"),
            QLabel(f"🗓️ Mês: {self.formatar_moeda(total_mes)}  ({len(despesas_mes)})"),
        ]

        for label in labels_faixa:
            label.setObjectName("linhaDespesa")
            label.setStyleSheet("font-size: 14px;")
            faixa_layout.addWidget(label)

        layout.addWidget(faixa)

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
            ])

        painel_layout.addWidget(tabela, 1)
        layout.addWidget(painel, 1)

    def abrir_nova_despesa(self):
        janela = NovaDespesa()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()
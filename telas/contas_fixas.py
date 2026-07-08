from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import QDate, Qt

from banco.banco import (
    listar_despesas,
    pagar_despesa,
    excluir_despesa,
    reabrir_despesa,
)
from telas.nova_despesa import NovaDespesa


class ConfirmacaoExclusaoContaFixa(QDialog):
    def __init__(self, descricao):
        super().__init__()

        self.setWindowTitle("Excluir conta fixa")
        self.setFixedSize(430, 230)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #0f1117;
            }

            QLabel {
                color: #f8fafc;
                font-family: Segoe UI;
                background-color: transparent;
            }

            QLabel#tituloConfirmacao {
                font-size: 24px;
                font-weight: 800;
            }

            QLabel#textoConfirmacao {
                font-size: 12px;
                color: #cbd5e1;
            }

            QLabel#itemConfirmacao {
                font-size: 15px;
                color: #ffffff;
                background-color: #151c2b;
                border: 1px solid #26364e;
                border-radius: 12px;
                padding: 12px;
            }

            QPushButton {
                min-height: 42px;
                border-radius: 11px;
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
                padding: 0 18px;
            }

            QPushButton#btnCancelarConfirmacao {
                background-color: #1f2937;
                border: 1px solid #334155;
            }

            QPushButton#btnCancelarConfirmacao:hover {
                background-color: #273449;
                border: 1px solid #64748b;
            }

            QPushButton#btnExcluirConfirmacao {
                background-color: #dc2626;
                border: 1px solid #ef4444;
            }

            QPushButton#btnExcluirConfirmacao:hover {
                background-color: #ef4444;
                border: 1px solid #f87171;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(14)

        titulo = QLabel("Excluir conta fixa")
        titulo.setObjectName("tituloConfirmacao")

        texto = QLabel("Tem certeza que deseja excluir esta conta fixa?")
        texto.setObjectName("textoConfirmacao")

        item = QLabel(descricao)
        item.setObjectName("itemConfirmacao")

        botoes = QHBoxLayout()
        botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelarConfirmacao")
        btn_cancelar.clicked.connect(self.reject)

        btn_excluir = QPushButton("🗑  Excluir")
        btn_excluir.setObjectName("btnExcluirConfirmacao")
        btn_excluir.clicked.connect(self.accept)

        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_excluir)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addWidget(item)
        layout.addStretch()
        layout.addLayout(botoes)


class TelaContasFixas(QWidget):
    def __init__(self, ao_alterar=None):
        super().__init__()

        self.ao_alterar = ao_alterar

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(36, 30, 36, 24)
        self.layout_principal.setSpacing(16)

        self.aplicar_estilo_local()
        self.montar_tela()

    def aplicar_estilo_local(self):
        self.setStyleSheet("""
            QFrame#cardContaFixaLista {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #223149;
                border-left: 4px solid #ef4444;
                border-radius: 9px;
            }

            QFrame#cardContaFixaLista:hover {
                border: 1px solid #fbbf24;
                background-color: rgba(24, 34, 52, 0.98);
            }

            QLabel#tituloContaFixaLista {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#valorContaFixaLista {
                color: #ffffff;
                font-size: 16px;
                font-weight: 900;
            }

            QLabel#infoContaFixaLista {
                color: #d7dcf0;
                font-size: 12px;
            }

            QLabel#statusPagoLista {
                color: #22c55e;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#statusAbertoLista {
                color: #22c55e;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#statusAtrasadoLista {
                color: #ef4444;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton#btnNovaContaFixa {
                background-color: rgba(30, 41, 59, 0.78);
                color: white;
                padding: 10px 18px;
                border-radius: 11px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #92400e;
            }

            QPushButton#btnNovaContaFixa:hover {
                background-color: rgba(74, 48, 11, 0.34);
                border: 1px solid #f59e0b;
            }

            QPushButton#btnPagarContaFixaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #16a34a;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnPagarContaFixaLista:hover {
                background-color: rgba(22, 163, 74, 0.24);
                border: 1px solid #4ade80;
            }

            QPushButton#btnEditarContaFixaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnEditarContaFixaLista:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnExcluirContaFixaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #7f1d1d;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnExcluirContaFixaLista:hover {
                background-color: rgba(127, 29, 29, 0.34);
                border: 1px solid #ef4444;
            }

            QScrollArea#areaContasFixas {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaContasFixas > QWidget > QWidget {
                background-color: transparent;
            }

            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 4px 0px 4px 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #334155;
                border-radius: 5px;
                min-height: 34px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #475569;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def limpar_tela(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa

        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def formatar_data(self, data):
        partes = data.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data

    def formatar_moeda(self, valor):
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def texto_status(self, vencimento, status):
        if status == "paga":
            return "Paga", "statusPagoLista"

        hoje = QDate.currentDate()
        data = QDate.fromString(vencimento, "yyyy-MM-dd")

        if data.isValid() and data < hoje:
            return "Atrasada", "statusAtrasadoLista"

        return "Em aberto", "statusAbertoLista"

    def obter_contas_fixas(self):
        contas = []
        for despesa in listar_despesas():
            dados = self.separar_despesa(despesa)
            if dados[5] == "Conta fixa":
                contas.append(despesa)
        return self.ordenar_contas(contas)

    def ordenar_contas(self, contas):
        hoje = QDate.currentDate()

        def ordem(conta):
            _, _, _, vencimento, _, _, _, _, _, status = self.separar_despesa(conta)
            data = QDate.fromString(vencimento, "yyyy-MM-dd")

            if status == "paga":
                return (2, vencimento)
            if data.isValid() and data < hoje:
                return (0, vencimento)
            return (1, vencimento)

        return sorted(contas, key=ordem)

    def criar_card_conta(self, conta):
        (
            id_despesa,
            descricao,
            valor,
            vencimento,
            categoria,
            tipo,
            parcela_atual,
            total_parcelas,
            valor_total,
            status,
        ) = self.separar_despesa(conta)

        card = QFrame()
        card.setObjectName("cardContaFixaLista")
        card.setMinimumHeight(72)
        card.setMaximumHeight(78)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 12, 8)
        card_layout.setSpacing(5)

        topo = QHBoxLayout()
        topo.setSpacing(10)

        titulo = QLabel(descricao)
        titulo.setObjectName("tituloContaFixaLista")

        valor_label = QLabel(self.formatar_moeda(valor))
        valor_label.setObjectName("valorContaFixaLista")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        topo.addWidget(titulo, 1)
        topo.addWidget(valor_label)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(8)

        info = QLabel(
            f"📅 {self.formatar_data(vencimento)}   "
            f"📂 {categoria}  •  "
            f"🔁 Conta fixa mensal"
        )
        info.setObjectName("infoContaFixaLista")
        info.setWordWrap(False)

        status_texto, status_objeto = self.texto_status(vencimento, status)
        status_label = QLabel(f"● {status_texto}")
        status_label.setObjectName(status_objeto)
        status_label.setAlignment(Qt.AlignCenter)

        if status == "paga":
            btn_pago = QPushButton("↩  Reabrir")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.reabrir(id))
        else:
            btn_pago = QPushButton("✓  Pagar")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.marcar_paga(id))

        btn_pago.setObjectName("btnPagarContaFixaLista")
        btn_pago.setToolTip("Pagar ou reabrir\n\nMarca a conta fixa do mês como paga ou desfaz o pagamento.")
        btn_pago.setFixedSize(82, 24)

        btn_editar = QPushButton("✏  Editar")
        btn_editar.setObjectName("btnEditarContaFixaLista")
        btn_editar.setToolTip("Editar conta fixa\n\nAltera os dados desta conta recorrente.")
        btn_editar.setFixedSize(82, 24)
        btn_editar.clicked.connect(lambda _, d=conta: self.editar(d))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnExcluirContaFixaLista")
        btn_excluir.setToolTip("Excluir conta fixa\n\nRemove esta conta recorrente do LFinance após confirmação.")
        btn_excluir.setFixedSize(36, 24)
        btn_excluir.clicked.connect(lambda _, id=id_despesa, d=descricao: self.excluir(id, d))

        detalhes.addWidget(info, 1)
        detalhes.addWidget(status_label)
        detalhes.addWidget(btn_pago)
        detalhes.addWidget(btn_editar)
        detalhes.addWidget(btn_excluir)

        card_layout.addLayout(topo)
        card_layout.addLayout(detalhes)

        card.mouseDoubleClickEvent = lambda evento, d=conta: self.editar(d)
        card.setToolTip("Dê dois cliques para editar esta conta fixa")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("📅 Contas Fixas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Contas recorrentes cadastradas como tipo Conta fixa")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nova = QPushButton("+  Nova conta fixa")
        btn_nova.setObjectName("btnNovaContaFixa")
        btn_nova.setToolTip("Nova conta fixa\\n\\nCadastre uma despesa recorrente que se repete todo mês, como internet, aluguel ou mensalidade.")
        btn_nova.clicked.connect(self.nova_conta_fixa)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_nova)

        self.layout_principal.addLayout(topo)

        contas = self.obter_contas_fixas()

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        abertas = sum(1 for c in contas if self.separar_despesa(c)[9] != "paga")
        pagas = sum(1 for c in contas if self.separar_despesa(c)[9] == "paga")
        resumo = QLabel(f"{len(contas)} conta(s) fixa(s) cadastrada(s)  •  {abertas} em aberto  •  {pagas} paga(s)")
        resumo.setObjectName("cardInfo")
        painel_layout.addWidget(resumo)

        area = QScrollArea()
        area.setObjectName("areaContasFixas")
        area.setWidgetResizable(True)

        conteudo = QWidget()
        conteudo.setAttribute(Qt.WA_StyledBackground, True)
        conteudo.setStyleSheet("background-color: transparent;")

        lista_layout = QVBoxLayout(conteudo)
        lista_layout.setContentsMargins(0, 0, 8, 0)
        lista_layout.setSpacing(12)

        if not contas:
            vazio = QLabel("Nenhuma conta fixa cadastrada. Cadastre uma despesa com o tipo Conta fixa para ela aparecer aqui.")
            vazio.setObjectName("cardInfo")
            vazio.setWordWrap(True)
            lista_layout.addWidget(vazio)
        else:
            for conta in contas:
                lista_layout.addWidget(self.criar_card_conta(conta))

        lista_layout.addStretch()
        area.setWidget(conteudo)

        painel_layout.addWidget(area, 1)
        self.layout_principal.addWidget(painel, 1)

    def nova_conta_fixa(self):
        janela = NovaDespesa()
        janela.tipo.setCurrentText("Conta fixa")

        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def marcar_paga(self, id_despesa):
        pagar_despesa(id_despesa)
        self.montar_tela()
        if self.ao_alterar:
            self.ao_alterar()

    def reabrir(self, id_despesa):
        reabrir_despesa(id_despesa)
        self.montar_tela()
        if self.ao_alterar:
            self.ao_alterar()

    def editar(self, conta):
        janela = NovaDespesa(conta)

        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def excluir(self, id_despesa, descricao="esta conta fixa"):
        janela = ConfirmacaoExclusaoContaFixa(descricao)

        if janela.exec():
            excluir_despesa(id_despesa)
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

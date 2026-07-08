from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import Qt

from banco.banco import listar_gastos, excluir_gasto
from telas.novo_gasto import NovoGasto


class ConfirmacaoExclusao(QDialog):
    def __init__(self, descricao):
        super().__init__()

        self.setWindowTitle("Excluir gasto")
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

        titulo = QLabel("Excluir gasto")
        titulo.setObjectName("tituloConfirmacao")

        texto = QLabel("Tem certeza que deseja excluir este gasto?")
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


class TelaGastos(QWidget):
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
            QFrame#cardGasto {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #223149;
                border-left: 4px solid #ef4444;
                border-radius: 9px;
            }

            QFrame#cardGasto:hover {
                border: 1px solid #ef4444;
                background-color: rgba(24, 34, 52, 0.98);
            }

            QLabel#tituloGasto {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#valorGasto {
                color: #ffffff;
                font-size: 16px;
                font-weight: 900;
            }

            QLabel#infoGasto {
                color: #d7dcf0;
                font-size: 12px;
            }

            QPushButton#btnEditarGasto {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnEditarGasto:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnExcluirGasto {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #7f1d1d;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnExcluirGasto:hover {
                background-color: rgba(127, 29, 29, 0.34);
                border: 1px solid #ef4444;
            }

            QScrollArea#areaGastos {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaGastos > QWidget > QWidget {
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

    def formatar_data(self, data):
        partes = data.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data

    def formatar_moeda(self, valor):
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def criar_card_gasto(self, gasto):
        id_gasto, descricao, valor, data_gasto, categoria, observacao = gasto

        card = QFrame()
        card.setObjectName("cardGasto")
        card.setMinimumHeight(72)
        card.setMaximumHeight(78)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 12, 8)
        card_layout.setSpacing(5)

        topo = QHBoxLayout()
        topo.setSpacing(10)

        titulo = QLabel(descricao)
        titulo.setObjectName("tituloGasto")

        valor_label = QLabel(self.formatar_moeda(valor))
        valor_label.setObjectName("valorGasto")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        topo.addWidget(titulo, 1)
        topo.addWidget(valor_label)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(8)

        extra = f"  •  📝 {observacao}" if observacao else ""
        info = QLabel(f"📅 {self.formatar_data(data_gasto)}   📂 {categoria}{extra}")
        info.setObjectName("infoGasto")
        info.setWordWrap(False)

        btn_editar = QPushButton("✏  Editar")
        btn_editar.setObjectName("btnEditarGasto")
        btn_editar.setToolTip("Editar gasto\n\nAltera descrição, valor, data ou observação deste gasto.")
        btn_editar.setFixedSize(82, 24)
        btn_editar.clicked.connect(lambda _, g=gasto: self.editar(g))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnExcluirGasto")
        btn_excluir.setToolTip("Excluir gasto\n\nRemove este gasto do LFinance após confirmação.")
        btn_excluir.setFixedSize(36, 24)
        btn_excluir.clicked.connect(lambda _, id=id_gasto, d=descricao: self.excluir(id, d))

        detalhes.addWidget(info, 1)
        detalhes.addWidget(btn_editar)
        detalhes.addWidget(btn_excluir)

        card_layout.addLayout(topo)
        card_layout.addLayout(detalhes)

        card.mouseDoubleClickEvent = lambda evento, g=gasto: self.editar(g)
        card.setToolTip("Dê dois cliques para editar este gasto")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("Gastos")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Gastos já pagos, como mercado, gasolina e compras do dia")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_novo = QPushButton("🛒  Novo gasto")
        btn_novo.setObjectName("btnDespesa")
        btn_novo.setToolTip("Novo gasto\\n\\nRegistre uma saída paga na hora, como mercado, combustível, farmácia ou lazer.")
        btn_novo.clicked.connect(self.novo_gasto)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_novo)

        self.layout_principal.addLayout(topo)

        gastos = listar_gastos()

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        resumo = QLabel(f"{len(gastos)} gasto(s) cadastrado(s)")
        resumo.setObjectName("cardInfo")
        painel_layout.addWidget(resumo)

        area = QScrollArea()
        area.setObjectName("areaGastos")
        area.setWidgetResizable(True)

        conteudo = QWidget()
        conteudo.setAttribute(Qt.WA_StyledBackground, True)
        conteudo.setStyleSheet("background-color: transparent;")

        lista_layout = QVBoxLayout(conteudo)
        lista_layout.setContentsMargins(0, 0, 8, 0)
        lista_layout.setSpacing(12)

        if not gastos:
            vazio = QLabel("Nenhum gasto cadastrado.")
            vazio.setObjectName("cardInfo")
            lista_layout.addWidget(vazio)
        else:
            for gasto in gastos:
                lista_layout.addWidget(self.criar_card_gasto(gasto))

        lista_layout.addStretch()
        area.setWidget(conteudo)

        painel_layout.addWidget(area, 1)
        self.layout_principal.addWidget(painel, 1)

    def novo_gasto(self):
        janela = NovoGasto()
        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def editar(self, gasto):
        janela = NovoGasto(gasto)
        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def excluir(self, id_gasto, descricao="este gasto"):
        janela = ConfirmacaoExclusao(descricao)

        if janela.exec():
            excluir_gasto(id_gasto)
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

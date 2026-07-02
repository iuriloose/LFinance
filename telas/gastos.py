from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QScrollArea
)

from banco.banco import listar_gastos, excluir_gasto
from telas.novo_gasto import NovoGasto


class TelaGastos(QWidget):
    def __init__(self, ao_alterar=None):
        super().__init__()

        self.ao_alterar = ao_alterar

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(36, 30, 36, 24)
        self.layout_principal.setSpacing(12)

        self.montar_tela()

    def limpar_tela(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        card.setObjectName("card")
        card.setFixedHeight(82)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 10, 18, 10)
        card_layout.setSpacing(12)

        linha1 = QLabel(
            f"<b>{descricao}</b> &nbsp;&nbsp; "
            f"<span style='color:#f59e0b;'>{self.formatar_moeda(valor)}</span>"
        )
        linha1.setObjectName("linhaDespesa")

        extra = f"  •  📝 {observacao}" if observacao else ""
        linha2 = QLabel(
            f"📅 {self.formatar_data(data_gasto)}  •  "
            f"📂 {categoria}{extra}"
        )
        linha2.setObjectName("cardInfo")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.addWidget(linha1)
        info_layout.addWidget(linha2)

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        btn_editar = QPushButton("✏")
        btn_editar.setObjectName("btnReceita")
        btn_editar.setFixedWidth(54)
        btn_editar.clicked.connect(lambda _, g=gasto: self.editar(g))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnDespesa")
        btn_excluir.setFixedWidth(54)
        btn_excluir.clicked.connect(lambda _, id=id_gasto: self.excluir(id))

        botoes.addWidget(btn_editar)
        botoes.addWidget(btn_excluir)

        card_layout.addLayout(info_layout, 1)
        card_layout.addLayout(botoes)

        card.mouseDoubleClickEvent = lambda evento, g=gasto: self.editar(g)
        card.setToolTip("Dê dois cliques para editar este gasto")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel("Gastos")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Gastos já pagos, como mercado, gasolina e compras do dia")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_novo = QPushButton("🛒  Novo gasto")
        btn_novo.setObjectName("btnDespesa")
        btn_novo.clicked.connect(self.novo_gasto)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_novo)

        self.layout_principal.addLayout(topo)

        gastos = listar_gastos()

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f1117;
            }

            QScrollArea > QWidget > QWidget {
                background-color: #0f1117;
            }

            QScrollBar:vertical {
                background-color: #0f1117;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #2d3447;
                border-radius: 5px;
                min-height: 30px;
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

        conteudo = QWidget()
        conteudo.setStyleSheet("background-color: #0f1117;")

        lista_layout = QVBoxLayout(conteudo)
        lista_layout.setContentsMargins(0, 0, 0, 0)
        lista_layout.setSpacing(10)

        if not gastos:
            vazio = QLabel("Nenhum gasto cadastrado.")
            vazio.setObjectName("cardInfo")
            lista_layout.addWidget(vazio)
        else:
            for gasto in gastos:
                lista_layout.addWidget(self.criar_card_gasto(gasto))

        lista_layout.addStretch()
        area.setWidget(conteudo)

        self.layout_principal.addWidget(area, 1)

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

    def excluir(self, id_gasto):
        resposta = QMessageBox.question(
            self,
            "Excluir gasto",
            "Tem certeza que deseja excluir este gasto?"
        )

        if resposta == QMessageBox.Yes:
            excluir_gasto(id_gasto)
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

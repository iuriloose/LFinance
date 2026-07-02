from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import QDate

from banco.banco import (
    listar_despesas,
    pagar_despesa,
    excluir_despesa,
    reabrir_despesa,
)

from telas.nova_despesa import NovaDespesa


class TelaDespesas(QWidget):
    def __init__(self):
        super().__init__()

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(36, 30, 36, 24)
        self.layout_principal.setSpacing(12)

        self.montar_tela()

    def limpar_tela(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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

    def texto_status(self, vencimento, status):
        if status == "paga":
            return "✅ Paga"

        hoje = QDate.currentDate()
        data = QDate.fromString(vencimento, "yyyy-MM-dd")

        if data.isValid() and data < hoje:
            return "🔴 Atrasada"

        return "🟢 Em aberto"

    def ordenar_despesas(self, despesas):
        hoje = QDate.currentDate()

        def ordem(despesa):
            _, _, _, vencimento, _, _, _, _, _, status = self.separar_despesa(despesa)

            if status == "paga":
                return (2, vencimento)

            data = QDate.fromString(vencimento, "yyyy-MM-dd")

            if data.isValid() and data < hoje:
                return (0, vencimento)

            return (1, vencimento)

        return sorted(despesas, key=ordem)

    def criar_card_despesa(self, despesa):
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
        ) = self.separar_despesa(despesa)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(82)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 10, 18, 10)
        card_layout.setSpacing(12)

        vencimento_formatado = self.formatar_data(vencimento)
        status_texto = self.texto_status(vencimento, status)

        parcela_texto = ""
        if tipo == "Parcelamento" and parcela_atual and total_parcelas:
            parcela_texto = f" • {parcela_atual}/{total_parcelas}"

        total_texto = ""
        if tipo == "Parcelamento" and valor_total:
            total_texto = f" • Total R$ {valor_total:.2f}"

        linha1 = QLabel(
            f"<b>{descricao}</b> &nbsp;&nbsp; "
            f"<span style='color:#ffffff;'>R$ {valor:.2f}</span>"
        )
        linha1.setObjectName("linhaDespesa")

        linha2 = QLabel(
            f"📅 {vencimento_formatado}  •  "
            f"📂 {categoria}  •  "
            f"📄 {tipo}"
            f"{parcela_texto}"
            f"{total_texto}  •  "
            f"{status_texto}"
        )
        linha2.setObjectName("cardInfo")

        linha1.setText(linha1.text().replace(".", ","))
        linha2.setText(linha2.text().replace(".", ","))

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.addWidget(linha1)
        info_layout.addWidget(linha2)

        botoes = QHBoxLayout()
        botoes.setSpacing(8)

        if status == "paga":
            btn_pago = QPushButton("↩")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.reabrir(id))
        else:
            btn_pago = QPushButton("✔")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.marcar_paga(id))

        btn_pago.setObjectName("btnReceita")
        btn_pago.setFixedWidth(54)

        btn_editar = QPushButton("✏")
        btn_editar.setObjectName("btnReceita")
        btn_editar.setFixedWidth(54)
        btn_editar.clicked.connect(lambda _, d=despesa: self.editar(d))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnDespesa")
        btn_excluir.setFixedWidth(54)
        btn_excluir.clicked.connect(lambda _, id=id_despesa: self.excluir(id))

        botoes.addWidget(btn_pago)
        botoes.addWidget(btn_editar)
        botoes.addWidget(btn_excluir)

        card_layout.addLayout(info_layout, 1)
        card_layout.addLayout(botoes)

        card.mouseDoubleClickEvent = lambda evento, d=despesa: self.editar(d)
        card.setToolTip("Dê dois cliques para editar esta despesa")

        return card

    def montar_tela(self):
        self.limpar_tela()

        titulo = QLabel("Despesas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Veja, edite, pague ou exclua suas despesas")
        subtitulo.setObjectName("subtitulo")

        self.layout_principal.addWidget(titulo)
        self.layout_principal.addWidget(subtitulo)

        despesas = self.ordenar_despesas(listar_despesas())

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

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada.")
            vazio.setObjectName("cardInfo")
            lista_layout.addWidget(vazio)
        else:
            for despesa in despesas:
                lista_layout.addWidget(self.criar_card_despesa(despesa))

        lista_layout.addStretch()
        area.setWidget(conteudo)

        self.layout_principal.addWidget(area, 1)

    def marcar_paga(self, id_despesa):
        pagar_despesa(id_despesa)
        self.montar_tela()

    def reabrir(self, id_despesa):
        reabrir_despesa(id_despesa)
        self.montar_tela()

    def editar(self, despesa):
        janela = NovaDespesa(despesa)

        if janela.exec():
            self.montar_tela()

    def excluir(self, id_despesa):
        resposta = QMessageBox.question(
            self,
            "Excluir despesa",
            "Tem certeza que deseja excluir esta despesa?"
        )

        if resposta == QMessageBox.Yes:
            excluir_despesa(id_despesa)
            self.montar_tela()

    def recarregar(self):
        self.montar_tela()
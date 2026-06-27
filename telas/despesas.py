from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)

from banco.banco import listar_despesas, marcar_despesa_como_paga, excluir_despesa


class TelaDespesas(QWidget):
    def __init__(self):
        super().__init__()
        self.montar_tela()

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(18)

        titulo = QLabel("Despesas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Veja, pague ou exclua suas despesas cadastradas")
        subtitulo.setObjectName("subtitulo")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        despesas = listar_despesas()

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada.")
            vazio.setObjectName("cardInfo")
            layout.addWidget(vazio)
            return

        for despesa in despesas:
            id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa

            card = QFrame()
            card.setObjectName("card")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(18, 14, 18, 14)
            card_layout.setSpacing(12)

            info = QLabel(
                f"{descricao}\n"
                f"Vencimento: {vencimento} • Categoria: {categoria} • Tipo: {tipo} • Status: {status}\n"
                f"R$ {valor:.2f}".replace(".", ",")
            )
            info.setObjectName("linhaDespesa")

            btn_pago = QPushButton("Marcar paga")
            btn_pago.setObjectName("btnReceita")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.marcar_paga(id))

            btn_excluir = QPushButton("Excluir")
            btn_excluir.setObjectName("btnDespesa")
            btn_excluir.clicked.connect(lambda _, id=id_despesa: self.excluir(id))

            card_layout.addWidget(info)
            card_layout.addStretch()
            card_layout.addWidget(btn_pago)
            card_layout.addWidget(btn_excluir)

            layout.addWidget(card)

        layout.addStretch()

    def marcar_paga(self, id_despesa):
        marcar_despesa_como_paga(id_despesa)
        self.recarregar()

    def excluir(self, id_despesa):
        resposta = QMessageBox.question(
            self,
            "Excluir despesa",
            "Tem certeza que deseja excluir esta despesa?"
        )

        if resposta == QMessageBox.Yes:
            excluir_despesa(id_despesa)
            self.recarregar()

    def recarregar(self):
        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.montar_tela()
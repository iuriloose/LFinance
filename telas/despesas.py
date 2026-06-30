from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import QDate

from banco.banco import (
    listar_despesas,
    marcar_despesa_como_paga,
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

    def montar_tela(self):
        self.limpar_tela()

        titulo = QLabel("Despesas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Veja, edite, pague ou exclua suas despesas")
        subtitulo.setObjectName("subtitulo")

        self.layout_principal.addWidget(titulo)
        self.layout_principal.addWidget(subtitulo)

        despesas = listar_despesas()

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada.")
            vazio.setObjectName("cardInfo")
            self.layout_principal.addWidget(vazio)
            self.layout_principal.addStretch()
            return

        for despesa in despesas:
            id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa

            card = QFrame()
            card.setObjectName("card")
            card.setMinimumHeight(118)

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(22, 14, 22, 14)
            card_layout.setSpacing(16)

            status_texto = self.texto_status(vencimento, status)
            vencimento_formatado = self.formatar_data(vencimento)

            texto = (
                f"<span style='font-size:18px;'><b>{descricao}</b></span><br>"
                f"💰 <b>R$ {valor:.2f}</b> &nbsp;&nbsp; "
                f"📅 {vencimento_formatado} &nbsp;&nbsp; "
                f"📂 {categoria} &nbsp;&nbsp; "
                f"📄 {tipo} &nbsp;&nbsp; "
                f"{status_texto}"
            )

            info = QLabel(texto.replace(".", ","))
            info.setObjectName("linhaDespesa")
            info.setWordWrap(True)

            botoes = QHBoxLayout()

            if status == "paga":
                btn_pago = QPushButton("↩ Desfazer")
                btn_pago.clicked.connect(lambda _, id=id_despesa: self.reabrir(id))
            else:
                btn_pago = QPushButton("✔ Pagar")
                btn_pago.clicked.connect(lambda _, id=id_despesa: self.marcar_paga(id))

            btn_pago.setObjectName("btnReceita")

            btn_editar = QPushButton("✏ Editar")
            btn_editar.setObjectName("btnReceita")
            btn_editar.clicked.connect(lambda _, d=despesa: self.editar(d))

            btn_excluir = QPushButton("🗑 Excluir")
            btn_excluir.setObjectName("btnDespesa")
            btn_excluir.clicked.connect(lambda _, id=id_despesa: self.excluir(id))

            botoes.addWidget(btn_pago)
            botoes.addWidget(btn_editar)
            botoes.addWidget(btn_excluir)

            card_layout.addWidget(info, 1)
            card_layout.addLayout(botoes)

            self.layout_principal.addWidget(card)

        self.layout_principal.addStretch()

    def marcar_paga(self, id_despesa):
        marcar_despesa_como_paga(id_despesa)
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
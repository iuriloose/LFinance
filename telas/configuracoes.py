from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)

from banco.banco import limpar_todos_os_dados


class TelaConfiguracoes(QWidget):
    def __init__(self, ao_limpar_dados=None):
        super().__init__()
        self.ao_limpar_dados = ao_limpar_dados
        self.montar_tela()

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(18)

        titulo = QLabel("⚙️ Configurações")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Ajustes e ferramentas do LFinance")
        subtitulo.setObjectName("subtitulo")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(10)

        card = QFrame()
        card.setObjectName("card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        titulo_card = QLabel("🧹 Ferramentas")
        titulo_card.setObjectName("cardValor")
        titulo_card.setStyleSheet("font-size: 22px;")

        texto = QLabel(
            "Use esta opção para apagar todos os lançamentos do programa e começar do zero.\n"
            "Isso remove receitas, gastos, despesas e histórico de pagamentos."
        )
        texto.setObjectName("cardInfo")
        texto.setWordWrap(True)

        aviso = QLabel("Atenção: essa ação não pode ser desfeita.")
        aviso.setObjectName("cardInfoMini")
        aviso.setStyleSheet("color: #fca5a5; font-size: 13px;")

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_limpar = QPushButton("🗑️ Limpar todos os dados")
        btn_limpar.setObjectName("btnLimparBanco")
        btn_limpar.clicked.connect(self.confirmar_limpeza)

        botoes.addWidget(btn_limpar)

        card_layout.addWidget(titulo_card)
        card_layout.addWidget(texto)
        card_layout.addWidget(aviso)
        card_layout.addLayout(botoes)

        layout.addWidget(card)
        layout.addStretch()

    def confirmar_limpeza(self):
        confirmar = QMessageBox.question(
            self,
            "Limpar todos os dados",
            "Tem certeza que deseja apagar todos os lançamentos?\n\n"
            "Serão apagados:\n"
            "• receitas\n"
            "• gastos\n"
            "• despesas\n"
            "• histórico de pagamentos\n\n"
            "Essa ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmar != QMessageBox.Yes:
            return

        confirmar_final = QMessageBox.question(
            self,
            "Confirmação final",
            "Última confirmação: deseja realmente limpar tudo e começar do zero?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmar_final != QMessageBox.Yes:
            return

        limpar_todos_os_dados()

        QMessageBox.information(
            self,
            "Dados apagados",
            "Tudo foi apagado com sucesso. Agora você pode cadastrar novamente suas contas."
        )

        if self.ao_limpar_dados:
            self.ao_limpar_dados()

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton


class MenuLateral(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 24, 22, 24)
        layout.setSpacing(12)

        logo = QLabel("📈 LFinance")
        logo.setObjectName("logo")

        subtitulo = QLabel("Controle financeiro pessoal")
        subtitulo.setObjectName("subtitle")

        layout.addWidget(logo)
        layout.addWidget(subtitulo)
        layout.addSpacing(28)

        botoes = [
            "🏠 Tela inicial",
            "💵 Receitas",
            "💳 Despesas",
            "📅 Contas fixas",
            "📄 Parcelamentos",
            "📊 Relatórios",
            "⚙️ Configurações",
        ]

        for i, texto in enumerate(botoes):
            botao = QPushButton(texto)
            botao.setObjectName("menuButton")
            botao.setCheckable(True)

            if i == 0:
                botao.setChecked(True)

            layout.addWidget(botao)

        layout.addStretch()

        versao = QLabel("v0.4")
        versao.setObjectName("rodape")
        layout.addWidget(versao)
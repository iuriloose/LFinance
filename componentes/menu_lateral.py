from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton


class MenuLateral(QFrame):
    def __init__(self, ao_clicar):
        super().__init__()
        self.ao_clicar = ao_clicar

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
            ("tela_inicial", "🏠 Tela inicial"),
            ("receitas", "💵 Receitas"),
            ("despesas", "💳 Despesas"),
            ("contas_fixas", "📅 Contas fixas"),
            ("parcelamentos", "📄 Parcelamentos"),
            ("relatorios", "📊 Relatórios"),
            ("configuracoes", "⚙️ Configurações"),
        ]

        for chave, texto in botoes:
            botao = QPushButton(texto)
            botao.setObjectName("menuButton")
            botao.clicked.connect(lambda _, c=chave: self.ao_clicar(c))
            layout.addWidget(botao)

        layout.addStretch()

        versao = QLabel("v0.7")
        versao.setObjectName("rodape")
        layout.addWidget(versao)
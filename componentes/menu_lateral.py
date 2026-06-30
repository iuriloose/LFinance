from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton


class MenuLateral(QFrame):
    def __init__(self, ao_clicar):
        super().__init__()

        self.ao_clicar = ao_clicar
        self.botoes = {}

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

        itens = [
            ("tela_inicial", "🏠 Tela inicial"),
            ("receitas", "💵 Receitas"),
            ("despesas", "💳 Despesas"),
            ("contas_fixas", "📅 Contas fixas"),
            ("parcelamentos", "📄 Parcelamentos"),
            ("relatorios", "📊 Relatórios"),
            ("configuracoes", "⚙️ Configurações"),
        ]

        for chave, texto in itens:
            botao = QPushButton(texto)
            botao.setObjectName("menuButton")
            botao.setCheckable(True)
            botao.clicked.connect(lambda _, c=chave: self.clicar(c))

            self.botoes[chave] = botao
            layout.addWidget(botao)

        layout.addStretch()

        versao = QLabel("v0.10")
        versao.setObjectName("rodape")
        layout.addWidget(versao)

        self.definir_ativo("tela_inicial")

    def clicar(self, chave):
        self.definir_ativo(chave)
        self.ao_clicar(chave)

    def definir_ativo(self, chave_ativa):
        for chave, botao in self.botoes.items():
            botao.setChecked(chave == chave_ativa)
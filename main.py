import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QMessageBox,
)
from PySide6.QtCore import Qt


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LFinance")
        self.resize(1200, 720)
        self.setMinimumSize(1000, 620)

        self.aplicar_estilo()
        self.montar_interface()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f1117;
            }

            QLabel {
                color: #f5f5f5;
                font-family: Segoe UI;
            }

            QPushButton {
                font-family: Segoe UI;
                border: none;
            }

            QFrame#sidebar {
                background-color: #151922;
                border-right: 1px solid #242938;
            }

            QLabel#logo {
                font-size: 26px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#subtitle {
                font-size: 13px;
                color: #8d93a6;
            }

            QPushButton#menuButton {
                background-color: transparent;
                color: #b8bfd6;
                text-align: left;
                padding: 14px 18px;
                border-radius: 10px;
                font-size: 15px;
            }

            QPushButton#menuButton:hover {
                background-color: #222838;
                color: #ffffff;
            }

            QPushButton#menuButton:checked {
                background-color: #2d6cdf;
                color: #ffffff;
                font-weight: bold;
            }

            QFrame#content {
                background-color: #0f1117;
            }

            QLabel#titulo {
                font-size: 30px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#subtitulo {
                font-size: 15px;
                color: #8d93a6;
            }

            QFrame#card {
                background-color: #181d29;
                border: 1px solid #252b3a;
                border-radius: 18px;
            }

            QLabel#cardTitulo {
                font-size: 14px;
                color: #9aa2b8;
            }

            QLabel#cardValor {
                font-size: 26px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#cardInfo {
                font-size: 13px;
                color: #7f879d;
            }

            QPushButton#primaryButton {
                background-color: #2d6cdf;
                color: white;
                padding: 13px 22px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #3d7dff;
            }

            QPushButton#secondaryButton {
                background-color: #202638;
                color: #d7dcf0;
                padding: 13px 22px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton#secondaryButton:hover {
                background-color: #2b3248;
            }

            QFrame#alerta {
                background-color: #221b1b;
                border: 1px solid #553030;
                border-radius: 16px;
            }

            QLabel#alertaTitulo {
                color: #ff7777;
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#alertaTexto {
                color: #d8d8d8;
                font-size: 14px;
            }

            QLabel#rodape {
                color: #6f768a;
                font-size: 12px;
            }
        """)

    def montar_interface(self):
        container = QWidget()
        layout_principal = QHBoxLayout(container)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        sidebar = self.criar_sidebar()
        conteudo = self.criar_conteudo()

        layout_principal.addWidget(sidebar)
        layout_principal.addWidget(conteudo)

        self.setCentralWidget(container)

    def criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 24, 22, 24)
        layout.setSpacing(12)

        logo = QLabel("💰 LFinance")
        logo.setObjectName("logo")

        subtitulo = QLabel("Controle financeiro pessoal")
        subtitulo.setObjectName("subtitle")

        layout.addWidget(logo)
        layout.addWidget(subtitulo)
        layout.addSpacing(28)

        botoes = [
            "🏠  Dashboard",
            "💵  Receitas",
            "💳  Despesas",
            "📅  Contas",
            "📊  Relatórios",
            "⚙️  Configurações",
        ]

        for i, texto in enumerate(botoes):
            botao = QPushButton(texto)
            botao.setObjectName("menuButton")
            botao.setCheckable(True)

            if i == 0:
                botao.setChecked(True)

            botao.clicked.connect(lambda checked, t=texto: self.menu_clicado(t))
            layout.addWidget(botao)

        layout.addStretch()

        versao = QLabel("v0.2 • Interface inicial")
        versao.setObjectName("rodape")
        layout.addWidget(versao)

        return sidebar

    def criar_conteudo(self):
        content = QFrame()
        content.setObjectName("content")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(24)

        topo = QHBoxLayout()

        textos_topo = QVBoxLayout()

        titulo = QLabel("Boa noite, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Resumo financeiro do mês")
        subtitulo.setObjectName("subtitulo")

        textos_topo.addWidget(titulo)
        textos_topo.addWidget(subtitulo)

        botoes_topo = QHBoxLayout()

        btn_despesa = QPushButton("+ Nova despesa")
        btn_despesa.setObjectName("primaryButton")
        btn_despesa.clicked.connect(self.em_breve)

        btn_receita = QPushButton("+ Nova receita")
        btn_receita.setObjectName("secondaryButton")
        btn_receita.clicked.connect(self.em_breve)

        botoes_topo.addWidget(btn_despesa)
        botoes_topo.addWidget(btn_receita)

        topo.addLayout(textos_topo)
        topo.addStretch()
        topo.addLayout(botoes_topo)

        layout.addLayout(topo)

        linha_cards = QHBoxLayout()
        linha_cards.setSpacing(18)

        linha_cards.addWidget(self.criar_card("Saldo atual", "R$ 0,00", "Ainda sem lançamentos"))
        linha_cards.addWidget(self.criar_card("Receitas do mês", "R$ 0,00", "Nenhuma receita cadastrada"))
        linha_cards.addWidget(self.criar_card("Despesas do mês", "R$ 0,00", "Nenhuma despesa cadastrada"))
        linha_cards.addWidget(self.criar_card("Contas atrasadas", "0", "Tudo certo por enquanto"))

        layout.addLayout(linha_cards)

        area_meio = QHBoxLayout()
        area_meio.setSpacing(18)

        painel_vencimentos = self.criar_painel_vencimentos()
        painel_resumo = self.criar_painel_resumo()

        area_meio.addWidget(painel_vencimentos, 2)
        area_meio.addWidget(painel_resumo, 1)

        layout.addLayout(area_meio)
        layout.addStretch()

        rodape = QLabel("Banco de dados ainda não criado • Próxima etapa: menu funcionando e primeira tela de cadastro")
        rodape.setObjectName("rodape")
        layout.addWidget(rodape)

        return content

    def criar_card(self, titulo, valor, info):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(130)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(8)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitulo")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("cardValor")

        lbl_info = QLabel(info)
        lbl_info.setObjectName("cardInfo")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addStretch()
        layout.addWidget(lbl_info)

        return card

    def criar_painel_vencimentos(self):
        painel = QFrame()
        painel.setObjectName("card")

        layout = QVBoxLayout(painel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        titulo = QLabel("📅 Próximos vencimentos")
        titulo.setObjectName("cardValor")
        titulo.setStyleSheet("font-size: 22px;")

        texto = QLabel("Quando cadastrarmos suas contas, elas aparecerão aqui organizadas por data de vencimento.")
        texto.setObjectName("cardInfo")
        texto.setWordWrap(True)

        alerta = QFrame()
        alerta.setObjectName("alerta")

        alerta_layout = QVBoxLayout(alerta)
        alerta_layout.setContentsMargins(18, 16, 18, 16)

        alerta_titulo = QLabel("🔔 Nenhum aviso no momento")
        alerta_titulo.setObjectName("alertaTitulo")

        alerta_texto = QLabel("As contas vencidas ou próximas do vencimento serão destacadas aqui.")
        alerta_texto.setObjectName("alertaTexto")
        alerta_texto.setWordWrap(True)

        alerta_layout.addWidget(alerta_titulo)
        alerta_layout.addWidget(alerta_texto)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addSpacing(8)
        layout.addWidget(alerta)
        layout.addStretch()

        return painel

    def criar_painel_resumo(self):
        painel = QFrame()
        painel.setObjectName("card")

        layout = QVBoxLayout(painel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        titulo = QLabel("📊 Resumo rápido")
        titulo.setObjectName("cardValor")
        titulo.setStyleSheet("font-size: 22px;")

        itens = [
            "🟢 Contas pagas: 0",
            "🟡 Vencem esta semana: 0",
            "🔴 Atrasadas: 0",
            "💾 Backup: ainda não configurado",
        ]

        layout.addWidget(titulo)
        layout.addSpacing(6)

        for item in itens:
            label = QLabel(item)
            label.setObjectName("alertaTexto")
            layout.addWidget(label)

        layout.addStretch()

        return painel

    def menu_clicado(self, texto):
        QMessageBox.information(
            self,
            "LFinance",
            f"A tela '{texto.strip()}' será criada nas próximas versões."
        )

    def em_breve(self):
        QMessageBox.information(
            self,
            "Em breve",
            "Na próxima etapa vamos começar a criar os cadastros de receitas e despesas."
        )


app = QApplication(sys.argv)

janela = JanelaPrincipal()
janela.show()

sys.exit(app.exec())
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton

from servicos.configuracoes_app import caminho_recurso


class MenuLateral(QFrame):
    def __init__(self, ao_clicar):
        super().__init__()

        self.ao_clicar = ao_clicar
        self.botoes = {}
        self.assets_path = caminho_recurso("assets")
        self.logo_path = self.assets_path / "logo.png"
        self.tooltips_menu = {
            "tela_inicial": "Tela inicial\n\nResumo do mês, saldo, receitas, valores pagos, contas a pagar e próximos vencimentos.",
            "pesquisar": "Pesquisar\n\nEncontre contas, gastos do dia e receitas em uma tela própria.",
            "receitas": "Receitas\n\nCadastre e acompanhe todo dinheiro que entrou, como salário, vendas ou outros recebimentos.",
            "gastos": "Gastos do dia\n\nUse para saídas pagas na hora, como mercado, combustível, farmácia, lanche ou compras à vista.",
            "despesas": "Contas a pagar\n\nUse para boletos, mensalidades e compromissos que podem ficar pendentes até o pagamento.",
            "contas_fixas": "Contas fixas\n\nControle contas recorrentes que se repetem todo mês, como internet, aluguel, energia ou mensalidades.",
            "parcelamentos": "Parcelamentos\n\nControle compras divididas em parcelas e acompanhe automaticamente o andamento de cada parcela.",
            "configuracoes": "Configurações\n\nFerramentas do sistema, backup, restauração e limpeza segura dos dados.",
        }

        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 16)
        layout.setSpacing(5)

        self.criar_logo(layout)

        self.adicionar_botao(layout, "tela_inicial", "menu_home.png", "Tela inicial")
        self.adicionar_botao(layout, "pesquisar", "menu_pesquisar.png", "🔎  Pesquisar")
        self.adicionar_botao(layout, "receitas", "menu_receitas.png", "Receitas")
        self.adicionar_botao(layout, "gastos", "menu_gastos.png", "Gastos do dia")
        self.adicionar_botao(layout, "despesas", "menu_despesas.png", "Contas a pagar")
        self.adicionar_botao(layout, "contas_fixas", "menu_contas.png", "Contas fixas")
        self.adicionar_botao(layout, "parcelamentos", "menu_parcelamentos.png", "Parcelamentos")

        layout.addStretch()

        divisor = QFrame()
        divisor.setObjectName("divisorMenu")
        divisor.setFixedHeight(1)
        layout.addWidget(divisor)
        layout.addSpacing(10)

        self.adicionar_botao(layout, "configuracoes", "menu_configuracoes.png", "Configurações")

        self.setStyleSheet("""
            QFrame#sidebar {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #07111d,
                    stop:0.56 #081522,
                    stop:1 #0b1220
                );
                border-right: 1px solid #1e2c44;
            }

            QFrame#logoCard {
                background-color: rgba(9, 22, 37, 0.78);
                border: none;
                border-radius: 16px;
            }

            QFrame#divisorMenu {
                background-color: #203049;
                border: none;
                margin-left: 8px;
                margin-right: 8px;
            }

            QPushButton#menuButton {
                background-color: transparent;
                color: #c4d0e3;
                border: none;
                border-radius: 12px;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 700;
                text-align: left;
                padding-left: 14px;
                height: 39px;
            }

            QPushButton#menuButton:hover {
                background-color: rgba(30, 41, 59, 0.92);
                color: #ffffff;
            }

            QPushButton#menuButton:checked {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb,
                    stop:1 #1d4ed8
                );
                color: #ffffff;
                font-weight: 800;
            }
        """)

        self.definir_ativo("tela_inicial")

    def criar_logo(self, layout):
        logo_card = QFrame()
        logo_card.setObjectName("logoCard")
        logo_card.setToolTip("LFinance\n\nControle financeiro pessoal para organizar receitas, gastos, despesas, contas fixas e parcelamentos.")
        logo_card.setFixedHeight(160)

        logo_layout = QVBoxLayout(logo_card)
        logo_layout.setContentsMargins(6, 4, 6, 4)
        logo_layout.setSpacing(0)

        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setAccessibleName("Logotipo do LFinance")
        lbl_logo.setStyleSheet("background: transparent; padding: 0px; margin: 0px;")

        if self.logo_path.exists():
            pixmap = QPixmap(str(self.logo_path))
            lbl_logo.setPixmap(
                pixmap.scaled(180, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            lbl_logo.setText("LFinance")
            lbl_logo.setStyleSheet("font-size: 24px; font-weight: 800; color: #ffffff; background: transparent;")

        logo_layout.addWidget(lbl_logo, alignment=Qt.AlignCenter)
        layout.addWidget(logo_card)
        layout.addSpacing(12)

    def adicionar_botao(self, layout, chave, icone_arquivo, texto):
        botao = QPushButton(texto)
        botao.setObjectName("menuButton")
        botao.setCheckable(True)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setIconSize(QSize(28, 28))
        descricao = self.tooltips_menu.get(chave, texto)
        botao.setToolTip(descricao)
        botao.setAccessibleName(texto.replace("🔎", "").strip())
        botao.setAccessibleDescription(descricao.replace("\n\n", ". "))

        icone_path = self.assets_path / icone_arquivo
        if icone_path.exists():
            botao.setIcon(QIcon(str(icone_path)))

        botao.clicked.connect(lambda _, c=chave: self.clicar(c))

        self.botoes[chave] = botao
        layout.addWidget(botao)

    def clicar(self, chave):
        self.definir_ativo(chave)
        self.ao_clicar(chave)

    def definir_ativo(self, chave_ativa):
        for chave, botao in self.botoes.items():
            botao.setChecked(chave == chave_ativa)

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
        self.logo_path = self.assets_path / "logo_sidebar.png"
        self.tooltips_menu = {
            "tela_inicial": "Tela inicial\n\nResumo do mês, saldo, receitas, valores pagos, contas a pagar e próximos vencimentos.",
            "pesquisar": "Pesquisar\n\nEncontre contas, gastos do dia e receitas em uma tela própria.",
            "receitas": "Receitas\n\nCadastre e acompanhe todo dinheiro que entrou, como salário, vendas ou outros recebimentos.",
            "a_receber": "A receber\n\nAcompanhe salários, comissões e valores previstos sem alterar o saldo atual.",
            "gastos": "Gastos do dia\n\nUse para saídas pagas na hora, como mercado, combustível, farmácia, lanche ou compras à vista.",
            "despesas": "Contas a pagar\n\nUse para boletos, mensalidades e compromissos que podem ficar pendentes até o pagamento.",
            "contas_fixas": "Contas fixas\n\nControle contas recorrentes que se repetem todo mês, como internet, aluguel, energia ou mensalidades.",
            "parcelamentos": "Parcelamentos\n\nControle compras divididas em parcelas e acompanhe automaticamente o andamento de cada parcela.",
            "relatorios": "Relatórios\n\nAcompanhe o resumo mensal: entradas reais, contas pagas, pendências e valores previstos a receber.",
            "configuracoes": "Configurações\n\nFerramentas do sistema, backup, restauração e limpeza segura dos dados.",
        }

        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 16)
        layout.setSpacing(5)

        self.criar_logo(layout)

        self.adicionar_botao(layout, "tela_inicial", "icons_lfinance/home.png", "Tela inicial")
        self.adicionar_botao(layout, "a_receber", "icons_lfinance/a_receber.png", "A receber")
        self.adicionar_botao(layout, "pesquisar", "icons_lfinance/pesquisar.png", "Pesquisar")
        self.adicionar_botao(layout, "receitas", "icons_lfinance/receitas.png", "Receitas")
        self.adicionar_botao(layout, "gastos", "icons_lfinance/gastos.png", "Gastos do dia")
        self.adicionar_botao(layout, "despesas", "icons_lfinance/contas_pagar.png", "Contas a pagar")
        self.adicionar_botao(layout, "contas_fixas", "icons_lfinance/contas_fixas.png", "Contas fixas")
        self.adicionar_botao(layout, "parcelamentos", "icons_lfinance/parcelamentos.png", "Parcelamentos")
        self.adicionar_botao(layout, "relatorios", "icons_lfinance/relatorios.png", "Relatórios")

        layout.addStretch()

        divisor = QFrame()
        divisor.setObjectName("divisorMenu")
        divisor.setFixedHeight(1)
        layout.addWidget(divisor)
        layout.addSpacing(10)

        self.adicionar_botao(layout, "configuracoes", "icons_lfinance/configuracoes.png", "Configurações")

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
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }

            QFrame#logoInner {
                background-color: transparent;
                border: none;
            }

            QLabel#logoImage {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
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
                border-radius: 10px;
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: 700;
                text-align: left;
                padding-left: 14px;
                height: 39px;
            }

            QPushButton#menuButton:hover {
                background-color: rgba(25, 42, 62, 0.92);
                color: #ffffff;
            }

            QPushButton#menuButton:checked {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1f5fbf,
                    stop:1 #204d8f
                );
                color: #ffffff;
                border-left: 3px solid #60a5fa;
                font-weight: 700;
            }
        """)

        self.definir_ativo("tela_inicial")

    def criar_logo(self, layout):
        logo_card = QFrame()
        logo_card.setObjectName("logoCard")
        logo_card.setToolTip(
            "LFinance\n\nControle financeiro pessoal para organizar receitas, "
            "gastos, despesas, contas fixas e parcelamentos."
        )
        logo_card.setFixedHeight(176)

        logo_layout = QVBoxLayout(logo_card)
        logo_layout.setContentsMargins(2, 2, 2, 2)
        logo_layout.setSpacing(0)

        lbl_logo = QLabel()
        lbl_logo.setObjectName("logoImage")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setAccessibleName("Logotipo do LFinance")

        if self.logo_path.exists():
            pixmap = QPixmap(str(self.logo_path))
            lbl_logo.setPixmap(
                pixmap.scaled(
                    184,
                    164,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            lbl_logo.setText("LFinance")

        logo_layout.addWidget(lbl_logo, alignment=Qt.AlignCenter)
        layout.addWidget(logo_card)
        layout.addSpacing(8)

    def adicionar_botao(self, layout, chave, icone_arquivo, texto):
        botao = QPushButton(texto)
        botao.setObjectName("menuButton")
        botao.setCheckable(True)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setIconSize(QSize(24, 24))
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

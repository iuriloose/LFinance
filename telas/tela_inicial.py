from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame
)

from componentes.menu_lateral import MenuLateral
from componentes.cards import CardResumo


class TelaInicial(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LFinance")
        self.resize(1200, 720)
        self.setMinimumSize(1000, 620)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f1117; }

            QLabel {
                color: #f5f5f5;
                font-family: Segoe UI;
            }

            QFrame#sidebar {
                background-color: #151922;
                border-right: 1px solid #242938;
            }

            QLabel#logo {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#subtitle {
                font-size: 13px;
                color: #8d93a6;
            }

            QPushButton#menuButton {
                background-color: transparent;
                color: #c8cee2;
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

            QFrame#content { background-color: #0f1117; }

            QLabel#titulo {
                font-size: 32px;
                font-weight: bold;
            }

            QLabel#subtitulo {
                font-size: 15px;
                color: #9aa2b8;
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
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#cardInfo {
                font-size: 13px;
                color: #7f879d;
            }

            QPushButton#btnDespesa {
                background-color: #202638;
                color: white;
                padding: 13px 22px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #553030;
            }

            QPushButton#btnReceita {
                background-color: #202638;
                color: white;
                padding: 13px 22px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #27553b;
            }

            QLabel#rodape {
                color: #6f768a;
                font-size: 12px;
            }
        """)

    def montar_tela(self):
        container = QWidget()
        layout_principal = QHBoxLayout(container)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        layout_principal.addWidget(MenuLateral())
        layout_principal.addWidget(self.criar_conteudo())

        self.setCentralWidget(container)

    def criar_conteudo(self):
        content = QFrame()
        content.setObjectName("content")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(24)

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        titulo = QLabel("Boa noite, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Aqui está o resumo da sua vida financeira")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        cards = QHBoxLayout()
        cards.setSpacing(18)

        cards.addWidget(CardResumo("Saldo atual", "R$ 0,00", "sem movimentação"))
        cards.addWidget(CardResumo("Receitas do mês", "R$ 0,00", "sem movimentação"))
        cards.addWidget(CardResumo("Despesas do mês", "R$ 0,00", "sem movimentação"))
        cards.addWidget(CardResumo("Contas atrasadas", "0", "sem pendências"))

        layout.addLayout(cards)

        vencimentos = QFrame()
        vencimentos.setObjectName("card")

        venc_layout = QVBoxLayout(vencimentos)
        venc_layout.setContentsMargins(24, 22, 24, 22)

        titulo_venc = QLabel("📅 Próximos vencimentos")
        titulo_venc.setObjectName("cardValor")
        titulo_venc.setStyleSheet("font-size: 22px;")

        texto_venc = QLabel("Ainda não há vencimentos cadastrados.")
        texto_venc.setObjectName("cardInfo")

        dica = QLabel("Dica: cadastre contas fixas uma vez e o LFinance cuidará dos próximos meses.")
        dica.setObjectName("subtitulo")
        dica.setWordWrap(True)

        venc_layout.addWidget(titulo_venc)
        venc_layout.addWidget(texto_venc)
        venc_layout.addSpacing(18)
        venc_layout.addWidget(dica)
        venc_layout.addStretch()

        layout.addWidget(vencimentos)

        rodape = QLabel("Banco de dados ainda não criado • Próxima etapa: cadastro de despesas")
        rodape.setObjectName("rodape")
        layout.addWidget(rodape)

        return content
from datetime import date

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame
)

from componentes.menu_lateral import MenuLateral
from componentes.cards import CardResumo
from telas.nova_despesa import NovaDespesa
from banco.banco import listar_despesas, somar_despesas_abertas, contar_despesas_atrasadas


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

            QLabel#linhaDespesa {
                color: #d7dcf0;
                font-size: 15px;
                padding: 6px;
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
        titulo = QLabel("Bom dia, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Aqui está o resumo da sua vida financeira")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")
        btn_despesa.clicked.connect(self.abrir_nova_despesa)

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        total_despesas = somar_despesas_abertas()
        atrasadas = contar_despesas_atrasadas(date.today().isoformat())

        cards = QHBoxLayout()
        cards.setSpacing(18)

        cards.addWidget(CardResumo("Saldo atual", "R$ 0,00", "receitas em breve"))
        cards.addWidget(CardResumo("Receitas do mês", "R$ 0,00", "em breve"))
        cards.addWidget(CardResumo("Despesas abertas", f"R$ {total_despesas:.2f}".replace(".", ","), "total em aberto"))
        cards.addWidget(CardResumo("Contas atrasadas", str(atrasadas), "vencidas e não pagas"))

        layout.addLayout(cards)

        painel = QFrame()
        painel.setObjectName("card")

        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(24, 22, 24, 22)
        painel_layout.setSpacing(10)

        titulo_lista = QLabel("📅 Despesas cadastradas")
        titulo_lista.setObjectName("cardValor")
        titulo_lista.setStyleSheet("font-size: 22px;")

        painel_layout.addWidget(titulo_lista)

        despesas = listar_despesas()

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada ainda.")
            vazio.setObjectName("cardInfo")
            painel_layout.addWidget(vazio)
        else:
            for despesa in despesas[:8]:
                _, descricao, valor, vencimento, categoria, tipo, status = despesa
                texto = f"{vencimento}  •  {descricao}  •  R$ {valor:.2f}  •  {categoria}  •  {tipo}  •  {status}"
                texto = texto.replace(".", ",")

                linha = QLabel(texto)
                linha.setObjectName("linhaDespesa")
                painel_layout.addWidget(linha)

        painel_layout.addStretch()
        layout.addWidget(painel)

        rodape = QLabel("v0.6 • Tela inicial mostrando despesas cadastradas")
        rodape.setObjectName("rodape")
        layout.addWidget(rodape)

        return content

    def abrir_nova_despesa(self):
        janela = NovaDespesa()
        if janela.exec():
            self.montar_tela()
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
)

from componentes.menu_lateral import MenuLateral
from telas.despesas import TelaDespesas
from telas.tela_inicial import TelaInicial


class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LFinance")
        self.resize(1200, 720)
        self.setMinimumSize(1000, 620)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f1117;
            }

            QWidget {
                font-family: Segoe UI;
            }

            QStackedWidget {
                background-color: #0f1117;
            }

            QLabel {
                background-color: transparent;
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
                border: none;
            }

            QPushButton#menuButton:hover {
                background-color: #222838;
                color: #ffffff;
            }

            QPushButton#menuButton:focus {
                background-color: #2d6cdf;
                color: #ffffff;
                font-weight: bold;
            }

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
                font-size: 14px;
                color: #d7dcf0;
            }

            QLabel#linhaDespesa {
                color: #d7dcf0;
                font-size: 15px;
            }

            QLabel#rodape {
                color: #6f768a;
                font-size: 12px;
            }

            QPushButton#btnDespesa {
                background-color: #202638;
                color: white;
                padding: 10px 16px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #553030;
            }

            QPushButton#btnReceita {
                background-color: #202638;
                color: white;
                padding: 10px 16px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #27553b;
            }
        """)

    def criar_pagina_texto(self, texto):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(36, 30, 36, 24)

        titulo = QLabel(texto)
        titulo.setObjectName("titulo")

        layout.addWidget(titulo)
        layout.addStretch()

        return pagina

    def montar_tela(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.paginas = QStackedWidget()

        self.pagina_inicial = TelaInicial(self.recarregar_home)
        self.pagina_receitas = self.criar_pagina_texto("💵 Receitas")
        self.pagina_despesas = TelaDespesas()
        self.pagina_contas = self.criar_pagina_texto("📅 Contas Fixas")
        self.pagina_parcelamentos = self.criar_pagina_texto("📄 Parcelamentos")
        self.pagina_relatorios = self.criar_pagina_texto("📊 Relatórios")
        self.pagina_configuracoes = self.criar_pagina_texto("⚙️ Configurações")

        self.paginas.addWidget(self.pagina_inicial)
        self.paginas.addWidget(self.pagina_receitas)
        self.paginas.addWidget(self.pagina_despesas)
        self.paginas.addWidget(self.pagina_contas)
        self.paginas.addWidget(self.pagina_parcelamentos)
        self.paginas.addWidget(self.pagina_relatorios)
        self.paginas.addWidget(self.pagina_configuracoes)

        self.menu = MenuLateral(self.menu_clicado)

        layout.addWidget(self.menu)
        layout.addWidget(self.paginas, 1)

        self.setCentralWidget(container)

    def menu_clicado(self, tela):
        if tela == "tela_inicial":
            self.recarregar_home()

        elif tela == "receitas":
            self.paginas.setCurrentWidget(self.pagina_receitas)

        elif tela == "despesas":
            self.pagina_despesas.recarregar()
            self.paginas.setCurrentWidget(self.pagina_despesas)

        elif tela == "contas_fixas":
            self.paginas.setCurrentWidget(self.pagina_contas)

        elif tela == "parcelamentos":
            self.paginas.setCurrentWidget(self.pagina_parcelamentos)

        elif tela == "relatorios":
            self.paginas.setCurrentWidget(self.pagina_relatorios)

        elif tela == "configuracoes":
            self.paginas.setCurrentWidget(self.pagina_configuracoes)

    def recarregar_home(self):
        nova_home = TelaInicial(self.recarregar_home)
        indice = self.paginas.indexOf(self.pagina_inicial)

        self.paginas.removeWidget(self.pagina_inicial)
        self.pagina_inicial.deleteLater()

        self.pagina_inicial = nova_home
        self.paginas.insertWidget(indice, self.pagina_inicial)
        self.paginas.setCurrentWidget(self.pagina_inicial)
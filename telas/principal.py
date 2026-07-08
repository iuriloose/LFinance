from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
)
from PySide6.QtGui import QIcon
from componentes.menu_lateral import MenuLateral
from telas.despesas import TelaDespesas
from telas.receitas import TelaReceitas
from telas.gastos import TelaGastos
from telas.tela_inicial import TelaInicial
from telas.configuracoes import TelaConfiguracoes
from telas.contas_fixas import TelaContasFixas
from telas.parcelamentos import TelaParcelamentos
from telas.relatorios import TelaRelatorios
from servicos.configuracoes_app import APP_VERSAO, caminho_recurso


class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"LFinance {APP_VERSAO}")
        icone = caminho_recurso("assets", "lfinance_logo.ico")
        if icone.exists():
            self.setWindowIcon(QIcon(str(icone)))
        self.resize(1200, 720)
        self.setMinimumSize(1000, 620)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #07111d;
            }

            QWidget {
                font-family: Segoe UI;
            }

            QToolTip {
                background-color: #101b2d;
                color: #f8fafc;
                border: 1px solid #3b82f6;
                border-radius: 8px;
                padding: 8px 10px;
                font-family: Segoe UI;
                font-size: 12px;
                opacity: 245;
            }

            QStackedWidget {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #07111d,
                    stop:0.55 #0b1220,
                    stop:1 #08101c
                );
            }

            QLabel {
                background-color: transparent;
                color: #f8fafc;
                font-family: Segoe UI;
            }

            QLabel#titulo {
                font-size: 31px;
                font-weight: 800;
                color: #ffffff;
            }

            QLabel#subtitulo {
                font-size: 14px;
                color: #a8b3c7;
            }

            QFrame#card {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #26364e;
                border-radius: 18px;
            }

            QLabel#cardTitulo {
                font-size: 14px;
                color: #a8b3c7;
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
                color: #e2e8f0;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#rodapeInfo {
                color: #728096;
                font-size: 11px;
            }

            QLineEdit#campoBusca {
                background-color: rgba(18, 29, 46, 0.96);
                color: #ffffff;
                border: 1px solid #26364e;
                border-radius: 14px;
                padding: 12px 18px;
                font-size: 14px;
                selection-background-color: #1d4ed8;
            }

            QLineEdit#campoBusca:focus {
                border: 1px solid #3b82f6;
                background-color: #121f33;
            }

            QPushButton#btnDespesa {
                background-color: rgba(30, 41, 59, 0.78);
                color: white;
                padding: 10px 18px;
                border-radius: 11px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #4b2f36;
            }

            QPushButton#btnDespesa:hover {
                background-color: rgba(55, 65, 81, 0.85);
                border: 1px solid #ef4444;
            }

            QPushButton#btnReceita {
                background-color: rgba(30, 41, 59, 0.78);
                color: white;
                padding: 10px 18px;
                border-radius: 11px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #26513a;
            }

            QPushButton#btnReceita:hover {
                background-color: rgba(22, 45, 34, 0.85);
                border: 1px solid #22c55e;
            }

            QPushButton#btnBackupBanco {
                background-color: #10253f;
                color: #ffffff;
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #1e88ff;
            }

            QPushButton#btnBackupBanco:hover {
                background-color: #12345a;
                border: 1px solid #60a5fa;
            }

            QPushButton#btnRestaurarBanco {
                background-color: #17331f;
                color: #ffffff;
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #22c55e;
            }

            QPushButton#btnRestaurarBanco:hover {
                background-color: #1f442a;
                border: 1px solid #4ade80;
            }

            QPushButton#btnLimparBanco {
                background-color: #3a1d1d;
                color: #ffffff;
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ef4444;
            }

            QPushButton#btnLimparBanco:hover {
                background-color: #4a2424;
                border: 1px solid #f87171;
            }

            QFrame#cardSaldo,
            QFrame#cardSaldoNegativo,
            QFrame#cardReceita,
            QFrame#cardDespesa,
            QFrame#cardAtrasada {
                border-radius: 16px;
                min-height: 78px;
                max-height: 78px;
            }

            QFrame#cardSaldo {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 46, 83, 0.98),
                    stop:0.55 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #1e88ff;
            }

            QFrame#cardSaldo:hover {
                border: 1px solid #60a5fa;
            }

            QFrame#cardSaldoNegativo {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(82, 25, 35, 0.98),
                    stop:0.55 rgba(38, 26, 39, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #ef4444;
            }

            QFrame#cardSaldoNegativo:hover {
                border: 1px solid #f87171;
            }

            QFrame#cardReceita {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(16, 65, 40, 0.96),
                    stop:0.55 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #22c55e;
            }

            QFrame#cardReceita:hover {
                border: 1px solid #4ade80;
            }

            QFrame#cardDespesa {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(74, 48, 11, 0.96),
                    stop:0.55 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #f59e0b;
            }

            QFrame#cardDespesa:hover {
                border: 1px solid #fbbf24;
            }

            QFrame#cardAtrasada {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(82, 25, 35, 0.96),
                    stop:0.55 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #ef4444;
            }

            QFrame#cardAtrasada:hover {
                border: 1px solid #f87171;
            }

            QLabel#cardIcone {
                font-size: 21px;
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                border-radius: 22px;
                background-color: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.10);
                qproperty-alignment: AlignCenter;
            }

            QLabel#cardIconeNegativo {
                font-size: 21px;
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                border-radius: 22px;
                background-color: rgba(239,68,68,0.14);
                border: 1px solid rgba(248,113,113,0.25);
                qproperty-alignment: AlignCenter;
            }

            QLabel#cardValorNegativo {
                font-size: 22px;
                font-weight: bold;
                color: #f87171;
            }

            QLabel#cardValorMini {
                font-size: 22px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#cardInfoMini {
                font-size: 12px;
                color: #cbd5e1;
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
        self.pagina_receitas = TelaReceitas(self.recarregar_home)
        self.pagina_gastos = TelaGastos(self.recarregar_home)
        self.pagina_despesas = TelaDespesas()
        self.pagina_contas = TelaContasFixas(self.recarregar_home)
        self.pagina_parcelamentos = TelaParcelamentos(self.recarregar_home)
        self.pagina_relatorios = TelaRelatorios()
        self.pagina_configuracoes = TelaConfiguracoes(lambda: self.recarregar_home(preservar_pagina=True))

        self.paginas.addWidget(self.pagina_inicial)
        self.paginas.addWidget(self.pagina_receitas)
        self.paginas.addWidget(self.pagina_gastos)
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
            self.pagina_receitas.recarregar()
            self.paginas.setCurrentWidget(self.pagina_receitas)

        elif tela == "gastos":
            self.pagina_gastos.recarregar()
            self.paginas.setCurrentWidget(self.pagina_gastos)

        elif tela == "despesas":
            self.pagina_despesas.recarregar()
            self.paginas.setCurrentWidget(self.pagina_despesas)

        elif tela == "contas_fixas":
            self.pagina_contas.recarregar()
            self.paginas.setCurrentWidget(self.pagina_contas)

        elif tela == "parcelamentos":
            self.pagina_parcelamentos.recarregar()
            self.paginas.setCurrentWidget(self.pagina_parcelamentos)

        elif tela == "relatorios":
            self.pagina_relatorios.recarregar()
            self.paginas.setCurrentWidget(self.pagina_relatorios)

        elif tela == "configuracoes":
            self.paginas.setCurrentWidget(self.pagina_configuracoes)

    def recarregar_home(self, preservar_pagina=False):
        pagina_atual = self.paginas.currentWidget()
        nova_home = TelaInicial(self.recarregar_home)
        indice = self.paginas.indexOf(self.pagina_inicial)

        self.paginas.removeWidget(self.pagina_inicial)
        self.pagina_inicial.deleteLater()

        self.pagina_inicial = nova_home
        self.paginas.insertWidget(indice, self.pagina_inicial)

        if preservar_pagina and pagina_atual is not None and pagina_atual != self.pagina_inicial:
            self.paginas.setCurrentWidget(pagina_atual)
        else:
            self.paginas.setCurrentWidget(self.pagina_inicial)
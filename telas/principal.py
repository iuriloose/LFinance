import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout,
    QMessageBox, QPushButton, QDialog, QCheckBox
)
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import QUrl, Signal
from componentes.menu_lateral import MenuLateral
from telas.despesas import TelaDespesas
from telas.receitas import TelaReceitas
from telas.gastos import TelaGastos
from telas.tela_inicial import TelaInicial
from telas.configuracoes import TelaConfiguracoes
from telas.contas_fixas import TelaContasFixas
from telas.parcelamentos import TelaParcelamentos
from telas.pesquisa import TelaPesquisa
from servicos.configuracoes_app import (
    APP_VERSAO, caminho_recurso, carregar_configuracoes, salvar_configuracoes
)
from servicos.atualizacoes import consultar_ultima_versao


class TelaPrincipal(QMainWindow):
    atualizacao_concluida = Signal(object)
    atualizacao_falhou = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"LFinance {APP_VERSAO}")
        icone = caminho_recurso("assets", "logo.ico")
        if icone.exists():
            self.setWindowIcon(QIcon(str(icone)))
        self.resize(1200, 720)
        self.setMinimumSize(1000, 620)

        self._verificacao_atualizacao_em_andamento = False
        self._mostrar_sem_atualizacao = False
        self.atualizacao_concluida.connect(self._finalizar_verificacao_atualizacao)
        self.atualizacao_falhou.connect(self._falha_verificacao_atualizacao)
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
        self.pagina_pesquisa = TelaPesquisa(lambda: self.recarregar_home(preservar_pagina=True))
        self.pagina_receitas = TelaReceitas(self.recarregar_home)
        self.pagina_gastos = TelaGastos(self.recarregar_home)
        self.pagina_despesas = TelaDespesas()
        self.pagina_contas = TelaContasFixas(self.recarregar_home)
        self.pagina_parcelamentos = TelaParcelamentos(self.recarregar_home)
        self.pagina_configuracoes = TelaConfiguracoes(lambda: self.recarregar_home(preservar_pagina=True))

        self.paginas.addWidget(self.pagina_inicial)
        self.paginas.addWidget(self.pagina_pesquisa)
        self.paginas.addWidget(self.pagina_receitas)
        self.paginas.addWidget(self.pagina_gastos)
        self.paginas.addWidget(self.pagina_despesas)
        self.paginas.addWidget(self.pagina_contas)
        self.paginas.addWidget(self.pagina_parcelamentos)
        self.paginas.addWidget(self.pagina_configuracoes)

        self.menu = MenuLateral(self.menu_clicado)

        layout.addWidget(self.menu)
        layout.addWidget(self.paginas, 1)

        self.setCentralWidget(container)

    def menu_clicado(self, tela):
        if tela == "tela_inicial":
            self.recarregar_home()

        elif tela == "pesquisar":
            self.pagina_pesquisa.recarregar()
            self.paginas.setCurrentWidget(self.pagina_pesquisa)

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

    def verificar_atualizacoes_automaticamente(self):
        self.verificar_atualizacoes(mostrar_sem_atualizacao=False)

    def verificar_atualizacoes(self, mostrar_sem_atualizacao=True):
        if self._verificacao_atualizacao_em_andamento:
            return

        self._mostrar_sem_atualizacao = mostrar_sem_atualizacao
        self._verificacao_atualizacao_em_andamento = True

        # A consulta roda em uma thread Python daemon. Isso evita bloquear a
        # interface e também evita que o encerramento da thread feche a janela
        # principal do programa.
        import threading

        def consultar():
            try:
                resultado = consultar_ultima_versao(timeout=8)
                self.atualizacao_concluida.emit(resultado)
            except Exception as erro:
                self.atualizacao_falhou.emit(str(erro))

        threading.Thread(
            target=consultar,
            name="LFinance-VerificadorAtualizacoes",
            daemon=True,
        ).start()

    def _mostrar_dialogo_atualizacao(self, titulo, mensagem, detalhes="", permitir_download=False, versao_disponivel=""):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(titulo)
        dialogo.setModal(True)
        dialogo.setMinimumWidth(500)
        dialogo.setStyleSheet("""
            QDialog {
                background-color: #0b1220;
            }
            QLabel {
                color: #f8fafc;
                background: transparent;
                font-family: Segoe UI;
            }
            QLabel#tituloAtualizacao {
                font-size: 19px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#detalhesAtualizacao {
                font-size: 13px;
                color: #cbd5e1;
            }
            QCheckBox {
                color: #cbd5e1;
                font-size: 13px;
                spacing: 9px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QPushButton {
                min-height: 38px;
                padding: 0 18px;
                border-radius: 9px;
                border: 1px solid #334155;
                background-color: #172033;
                color: #f8fafc;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #22304a;
            }
            QPushButton#principalAtualizacao {
                background-color: #2563eb;
                border-color: #3b82f6;
                color: #ffffff;
            }
            QPushButton#principalAtualizacao:hover {
                background-color: #1d4ed8;
            }
        """)

        layout = QVBoxLayout(dialogo)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)

        lbl_titulo = QLabel(mensagem)
        lbl_titulo.setObjectName("tituloAtualizacao")
        lbl_titulo.setWordWrap(True)
        layout.addWidget(lbl_titulo)

        if detalhes:
            lbl_detalhes = QLabel(detalhes)
            lbl_detalhes.setObjectName("detalhesAtualizacao")
            lbl_detalhes.setWordWrap(True)
            layout.addWidget(lbl_detalhes)

        chk_nao_avisar = None
        if permitir_download and versao_disponivel:
            chk_nao_avisar = QCheckBox(f"Não avisar novamente sobre a versão {versao_disponivel}")
            layout.addWidget(chk_nao_avisar)

        botoes = QHBoxLayout()
        botoes.addStretch()

        if permitir_download:
            btn_depois = QPushButton("Lembrar depois")
            btn_depois.clicked.connect(dialogo.reject)
            botoes.addWidget(btn_depois)

            btn_principal = QPushButton("Baixar atualização")
            btn_principal.setObjectName("principalAtualizacao")
            btn_principal.clicked.connect(dialogo.accept)
            botoes.addWidget(btn_principal)
        else:
            btn_principal = QPushButton("OK")
            btn_principal.setObjectName("principalAtualizacao")
            btn_principal.clicked.connect(dialogo.accept)
            botoes.addWidget(btn_principal)

        layout.addLayout(botoes)
        aceitou = dialogo.exec() == QDialog.Accepted
        nao_avisar = bool(chk_nao_avisar and chk_nao_avisar.isChecked())
        return aceitou, nao_avisar

    def _formatar_descricao_atualizacao(self, descricao):
        """Converte a descrição em Markdown da Release para texto limpo na janela."""
        texto = str(descricao or "").strip()
        if not texto:
            return ""

        linhas = []
        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha:
                if linhas and linhas[-1] != "":
                    linhas.append("")
                continue

            # Remove títulos e formatações simples do Markdown do GitHub.
            linha = re.sub(r"^#{1,6}\s*", "", linha)
            linha = re.sub(r"\*\*(.*?)\*\*", r"\1", linha)
            linha = re.sub(r"__(.*?)__", r"\1", linha)
            linha = re.sub(r"`([^`]*)`", r"\1", linha)
            linha = re.sub(r"^[-*+]\s+", "• ", linha)
            linha = re.sub(r"^\d+[.)]\s+", "• ", linha)
            linhas.append(linha)

        while linhas and linhas[-1] == "":
            linhas.pop()

        texto_limpo = "\n".join(linhas).strip()
        if len(texto_limpo) > 1400:
            texto_limpo = texto_limpo[:1397].rstrip() + "..."
        return texto_limpo

    def _finalizar_verificacao_atualizacao(self, resultado):
        self._verificacao_atualizacao_em_andamento = False
        mostrar_sem_atualizacao = self._mostrar_sem_atualizacao

        if not resultado.disponivel:
            if mostrar_sem_atualizacao:
                self._mostrar_dialogo_atualizacao(
                    "Atualizações",
                    "Você já está usando a versão mais recente do LFinance.",
                    f"Versão instalada: {APP_VERSAO}\n\nNenhuma atualização disponível no momento.",
                )
            return

        # A opção de ignorar vale somente para a verificação automática.
        # A verificação manual em Configurações continua mostrando a versão disponível.
        config = carregar_configuracoes()
        versao_ignorada = str(config.get("atualizacao_ignorada") or "").strip()
        if not mostrar_sem_atualizacao and versao_ignorada == resultado.nova_versao:
            return

        descricao_release = self._formatar_descricao_atualizacao(resultado.descricao)
        detalhes = (
            f"Sua versão: {resultado.versao_atual}\n"
            f"Nova versão: {resultado.nova_versao}"
        )
        if descricao_release:
            detalhes += f"\n\nNovidades desta versão:\n{descricao_release}"
        detalhes += "\n\nClique em Baixar atualização para abrir o instalador."

        baixar, nao_avisar = self._mostrar_dialogo_atualizacao(
            "Nova versão disponível",
            f"LFinance {resultado.nova_versao} está disponível!",
            detalhes,
            permitir_download=True,
            versao_disponivel=resultado.nova_versao,
        )

        if nao_avisar:
            salvar_configuracoes({"atualizacao_ignorada": resultado.nova_versao})
        elif versao_ignorada:
            # Ao desmarcar em uma verificação manual, volta a avisar automaticamente.
            salvar_configuracoes({"atualizacao_ignorada": ""})

        if baixar:
            destino = resultado.url_download or resultado.url_release
            QDesktopServices.openUrl(QUrl(destino))

    def _falha_verificacao_atualizacao(self, erro):
        self._verificacao_atualizacao_em_andamento = False
        if self._mostrar_sem_atualizacao:
            self._mostrar_dialogo_atualizacao(
                "Não foi possível verificar",
                "O LFinance não conseguiu consultar as atualizações agora.",
                "Verifique sua conexão com a internet e tente novamente.",
            )

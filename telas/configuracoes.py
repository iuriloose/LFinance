from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QFileDialog, QDialog, QLineEdit, QApplication,
    QScrollArea
)
from PySide6.QtCore import Qt, QStandardPaths

from pathlib import Path
from datetime import datetime
import shutil
import os
import sys
import subprocess

from banco.banco import limpar_todos_os_dados, CAMINHO_BANCO
from servicos.configuracoes_app import (
    APP_VERSAO, PASTA_DADOS, carregar_configuracoes,
    salvar_configuracoes, salvar_nome_usuario, executando_como_exe
)


class TelaConfiguracoes(QWidget):
    def __init__(self, ao_limpar_dados=None):
        super().__init__()
        self.ao_limpar_dados = ao_limpar_dados
        self.campo_nome_usuario = None
        self.aplicar_estilo_local()
        self.montar_tela()

    def aplicar_estilo_local(self):
        self.setStyleSheet("""
            QFrame#configCard {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #26364e;
                border-radius: 16px;
            }

            QFrame#configLinhaVerde,
            QFrame#configLinhaAzul,
            QFrame#configLinhaVermelha {
                background-color: rgba(13, 27, 45, 0.75);
                border: 1px solid #223149;
                border-radius: 10px;
            }

            QFrame#configLinhaVerde { border-left: 4px solid #22c55e; }
            QFrame#configLinhaAzul { border-left: 4px solid #1e88ff; }
            QFrame#configLinhaVermelha { border-left: 4px solid #ef4444; }

            QLabel#configTituloCard {
                color: #ffffff;
                font-size: 22px;
                font-weight: 800;
                background: transparent;
                border: none;
            }

            QLabel#configTexto {
                color: #d7dcf0;
                font-size: 14px;
                background: transparent;
                border: none;
            }

            QLabel#configRotulo {
                color: #a8b3c7;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
            }

            QLabel#configValor {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
            }

            QLabel#configCaminho {
                color: #d7dcf0;
                font-size: 12px;
                background: transparent;
                border: none;
            }

            QLabel#configAvisoAmarelo {
                color: #fbbf24;
                font-size: 13px;
                background: transparent;
                border: none;
            }

            QLabel#configAvisoVermelho {
                color: #fca5a5;
                font-size: 13px;
                background: transparent;
                border: none;
            }

            QLineEdit#campoNomeUsuario {
                background-color: #07111d;
                color: #ffffff;
                border: 1px solid #26364e;
                border-radius: 9px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 28px;
                selection-background-color: #1d4ed8;
            }

            QLineEdit#campoNomeUsuario:focus {
                border: 1px solid #3b82f6;
                background-color: #0b1626;
            }
        """)

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(14)

        titulo = QLabel("⚙️ Configurações")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Ajustes e ferramentas do LFinance")
        subtitulo.setObjectName("subtitulo")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        conteudo = QWidget()
        conteudo.setStyleSheet("background: transparent;")
        conteudo_layout = QVBoxLayout(conteudo)
        conteudo_layout.setContentsMargins(0, 0, 0, 0)
        conteudo_layout.setSpacing(14)

        conteudo_layout.addWidget(self.criar_card_sistema())
        conteudo_layout.addWidget(self.criar_card_sobre())
        conteudo_layout.addWidget(self.criar_card_backup())
        conteudo_layout.addWidget(self.criar_card_ferramentas())
        conteudo_layout.addStretch()

        scroll.setWidget(conteudo)
        layout.addWidget(scroll, 1)

    def estilo_botao_config(self, tipo="azul"):
        cores = {
            "azul": ("#10253f", "#1e88ff", "#12345a", "#60a5fa"),
            "verde": ("#17331f", "#22c55e", "#1f442a", "#4ade80"),
            "vermelho": ("#3a1d1d", "#ef4444", "#4a2424", "#f87171"),
            "cinza": ("#162133", "#334155", "#1e293b", "#64748b"),
        }
        fundo, borda, fundo_hover, borda_hover = cores.get(tipo, cores["azul"])
        return f"""
            QPushButton {{
                background-color: {fundo};
                color: #ffffff;
                border: 1px solid {borda};
                border-radius: 9px;
                padding: 7px 13px;
                font-size: 12px;
                font-weight: bold;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {fundo_hover};
                border: 1px solid {borda_hover};
            }}
        """

    def criar_label(self, texto, nome="configTexto", wrap=True):
        label = QLabel(texto)
        label.setObjectName(nome)
        label.setWordWrap(wrap)
        return label

    def criar_card_base(self, titulo, descricao):
        card = QFrame()
        card.setObjectName("configCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 18, 24, 18)
        card_layout.setSpacing(12)

        titulo_card = self.criar_label(titulo, "configTituloCard", False)
        texto = self.criar_label(descricao, "configTexto", True)

        card_layout.addWidget(titulo_card)
        card_layout.addWidget(texto)
        return card, card_layout

    def criar_linha_info(self, cor, titulo, valor, complemento=None):
        linha = QFrame()
        linha.setObjectName(cor)
        layout = QVBoxLayout(linha)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(4)

        layout.addWidget(self.criar_label(titulo, "configRotulo", False))
        layout.addWidget(self.criar_label(valor, "configValor", True))
        if complemento:
            layout.addWidget(self.criar_label(complemento, "configCaminho", True))
        return linha

    def criar_card_sistema(self):
        card, card_layout = self.criar_card_base(
            "🛠️ Dados do sistema",
            "Ajuste o nome exibido na tela inicial e consulte as informações técnicas do LFinance."
        )

        config = carregar_configuracoes()
        modo_execucao = "Executável instalado" if executando_como_exe() else "Projeto Python"

        linha_usuario = QFrame()
        linha_usuario.setObjectName("configLinhaVerde")
        usuario_layout = QVBoxLayout(linha_usuario)
        usuario_layout.setContentsMargins(16, 10, 16, 12)
        usuario_layout.setSpacing(7)
        usuario_layout.addWidget(self.criar_label("👤 Usuário", "configRotulo", False))
        usuario_layout.addWidget(self.criar_label("Nome usado na saudação da tela inicial.", "configCaminho", False))

        linha_nome = QHBoxLayout()
        linha_nome.setSpacing(10)
        self.campo_nome_usuario = QLineEdit()
        self.campo_nome_usuario.setObjectName("campoNomeUsuario")
        self.campo_nome_usuario.setText(config.get("nome_usuario", "Usuário"))
        self.campo_nome_usuario.setPlaceholderText("Digite seu nome")
        self.campo_nome_usuario.setToolTip(
            "Nome do usuário\n\nEsse nome aparece na saudação da tela inicial do LFinance."
        )

        btn_salvar_nome = QPushButton("💾 Salvar nome")
        btn_salvar_nome.setStyleSheet(self.estilo_botao_config("verde"))
        btn_salvar_nome.setMinimumWidth(140)
        btn_salvar_nome.setToolTip(
            "Salvar nome\n\nGrava o nome usado na saudação da tela inicial."
        )
        btn_salvar_nome.clicked.connect(self.salvar_nome_usuario)

        linha_nome.addWidget(self.campo_nome_usuario, 1)
        linha_nome.addWidget(btn_salvar_nome)
        usuario_layout.addLayout(linha_nome)

        linha_sistema = QHBoxLayout()
        linha_sistema.setSpacing(12)

        info_versao = self.criar_linha_info(
            "configLinhaAzul",
            "📌 Versão",
            f"LFinance {APP_VERSAO}",
            f"Modo: {modo_execucao}"
        )

        info_banco = QFrame()
        info_banco.setObjectName("configLinhaAzul")
        banco_layout = QVBoxLayout(info_banco)
        banco_layout.setContentsMargins(16, 10, 16, 12)
        banco_layout.setSpacing(6)

        banco_layout.addWidget(self.criar_label("💾 Local dos dados", "configRotulo", False))
        lbl_caminho = self.criar_label(str(PASTA_DADOS), "configCaminho", True)
        lbl_caminho.setTextInteractionFlags(lbl_caminho.textInteractionFlags() | Qt.TextSelectableByMouse)
        lbl_caminho.setToolTip(
            "Local dos dados\n\nO banco fica em uma pasta segura do Windows, fora da pasta do programa."
        )
        banco_layout.addWidget(lbl_caminho)

        aviso_persistencia = self.criar_label(
            "Se o LFinance for desinstalado ou atualizado, suas contas continuam salvas neste local. "
            "Os arquivos de backup não são carregados automaticamente; eles só são usados quando você clica em Restaurar backup.",
            "configAvisoAmarelo",
            True
        )
        aviso_persistencia.setToolTip(
            "Seus dados ficam separados do programa instalado. Reinstalar o LFinance não apaga nem restaura backups automaticamente."
        )
        banco_layout.addWidget(aviso_persistencia)

        botoes_banco = QHBoxLayout()
        botoes_banco.setSpacing(10)
        botoes_banco.addStretch()

        btn_copiar_banco = QPushButton("📋 Copiar caminho")
        btn_copiar_banco.setStyleSheet(self.estilo_botao_config("azul"))
        btn_copiar_banco.setToolTip(
            "Copiar caminho\n\nCopia o caminho completo do banco de dados para a área de transferência."
        )
        btn_copiar_banco.clicked.connect(self.copiar_caminho_banco)

        btn_abrir_pasta = QPushButton("📂 Abrir pasta")
        btn_abrir_pasta.setStyleSheet(self.estilo_botao_config("verde"))
        btn_abrir_pasta.setToolTip(
            "Abrir pasta\n\nAbre a pasta onde ficam o banco de dados e os arquivos internos do LFinance."
        )
        btn_abrir_pasta.clicked.connect(lambda: self.abrir_pasta_backup(PASTA_DADOS))

        botoes_banco.addWidget(btn_copiar_banco)
        botoes_banco.addWidget(btn_abrir_pasta)
        banco_layout.addLayout(botoes_banco)

        linha_sistema.addWidget(info_versao, 1)
        linha_sistema.addWidget(info_banco, 2)

        card_layout.addWidget(linha_usuario)
        card_layout.addLayout(linha_sistema)
        return card

    def criar_card_sobre(self):
        card, card_layout = self.criar_card_base(
            "ℹ️ Sobre o LFinance",
            "Sistema de gerenciamento financeiro pessoal desenvolvido para organizar receitas, despesas, gastos e compromissos do dia a dia."
        )

        linha_sobre = QHBoxLayout()
        linha_sobre.setSpacing(12)

        info_produto = self.criar_linha_info(
            "configLinhaAzul",
            "📦 Produto",
            "LFinance",
            f"Versão {APP_VERSAO}"
        )

        info_autor = self.criar_linha_info(
            "configLinhaVerde",
            "👨‍💻 Desenvolvedor",
            "Iuri Loose",
            "© 2026 Iuri Loose. Todos os direitos reservados."
        )

        linha_sobre.addWidget(info_produto, 1)
        linha_sobre.addWidget(info_autor, 2)
        card_layout.addLayout(linha_sobre)

        return card

    def salvar_nome_usuario(self):
        nome = (self.campo_nome_usuario.text() if self.campo_nome_usuario else "").strip()

        if not nome:
            self.dialogo_lfinance(
                titulo_janela="Nome do usuário",
                icone="⚠️",
                titulo="Informe um nome válido",
                mensagem="Digite o nome que deve aparecer na saudação da tela inicial.",
                tipo="aviso",
                texto_confirmar="OK",
            )
            return

        salvar_nome_usuario(nome)

        self.dialogo_lfinance(
            titulo_janela="Nome salvo",
            icone="✅",
            titulo="Nome salvo com sucesso!",
            mensagem="A saudação da tela inicial foi atualizada. Ao voltar para a tela inicial, o novo nome já aparecerá.",
            tipo="sucesso",
            texto_confirmar="OK",
        )

        if self.ao_limpar_dados:
            self.ao_limpar_dados()

    def copiar_caminho_banco(self):
        QApplication.clipboard().setText(str(CAMINHO_BANCO))
        self.dialogo_lfinance(
            titulo_janela="Caminho copiado",
            icone="✅",
            titulo="Caminho copiado!",
            mensagem="O caminho do banco de dados foi copiado para a área de transferência.",
            detalhes=str(CAMINHO_BANCO),
            tipo="sucesso",
            texto_confirmar="OK",
        )

    def criar_card_backup(self):
        pasta_padrao = self.obter_pasta_padrao_backups()
        card, card_layout = self.criar_card_base(
            "💾 Backup e restauração",
            "Faça uma cópia de segurança do banco de dados ou restaure um backup anterior."
        )

        local_backup = self.criar_label(
            f"Os backups são sugeridos automaticamente em:\n{pasta_padrao}",
            "configCaminho",
            True
        )
        local_backup.setTextInteractionFlags(local_backup.textInteractionFlags() | Qt.TextSelectableByMouse)

        aviso = self.criar_label(
            "Ao restaurar um backup, os dados atuais serão substituídos pelos dados do arquivo escolhido.",
            "configAvisoAmarelo",
            True
        )

        botoes = QHBoxLayout()
        botoes.setSpacing(12)
        botoes.addStretch()

        btn_backup = QPushButton("💾 Fazer backup")
        btn_backup.setStyleSheet(self.estilo_botao_config("azul"))
        btn_backup.setMinimumWidth(170)
        btn_backup.setToolTip("Fazer backup\n\nAbre a pasta padrão Documentos\\LFinance\\Backups com o nome do arquivo já preenchido. Basta clicar em Salvar.")
        btn_backup.clicked.connect(self.fazer_backup)

        btn_restaurar = QPushButton("📂 Restaurar backup")
        btn_restaurar.setStyleSheet(self.estilo_botao_config("verde"))
        btn_restaurar.setMinimumWidth(190)
        btn_restaurar.setToolTip("Restaurar backup\n\nSubstitui o banco atual por um arquivo de backup escolhido.")
        btn_restaurar.clicked.connect(self.restaurar_backup)

        botoes.addWidget(btn_backup)
        botoes.addWidget(btn_restaurar)

        card_layout.addWidget(local_backup)
        card_layout.addWidget(aviso)
        card_layout.addLayout(botoes)
        return card

    def criar_card_ferramentas(self):
        card, card_layout = self.criar_card_base(
            "🧹 Ferramentas",
            "Use esta opção para apagar todos os lançamentos do programa e começar do zero."
        )

        aviso = self.criar_label("Atenção: essa ação não pode ser desfeita.", "configAvisoVermelho", True)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_limpar = QPushButton("🗑️ Limpar todos os dados")
        btn_limpar.setStyleSheet(self.estilo_botao_config("vermelho"))
        btn_limpar.setMinimumWidth(220)
        btn_limpar.setToolTip("Limpar todos os dados\n\nApaga receitas, gastos, despesas, contas, parcelamentos e histórico.")
        btn_limpar.clicked.connect(self.confirmar_limpeza)

        botoes.addWidget(btn_limpar)

        card_layout.addWidget(self.criar_label(
            "Isso remove receitas, gastos, despesas, contas, parcelamentos e histórico de pagamentos.",
            "configTexto",
            True
        ))
        card_layout.addWidget(aviso)
        card_layout.addLayout(botoes)
        return card

    def obter_pasta_padrao_backups(self):
        documentos = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        base = Path(documentos) if documentos else Path.home() / "Documents"
        return base / "LFinance" / "Backups"

    def fazer_backup(self):
        if not CAMINHO_BANCO.exists():
            self.dialogo_lfinance(
                titulo_janela="Backup não realizado",
                icone="⚠️",
                titulo="Banco de dados não encontrado",
                mensagem="Abra o programa novamente ou cadastre algum lançamento antes de fazer o backup.",
                tipo="aviso",
                texto_confirmar="OK",
            )
            return

        pasta_padrao = self.obter_pasta_padrao_backups()
        pasta_padrao.mkdir(parents=True, exist_ok=True)

        data_hora = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nome_sugerido = pasta_padrao / f"LFinance_Backup_{data_hora}.db"

        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar backup do LFinance",
            str(nome_sugerido),
            "Banco de dados SQLite (*.db)"
        )

        if not arquivo:
            return

        destino = Path(arquivo)
        if destino.suffix.lower() != ".db":
            destino = destino.with_suffix(".db")

        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CAMINHO_BANCO, destino)
        except Exception as erro:
            self.dialogo_lfinance(
                titulo_janela="Erro ao fazer backup",
                icone="⚠️",
                titulo="Não foi possível salvar o backup",
                mensagem="Ocorreu um erro ao copiar o banco de dados.",
                detalhes=str(erro),
                tipo="perigo",
                texto_confirmar="OK",
                perigo=True,
            )
            return

        self.mostrar_backup_realizado(destino)


    def abrir_pasta_backup(self, pasta):
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(pasta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(pasta)])
            else:
                subprocess.Popen(["xdg-open", str(pasta)])
        except Exception:
            self.dialogo_lfinance(
                titulo_janela="Abrir pasta",
                icone="⚠️",
                titulo="Não foi possível abrir a pasta",
                mensagem="O arquivo foi criado, mas o Windows não permitiu abrir a pasta automaticamente.",
                tipo="aviso",
                texto_confirmar="OK",
            )

    def mostrar_backup_realizado(self, destino):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Backup realizado")
        dialogo.setModal(True)
        dialogo.setMinimumWidth(560)
        dialogo.setStyleSheet("""
            QDialog {
                background-color: #07111d;
                border: 1px solid #26364e;
            }
            QLabel {
                background-color: transparent;
                color: #d7dcf0;
                font-family: Segoe UI;
            }
            QLabel#iconeSucesso {
                font-size: 42px;
            }
            QLabel#tituloDialogo {
                color: #ffffff;
                font-size: 22px;
                font-weight: bold;
            }
            QLabel#textoDialogo {
                color: #cbd5e1;
                font-size: 14px;
            }
            QLabel#caixaCaminho {
                background-color: #0d1b2d;
                color: #e2e8f0;
                border: 1px solid #26364e;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton {
                color: #ffffff;
                padding: 10px 18px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#btnAbrirPasta {
                background-color: #10253f;
                border: 1px solid #1e88ff;
            }
            QPushButton#btnAbrirPasta:hover {
                background-color: #12345a;
                border: 1px solid #60a5fa;
            }
            QPushButton#btnOkBackup {
                background-color: #17331f;
                border: 1px solid #22c55e;
                min-width: 90px;
            }
            QPushButton#btnOkBackup:hover {
                background-color: #1f442a;
                border: 1px solid #4ade80;
            }
        """)

        layout = QVBoxLayout(dialogo)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        topo = QHBoxLayout()
        topo.setSpacing(14)

        icone = QLabel("✅")
        icone.setObjectName("iconeSucesso")

        textos_topo = QVBoxLayout()
        textos_topo.setSpacing(4)

        titulo = QLabel("Backup realizado com sucesso!")
        titulo.setObjectName("tituloDialogo")

        texto = QLabel("Seu banco de dados foi salvo com segurança.")
        texto.setObjectName("textoDialogo")
        texto.setWordWrap(True)

        textos_topo.addWidget(titulo)
        textos_topo.addWidget(texto)

        topo.addWidget(icone)
        topo.addLayout(textos_topo)
        topo.addStretch()

        pasta = Path(destino).parent
        arquivo = Path(destino).name

        detalhes = QLabel(
            f"Pasta:\n{pasta}\n\n"
            f"Arquivo:\n{arquivo}"
        )
        detalhes.setObjectName("caixaCaminho")
        detalhes.setTextInteractionFlags(detalhes.textInteractionFlags() | Qt.TextSelectableByMouse)
        detalhes.setWordWrap(True)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_abrir = QPushButton("📂 Abrir pasta")
        btn_abrir.setObjectName("btnAbrirPasta")
        btn_abrir.setToolTip("Abrir pasta\\n\\nAbre no Windows Explorer a pasta onde o backup foi salvo.")
        btn_abrir.clicked.connect(lambda: self.abrir_pasta_backup(pasta))

        btn_ok = QPushButton("OK")
        btn_ok.setObjectName("btnOkBackup")
        btn_ok.clicked.connect(dialogo.accept)

        botoes.addWidget(btn_abrir)
        botoes.addWidget(btn_ok)

        layout.addLayout(topo)
        layout.addWidget(detalhes)
        layout.addLayout(botoes)

        dialogo.exec()

    def dialogo_lfinance(
        self,
        titulo_janela,
        icone,
        titulo,
        mensagem,
        detalhes=None,
        tipo="info",
        texto_confirmar="OK",
        texto_cancelar=None,
        perigo=False,
    ):
        dialogo = QDialog(self)
        dialogo.setWindowTitle(titulo_janela)
        dialogo.setModal(True)
        dialogo.setMinimumWidth(560)

        cor_icone = {
            "sucesso": "#22c55e",
            "aviso": "#fbbf24",
            "perigo": "#ef4444",
            "info": "#1e88ff",
        }.get(tipo, "#1e88ff")

        dialogo.setStyleSheet(f"""
            QDialog {{
                background-color: #07111d;
                border: 1px solid #26364e;
            }}
            QLabel {{
                background-color: transparent;
                color: #d7dcf0;
                font-family: Segoe UI;
            }}
            QLabel#iconeDialogo {{
                color: {cor_icone};
                font-size: 42px;
            }}
            QLabel#tituloDialogo {{
                color: #ffffff;
                font-size: 22px;
                font-weight: bold;
            }}
            QLabel#textoDialogo {{
                color: #cbd5e1;
                font-size: 14px;
                line-height: 1.4;
            }}
            QLabel#detalhesDialogo {{
                background-color: #0d1b2d;
                color: #e2e8f0;
                border: 1px solid #26364e;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
            }}
            QPushButton {{
                color: #ffffff;
                padding: 10px 18px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton#btnCancelar {{
                background-color: #17331f;
                border: 1px solid #22c55e;
            }}
            QPushButton#btnCancelar:hover {{
                background-color: #1f442a;
                border: 1px solid #4ade80;
            }}
            QPushButton#btnConfirmar {{
                background-color: #10253f;
                border: 1px solid #1e88ff;
            }}
            QPushButton#btnConfirmar:hover {{
                background-color: #12345a;
                border: 1px solid #60a5fa;
            }}
            QPushButton#btnPerigo {{
                background-color: #3a1115;
                border: 1px solid #ef4444;
            }}
            QPushButton#btnPerigo:hover {{
                background-color: #511820;
                border: 1px solid #f87171;
            }}
        """)

        layout = QVBoxLayout(dialogo)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        topo = QHBoxLayout()
        topo.setSpacing(14)

        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("iconeDialogo")
        lbl_icone.setFixedWidth(56)
        lbl_icone.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        textos_topo = QVBoxLayout()
        textos_topo.setSpacing(6)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloDialogo")
        lbl_titulo.setWordWrap(True)

        lbl_msg = QLabel(mensagem)
        lbl_msg.setObjectName("textoDialogo")
        lbl_msg.setWordWrap(True)

        textos_topo.addWidget(lbl_titulo)
        textos_topo.addWidget(lbl_msg)

        topo.addWidget(lbl_icone)
        topo.addLayout(textos_topo)
        topo.addStretch()

        layout.addLayout(topo)

        if detalhes:
            lbl_detalhes = QLabel(detalhes)
            lbl_detalhes.setObjectName("detalhesDialogo")
            lbl_detalhes.setTextInteractionFlags(lbl_detalhes.textInteractionFlags() | Qt.TextSelectableByMouse)
            lbl_detalhes.setWordWrap(True)
            layout.addWidget(lbl_detalhes)

        botoes = QHBoxLayout()
        botoes.addStretch()

        if texto_cancelar:
            btn_cancelar = QPushButton(texto_cancelar)
            btn_cancelar.setObjectName("btnCancelar")
            btn_cancelar.clicked.connect(dialogo.reject)
            botoes.addWidget(btn_cancelar)

        btn_confirmar = QPushButton(texto_confirmar)
        btn_confirmar.setObjectName("btnPerigo" if perigo else "btnConfirmar")
        btn_confirmar.clicked.connect(dialogo.accept)
        botoes.addWidget(btn_confirmar)

        layout.addLayout(botoes)

        return dialogo.exec() == QDialog.Accepted

    def restaurar_backup(self):
        pasta_padrao = self.obter_pasta_padrao_backups()
        pasta_padrao.mkdir(parents=True, exist_ok=True)

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Escolher arquivo de backup",
            str(pasta_padrao),
            "Banco de dados SQLite (*.db);;Todos os arquivos (*)"
        )

        if not arquivo:
            return

        origem = Path(arquivo)

        if not origem.exists():
            self.dialogo_lfinance(
                titulo_janela="Arquivo não encontrado",
                icone="⚠️",
                titulo="Arquivo não encontrado",
                mensagem="O arquivo de backup selecionado não foi encontrado.",
                tipo="aviso",
                texto_confirmar="OK",
            )
            return

        confirmar = self.dialogo_lfinance(
            titulo_janela="Restaurar backup",
            icone="⚠️",
            titulo="Restaurar backup selecionado?",
            mensagem=(
                "Os dados atuais do LFinance serão substituídos pelos dados do arquivo escolhido.\n\n"
                "Antes de restaurar, o programa criará automaticamente uma cópia de segurança do banco atual."
            ),
            detalhes=f"Arquivo selecionado:\n{origem.name}",
            tipo="aviso",
            texto_confirmar="Restaurar backup",
            texto_cancelar="Cancelar",
        )

        if not confirmar:
            return

        try:
            CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

            if CAMINHO_BANCO.exists():
                pasta_backup_auto = CAMINHO_BANCO.parent / "backups_automaticos"
                pasta_backup_auto.mkdir(parents=True, exist_ok=True)
                data_hora = datetime.now().strftime("%d-%m-%Y_%H-%M")
                destino_auto = pasta_backup_auto / f"antes_restauracao_{data_hora}.db"
                shutil.copy2(CAMINHO_BANCO, destino_auto)

            shutil.copy2(origem, CAMINHO_BANCO)
        except Exception as erro:
            self.dialogo_lfinance(
                titulo_janela="Erro ao restaurar backup",
                icone="⚠️",
                titulo="Não foi possível restaurar o backup",
                mensagem="Ocorreu um erro ao substituir o banco de dados atual.",
                detalhes=str(erro),
                tipo="perigo",
                texto_confirmar="OK",
                perigo=True,
            )
            return

        self.dialogo_lfinance(
            titulo_janela="Backup restaurado",
            icone="✅",
            titulo="Backup restaurado com sucesso!",
            mensagem=(
                "Os dados do LFinance foram recuperados com segurança.\n\n"
                "Se alguma informação antiga ainda aparecer na tela, feche e abra o programa novamente."
            ),
            tipo="sucesso",
            texto_confirmar="OK",
        )

        if self.ao_limpar_dados:
            self.ao_limpar_dados()

    def confirmar_limpeza(self):
        confirmar = self.dialogo_lfinance(
            titulo_janela="Limpar todos os dados",
            icone="🗑️",
            titulo="Apagar todos os dados do LFinance?",
            mensagem=(
                "Esta ação remove permanentemente todos os lançamentos cadastrados no programa.\n\n"
                "Antes de continuar, confirme que você já fez um backup recente."
            ),
            detalhes=(
                "Serão apagados:\n"
                "• Receitas\n"
                "• Gastos\n"
                "• Despesas\n"
                "• Contas fixas\n"
                "• Parcelamentos\n"
                "• Histórico de pagamentos\n\n"
                "Esta ação não pode ser desfeita."
            ),
            tipo="perigo",
            texto_confirmar="Apagar dados",
            texto_cancelar="Cancelar",
            perigo=True,
        )

        if not confirmar:
            return

        confirmar_final = self.dialogo_lfinance(
            titulo_janela="Confirmação final",
            icone="⚠️",
            titulo="Última confirmação",
            mensagem="Deseja realmente limpar tudo e começar do zero?",
            detalhes="Depois de confirmar, os dados atuais serão apagados do banco do LFinance.",
            tipo="aviso",
            texto_confirmar="Sim, limpar tudo",
            texto_cancelar="Cancelar",
            perigo=True,
        )

        if not confirmar_final:
            return

        limpar_todos_os_dados()

        self.dialogo_lfinance(
            titulo_janela="Dados apagados",
            icone="✅",
            titulo="Dados apagados com sucesso!",
            mensagem="O LFinance foi limpo e está pronto para receber novos lançamentos.",
            tipo="sucesso",
            texto_confirmar="OK",
        )

        if self.ao_limpar_dados:
            self.ao_limpar_dados()

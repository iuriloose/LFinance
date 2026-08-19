from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class DialogoConfirmacao(QDialog):
    """Confirma uma ação sensível mantendo o padrão visual escuro do LFinance."""

    def __init__(self, titulo, mensagem, acao, parent=None, cor="#f59e0b"):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(470)
        self.setModal(True)
        self.setStyleSheet(
            f"""
            QDialog {{ background-color: #0f1726; }}
            QLabel {{ color: #d7dcf0; font: 13px 'Segoe UI'; background: transparent; }}
            QLabel#tituloConfirmacao {{ color: #ffffff; font-size: 21px; font-weight: 800; }}
            QLabel#mensagemConfirmacao {{ color: #cbd5e1; line-height: 1.4; }}
            QPushButton {{
                min-height: 38px; border-radius: 9px; padding: 0 18px;
                color: #ffffff; font-weight: 700;
            }}
            QPushButton#cancelarConfirmacao {{ background: #1f2937; border: 1px solid #475569; }}
            QPushButton#cancelarConfirmacao:hover {{ background: #273449; border-color: #64748b; }}
            QPushButton#confirmarAcao {{ background: {cor}; border: 1px solid {cor}; }}
            QPushButton#confirmarAcao:hover {{ background: #fbbf24; border-color: #fcd34d; color: #111827; }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(14)

        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("tituloConfirmacao")
        mensagem_label = QLabel(mensagem)
        mensagem_label.setObjectName("mensagemConfirmacao")
        mensagem_label.setWordWrap(True)

        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("cancelarConfirmacao")
        cancelar.clicked.connect(self.reject)
        confirmar = QPushButton(acao)
        confirmar.setObjectName("confirmarAcao")
        confirmar.clicked.connect(self.accept)
        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)

        layout.addWidget(titulo_label)
        layout.addWidget(mensagem_label)
        layout.addSpacing(4)
        layout.addLayout(botoes)


def confirmar_acao(titulo, mensagem, acao, parent=None, cor="#f59e0b"):
    return DialogoConfirmacao(titulo, mensagem, acao, parent, cor).exec() == QDialog.Accepted

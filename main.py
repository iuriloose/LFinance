import sys

from PySide6.QtCore import QTimer

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from banco.banco import criar_tabelas
from telas.principal import TelaPrincipal
from servicos.configuracoes_app import (
    APP_VERSAO,
    caminho_recurso,
    nome_inicial_precisa_ser_configurado,
    salvar_nome_usuario,
)


class JanelaBoasVindas(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bem-vindo ao LFinance")
        self.setFixedSize(440, 260)
        icone = caminho_recurso("assets", "logo.ico")
        if icone.exists():
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(icone)))

        self.setStyleSheet("""
            QDialog { background-color: #07111d; }
            QLabel { color: #f8fafc; font-family: Segoe UI; }
            QLabel#tituloBoasVindas { font-size: 24px; font-weight: 800; }
            QLabel#textoBoasVindas { font-size: 14px; color: #cbd5e1; }
            QLineEdit {
                background-color: #101b2d;
                color: #ffffff;
                border: 1px solid #26364e;
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 15px;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; }
            QPushButton {
                background-color: #17331f;
                color: #ffffff;
                border: 1px solid #22c55e;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1f442a; border: 1px solid #4ade80; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        titulo = QLabel("Bem-vindo ao LFinance")
        titulo.setObjectName("tituloBoasVindas")

        texto = QLabel("Antes de começar, como você gostaria de ser chamado?")
        texto.setObjectName("textoBoasVindas")
        texto.setWordWrap(True)

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Digite seu nome")
        self.campo_nome.returnPressed.connect(self.confirmar)

        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_continuar = QPushButton("Continuar")
        btn_continuar.clicked.connect(self.confirmar)
        botoes.addWidget(btn_continuar)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addSpacing(8)
        layout.addWidget(self.campo_nome)
        layout.addStretch()
        layout.addLayout(botoes)

    def confirmar(self):
        nome = self.campo_nome.text().strip()
        if not nome:
            self.campo_nome.setFocus()
            return
        salvar_nome_usuario(nome)
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LFinance")
    app.setApplicationVersion(APP_VERSAO)

    try:
        criar_tabelas()
    except Exception as erro:
        QMessageBox.critical(
            None,
            "Não foi possível iniciar o LFinance",
            "O banco de dados não pôde ser preparado.\n\n"
            f"Detalhes: {erro}",
        )
        return 1

    if nome_inicial_precisa_ser_configurado():
        boas_vindas = JanelaBoasVindas()
        boas_vindas.exec()

    janela = TelaPrincipal()
    janela.showMaximized()
    QTimer.singleShot(1200, janela.verificar_atualizacoes_automaticamente)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

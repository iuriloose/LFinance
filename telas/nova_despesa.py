from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate

from banco.banco import inserir_despesa


class NovaDespesa(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nova despesa")
        self.setFixedSize(440, 470)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1117;
            }

            QLabel {
                color: #f5f5f5;
                font-family: Segoe UI;
                font-size: 14px;
            }

            QLabel#titulo {
                font-size: 26px;
                font-weight: bold;
            }

            QLineEdit, QComboBox, QDateEdit {
                background-color: #181d29;
                color: white;
                border: 1px solid #252b3a;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }

            QPushButton {
                padding: 12px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#cancelar {
                background-color: #202638;
                color: #d7dcf0;
                border: none;
            }

            QPushButton#salvar {
                background-color: #2d6cdf;
                color: white;
                border: none;
            }
        """)

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        titulo = QLabel("Nova despesa")
        titulo.setObjectName("titulo")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: Internet, mercado, luz...")

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Ex: 129,90")

        self.vencimento = QDateEdit()
        self.vencimento.setCalendarPopup(True)
        self.vencimento.setDate(QDate.currentDate())
        self.vencimento.setDisplayFormat("dd/MM/yyyy")

        self.categoria = QComboBox()
        self.categoria.addItems(["Casa", "Mercado", "Internet", "Luz", "Água", "Carro", "Outros"])

        self.tipo = QComboBox()
        self.tipo.addItems(["Despesa única", "Conta fixa", "Parcelamento"])

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("salvar")
        btn_salvar.clicked.connect(self.salvar_despesa)

        botoes = QHBoxLayout()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)

        layout.addWidget(titulo)
        layout.addSpacing(8)

        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(self.descricao)

        layout.addWidget(QLabel("Valor"))
        layout.addWidget(self.valor)

        layout.addWidget(QLabel("Vencimento"))
        layout.addWidget(self.vencimento)

        layout.addWidget(QLabel("Categoria"))
        layout.addWidget(self.categoria)

        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.tipo)

        layout.addStretch()
        layout.addLayout(botoes)

    def salvar_despesa(self):
        descricao = self.descricao.text().strip()
        valor_texto = self.valor.text().strip().replace(",", ".")
        vencimento = self.vencimento.date().toString("yyyy-MM-dd")
        categoria = self.categoria.currentText()
        tipo = self.tipo.currentText()

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Preencha a descrição.")
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Digite um valor válido. Ex: 129,90")
            return

        if valor <= 0:
            QMessageBox.warning(self, "Atenção", "O valor precisa ser maior que zero.")
            return

        inserir_despesa(descricao, valor, vencimento, categoria, tipo)

        self.accept()
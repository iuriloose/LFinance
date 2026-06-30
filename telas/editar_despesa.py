from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate

from banco.banco import atualizar_despesa


class EditarDespesa(QDialog):
    def __init__(self, despesa):
        super().__init__()

        self.id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa

        self.setWindowTitle("Editar despesa")
        self.setFixedSize(440, 470)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        titulo = QLabel("Editar despesa")
        titulo.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.descricao = QLineEdit(descricao)
        self.valor = QLineEdit(str(valor).replace(".", ","))

        self.vencimento = QDateEdit()
        self.vencimento.setCalendarPopup(True)
        self.vencimento.setDisplayFormat("dd/MM/yyyy")
        self.vencimento.setDate(QDate.fromString(vencimento, "yyyy-MM-dd"))

        self.categoria = QComboBox()
        self.categoria.addItems(["Casa", "Mercado", "Internet", "Luz", "Água", "Carro", "Outros"])
        self.categoria.setCurrentText(categoria)

        self.tipo = QComboBox()
        self.tipo.addItems(["Despesa única", "Conta fixa", "Parcelamento"])
        self.tipo.setCurrentText(tipo)

        btn_cancelar = QPushButton("Cancelar")
        btn_salvar = QPushButton("Salvar alterações")

        btn_cancelar.clicked.connect(self.reject)
        btn_salvar.clicked.connect(self.salvar)

        botoes = QHBoxLayout()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)

        layout.addWidget(titulo)
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

    def salvar(self):
        descricao = self.descricao.text().strip()
        valor_texto = self.valor.text().strip().replace(",", ".")

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Preencha a descrição.")
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Digite um valor válido.")
            return

        atualizar_despesa(
            self.id_despesa,
            descricao,
            valor,
            self.vencimento.date().toString("yyyy-MM-dd"),
            self.categoria.currentText(),
            self.tipo.currentText(),
        )

        self.accept()
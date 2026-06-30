from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate

from modelos.despesa import Despesa
from servicos.financeiro import Financeiro
from banco.banco import atualizar_despesa


class NovaDespesa(QDialog):
    def __init__(self, despesa=None):
        super().__init__()

        self.despesa = despesa
        self.modo_edicao = despesa is not None

        self.setWindowTitle("Editar despesa" if self.modo_edicao else "Nova despesa")
        self.setFixedSize(520, 380)

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
                background-color: transparent;
            }

            QLabel#titulo {
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#subtitulo {
                color: #9aa2b8;
                font-size: 13px;
            }

            QLineEdit, QComboBox {
                background-color: #181d29;
                color: white;
                border: 1px solid #252b3a;
                border-radius: 8px;
                padding: 5px 10px;
                min-height: 28px;
                font-size: 14px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2d6cdf;
            }

            QComboBox::drop-down {
                border: none;
                background-color: #181d29;
                width: 28px;
            }

            QPushButton {
                min-height: 34px;
                border-radius: 9px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }

            QPushButton#cancelar {
                background-color: #202638;
                color: #d7dcf0;
            }

            QPushButton#salvar {
                background-color: #2d6cdf;
                color: white;
            }
        """)

    def campo(self, titulo, widget):
        bloco = QVBoxLayout()
        bloco.setSpacing(4)

        label = QLabel(titulo)
        bloco.addWidget(label)
        bloco.addWidget(widget)

        return bloco

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        titulo = QLabel("Editar despesa" if self.modo_edicao else "Nova despesa")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Altere os dados da despesa"
            if self.modo_edicao
            else "Cadastre uma saída de dinheiro"
        )
        subtitulo.setObjectName("subtitulo")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: Internet, mercado, luz...")
        self.descricao.returnPressed.connect(self.salvar_despesa)

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("129,90")
        self.valor.returnPressed.connect(self.salvar_despesa)

        self.vencimento = QLineEdit()
        self.vencimento.setInputMask("00/00/0000")
        self.vencimento.setText(QDate.currentDate().toString("dd/MM/yyyy"))
        self.vencimento.returnPressed.connect(self.salvar_despesa)

        self.categoria = QComboBox()
        self.categoria.addItems(["Casa", "Mercado", "Internet", "Luz", "Água", "Carro", "Outros"])

        self.tipo = QComboBox()
        self.tipo.addItems(["Despesa única", "Conta fixa", "Parcelamento"])

        self.valor.setMinimumWidth(220)
        self.vencimento.setMinimumWidth(220)
        self.categoria.setMinimumWidth(220)
        self.tipo.setMinimumWidth(220)

        if self.modo_edicao:
            self.preencher_campos()

        linha_valor_data = QHBoxLayout()
        linha_valor_data.setSpacing(12)
        linha_valor_data.addLayout(self.campo("Valor", self.valor))
        linha_valor_data.addLayout(self.campo("Vencimento", self.vencimento))

        linha_categoria_tipo = QHBoxLayout()
        linha_categoria_tipo.setSpacing(12)
        linha_categoria_tipo.addLayout(self.campo("Categoria", self.categoria))
        linha_categoria_tipo.addLayout(self.campo("Tipo", self.tipo))

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.setFixedWidth(120)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("salvar")
        btn_salvar.setFixedWidth(120)
        btn_salvar.clicked.connect(self.salvar_despesa)

        botoes = QHBoxLayout()
        botoes.setSpacing(12)
        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)
        layout.addLayout(self.campo("Descrição", self.descricao))
        layout.addLayout(linha_valor_data)
        layout.addLayout(linha_categoria_tipo)
        layout.addStretch()
        layout.addLayout(botoes)

        self.descricao.setFocus()

    def preencher_campos(self):
        id_despesa, descricao, valor, vencimento, categoria, tipo, status = self.despesa

        self.descricao.setText(descricao)
        self.valor.setText(f"{valor:.2f}".replace(".", ","))

        data = QDate.fromString(vencimento, "yyyy-MM-dd")
        self.vencimento.setText(data.toString("dd/MM/yyyy"))

        self.categoria.setCurrentText(categoria)
        self.tipo.setCurrentText(tipo)

    def salvar_despesa(self):
        descricao = self.descricao.text().strip()
        valor_texto = self.valor.text().strip().replace(",", ".")
        data_texto = self.vencimento.text().strip()
        categoria = self.categoria.currentText()
        tipo = self.tipo.currentText()

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Preencha a descrição.")
            self.descricao.setFocus()
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Digite um valor válido. Ex: 129,90")
            self.valor.setFocus()
            return

        data = QDate.fromString(data_texto, "dd/MM/yyyy")
        if not data.isValid():
            QMessageBox.warning(self, "Atenção", "Digite uma data válida. Ex: 30/06/2026")
            self.vencimento.setFocus()
            return

        vencimento = data.toString("yyyy-MM-dd")

        if self.modo_edicao:
            id_despesa = self.despesa[0]
            atualizar_despesa(id_despesa, descricao, valor, vencimento, categoria, tipo)
        else:
            despesa = Despesa(descricao, valor, vencimento, categoria, tipo)
            Financeiro.adicionar_despesa(despesa)

        self.accept()
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate

from banco.banco import inserir_gasto, atualizar_gasto
from servicos.valores import converter_texto_moeda


class NovoGasto(QDialog):
    def __init__(self, gasto=None):
        super().__init__()

        self.gasto = gasto
        self.modo_edicao = gasto is not None

        self.setWindowTitle("Editar gasto" if self.modo_edicao else "Novo gasto")
        self.setFixedSize(520, 460)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog { background-color: #0f1117; }

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
                border: 1px solid #f59e0b;
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
                background-color: #f59e0b;
                color: white;
            }

            QPushButton#salvar:hover {
                background-color: #fbbf24;
            }
        """)

    def campo(self, titulo, widget):
        bloco = QVBoxLayout()
        bloco.setSpacing(4)

        label = QLabel(titulo)
        bloco.addWidget(label)
        bloco.addWidget(widget)

        return bloco, label

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        titulo = QLabel("Editar gasto" if self.modo_edicao else "Novo gasto")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Altere os dados do gasto" if self.modo_edicao else "Cadastre um gasto já realizado, sem virar conta ativa"
        )
        subtitulo.setObjectName("subtitulo")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: Mercado, gasolina, farmácia...")

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Ex: 100,00")

        self.data_gasto = QLineEdit()
        self.data_gasto.setInputMask("00/00/0000")
        self.data_gasto.setText(QDate.currentDate().toString("dd/MM/yyyy"))

        self.categoria = QComboBox()
        self.categoria.addItems(["Mercado", "Gasolina", "Farmácia", "Casa", "Comida", "Carro", "PIX", "Outros"])

        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText("Observação opcional")

        self.valor.setMinimumWidth(220)
        self.data_gasto.setMinimumWidth(220)
        self.categoria.setMinimumWidth(220)
        self.observacao.setMinimumWidth(220)

        if self.modo_edicao:
            self.preencher_campos()

        campo_descricao, _ = self.campo("Descrição", self.descricao)

        linha_valor_data = QHBoxLayout()
        linha_valor_data.setSpacing(12)
        campo_valor, _ = self.campo("Valor", self.valor)
        campo_data, _ = self.campo("Data", self.data_gasto)
        linha_valor_data.addLayout(campo_valor)
        linha_valor_data.addLayout(campo_data)

        linha_categoria = QHBoxLayout()
        linha_categoria.setSpacing(12)
        campo_categoria, _ = self.campo("Categoria", self.categoria)
        campo_observacao, _ = self.campo("Observação", self.observacao)
        linha_categoria.addLayout(campo_categoria)
        linha_categoria.addLayout(campo_observacao)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.setFixedWidth(120)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("salvar")
        btn_salvar.setFixedWidth(120)
        btn_salvar.clicked.connect(self.salvar_gasto)

        botoes = QHBoxLayout()
        botoes.setSpacing(12)
        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)
        layout.addLayout(campo_descricao)
        layout.addLayout(linha_valor_data)
        layout.addLayout(linha_categoria)
        layout.addStretch()
        layout.addLayout(botoes)

        self.descricao.setFocus()

    def preencher_campos(self):
        id_gasto, descricao, valor, data_gasto, categoria, observacao = self.gasto

        self.descricao.setText(descricao or "")
        self.valor.setText(f"{float(valor):.2f}".replace(".", ","))

        data = QDate.fromString(data_gasto, "yyyy-MM-dd")
        if data.isValid():
            self.data_gasto.setText(data.toString("dd/MM/yyyy"))

        indice = self.categoria.findText(categoria or "")
        if indice >= 0:
            self.categoria.setCurrentIndex(indice)

        self.observacao.setText(observacao or "")

    def salvar_gasto(self):
        descricao = self.descricao.text().strip()
        data_texto = self.data_gasto.text().strip()
        categoria = self.categoria.currentText()
        observacao = self.observacao.text().strip()

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Informe a descrição do gasto.")
            self.descricao.setFocus()
            return

        try:
            valor = converter_texto_moeda(self.valor.text())
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Informe um valor maior que zero. Ex: 100,00")
            self.valor.setFocus()
            return

        data = QDate.fromString(data_texto, "dd/MM/yyyy")
        if not data.isValid():
            QMessageBox.warning(self, "Atenção", "Informe uma data válida. Ex: 30/06/2026")
            self.data_gasto.setFocus()
            return

        data_banco = data.toString("yyyy-MM-dd")

        if self.modo_edicao:
            atualizar_gasto(self.gasto[0], descricao, valor, data_banco, categoria, observacao)
        else:
            inserir_gasto(descricao, valor, data_banco, categoria, observacao)

        self.accept()

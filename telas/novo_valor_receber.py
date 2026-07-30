from PySide6.QtCore import QDate, QLocale
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from banco.valores_receber import inserir_valor_receber, atualizar_valor_receber


class NovoValorReceber(QDialog):
    def __init__(self, valor_receber=None, parent=None):
        super().__init__(parent)
        self.valor_receber = valor_receber
        self.modo_edicao = valor_receber is not None
        self.setWindowTitle(
            "Editar valor a receber" if self.modo_edicao else "Novo valor a receber"
        )
        self.setFixedSize(560, 560)
        self.setModal(True)
        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog { background-color: #0f1726; }
            QLabel {
                color: #d7dcf0;
                font: 12px 'Segoe UI';
                background: transparent;
            }
            QLabel#tituloCadastro {
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#subtituloCadastro {
                color: #94a3b8;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                background: #151c2b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 13px;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 1px solid #38bdf8;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 28px;
            }
            QPushButton {
                min-height: 40px;
                border-radius: 9px;
                padding: 0 20px;
                color: #ffffff;
                font-weight: 700;
            }
            QPushButton#cancelar {
                background: #1f2937;
                border: 1px solid #475569;
            }
            QPushButton#salvar {
                background: #0369a1;
                border: 1px solid #38bdf8;
            }
            QPushButton#salvar:hover { background: #0284c7; }
        """)

    def criar_campo(self, titulo, widget):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.addWidget(QLabel(titulo))
        layout.addWidget(widget)
        return layout

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)

        titulo = QLabel(
            "Editar valor a receber" if self.modo_edicao else "Novo valor a receber"
        )
        titulo.setObjectName("tituloCadastro")
        subtitulo = QLabel("Registre um dinheiro previsto, sem alterar seu saldo atual")
        subtitulo.setObjectName("subtituloCadastro")
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)

        self.pagador = QLineEdit()
        self.pagador.setPlaceholderText("Ex.: Empresa, cliente ou pessoa")
        self.pagador.setAccessibleName("Pessoa ou empresa pagadora")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex.: Salário, comissão ou empréstimo")
        self.descricao.setAccessibleName("Descrição do valor a receber")

        self.valor = QDoubleSpinBox()
        self.valor.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.valor.setRange(0.01, 999999999.99)
        self.valor.setDecimals(2)
        self.valor.setPrefix("R$ ")
        self.valor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.valor.setAccessibleName("Valor total previsto")

        self.data_prevista = QDateEdit(QDate.currentDate())
        self.data_prevista.setCalendarPopup(True)
        self.data_prevista.setDisplayFormat("dd/MM/yyyy")
        self.data_prevista.setAccessibleName("Data prevista")

        self.categoria = QComboBox()
        self.categoria.addItems(
            ["Salário", "Comissão", "Venda", "Empréstimo", "Reembolso", "Outros"]
        )
        self.categoria.setAccessibleName("Categoria")

        self.recorrencia = QComboBox()
        self.recorrencia.addItem("Recebimento único", False)
        self.recorrencia.addItem("Repetir mensalmente", True)
        self.recorrencia.setAccessibleName("Recorrência")
        self.recorrencia.setToolTip(
            "Ao concluir um recebimento mensal, o próximo mês será criado automaticamente."
        )

        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText("Informação opcional")
        self.observacao.setAccessibleName("Observação")

        layout.addLayout(self.criar_campo("Pessoa ou empresa", self.pagador))
        layout.addLayout(self.criar_campo("Descrição", self.descricao))

        linha_valor_data = QHBoxLayout()
        linha_valor_data.setSpacing(12)
        linha_valor_data.addLayout(self.criar_campo("Valor total", self.valor))
        linha_valor_data.addLayout(
            self.criar_campo("Previsão de recebimento", self.data_prevista)
        )
        layout.addLayout(linha_valor_data)

        linha_categoria_recorrencia = QHBoxLayout()
        linha_categoria_recorrencia.setSpacing(12)
        linha_categoria_recorrencia.addLayout(
            self.criar_campo("Categoria", self.categoria)
        )
        linha_categoria_recorrencia.addLayout(
            self.criar_campo("Frequência", self.recorrencia)
        )
        layout.addLayout(linha_categoria_recorrencia)
        layout.addLayout(self.criar_campo("Observação", self.observacao))

        if self.modo_edicao:
            self.preencher()

        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("cancelar")
        cancelar.clicked.connect(self.reject)
        salvar = QPushButton("Salvar alterações" if self.modo_edicao else "Cadastrar")
        salvar.setObjectName("salvar")
        salvar.clicked.connect(self.salvar)
        botoes.addWidget(cancelar)
        botoes.addWidget(salvar)

        layout.addStretch()
        layout.addLayout(botoes)
        self.pagador.setFocus()

    def preencher(self):
        atual = self.valor_receber
        self.pagador.setText(atual[1] or "")
        self.descricao.setText(atual[2] or "")
        self.valor.setValue(float(atual[3] or 0))
        data = QDate.fromString(atual[4], "yyyy-MM-dd")
        if data.isValid():
            self.data_prevista.setDate(data)
        indice_categoria = self.categoria.findText(atual[5] or "")
        if indice_categoria >= 0:
            self.categoria.setCurrentIndex(indice_categoria)
        indice_recorrencia = self.recorrencia.findData(bool(atual[6]))
        if indice_recorrencia >= 0:
            self.recorrencia.setCurrentIndex(indice_recorrencia)
        self.observacao.setText(atual[8] or "")

    def salvar(self):
        pagador = self.pagador.text().strip()
        descricao = self.descricao.text().strip()
        if not pagador:
            QMessageBox.warning(self, "Atenção", "Informe a pessoa ou empresa.")
            self.pagador.setFocus()
            return
        if not descricao:
            QMessageBox.warning(self, "Atenção", "Informe a descrição.")
            self.descricao.setFocus()
            return

        argumentos = (
            pagador,
            descricao,
            self.valor.value(),
            self.data_prevista.date().toString("yyyy-MM-dd"),
            self.categoria.currentText(),
            self.recorrencia.currentData(),
            self.observacao.text().strip(),
        )
        try:
            if self.modo_edicao:
                sucesso, mensagem = atualizar_valor_receber(
                    self.valor_receber[0], *argumentos
                )
                if not sucesso:
                    QMessageBox.warning(self, "Alteração não realizada", mensagem)
                    return
            else:
                inserir_valor_receber(*argumentos)
        except (TypeError, ValueError) as erro:
            QMessageBox.warning(self, "Atenção", str(erro))
            return

        self.accept()

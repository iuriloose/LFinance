from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox,
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

from banco.valores_receber import registrar_recebimento


def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class ReceberValor(QDialog):
    def __init__(self, valor_receber, parent=None):
        super().__init__(parent)
        self.valor_receber = valor_receber
        self.setWindowTitle("Registrar recebimento")
        self.setFixedSize(520, 540)
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
            QLabel#tituloRecebimento {
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#descricaoRecebimento {
                color: #94a3b8;
                font-size: 14px;
            }
            QLabel#resumoRecebimento {
                color: #e2e8f0;
                font-size: 13px;
                padding: 14px;
                background: #151c2b;
                border: 1px solid #26364e;
                border-radius: 9px;
            }
            QDoubleSpinBox, QDateEdit, QLineEdit {
                background: #151c2b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                min-height: 28px;
            }
            QDoubleSpinBox:focus, QDateEdit:focus, QLineEdit:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                min-height: 40px;
                border-radius: 9px;
                padding: 0 18px;
                color: #ffffff;
                font-weight: 700;
            }
            QPushButton#cancelar {
                background: #1f2937;
                border: 1px solid #475569;
            }
            QPushButton#confirmar {
                background: #15803d;
                border: 1px solid #22c55e;
            }
            QPushButton#confirmar:hover { background: #16a34a; }
        """)

    def montar_tela(self):
        atual = self.valor_receber
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(10)

        titulo = QLabel("Registrar recebimento")
        titulo.setObjectName("tituloRecebimento")
        descricao = QLabel(f"{atual[2]}  •  {atual[1]}")
        descricao.setObjectName("descricaoRecebimento")
        layout.addWidget(titulo)
        layout.addWidget(descricao)

        resumo = QLabel(
            f"Valor previsto:  {formatar_moeda(atual[3])}\n"
            f"Já recebido:      {formatar_moeda(atual[9])}\n"
            f"Saldo restante:  {formatar_moeda(atual[10])}"
        )
        resumo.setObjectName("resumoRecebimento")
        resumo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(resumo)

        layout.addWidget(QLabel("Valor recebido agora"))
        self.valor = QDoubleSpinBox()
        self.valor.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.valor.setRange(0.01, 999999999.99)
        self.valor.setDecimals(2)
        self.valor.setPrefix("R$ ")
        self.valor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.valor.setValue(float(atual[10]))
        self.valor.setAccessibleName("Valor recebido agora")
        layout.addWidget(self.valor)

        layout.addWidget(QLabel("Data do recebimento"))
        self.data = QDateEdit(QDate.currentDate())
        self.data.setCalendarPopup(True)
        self.data.setDisplayFormat("dd/MM/yyyy")
        self.data.setAccessibleName("Data do recebimento")
        layout.addWidget(self.data)

        layout.addWidget(QLabel("Observação (opcional)"))
        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText("Ex.: primeira parcela, pagamento via PIX")
        self.observacao.setAccessibleName("Observação do recebimento")
        layout.addWidget(self.observacao)

        aviso = QLabel(
            "Ao confirmar, este valor será registrado automaticamente em Receitas.\n"
            "Se recebeu mais que o previsto, informe o valor real: este lançamento será ajustado, "
            "mas a próxima recorrência manterá o valor previsto original."
        )
        aviso.setWordWrap(True)
        aviso.setStyleSheet("color: #7dd3fc; font-size: 11px;")
        layout.addWidget(aviso)

        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("cancelar")
        cancelar.clicked.connect(self.reject)
        confirmar = QPushButton("✓ Confirmar recebimento")
        confirmar.setObjectName("confirmar")
        confirmar.clicked.connect(self.confirmar)
        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)

        layout.addStretch()
        layout.addLayout(botoes)
        self.valor.setFocus()

    def confirmar(self):
        sucesso, mensagem = registrar_recebimento(
            self.valor_receber[0],
            self.valor.value(),
            self.data.date().toString("yyyy-MM-dd"),
            self.observacao.text().strip(),
        )
        if not sucesso:
            QMessageBox.warning(self, "Recebimento não registrado", mensagem)
            return
        self.accept()

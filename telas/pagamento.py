from PySide6.QtCore import QDate, QLocale, Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox, QDateEdit, QDialog, QDoubleSpinBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QVBoxLayout
)

from banco.banco import buscar_despesa_por_id, pagar_despesa


class PagamentoDespesa(QDialog):
    def __init__(self, despesa, parent=None):
        super().__init__(parent)
        self.despesa = despesa
        self.valor_original = float(despesa[2] or 0)
        self.setWindowTitle("Registrar pagamento")
        self.setFixedSize(520, 535)
        self.setModal(True)
        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog { background-color: #0f1726; }
            QLabel { color: #d7dcf0; font: 12px 'Segoe UI'; }
            QLabel#tituloPagamento { color: #ffffff; font-size: 24px; font-weight: 800; }
            QLabel#descricaoPagamento { color: #a8b3c7; font-size: 14px; }
            QLabel#valorOriginal { color: #ffffff; font-size: 18px; font-weight: 800; }
            QLabel#diferencaPagamento { font-size: 13px; font-weight: 700; padding: 12px; background: #151c2b; border: 1px solid #26364e; border-radius: 8px; }
            QDoubleSpinBox, QDateEdit, QLineEdit { background: #151c2b; color: #ffffff; border: 1px solid #334155; border-radius: 8px; padding: 8px; font-size: 13px; min-height: 26px; }
            QPushButton { min-height: 40px; border-radius: 9px; padding: 0 18px; color: white; font-weight: 700; }
            QPushButton#cancelar { background: #1f2937; border: 1px solid #475569; }
            QPushButton#confirmar { background: #15803d; border: 1px solid #22c55e; }
            QPushButton#confirmar:hover { background: #16a34a; }
        """)

    def moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(9)

        titulo = QLabel("Registrar pagamento")
        titulo.setObjectName("tituloPagamento")
        descricao = QLabel(str(self.despesa[1]))
        descricao.setObjectName("descricaoPagamento")
        layout.addWidget(titulo)
        layout.addWidget(descricao)

        layout.addWidget(QLabel("Valor original"))
        original = QLabel(self.moeda(self.valor_original))
        original.setObjectName("valorOriginal")
        layout.addWidget(original)

        layout.addSpacing(4)
        layout.addWidget(QLabel("Valor final pago (incluindo juros ou multa)"))
        self.valor_pago = QDoubleSpinBox()
        self.valor_pago.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.valor_pago.setRange(0, 999999999.99)
        self.valor_pago.setDecimals(2)
        self.valor_pago.setPrefix("R$ ")
        self.valor_pago.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.valor_pago.setValue(self.valor_original)
        self.valor_pago.setFixedHeight(46)
        self.valor_pago.valueChanged.connect(self.atualizar_diferenca)
        layout.addWidget(self.valor_pago)

        self.diferenca = QLabel()
        self.diferenca.setObjectName("diferencaPagamento")
        self.diferenca.setMinimumHeight(76)
        self.diferenca.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.diferenca)

        layout.addSpacing(4)
        layout.addWidget(QLabel("Data do pagamento"))
        self.data_pagamento = QDateEdit(QDate.currentDate())
        self.data_pagamento.setCalendarPopup(True)
        self.data_pagamento.setDisplayFormat("dd/MM/yyyy")
        self.data_pagamento.setFixedHeight(46)
        layout.addWidget(self.data_pagamento)

        layout.addWidget(QLabel("Observação (opcional)"))
        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText("Ex.: multa por atraso")
        self.observacao.setFixedHeight(46)
        layout.addWidget(self.observacao)

        layout.addStretch()
        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("cancelar")
        cancelar.clicked.connect(self.reject)
        confirmar = QPushButton("✓ Confirmar pagamento")
        confirmar.setObjectName("confirmar")
        confirmar.clicked.connect(self.confirmar)
        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)
        layout.addLayout(botoes)
        self.atualizar_diferenca()

    def atualizar_diferenca(self):
        total_pago = round(self.valor_pago.value(), 2)
        diferenca = round(total_pago - self.valor_original, 2)
        acrescimo = max(diferenca, 0)
        desconto = max(-diferenca, 0)
        self.diferenca.setText(
            f"Juros/multa:  {self.moeda(acrescimo)}\n"
            f"Desconto:       {self.moeda(desconto)}\n"
            f"Total pago:     {self.moeda(total_pago)}"
        )
        if acrescimo > 0:
            self.diferenca.setStyleSheet("color: #f59e0b;")
        elif desconto > 0:
            self.diferenca.setStyleSheet("color: #22c55e;")
        else:
            self.diferenca.setStyleSheet("color: #d7dcf0;")

    def confirmar(self):
        sucesso, mensagem = pagar_despesa(
            self.despesa[0],
            valor_pago=self.valor_pago.value(),
            data_pagamento=self.data_pagamento.date().toString("yyyy-MM-dd"),
            observacao=self.observacao.text(),
        )
        if not sucesso:
            QMessageBox.warning(self, "Pagamento não registrado", mensagem)
            return
        self.accept()


def abrir_pagamento(id_despesa, parent=None):
    despesa = buscar_despesa_por_id(id_despesa)
    if not despesa:
        QMessageBox.warning(parent, "Pagamento", "A despesa não foi encontrada.")
        return False
    return PagamentoDespesa(despesa, parent).exec() == QDialog.Accepted

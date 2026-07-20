from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


ESTILO_TABELA_REGISTROS = """
    QTableWidget#tabelaRegistros {
        background-color: #111827;
        color: #f8fafc;
        border: 1px solid #263244;
        alternate-background-color: #162033;
        selection-background-color: #1e3a5f;
        selection-color: #ffffff;
        font-size: 13px;
    }
    QTableWidget#tabelaRegistros::item {
        padding: 0 8px;
        border-bottom: 1px solid #263244;
    }
    QHeaderView::section {
        background-color: #1f2937;
        color: #f8fafc;
        border: none;
        border-right: 1px solid #253044;
        border-bottom: 1px solid #334155;
        padding: 0 8px;
        font-weight: bold;
        font-size: 13px;
    }
    QScrollBar:vertical {
        background: #111827;
        width: 9px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #475569;
        min-height: 28px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover { background: #3b82f6; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""


class TabelaRegistros(QTableWidget):
    """Tabela compacta usada nas telas de cadastro e nos detalhes da tela inicial."""

    def __init__(
        self,
        colunas,
        larguras=None,
        coluna_flexivel=1,
        selecao_multipla=False,
        altura_linha=38,
    ):
        super().__init__()
        self.altura_linha = altura_linha
        self.setObjectName("tabelaRegistros")
        self.setColumnCount(len(colunas))
        self.setHorizontalHeaderLabels(colunas)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(
            QAbstractItemView.MultiSelection
            if selecao_multipla
            else QAbstractItemView.SingleSelection
        )
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setFixedHeight(34)
        self.horizontalHeader().setStretchLastSection(False)
        self.setStyleSheet(ESTILO_TABELA_REGISTROS)

        larguras = larguras or {}
        for indice in range(len(colunas)):
            if indice == coluna_flexivel:
                self.horizontalHeader().setSectionResizeMode(indice, QHeaderView.Stretch)
            else:
                self.horizontalHeader().setSectionResizeMode(indice, QHeaderView.Fixed)
                self.setColumnWidth(indice, larguras.get(indice, 120))

    def adicionar_linha(
        self,
        valores,
        dados=None,
        colunas_esquerda=(1,),
        cores=None,
        tooltips=None,
    ):
        linha = self.rowCount()
        self.insertRow(linha)
        self.setRowHeight(linha, self.altura_linha)

        cores = cores or {}
        tooltips = tooltips or {}
        for coluna, valor in enumerate(valores):
            item = QTableWidgetItem(str(valor if valor is not None else ""))
            if coluna in colunas_esquerda:
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            else:
                item.setTextAlignment(Qt.AlignCenter)
            if coluna in cores:
                item.setForeground(QColor(cores[coluna]))
            if coluna in tooltips and tooltips[coluna]:
                item.setToolTip(str(tooltips[coluna]))
            if dados is not None:
                item.setData(Qt.UserRole, dados)
            self.setItem(linha, coluna, item)
        return linha

    def definir_acoes(self, linha, botoes, coluna=None):
        coluna = self.columnCount() - 1 if coluna is None else coluna
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)
        for botao in botoes:
            layout.addWidget(botao)
        self.setCellWidget(linha, coluna, container)

    def mostrar_vazio(self, texto):
        self.setRowCount(1)
        self.setSpan(0, 0, 1, self.columnCount())
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QColor("#94a3b8"))
        item.setFlags(Qt.NoItemFlags)
        self.setItem(0, 0, item)
        self.setRowHeight(0, 44)


def criar_botao_acao(texto, callback, cor="#3b82f6", largura=80, tooltip=""):
    botao = QPushButton(texto)
    botao.setFixedHeight(27)
    botao.setMinimumWidth(largura)
    botao.setCursor(Qt.PointingHandCursor)
    if tooltip:
        botao.setToolTip(tooltip)
    botao.setStyleSheet(f"""
        QPushButton {{
            background-color: #182235;
            color: #e2e8f0;
            border: 1px solid {cor};
            border-radius: 6px;
            padding: 0 9px;
            font-size: 10px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {cor}; color: #ffffff; }}
    """)
    botao.clicked.connect(callback)
    return botao


def cor_status(texto):
    texto = str(texto).lower()
    if "atras" in texto:
        return "#ef4444"
    if texto in ("paga", "pago", "recebida"):
        return "#22c55e"
    if texto in ("hoje", "amanhã"):
        return "#f59e0b"
    return "#22c55e"


def criar_resumo_textual(textos):
    linha = QHBoxLayout()
    linha.setSpacing(18)
    for titulo, valor, cor in textos:
        label = QLabel(f"{titulo}: <b>{valor}</b>")
        label.setStyleSheet(f"color: {cor}; font-size: 12px;")
        linha.addWidget(label)
    linha.addStretch()
    return linha

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QWidget, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt


class TabelaFinanceira(QTableWidget):
    def __init__(self, colunas):
        super().__init__()

        self.setColumnCount(len(colunas))
        self.setHorizontalHeaderLabels(colunas)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.horizontalHeader().setFixedHeight(32)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.setObjectName("tabelaFinanceira")

        self.setStyleSheet("""
            QTableWidget#tabelaFinanceira {
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #263244;
                border-radius: 12px;
                alternate-background-color: #162033;
                selection-background-color: #1d4ed8;
                selection-color: white;
                font-size: 14px;
            }

            QTableWidget#tabelaFinanceira::item {
                padding-left: 8px;
                padding-right: 8px;
                border-bottom: 1px solid #263244;
            }

            QHeaderView::section {
                background-color: #1f2937;
                color: #f8fafc;
                border: none;
                border-bottom: 1px solid #334155;
                font-weight: bold;
                font-size: 14px;
            }

            QScrollBar:vertical {
                background: #111827;
                width: 10px;
                margin: 3px 2px 3px 2px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #475569;
                min-height: 28px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #3b82f6;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.configurar_larguras(len(colunas))

    def configurar_larguras(self, quantidade_colunas):
        if quantidade_colunas == 5:
            self.setColumnWidth(0, 90)
            self.setColumnWidth(1, 500)
            self.setColumnWidth(2, 150)
            self.setColumnWidth(3, 160)
            self.setColumnWidth(4, 90)

            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
            self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        else:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def limpar(self):
        self.setRowCount(0)

    def criar_item(self, texto, alinhamento):
        item = QTableWidgetItem(str(texto))
        item.setTextAlignment(alinhamento)
        return item

    def criar_etiqueta_situacao(self, texto):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(texto)
        label.setAlignment(Qt.AlignCenter)

        if texto == "Hoje":
            cor_fundo = "#facc15"
            cor_texto = "#111827"
        elif texto == "Amanhã":
            cor_fundo = "#f97316"
            cor_texto = "#ffffff"
        elif texto == "Atrasada":
            cor_fundo = "#ef4444"
            cor_texto = "#ffffff"
        else:
            cor_fundo = "#1d4ed8"
            cor_texto = "#dbeafe"

        label.setStyleSheet(f"""
            QLabel {{
                background-color: {cor_fundo};
                color: {cor_texto};
                border-radius: 8px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)

        layout.addWidget(label)
        return container

    def adicionar_linha(self, valores):
        linha = self.rowCount()
        self.insertRow(linha)
        self.setRowHeight(linha, 32)

        self.setItem(linha, 0, self.criar_item(valores[0], Qt.AlignCenter))
        self.setItem(linha, 1, self.criar_item(valores[1], Qt.AlignLeft | Qt.AlignVCenter))
        self.setItem(linha, 2, self.criar_item(valores[2], Qt.AlignCenter))
        self.setCellWidget(linha, 3, self.criar_etiqueta_situacao(str(valores[3])))
        self.setItem(linha, 4, self.criar_item(valores[4], Qt.AlignCenter))
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QSizePolicy,
)

from banco.banco import listar_despesas, listar_receitas, listar_gastos
from telas.nova_despesa import NovaDespesa
from telas.nova_receita import NovaReceita
from telas.novo_gasto import NovoGasto


class TelaPesquisa(QWidget):
    def __init__(self, ao_alterar=None):
        super().__init__()
        self.ao_alterar = ao_alterar
        self.registros = []
        self.montar_tela()
        self.recarregar()

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 26, 36, 24)
        layout.setSpacing(14)

        titulo = QLabel("🔎 Pesquisar")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Encontre contas, gastos do dia e receitas em um só lugar")
        subtitulo.setObjectName("subtitulo")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        painel_busca = QFrame()
        painel_busca.setObjectName("painelPesquisa")
        painel_busca.setStyleSheet("""
            QFrame#painelPesquisa {
                background-color: rgba(17, 28, 46, 0.96);
                border: 1px solid #26364e;
                border-radius: 14px;
            }
            QLineEdit {
                background-color: #0f1a2b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 9px;
                padding: 9px 13px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #3b82f6; }
            QComboBox {
                background-color: #0f1a2b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 9px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:focus { border-color: #3b82f6; }
            QComboBox::drop-down {
                width: 26px;
                border: none;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
            }
        """)
        busca_layout = QHBoxLayout(painel_busca)
        busca_layout.setContentsMargins(14, 12, 14, 12)
        busca_layout.setSpacing(10)

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Digite um nome, categoria, valor ou situação...")
        self.campo_busca.setClearButtonEnabled(True)
        self.campo_busca.textChanged.connect(self.filtrar)

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.setMinimumWidth(180)
        self.filtro_tipo.addItem("Todos os lançamentos", "todos")
        self.filtro_tipo.addItem("Contas a pagar", "conta")
        self.filtro_tipo.addItem("Gastos do dia", "gasto")
        self.filtro_tipo.addItem("Receitas", "receita")
        self.filtro_tipo.currentIndexChanged.connect(self.filtrar)

        busca_layout.addWidget(self.campo_busca, 1)
        busca_layout.addWidget(self.filtro_tipo)
        layout.addWidget(painel_busca)

        linha_info = QHBoxLayout()
        self.resumo = QLabel("0 lançamentos encontrados")
        self.resumo.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: bold;")
        dica = QLabel("Clique em Abrir ou dê dois cliques em uma linha")
        dica.setStyleSheet("color: #78869c; font-size: 11px;")
        linha_info.addWidget(self.resumo)
        linha_info.addStretch()
        linha_info.addWidget(dica)
        layout.addLayout(linha_info)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Descrição", "Categoria", "Tipo", "Situação", "Valor", "Ação"
        ])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setFocusPolicy(Qt.NoFocus)
        self.tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabela.cellDoubleClicked.connect(self.abrir_linha)

        header = self.tabela.horizontalHeader()
        header.setFixedHeight(34)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.tabela.setColumnWidth(0, 100)
        self.tabela.setColumnWidth(2, 135)
        self.tabela.setColumnWidth(3, 130)
        self.tabela.setColumnWidth(4, 110)
        self.tabela.setColumnWidth(5, 130)
        self.tabela.setColumnWidth(6, 100)

        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #263244;
                border-radius: 10px;
                alternate-background-color: #162033;
                selection-background-color: #1d4ed8;
                selection-color: #ffffff;
                font-size: 13px;
            }
            QTableWidget::item {
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
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #475569;
                min-height: 28px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0px; }
        """)
        layout.addWidget(self.tabela, 1)

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa
        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status
        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def formatar_data(self, texto):
        try:
            return datetime.strptime(texto, "%Y-%m-%d").strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return texto or ""

    def formatar_moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def recarregar(self):
        registros = []

        for despesa in listar_despesas():
            dados = self.separar_despesa(despesa)
            _, descricao, valor, vencimento, categoria, tipo, _, _, _, status = dados
            situacao = "Paga" if str(status).lower() == "paga" else "Em aberto"
            registros.append({
                "grupo": "conta",
                "data_banco": vencimento or "",
                "data": self.formatar_data(vencimento),
                "descricao": descricao or "",
                "categoria": categoria or "",
                "tipo": tipo or "Conta a pagar",
                "situacao": situacao,
                "valor": float(valor or 0),
                "registro": despesa,
            })

        for gasto in listar_gastos():
            _, descricao, valor, data_gasto, categoria, observacao = gasto
            registros.append({
                "grupo": "gasto",
                "data_banco": data_gasto or "",
                "data": self.formatar_data(data_gasto),
                "descricao": descricao or "",
                "categoria": categoria or "",
                "tipo": "Gasto do dia",
                "situacao": "Pago",
                "valor": float(valor or 0),
                "observacao": observacao or "",
                "registro": gasto,
            })

        for receita in listar_receitas():
            _, descricao, valor, data_recebimento, categoria, observacao = receita
            registros.append({
                "grupo": "receita",
                "data_banco": data_recebimento or "",
                "data": self.formatar_data(data_recebimento),
                "descricao": descricao or "",
                "categoria": categoria or "",
                "tipo": "Receita",
                "situacao": "Recebida",
                "valor": float(valor or 0),
                "observacao": observacao or "",
                "registro": receita,
            })

        self.registros = sorted(registros, key=lambda item: item["data_banco"], reverse=True)
        self.filtrar()

    def filtrar(self, *_):
        termo = self.campo_busca.text().strip().lower()
        grupo = self.filtro_tipo.currentData()

        resultados = []
        for item in self.registros:
            if grupo != "todos" and item["grupo"] != grupo:
                continue
            campos = [
                item["descricao"], item["categoria"], item["tipo"],
                item["situacao"], item.get("observacao", ""),
                self.formatar_moeda(item["valor"]),
            ]
            if termo and not any(termo in str(campo).lower() for campo in campos):
                continue
            resultados.append(item)

        self.preencher_tabela(resultados)

    def preencher_tabela(self, resultados):
        self.tabela.setRowCount(len(resultados))
        self.resumo.setText(
            f"{len(resultados)} lançamento encontrado" if len(resultados) == 1
            else f"{len(resultados)} lançamentos encontrados"
        )

        cores = {
            "Paga": "#22c55e",
            "Pago": "#22c55e",
            "Recebida": "#22c55e",
            "Em aberto": "#f59e0b",
        }

        for linha, item in enumerate(resultados):
            self.tabela.setRowHeight(linha, 38)
            valores = [
                item["data"], item["descricao"], item["categoria"], item["tipo"],
                item["situacao"], self.formatar_moeda(item["valor"]),
            ]
            for coluna, texto in enumerate(valores):
                celula = QTableWidgetItem(str(texto))
                alinhamento = Qt.AlignCenter
                celula.setTextAlignment(alinhamento)
                if coluna == 0:
                    celula.setData(Qt.UserRole, item)
                if coluna == 4:
                    celula.setForeground(QColor(cores.get(item["situacao"], "#cbd5e1")))
                self.tabela.setItem(linha, coluna, celula)

            container = QWidget()
            botoes = QHBoxLayout(container)
            botoes.setContentsMargins(5, 3, 5, 3)
            botao = QPushButton("Abrir")
            botao.setFixedHeight(26)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet("""
                QPushButton {
                    background-color: #17243a;
                    color: #ffffff;
                    border: 1px solid #3b82f6;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #2563eb; }
            """)
            botao.clicked.connect(lambda _, registro=item: self.abrir_registro(registro))
            botoes.addWidget(botao)
            self.tabela.setCellWidget(linha, 6, container)

    def abrir_linha(self, linha, _coluna):
        item = self.tabela.item(linha, 0)
        if item is not None:
            registro = item.data(Qt.UserRole)
            if registro:
                self.abrir_registro(registro)

    def abrir_registro(self, item):
        if item["grupo"] == "conta":
            janela = NovaDespesa(item["registro"])
        elif item["grupo"] == "gasto":
            janela = NovoGasto(item["registro"])
        else:
            janela = NovaReceita(item["registro"])

        if janela.exec():
            self.recarregar()
            if self.ao_alterar:
                self.ao_alterar()


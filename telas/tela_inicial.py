from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QGridLayout, QSizePolicy, QLineEdit, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtGui import QColor

from componentes.tabela import TabelaFinanceira
from telas.nova_despesa import NovaDespesa
from telas.nova_receita import NovaReceita
from telas.novo_gasto import NovoGasto
from telas.pagamento import abrir_pagamento
from servicos.configuracoes_app import obter_nome_usuario
from banco.banco import (
    listar_despesas,
    buscar_despesa_por_id,
    listar_receitas,
    listar_gastos,
    listar_pagamentos,
    pagar_despesa,
    desfazer_pagamento,
    reabrir_despesa,
    excluir_despesa_com_historico,
    excluir_despesa,
    excluir_gasto,
)


class JanelaDetalhesMes(QDialog):
    def __init__(self, titulo, subtitulo, secoes, cor="#3b82f6"):
        super().__init__()
        self.setWindowTitle(titulo)
        self.resize(760, 560)
        self.setMinimumSize(720, 500)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0f1117;
                color: #f8fafc;
                font-family: Segoe UI;
            }}
            QLabel#tituloDetalhe {{
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
            }}
            QLabel#subtituloDetalhe {{
                color: #9aa2b8;
                font-size: 13px;
            }}
            QLabel#secaoTitulo {{
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
            }}
            QLabel#resumoSecao {{
                color: #cbd5e1;
                font-size: 13px;
            }}
            QTableWidget {{
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #263244;
                border-radius: 8px;
                gridline-color: #263244;
                alternate-background-color: #162033;
                selection-background-color: {cor};
                selection-color: #ffffff;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding-left: 8px;
                padding-right: 8px;
                border-bottom: 1px solid #263244;
            }}
            QHeaderView::section {{
                background-color: #1f2937;
                color: #f8fafc;
                border: none;
                border-right: 1px solid #253044;
                border-bottom: 1px solid #334155;
                padding: 5px 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton#btnFechar {{
                background-color: #202638;
                color: #ffffff;
                padding: 8px 24px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #2d3447;
            }}
            QPushButton#btnFechar:hover {{
                background-color: #2d3447;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(10)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloDetalhe")

        lbl_subtitulo = QLabel(subtitulo)
        lbl_subtitulo.setObjectName("subtituloDetalhe")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_subtitulo)

        for secao in secoes:
            itens = secao.get("itens", [])
            total = sum(float(item.get("valor", 0) or 0) for item in itens)

            cabecalho = QHBoxLayout()

            lbl_secao = QLabel(secao.get("titulo", ""))
            lbl_secao.setObjectName("secaoTitulo")

            lbl_resumo = QLabel(f"{len(itens)} itens • {self.formatar_moeda(total)}")
            lbl_resumo.setObjectName("resumoSecao")
            lbl_resumo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            cabecalho.addWidget(lbl_secao)
            cabecalho.addStretch()
            cabecalho.addWidget(lbl_resumo)
            layout.addLayout(cabecalho)

            tabela = self.criar_tabela(itens)
            layout.addWidget(tabela, 1)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("btnFechar")
        btn_fechar.clicked.connect(self.accept)

        botoes.addWidget(btn_fechar)
        layout.addLayout(botoes)

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def criar_item(self, texto, alinhamento=Qt.AlignCenter):
        item = QTableWidgetItem(str(texto))
        item.setTextAlignment(alinhamento)
        return item

    def criar_tabela(self, itens):
        tabela = QTableWidget()
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Tipo", "Situação"])
        tabela.verticalHeader().setVisible(False)
        tabela.setShowGrid(False)
        tabela.setAlternatingRowColors(True)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setFocusPolicy(Qt.NoFocus)
        tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabela.horizontalHeader().setStretchLastSection(False)
        tabela.horizontalHeader().setFixedHeight(30)

        larguras = [90, 250, 110, 120, 110]
        for indice, largura in enumerate(larguras):
            tabela.setColumnWidth(indice, largura)
            tabela.horizontalHeader().setSectionResizeMode(indice, QHeaderView.Fixed)

        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        tabela.setRowCount(len(itens))
        for linha, item in enumerate(itens):
            tabela.setRowHeight(linha, 30)
            tabela.setItem(linha, 0, self.criar_item(item.get("data", "")))
            tabela.setItem(linha, 1, self.criar_item(item.get("descricao", ""), Qt.AlignCenter))
            tabela.setItem(linha, 2, self.criar_item(self.formatar_moeda(item.get("valor", 0))))
            tabela.setItem(linha, 3, self.criar_item(item.get("tipo", "")))
            tabela.setItem(linha, 4, self.criar_item(item.get("situacao", "")))

        if not itens:
            tabela.setRowCount(1)
            tabela.setSpan(0, 0, 1, 5)
            tabela.setItem(0, 0, self.criar_item("Nenhum item encontrado para este mês."))
            tabela.setRowHeight(0, 36)

        return tabela


class TelaInicial(QWidget):
    def __init__(self, ao_salvar_despesa=None):
        super().__init__()
        self.ao_salvar_despesa = ao_salvar_despesa
        self.caixa_busca = None
        self.montar_tela()

    def saudacao_atual(self):
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return "Bom dia"
        if 12 <= hora < 18:
            return "Boa tarde"
        return "Boa noite"

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa
        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status
        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m")
        except Exception:
            return data

    def converter_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").date()
        except Exception:
            return None

    def status_vencimento(self, data):
        hoje = date.today()
        if data < hoje:
            return "Atrasada"
        if data == hoje:
            return "Hoje"
        if data == hoje + timedelta(days=1):
            return "Amanhã"
        return f"Em {(data - hoje).days} dias"

    def aplicar_destaque_data_mes_atual(self, tabela, linha, data_vencimento):
        """Destaca de forma discreta as datas que vencem no mês atual."""
        hoje = date.today()
        if not data_vencimento or data_vencimento.month != hoje.month or data_vencimento.year != hoje.year:
            return

        item_data = tabela.item(linha, 0)
        if item_data is None:
            return

        item_data.setForeground(QColor("#eab308"))
        fonte = item_data.font()
        fonte.setBold(True)
        item_data.setFont(fonte)
        item_data.setToolTip("Esta conta vence no mês atual.")

    def obter_todas_despesas(self):
        despesas = []
        for despesa in listar_despesas():
            (
                id_despesa,
                descricao,
                valor,
                vencimento,
                categoria,
                tipo,
                parcela_atual,
                total_parcelas,
                _,
                status,
            ) = self.separar_despesa(despesa)
            data = self.converter_data(vencimento)
            if data is None:
                continue
            despesas.append({
                "id": id_despesa,
                "descricao": descricao,
                "valor": float(valor or 0),
                "vencimento": vencimento,
                "data": data,
                "tipo": tipo,
                "categoria": categoria,
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
                "status": status,
            })
        return despesas

    def obter_despesas(self):
        return [d for d in self.obter_todas_despesas() if d["status"] != "paga"]

    def obter_receitas(self):
        receitas = []
        for receita in listar_receitas():
            id_receita, descricao, valor, data_recebimento, categoria, observacao = receita
            data = self.converter_data(data_recebimento)
            if data is None:
                continue
            receitas.append({
                "id": id_receita,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_recebimento": data_recebimento,
                "data": data,
                "categoria": categoria,
                "observacao": observacao,
            })
        return receitas

    def obter_gastos(self):
        gastos = []
        for gasto in listar_gastos():
            id_gasto, descricao, valor, data_gasto, categoria, observacao = gasto
            data = self.converter_data(data_gasto)
            if data is None:
                continue
            gastos.append({
                "id": id_gasto,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_gasto": data_gasto,
                "data": data,
                "categoria": categoria,
                "observacao": observacao,
            })
        return gastos

    def obter_pagamentos(self):
        pagamentos = []
        for pagamento in listar_pagamentos():
            if len(pagamento) >= 10:
                id_pagamento, id_despesa, descricao, valor, data_pagamento, categoria, tipo, parcela_atual, total_parcelas, forma_pagamento = pagamento
            else:
                id_pagamento, id_despesa, descricao, valor, data_pagamento, categoria, tipo, parcela_atual, total_parcelas = pagamento
                forma_pagamento = "Não informado"
            data = self.converter_data(data_pagamento)
            if data is None:
                continue
            pagamentos.append({
                "id": id_pagamento,
                "id_despesa": id_despesa,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data_pagamento": data_pagamento,
                "data": data,
                "categoria": categoria,
                "tipo": tipo,
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
                "forma_pagamento": forma_pagamento,
            })
        return pagamentos

    def criar_card_resumo(self, objeto, icone, titulo, valor, info="", acao=None, tooltip=""):
        card = QFrame()
        card.setObjectName(objeto)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        lbl_icone = QLabel(icone)
        if objeto == "cardSaldoNegativo":
            lbl_icone.setObjectName("cardIconeNegativo")
        else:
            lbl_icone.setObjectName("cardIcone")

        textos = QVBoxLayout()
        textos.setSpacing(0)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitulo")

        lbl_valor = QLabel(valor)
        if objeto == "cardSaldoNegativo":
            lbl_valor.setObjectName("cardValorNegativo")
        else:
            lbl_valor.setObjectName("cardValorMini")

        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_valor)

        if info:
            lbl_info = QLabel(info)
            lbl_info.setObjectName("cardInfoMini")
            textos.addWidget(lbl_info)

        layout.addWidget(lbl_icone)
        layout.addLayout(textos)
        layout.addStretch()

        if tooltip:
            card.setToolTip(tooltip)
        if acao:
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda evento: acao()
            if not tooltip:
                card.setToolTip("Clique para ver os detalhes")
        return card

    def ajustar_tabela(self, tabela):
        tabela.horizontalHeader().setStretchLastSection(False)

    def item_detalhe(self, data, descricao, valor, tipo, situacao, id_despesa=None, origem="", id_pagamento=None, id_gasto=None, forma_pagamento=None):
        return {
            "data": self.formatar_data(data),
            "descricao": descricao,
            "valor": float(valor or 0),
            "tipo": tipo,
            "situacao": situacao,
            "id_despesa": id_despesa,
            "id_pagamento": id_pagamento,
            "id_gasto": id_gasto,
            "origem": origem,
            "forma_pagamento": forma_pagamento,
        }
    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 14, 24, 10)
        layout.setSpacing(10)

        hoje = date.today()
        inicio_mes = hoje.replace(day=1)

        if hoje.month == 12:
            fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)

        despesas = self.obter_despesas()
        self.despesas = despesas
        todas_despesas = self.obter_todas_despesas()
        receitas = self.obter_receitas()
        gastos = self.obter_gastos()
        pagamentos = self.obter_pagamentos()

        despesas_pendentes_mes = [d for d in despesas if inicio_mes <= d["data"] <= fim_mes]
        despesas_atrasadas = [d for d in despesas if d["data"] < hoje]
        receitas_mes = [r for r in receitas if inicio_mes <= r["data"] <= fim_mes]
        gastos_mes = [g for g in gastos if inicio_mes <= g["data"] <= fim_mes]
        pagamentos_mes = [p for p in pagamentos if inicio_mes <= p["data"] <= fim_mes]
        ids_despesas_com_pagamento = {
            p.get("id_despesa") for p in pagamentos_mes if p.get("id_despesa") is not None
        }
        despesas_pagas_mes_sem_historico = [
            d for d in todas_despesas
            if d["status"] == "paga"
            and inicio_mes <= d["data"] <= fim_mes
            and d.get("id") not in ids_despesas_com_pagamento
        ]

        total_receitas_mes = sum(r["valor"] for r in receitas_mes)
        total_gastos_mes = sum(g["valor"] for g in gastos_mes)
        total_pagamentos_mes = sum(p["valor"] for p in pagamentos_mes)
        total_pagas_sem_historico = sum(d["valor"] for d in despesas_pagas_mes_sem_historico)
        total_pago_mes = total_gastos_mes + total_pagamentos_mes + total_pagas_sem_historico
        total_a_pagar_mes = sum(d["valor"] for d in despesas_pendentes_mes)
        saldo_mes = total_receitas_mes - total_pago_mes

        itens_pagos_contas = [
            self.item_detalhe(
                p["data_pagamento"],
                p["descricao"],
                p["valor"],
                p["tipo"],
                "Paga",
                p.get("id_despesa"),
                "despesa_paga",
                p.get("id"),
                None,
                p.get("forma_pagamento", "Não informado"),
            )
            for p in pagamentos_mes
        ]

        itens_pagos_contas.extend([
            self.item_detalhe(
                d["vencimento"],
                d["descricao"],
                d["valor"],
                d["tipo"],
                "Paga",
                d.get("id"),
                "despesa_paga",  # Corrigido origem para identificar como paga
            )
            for d in despesas_pagas_mes_sem_historico
        ])

        itens_gastos = [
            self.item_detalhe(
                g["data_gasto"],
                g["descricao"],
                g["valor"],
                "Gasto",
                "Pago",
                None,
                "gasto",
                None,
                g.get("id"),
            )
            for g in gastos_mes
        ]

        itens_pendentes = [
            self.item_detalhe(
                d["vencimento"],
                d["descricao"],
                d["valor"],
                d["tipo"],
                self.status_vencimento(d["data"]),
                d.get("id"),
                "despesa_aberta",
            )
            for d in sorted(despesas_pendentes_mes, key=lambda item: item["data"])
        ]

        self.detalhes_pagos = [
            {"titulo": "Contas pagas", "itens": sorted(itens_pagos_contas, key=lambda item: item["data"])},
            {"titulo": "Gastos realizados", "itens": sorted(itens_gastos, key=lambda item: item["data"])},
        ]
        self.detalhes_pendentes = [
            {"titulo": "Contas pendentes do mês", "itens": itens_pendentes},
        ]

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel(f"{self.saudacao_atual()}, {obter_nome_usuario()} 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Resumo financeiro deste mês")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")
        btn_despesa.setToolTip("Nova despesa\n\nUse para contas a pagar, boletos, mensalidades ou compromissos futuros.\nA despesa ficará pendente até ser marcada como paga.")
        btn_despesa.clicked.connect(self.abrir_nova_despesa)

        btn_gasto = QPushButton("🛒  Novo gasto")
        btn_gasto.setObjectName("btnDespesa")
        btn_gasto.setToolTip("Novo gasto\n\nUse para compras pagas na hora, como mercado, combustível, farmácia ou lazer.\nO valor entra como pago imediatamente no mês atual.")
        btn_gasto.clicked.connect(self.abrir_novo_gasto)

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")
        btn_receita.setToolTip("Nova receita\n\nUse para registrar dinheiro que entrou, como salário, venda, comissão ou outro recebimento.")
        btn_receita.clicked.connect(self.abrir_nova_receita)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_gasto)
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        resumo = QHBoxLayout()
        resumo.setSpacing(12)

        if saldo_mes < 0:
            resumo.addWidget(self.criar_card_resumo("cardSaldoNegativo", "💸", "Saldo do mês", self.formatar_moeda(saldo_mes), tooltip="Saldo do mês\n\nReceitas do mês menos tudo que foi efetivamente pago no mês.\nInclui gastos registrados e contas marcadas como pagas."))
        else:
            resumo.addWidget(self.criar_card_resumo("cardSaldo", "💰", "Saldo do mês", self.formatar_moeda(saldo_mes), tooltip="Saldo do mês\n\nReceitas do mês menos tudo que foi efetivamente pago no mês.\nInclui gastos registrados e contas marcadas como pagas."))
        resumo.addWidget(self.criar_card_resumo("cardReceita", "📈", "Receitas do mês", self.formatar_moeda(total_receitas_mes), f"{len(receitas_mes)} entradas", tooltip="Receitas do mês\n\nTotal de entradas cadastradas dentro do mês atual."))
        resumo.addWidget(self.criar_card_resumo(
            "cardDespesa",
            "✅",
            "Pago no mês",
            self.formatar_moeda(total_pago_mes),
            f"{len(itens_pagos_contas)} contas + {len(gastos_mes)} gastos",
            self.abrir_detalhes_pagos,
            "Pago no mês\n\nMostra tudo que já saiu do seu dinheiro neste mês.\nInclui contas marcadas como pagas e gastos registrados.\nClique para ver os detalhes.",
        ))
        resumo.addWidget(self.criar_card_resumo(
            "cardAtrasada",
            "📌",
            "A pagar",
            self.formatar_moeda(total_a_pagar_mes),
            f"{len(despesas_pendentes_mes)} pendentes",
            self.abrir_detalhes_pendentes,
            "A pagar\n\nSoma das contas, despesas e parcelas que ainda estão pendentes no mês atual.\nClique para ver os detalhes.",
        ))

        layout.addLayout(resumo)

        busca_layout = QHBoxLayout()
        busca_layout.setSpacing(10)

        self.caixa_busca = QLineEdit()
        self.caixa_busca.setObjectName("campoBusca")
        self.caixa_busca.setPlaceholderText("Pesquisar conta, gasto ou receita...")
        self.caixa_busca.setToolTip("Busca rápida\n\nDigite parte do nome, valor, tipo ou observação para localizar receitas, gastos, despesas e pagamentos.")
        self.caixa_busca.setClearButtonEnabled(True)
        self.caixa_busca.textChanged.connect(self.buscar_rapido)

        busca_layout.addWidget(self.caixa_busca, 1)
        layout.addLayout(busca_layout)

        self.painel_home = QFrame()
        self.painel_home.setObjectName("card")

        self.painel_home_layout = QVBoxLayout(self.painel_home)
        self.painel_home_layout.setContentsMargins(16, 10, 16, 10)
        self.painel_home_layout.setSpacing(6)

        self.mostrar_proximos_vencimentos()

        layout.addWidget(self.painel_home, 1)

    def limpar_painel_home(self):
        while self.painel_home_layout.count():
            item = self.painel_home_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.limpar_layout(item.layout())

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.limpar_layout(item.layout())

    def criar_botao_voltar(self):
        botao = QPushButton("↩  Próximos vencimentos")
        botao.setObjectName("btnReceita")
        botao.setFixedHeight(34)
        botao.clicked.connect(self.mostrar_proximos_vencimentos)
        return botao

    def criar_card_item_detalhe(self, item, cor="#ef4444", compacto=False):
        card = QFrame()
        card.setObjectName("card")
        
        if compacto:
            card.setMinimumHeight(64)
            card.setMaximumHeight(70)
        else:
            card.setMinimumHeight(72)
            card.setMaximumHeight(78)
            
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(f"QFrame#card {{ background-color: #111827; border: 1px solid #1f2937; border-left: 4px solid {cor}; border-radius: 8px; }}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(4)

        topo = QHBoxLayout()
        descricao = QLabel(item.get("descricao", ""))
        descricao.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")

        valor = QLabel(self.formatar_moeda(item.get("valor", 0)))
        valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        valor.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")

        topo.addWidget(descricao, 1)
        topo.addWidget(valor)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(6)

        data = QLabel(f"📅 {item.get('data', '')}")
        tipo = QLabel(f"📄 {item.get('tipo', '')}")
        situacao = QLabel(item.get("situacao", ""))
        situacao.setAlignment(Qt.AlignCenter)

        texto_situacao = item.get("situacao", "")
        if texto_situacao in ["Atrasada"]:
            cor_status = "#ef4444"
        elif texto_situacao in ["Paga", "Pago"]:
            cor_status = "#22c55e"
        elif texto_situacao in ["Hoje", "Amanhã"]:
            cor_status = "#f59e0b"
        else:
            cor_status = "#2563eb"

        for label in (data, tipo):
            label.setStyleSheet("font-size: 11px; color: #cbd5e1;")

        situacao.setMinimumWidth(72)
        situacao.setFixedHeight(20)
        situacao.setStyleSheet(f"QLabel {{ background-color: {cor_status}; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 10px; }}")

        detalhes.addWidget(data)
        detalhes.addSpacing(4)
        detalhes.addWidget(tipo)
        detalhes.addStretch()
        detalhes.addWidget(situacao)

        id_despesa = item.get("id_despesa")
        origem = item.get("origem")

        if origem == "despesa_aberta" and id_despesa:
            btn_pagar = QPushButton("✓  Pagar")
            btn_pagar.setMinimumWidth(76)
            btn_pagar.setFixedWidth(76)
            btn_pagar.setFixedHeight(20)
            btn_pagar.setCursor(Qt.PointingHandCursor)
            btn_pagar.setToolTip("Marcar como pago\n\nRegistra esta conta como paga e ela passa a entrar no total Pago no mês.")
            btn_pagar.setStyleSheet("QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #3b82f6; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #3b82f6; }")
            btn_pagar.clicked.connect(lambda _, id=id_despesa: self.marcar_despesa_home(id))

            btn_excluir = QPushButton("🗑")
            btn_excluir.setFixedWidth(34)
            btn_excluir.setFixedHeight(20)
            btn_excluir.setCursor(Qt.PointingHandCursor)
            btn_excluir.setToolTip("Excluir despesa")
            btn_excluir.setStyleSheet("QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #ef4444; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #ef4444; color: white; }")
            btn_excluir.clicked.connect(lambda _, item=item: self.excluir_item_pago_home(item))

            detalhes.addSpacing(4)
            detalhes.addWidget(btn_pagar)
            detalhes.addWidget(btn_excluir)

        elif origem == "despesa_paga" and id_despesa:
            btn_desfazer = QPushButton("↩")
            btn_desfazer.setFixedWidth(34)
            btn_desfazer.setFixedHeight(20)
            btn_desfazer.setCursor(Qt.PointingHandCursor)
            btn_desfazer.setToolTip("Desfazer pagamento")
            btn_desfazer.setStyleSheet("QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #3b82f6; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #3b82f6; color: white; }")
            btn_desfazer.clicked.connect(lambda _, item=item: self.desfazer_pagamento_home(item))

            detalhes.addSpacing(4)
            detalhes.addWidget(btn_desfazer)

            # Pagamentos de contas fixas e parcelamentos compartilham o mesmo
            # cadastro com a próxima cobrança. Eles só podem ser desfeitos aqui;
            # a exclusão do cadastro continua nas telas específicas.
            if not item.get("id_pagamento"):
                btn_excluir = QPushButton("🗑")
                btn_excluir.setFixedWidth(34)
                btn_excluir.setFixedHeight(20)
                btn_excluir.setCursor(Qt.PointingHandCursor)
                btn_excluir.setToolTip("Excluir despesa")
                btn_excluir.setStyleSheet("QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #ef4444; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #ef4444; color: white; }")
                btn_excluir.clicked.connect(lambda _, item=item: self.excluir_item_pago_home(item))
                detalhes.addWidget(btn_excluir)

        elif origem == "gasto" and item.get("id_gasto"):
            btn_excluir = QPushButton("🗑")
            btn_excluir.setFixedWidth(34)
            btn_excluir.setFixedHeight(20)
            btn_excluir.setCursor(Qt.PointingHandCursor)
            btn_excluir.setToolTip("Excluir gasto")
            btn_excluir.setStyleSheet("QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #ef4444; border-radius: 4px; font-size: 10px; font-weight: bold; } QPushButton:hover { background-color: #ef4444; color: white; }")
            btn_excluir.clicked.connect(lambda _, item=item: self.excluir_item_pago_home(item))

            detalhes.addSpacing(4)
            detalhes.addWidget(btn_excluir)

        layout.addLayout(topo)
        layout.addLayout(detalhes)
        return card

    def criar_resumo_detalhe(self, titulo, valor, info, cor):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(60)
        card.setMaximumHeight(66)
        card.setStyleSheet(f"QFrame#card {{ background-color: #181d29; border: 1px solid #263244; border-left: 3px solid {cor}; border-radius: 8px; }}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(1)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 11px; color: #9aa2b8;")

        lbl_valor = QLabel(self.formatar_moeda(valor))
        lbl_valor.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")

        lbl_info = QLabel(info)
        lbl_info.setStyleSheet("font-size: 11px; color: #cbd5e1;")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addWidget(lbl_info)
        return card

    def mostrar_detalhes_inline(self, titulo, subtitulo, secoes, cor, mostrar_voltar=True, compacto=False, ocultar_resumo=False):
        self.limpar_painel_home()
        cabecalho = QHBoxLayout()

        textos = QVBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")

        lbl_subtitulo = QLabel(subtitulo)
        lbl_subtitulo.setStyleSheet("font-size: 12px; color: #9aa2b8;")

        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_subtitulo)

        cabecalho.addLayout(textos)
        cabecalho.addStretch()

        if mostrar_voltar:
            cabecalho.addWidget(self.criar_botao_voltar())

        self.painel_home_layout.addLayout(cabecalho)

        if not ocultar_resumo:
            resumo = QHBoxLayout()
            resumo.setSpacing(8)
            for secao in secoes:
                itens = secao.get("itens", [])
                total = sum(float(item.get("valor", 0) or 0) for item in itens)
                resumo.addWidget(self.criar_resumo_detalhe(secao.get("titulo", ""), total, f"{len(itens)} item(ns)", cor))
            self.painel_home_layout.addLayout(resumo)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea > QWidget > QWidget { background: transparent; } QScrollBar:vertical { background: #111827; width: 8px; border-radius: 4px; } QScrollBar::handle:vertical { background: #475569; border-radius: 4px; } QScrollBar::handle:vertical:hover { background: #3b82f6; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }")

        conteudo = QWidget()
        grid = QGridLayout(conteudo)
        grid.setContentsMargins(0, 4, 8, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)

        linha = 0
        coluna = 0
        houve_item = False

        for secao in secoes:
            itens = secao.get("itens", [])
            if not itens:
                continue

            lbl_secao = QLabel(secao.get("titulo", ""))
            lbl_secao.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff; margin-top: 4px;")
            grid.addWidget(lbl_secao, linha, 0, 1, 2)
            linha += 1
            coluna = 0

            for item in itens:
                grid.addWidget(self.criar_card_item_detalhe(item, cor, compacto), linha, coluna)
                houve_item = True
                coluna += 1
                if coluna >= 2:
                    coluna = 0
                    linha += 1

            if coluna != 0:
                linha += 1
                coluna = 0

        if not houve_item:
            vazio = QLabel("Nenhum item encontrado para este mês.")
            vazio.setAlignment(Qt.AlignCenter)
            vazio.setStyleSheet("font-size: 13px; color: #9aa2b8; padding: 20px;")
            grid.addWidget(vazio, 0, 0, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(linha + 1, 1)

        area.setWidget(conteudo)
        self.painel_home_layout.addWidget(area, 1)

    def mostrar_proximos_vencimentos(self):
        self.limpar_painel_home()
        cabecalho_lista = QHBoxLayout()
        cabecalho_lista.setContentsMargins(0, 0, 0, 0)
        cabecalho_lista.setSpacing(6)
        titulo_lista = QLabel("📅 Próximos vencimentos")
        titulo_lista.setToolTip("Próximos vencimentos\n\nLista de contas, despesas e parcelas em aberto, ordenadas pela data de vencimento.")
        titulo_lista.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        btn_proximo_mes = QPushButton("Selecionar próximo mês")
        btn_proximo_mes.setFixedHeight(27)
        btn_proximo_mes.setCursor(Qt.PointingHandCursor)
        btn_proximo_mes.setToolTip("Seleciona automaticamente as contas com vencimento no próximo mês.")
        btn_proximo_mes.setStyleSheet("""
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #3b82f6; border-radius: 7px; padding: 0 14px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        cabecalho_lista.addWidget(titulo_lista)
        cabecalho_lista.addStretch()
        cabecalho_lista.addWidget(btn_proximo_mes)
        self.painel_home_layout.addLayout(cabecalho_lista)

        tabela = TabelaFinanceira(["Data", "Descrição", "Valor", "Situação", "Parcela"])
        tabela.setSelectionMode(QTableWidget.ExtendedSelection)
        tabela.horizontalHeader().setFixedHeight(29)
        self.ajustar_tabela(tabela)
        tabela.cellDoubleClicked.connect(lambda l, c, t=tabela: self.editar_despesa_tabela(t, l))

        proximas = sorted(self.despesas, key=lambda d: d["data"])
        despesas_por_id = {despesa["id"]: despesa for despesa in proximas}
        for despesa in proximas:
            parcela = "-"
            if despesa["tipo"] == "Parcelamento" and despesa["parcela_atual"] and despesa["total_parcelas"]:
                parcela = f"{despesa['parcela_atual']}/{despesa['total_parcelas']}"
            elif despesa["tipo"] == "Conta fixa":
                parcela = "FIXA"

            tabela.adicionar_linha([
                self.formatar_data(despesa["vencimento"]),
                despesa["descricao"],
                self.formatar_moeda(despesa["valor"]),
                self.status_vencimento(despesa["data"]),
                parcela
            ], despesa["id"])
            tabela.setRowHeight(tabela.rowCount() - 1, 28)
            self.aplicar_destaque_data_mes_atual(tabela, tabela.rowCount() - 1, despesa["data"])
        self.painel_home_layout.addWidget(tabela, 1)

        rodape_selecao = QFrame()
        rodape_selecao.setFixedHeight(48)
        rodape_selecao.setStyleSheet("QFrame { background-color: #111c2e; border: 1px solid #26364e; border-radius: 9px; }")
        layout_rodape = QHBoxLayout(rodape_selecao)
        layout_rodape.setContentsMargins(12, 5, 10, 5)
        layout_rodape.setSpacing(10)

        dica = QLabel("Selecione as contas para calcular o total")
        dica.setStyleSheet("color: #9aa2b8; font-size: 11px; border: 0;")
        resumo_selecao = QLabel("0 contas selecionadas  •  Total: R$ 0,00")
        resumo_selecao.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold; border: 0;")
        btn_limpar = QPushButton("Limpar seleção")
        btn_limpar.setFixedHeight(25)
        btn_limpar.setCursor(Qt.PointingHandCursor)
        btn_limpar.setStyleSheet("""
            QPushButton { background-color: #1f2937; color: #dbeafe; border: 1px solid #475569; border-radius: 6px; padding: 0 11px; font-size: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #334155; }
        """)

        layout_rodape.addWidget(dica)
        layout_rodape.addStretch()
        layout_rodape.addWidget(resumo_selecao)
        layout_rodape.addWidget(btn_limpar)
        self.painel_home_layout.addWidget(rodape_selecao)

        def atualizar_total_selecionado():
            ids = []
            for indice in tabela.selectionModel().selectedRows(0):
                item = tabela.item(indice.row(), 0)
                if item is not None:
                    ids.append(item.data(Qt.UserRole))
            selecionadas = [despesas_por_id[id_] for id_ in ids if id_ in despesas_por_id]
            total = sum(float(item.get("valor", 0) or 0) for item in selecionadas)
            quantidade = len(selecionadas)
            palavra = "conta selecionada" if quantidade == 1 else "contas selecionadas"
            resumo_selecao.setText(
                f"{quantidade} {palavra}  •  Total: {self.formatar_moeda(total)}"
            )

        def selecionar_proximo_mes():
            hoje = date.today()
            if hoje.month == 12:
                ano, mes = hoje.year + 1, 1
            else:
                ano, mes = hoje.year, hoje.month + 1
            tabela.clearSelection()
            selecao = tabela.selectionModel()
            for linha, despesa in enumerate(proximas):
                data_vencimento = despesa.get("data")
                if data_vencimento and data_vencimento.year == ano and data_vencimento.month == mes:
                    indice = tabela.model().index(linha, 0)
                    selecao.select(indice, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            atualizar_total_selecionado()

        tabela.itemSelectionChanged.connect(atualizar_total_selecionado)
        btn_limpar.clicked.connect(tabela.clearSelection)
        btn_proximo_mes.clicked.connect(selecionar_proximo_mes)

    def buscar_rapido(self, texto):
        termo = texto.strip().lower()
        if not termo:
            self.mostrar_proximos_vencimentos()
            return

        resultados = []
        for despesa in self.obter_todas_despesas():
            campos = [despesa.get("descricao", ""), despesa.get("categoria", ""), despesa.get("tipo", ""), despesa.get("status", ""), self.formatar_moeda(despesa.get("valor", 0))]
            if any(termo in str(campo).lower() for campo in campos):
                situacao = "Paga" if despesa.get("status") == "paga" else self.status_vencimento(despesa.get("data"))
                origem = "despesa_paga" if despesa.get("status") == "paga" else "despesa_aberta"
                
                # CORREÇÃO AQUI: Passando o despesa.get("id") no campo correto
                resultados.append(self.item_detalhe(
                    despesa.get("vencimento"), 
                    despesa.get("descricao"), 
                    despesa.get("valor"), 
                    despesa.get("tipo"), 
                    situacao, 
                    despesa.get("id"), # Antes estava None aqui!
                    origem
                ))

        for receita in self.obter_receitas():
            campos = [receita.get("descricao", ""), receita.get("categoria", ""), receita.get("observacao", ""), self.formatar_moeda(receita.get("valor", 0))]
            if any(termo in str(campo).lower() for campo in campos):
                resultados.append(self.item_detalhe(receita.get("data_recebimento"), receita.get("descricao"), receita.get("valor"), "Receita", "Entrada", None, "receita"))

        for gasto in self.obter_gastos():
            campos = [gasto.get("descricao", ""), gasto.get("categoria", ""), gasto.get("observacao", ""), self.formatar_moeda(gasto.get("valor", 0))]
            if any(termo in str(campo).lower() for campo in campos):
                resultados.append(self.item_detalhe(gasto.get("data_gasto"), gasto.get("descricao"), gasto.get("valor"), "Gasto", "Pago", None, "gasto", None, gasto.get("id")))

        secoes = [{"titulo": f"Resultados para '{texto}'", "itens": resultados}]
        self.mostrar_detalhes_inline("🔎 Busca rápida", f"{len(resultados)} resultado(s).", secoes, "#3b82f6", mostrar_voltar=False)

    def marcar_despesa_home(self, id_despesa):
        despesa = buscar_despesa_por_id(id_despesa)
        if not despesa:
            return

        status_atual = str(despesa[-1]).lower()
        is_paga = status_atual in ("paga", "pago")

        if is_paga:
            titulo_janela = "Reverter Pagamento"
            texto_principal = "Esta conta já está marcada como PAGA."
            texto_informativo = "Deseja REVERTER o pagamento para colocá-la em aberto novamente?"
            texto_botao_confirmar = "Sim, reverter"
            cor_borda = "#ef4444"
        else:
            if not abrir_pagamento(id_despesa, self):
                return
            if self.ao_salvar_despesa:
                self.ao_salvar_despesa()
            else:
                self.montar_tela()
            return

        caixa = QMessageBox(self)
        caixa.setWindowTitle(titulo_janela)
        caixa.setText(f"<b style='font-size: 15px; color: #ffffff;'>{texto_principal}</b>")
        caixa.setInformativeText(texto_informativo)
        caixa.setIcon(QMessageBox.Question)

        btn_sim = caixa.addButton(texto_botao_confirmar, QMessageBox.YesRole)
        btn_nao = caixa.addButton("Cancelar", QMessageBox.NoRole)
        
        caixa.setStyleSheet(f"""
            QMessageBox {{ background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid {cor_borda}; border-radius: 10px; }}
            QLabel {{ color: #9aa2b8; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }}
            QPushButton {{ background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 85px; }}
            QPushButton:hover {{ background-color: {cor_borda}; border: 1px solid {cor_borda}; }}
        """)
        
        caixa.exec()
        if caixa.clickedButton() == btn_nao:
            return

        if is_paga:
            sucesso, mensagem = reabrir_despesa(id_despesa)
            if not sucesso:
                QMessageBox.warning(self, "Pagamento não alterado", mensagem)
                return
        if self.ao_salvar_despesa:
            self.ao_salvar_despesa()
        else:
            self.montar_tela()


    def confirmar_acao_home(self, titulo, texto, botao, cor):
        caixa = QMessageBox(self)
        caixa.setWindowTitle(titulo)
        caixa.setText(f"<b style='font-size: 15px; color: #ffffff;'>{texto}</b>")
        caixa.setIcon(QMessageBox.Question)

        btn_sim = caixa.addButton(botao, QMessageBox.YesRole)
        btn_nao = caixa.addButton("Cancelar", QMessageBox.NoRole)

        caixa.setStyleSheet(f"""
            QMessageBox {{ background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid {cor}; border-radius: 10px; }}
            QLabel {{ color: #9aa2b8; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }}
            QPushButton {{ background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 85px; }}
            QPushButton:hover {{ background-color: {cor}; border: 1px solid {cor}; }}
        """)

        caixa.exec()
        return caixa.clickedButton() == btn_sim

    def confirmar_exclusao_despesa_paga_home(self):
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Excluir conta paga")
        caixa.setText("<b style='font-size: 15px; color: #ffffff;'>Esta conta já foi paga.</b>")
        caixa.setInformativeText(
            "Escolha se deseja manter o valor no histórico ou estornar o pagamento mais recente."
        )
        caixa.setIcon(QMessageBox.Warning)

        btn_manter = caixa.addButton("Manter no histórico", QMessageBox.YesRole)
        btn_estornar = caixa.addButton("Estornar pagamento", QMessageBox.DestructiveRole)
        btn_cancelar = caixa.addButton("Cancelar", QMessageBox.NoRole)

        caixa.setStyleSheet("""
            QMessageBox { background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid #ef4444; border-radius: 10px; }
            QLabel { color: #d7dcf0; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 170px; }
            QPushButton:hover { background-color: #ef4444; border: 1px solid #ef4444; }
        """)

        caixa.exec()
        if caixa.clickedButton() == btn_manter:
            return "manter_saldo"
        if caixa.clickedButton() == btn_estornar:
            return "estornar"
        if caixa.clickedButton() == btn_cancelar:
            return "cancelar"
        return "cancelar"

    def desfazer_pagamento_home(self, item):
        id_pagamento = item.get("id_pagamento")
        id_despesa = item.get("id_despesa")
        if not self.confirmar_acao_home("Desfazer pagamento", "Deseja desfazer este pagamento?", "Desfazer", "#3b82f6"):
            return
        if id_pagamento:
            sucesso, mensagem = desfazer_pagamento(id_pagamento)
        elif id_despesa:
            sucesso, mensagem = reabrir_despesa(id_despesa)
        else:
            return

        if not sucesso:
            QMessageBox.warning(self, "Pagamento não alterado", mensagem)
            return

        if self.ao_salvar_despesa:
            self.ao_salvar_despesa()
        else:
            self.montar_tela()

    def excluir_item_pago_home(self, item):
        origem = item.get("origem")

        if origem == "gasto" and item.get("id_gasto"):
            if not self.confirmar_acao_home("Excluir gasto", "Deseja excluir este gasto definitivamente?", "Excluir", "#ef4444"):
                return
            excluir_gasto(item.get("id_gasto"))
        elif origem == "despesa_aberta" and item.get("id_despesa"):
            if not self.confirmar_acao_home("Excluir despesa", "Deseja excluir esta despesa definitivamente?", "Excluir", "#ef4444"):
                return
            excluir_despesa(item.get("id_despesa"))
        elif item.get("id_despesa"):
            escolha = self.confirmar_exclusao_despesa_paga_home()
            if escolha == "cancelar":
                return
            if escolha == "manter_saldo":
                excluir_despesa(item.get("id_despesa"))
            elif escolha == "estornar":
                excluir_despesa_com_historico(item.get("id_despesa"))

        if self.ao_salvar_despesa:
            self.ao_salvar_despesa()
        else:
            self.montar_tela()

    def abrir_detalhes_pagos(self):
        self.mostrar_detalhes_inline("✅ Pago no mês", "Contas e gastos efetuados.", self.detalhes_pagos, "#ef4444")

    def abrir_detalhes_pendentes(self):
        self.mostrar_detalhes_inline("📌 A pagar", "Contas pendentes.", self.detalhes_pendentes, "#ef4444", compacto=True, ocultar_resumo=True)

    def editar_despesa_tabela(self, tabela, linha):
        item = tabela.item(linha, 0)
        if item is None: return
        id_despesa = item.data(Qt.UserRole)
        if not id_despesa: return
        despesa = buscar_despesa_por_id(id_despesa)
        if not despesa: return
        janela = NovaDespesa(despesa)
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_nova_despesa(self):
        janela = NovaDespesa()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_novo_gasto(self):
        janela = NovoGasto()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

    def abrir_nova_receita(self):
        janela = NovaReceita()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()

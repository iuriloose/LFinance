from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import QDate, Qt

from banco.banco import (
    listar_despesas,
    pagar_despesa,
    excluir_despesa,
    reabrir_despesa,
    listar_pagamentos,
)
from componentes.tabela_registros import TabelaRegistros, cor_status, criar_botao_acao
from telas.pagamento import abrir_pagamento
from telas.nova_despesa import NovaDespesa


class ConfirmacaoExclusaoParcelamento(QDialog):
    def __init__(self, descricao):
        super().__init__()

        self.setWindowTitle("Excluir parcelamento")
        self.setFixedSize(430, 230)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #0f1117;
            }

            QLabel {
                color: #f8fafc;
                font-family: Segoe UI;
                background-color: transparent;
            }

            QLabel#tituloConfirmacao {
                font-size: 24px;
                font-weight: 800;
            }

            QLabel#textoConfirmacao {
                font-size: 12px;
                color: #cbd5e1;
            }

            QLabel#itemConfirmacao {
                font-size: 15px;
                color: #ffffff;
                background-color: #151c2b;
                border: 1px solid #26364e;
                border-radius: 12px;
                padding: 12px;
            }

            QPushButton {
                min-height: 42px;
                border-radius: 11px;
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
                padding: 0 18px;
            }

            QPushButton#btnCancelarConfirmacao {
                background-color: #1f2937;
                border: 1px solid #334155;
            }

            QPushButton#btnCancelarConfirmacao:hover {
                background-color: #273449;
                border: 1px solid #64748b;
            }

            QPushButton#btnExcluirConfirmacao {
                background-color: #dc2626;
                border: 1px solid #ef4444;
            }

            QPushButton#btnExcluirConfirmacao:hover {
                background-color: #ef4444;
                border: 1px solid #f87171;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(14)

        titulo = QLabel("Excluir parcelamento")
        titulo.setObjectName("tituloConfirmacao")

        texto = QLabel("Tem certeza que deseja excluir este parcelamento?")
        texto.setObjectName("textoConfirmacao")

        item = QLabel(descricao)
        item.setObjectName("itemConfirmacao")

        botoes = QHBoxLayout()
        botoes.setSpacing(12)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelarConfirmacao")
        btn_cancelar.clicked.connect(self.reject)

        btn_excluir = QPushButton("🗑  Excluir")
        btn_excluir.setObjectName("btnExcluirConfirmacao")
        btn_excluir.clicked.connect(self.accept)

        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_excluir)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addWidget(item)
        layout.addStretch()
        layout.addLayout(botoes)


class TelaParcelamentos(QWidget):
    def __init__(self, ao_alterar=None):
        super().__init__()

        self.ao_alterar = ao_alterar

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(36, 30, 36, 24)
        self.layout_principal.setSpacing(16)

        self.aplicar_estilo_local()
        self.montar_tela()

    def aplicar_estilo_local(self):
        self.setStyleSheet("""
            QFrame#cardParcelamentoLista {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #223149;
                border-left: 4px solid #ef4444;
                border-radius: 9px;
            }

            QFrame#cardParcelamentoLista:hover {
                border: 1px solid #ef4444;
                background-color: rgba(24, 34, 52, 0.98);
            }

            QLabel#tituloParcelamentoLista {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#valorParcelamentoLista {
                color: #ffffff;
                font-size: 16px;
                font-weight: 900;
            }

            QLabel#infoParcelamentoLista {
                color: #d7dcf0;
                font-size: 12px;
            }

            QLabel#statusPagoLista {
                color: #22c55e;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#statusAbertoLista {
                color: #22c55e;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#statusAtrasadoLista {
                color: #ef4444;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton#btnNovaParcelamento {
                background-color: rgba(30, 41, 59, 0.78);
                color: white;
                padding: 10px 18px;
                border-radius: 11px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #ef4444;
            }

            QPushButton#btnNovaParcelamento:hover {
                background-color: rgba(239, 68, 68, 0.18);
                border: 1px solid #f87171;
            }

            QPushButton#btnPagarParcelamentoLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #16a34a;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnPagarParcelamentoLista:hover {
                background-color: rgba(22, 163, 74, 0.24);
                border: 1px solid #4ade80;
            }

            QPushButton#btnEditarParcelamentoLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnEditarParcelamentoLista:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnExcluirParcelamentoLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #7f1d1d;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnExcluirParcelamentoLista:hover {
                background-color: rgba(127, 29, 29, 0.34);
                border: 1px solid #ef4444;
            }

            QScrollArea#areaParcelamentos {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaParcelamentos > QWidget > QWidget {
                background-color: transparent;
            }

            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 4px 0px 4px 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #334155;
                border-radius: 5px;
                min-height: 34px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #475569;
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

    def limpar_tela(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa

        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def formatar_data(self, data):
        partes = data.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data

    def formatar_moeda(self, valor):
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def texto_status(self, vencimento, status):
        if status == "paga":
            return "Paga", "statusPagoLista"

        hoje = QDate.currentDate()
        data = QDate.fromString(vencimento, "yyyy-MM-dd")

        if data.isValid() and data < hoje:
            return "Atrasada", "statusAtrasadoLista"

        return "Em aberto", "statusAbertoLista"

    def obter_parcelamentos(self):
        parcelamentos = []
        for despesa in listar_despesas():
            dados = self.separar_despesa(despesa)
            if dados[5] == "Parcelamento":
                parcelamentos.append(despesa)
        return self.ordenar_parcelamentos(parcelamentos)

    def ordenar_parcelamentos(self, parcelamentos):
        hoje = QDate.currentDate()

        def ordem(conta):
            _, _, _, vencimento, _, _, _, _, _, status = self.separar_despesa(conta)
            data = QDate.fromString(vencimento, "yyyy-MM-dd")

            if status == "paga":
                return (2, vencimento)
            if data.isValid() and data < hoje:
                return (0, vencimento)
            return (1, vencimento)

        return sorted(parcelamentos, key=ordem)

    def criar_card_parcelamento(self, parcelamento):
        (
            id_despesa,
            descricao,
            valor,
            vencimento,
            categoria,
            tipo,
            parcela_atual,
            total_parcelas,
            valor_total,
            status,
        ) = self.separar_despesa(parcelamento)

        card = QFrame()
        card.setObjectName("cardParcelamentoLista")
        card.setMinimumHeight(72)
        card.setMaximumHeight(78)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 12, 8)
        card_layout.setSpacing(5)

        topo = QHBoxLayout()
        topo.setSpacing(10)

        titulo = QLabel(descricao)
        titulo.setObjectName("tituloParcelamentoLista")

        valor_label = QLabel(self.formatar_moeda(valor))
        valor_label.setObjectName("valorParcelamentoLista")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        topo.addWidget(titulo, 1)
        topo.addWidget(valor_label)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(8)

        parcela_texto = ""
        if parcela_atual and total_parcelas:
            parcela_texto = f"  •  Parcela {parcela_atual}/{total_parcelas}"

        total_texto = ""
        if valor_total:
            total_texto = f"  •  Total {self.formatar_moeda(valor_total)}"

        info = QLabel(
            f"📅 {self.formatar_data(vencimento)}   "
            f"📂 {categoria}  •  "
            f"📄 Parcelamento{parcela_texto}{total_texto}"
        )
        info.setObjectName("infoParcelamentoLista")
        info.setWordWrap(False)

        status_texto, status_objeto = self.texto_status(vencimento, status)
        status_label = QLabel(f"● {status_texto}")
        status_label.setObjectName(status_objeto)
        status_label.setAlignment(Qt.AlignCenter)

        if status == "paga":
            btn_pago = QPushButton("↩  Reabrir")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.reabrir(id))
        else:
            btn_pago = QPushButton("✓  Pagar")
            btn_pago.clicked.connect(lambda _, id=id_despesa: self.marcar_paga(id))

        btn_pago.setObjectName("btnPagarParcelamentoLista")
        btn_pago.setToolTip("Pagar ou reabrir\n\nMarca a parcela como paga ou desfaz o pagamento.")
        btn_pago.setFixedSize(82, 24)

        btn_editar = QPushButton("✏  Editar")
        btn_editar.setObjectName("btnEditarParcelamentoLista")
        btn_editar.setToolTip("Editar parcelamento\n\nAltera os dados deste parcelamento.")
        btn_editar.setFixedSize(82, 24)
        btn_editar.clicked.connect(lambda _, d=parcelamento: self.editar(d))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnExcluirParcelamentoLista")
        btn_excluir.setToolTip("Excluir parcelamento\n\nRemove este parcelamento do LFinance após confirmação.")
        btn_excluir.setFixedSize(36, 24)
        btn_excluir.clicked.connect(lambda _, id=id_despesa, d=descricao: self.excluir(id, d))

        detalhes.addWidget(info, 1)
        detalhes.addWidget(status_label)
        detalhes.addWidget(btn_pago)
        detalhes.addWidget(btn_editar)
        detalhes.addWidget(btn_excluir)

        card_layout.addLayout(topo)
        card_layout.addLayout(detalhes)

        card.mouseDoubleClickEvent = lambda evento, d=parcelamento: self.editar(d)
        card.setToolTip("Dê dois cliques para editar este parcelamento")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("📄 Parcelamentos")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Compras parceladas cadastradas no LFinance")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nova = QPushButton("+  Novo parcelamento")
        btn_nova.setObjectName("btnNovaParcelamento")
        btn_nova.setToolTip("Novo parcelamento\n\nCadastre uma compra dividida em parcelas para acompanhar vencimentos e parcelas restantes.")
        btn_nova.clicked.connect(self.novo_parcelamento)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_nova)

        self.layout_principal.addLayout(topo)

        parcelamentos = self.obter_parcelamentos()

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        abertas = sum(1 for c in parcelamentos if self.separar_despesa(c)[9] != "paga")
        pagas = sum(1 for c in parcelamentos if self.separar_despesa(c)[9] == "paga")
        resumo = QLabel(f"{len(parcelamentos)} parcelamento(s) cadastrado(s)  •  {abertas} em aberto  •  {pagas} paga(s)")
        resumo.setObjectName("cardInfo")
        painel_layout.addWidget(resumo)

        saldo_restante = 0
        for item in parcelamentos:
            dados = self.separar_despesa(item)
            if dados[9] != "paga":
                restantes = max((dados[7] or 1) - (dados[6] or 1) + 1, 1)
                saldo_restante += float(dados[2] or 0) * restantes
        total_pago = sum(float(p[3] or 0) for p in listar_pagamentos() if p[6] == "Parcelamento")
        totais = QLabel(
            f"Saldo restante: {self.formatar_moeda(saldo_restante)}  •  "
            f"Total pago: {self.formatar_moeda(total_pago)}"
        )
        totais.setObjectName("cardInfo")
        painel_layout.addWidget(totais)

        tabela = TabelaRegistros(
            ["Vencimento", "Descrição", "Categoria", "Parcela", "Situação", "Valor da parcela", "Ação"],
            larguras={0: 90, 2: 100, 3: 80, 4: 85, 5: 115, 6: 205},
            coluna_flexivel=1,
            colunas_ocultar_compacto=(2,),
        )
        if not parcelamentos:
            tabela.mostrar_vazio(
                "Nenhum parcelamento cadastrado. Adicione uma compra parcelada para ela aparecer aqui."
            )
        else:
            for parcelamento in parcelamentos:
                (
                    id_despesa,
                    descricao,
                    valor,
                    vencimento,
                    categoria,
                    _tipo,
                    parcela_atual,
                    total_parcelas,
                    valor_total,
                    status,
                ) = self.separar_despesa(parcelamento)
                status_texto, _ = self.texto_status(vencimento, status)
                parcela_texto = (
                    f"{parcela_atual}/{total_parcelas}"
                    if parcela_atual and total_parcelas else "—"
                )
                linha = tabela.adicionar_linha(
                    [
                        self.formatar_data(vencimento),
                        descricao,
                        categoria or "—",
                        parcela_texto,
                        status_texto,
                        self.formatar_moeda(valor),
                        "",
                    ],
                    dados=parcelamento,
                    colunas_esquerda=(1,),
                    cores={4: cor_status(status_texto)},
                    tooltips={
                        3: (
                            f"Valor total: {self.formatar_moeda(valor_total)}"
                            if valor_total else ""
                        )
                    },
                )
                if status == "paga":
                    btn_pago = criar_botao_acao(
                        "Reabrir",
                        lambda _, id=id_despesa: self.reabrir(id),
                        "#3b82f6",
                        70,
                        "Reabrir esta parcela",
                    )
                else:
                    btn_pago = criar_botao_acao(
                        "Pagar",
                        lambda _, id=id_despesa: self.marcar_paga(id),
                        "#22c55e",
                        66,
                        "Registrar o pagamento desta parcela",
                    )
                btn_editar = criar_botao_acao(
                    "Editar",
                    lambda _, d=parcelamento: self.editar(d),
                    "#3b82f6",
                    64,
                    "Editar este parcelamento",
                )
                btn_excluir = criar_botao_acao(
                    "🗑",
                    lambda _, id=id_despesa, d=descricao: self.excluir(id, d),
                    "#ef4444",
                    34,
                    "Excluir este parcelamento",
                )
                tabela.definir_acoes(linha, [btn_pago, btn_editar, btn_excluir])
            tabela.cellDoubleClicked.connect(
                lambda linha, _coluna: self.editar(tabela.item(linha, 0).data(Qt.UserRole))
            )

        painel_layout.addWidget(tabela, 1)
        self.layout_principal.addWidget(painel, 1)

    def novo_parcelamento(self):
        janela = NovaDespesa()
        janela.tipo.setCurrentText("Parcelamento")

        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def marcar_paga(self, id_despesa):
        if abrir_pagamento(id_despesa, self):
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def reabrir(self, id_despesa):
        reabrir_despesa(id_despesa)
        self.montar_tela()
        if self.ao_alterar:
            self.ao_alterar()

    def editar(self, conta):
        janela = NovaDespesa(conta)

        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def excluir(self, id_despesa, descricao="este parcelamento"):
        janela = ConfirmacaoExclusaoParcelamento(descricao)

        if janela.exec():
            excluir_despesa(id_despesa)
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

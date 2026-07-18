from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import QDate, Qt

from banco.banco import (
    listar_despesas,
    pagar_despesa,
    excluir_despesa,
    excluir_despesa_com_historico,
    buscar_despesa_por_id,
    reabrir_despesa,
    listar_pagamentos,
)
from telas.pagamento import abrir_pagamento

from telas.nova_despesa import NovaDespesa


class ConfirmacaoExclusaoDespesa(QDialog):
    def __init__(self, descricao):
        super().__init__()

        self.setWindowTitle("Excluir despesa")
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

        titulo = QLabel("Excluir despesa")
        titulo.setObjectName("tituloConfirmacao")

        texto = QLabel("Tem certeza que deseja excluir esta despesa?")
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


class TelaDespesas(QWidget):
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
            QFrame#cardDespesaLista {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #223149;
                border-left: 4px solid #ef4444;
                border-radius: 9px;
            }

            QFrame#cardDespesaLista:hover {
                border: 1px solid #ef4444;
                background-color: rgba(24, 34, 52, 0.98);
            }

            QLabel#tituloDespesaLista {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#valorDespesaLista {
                color: #ffffff;
                font-size: 16px;
                font-weight: 900;
            }

            QLabel#infoDespesaLista {
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

            QPushButton#btnPagarDespesaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #16a34a;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnPagarDespesaLista:hover {
                background-color: rgba(22, 163, 74, 0.24);
                border: 1px solid #4ade80;
            }

            QPushButton#btnEditarDespesaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnEditarDespesaLista:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnExcluirDespesaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #7f1d1d;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnExcluirDespesaLista:hover {
                background-color: rgba(127, 29, 29, 0.34);
                border: 1px solid #ef4444;
            }

            QScrollArea#areaDespesas {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaDespesas > QWidget > QWidget {
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

    def ordenar_despesas(self, despesas):
        hoje = QDate.currentDate()

        def ordem(despesa):
            _, _, _, vencimento, _, _, _, _, _, status = self.separar_despesa(despesa)

            if status == "paga":
                return (2, vencimento)

            data = QDate.fromString(vencimento, "yyyy-MM-dd")

            if data.isValid() and data < hoje:
                return (0, vencimento)

            return (1, vencimento)

        return sorted(despesas, key=ordem)

    def criar_card_despesa(self, despesa):
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
        ) = self.separar_despesa(despesa)

        card = QFrame()
        card.setObjectName("cardDespesaLista")
        card.setMinimumHeight(72)
        card.setMaximumHeight(78)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 12, 8)
        card_layout.setSpacing(5)

        topo = QHBoxLayout()
        topo.setSpacing(10)

        titulo = QLabel(descricao)
        titulo.setObjectName("tituloDespesaLista")

        valor_label = QLabel(self.formatar_moeda(valor))
        valor_label.setObjectName("valorDespesaLista")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        topo.addWidget(titulo, 1)
        topo.addWidget(valor_label)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(8)

        parcela_texto = ""
        if tipo == "Parcelamento" and parcela_atual and total_parcelas:
            parcela_texto = f"  •  Parcela {parcela_atual}/{total_parcelas}"

        total_texto = ""
        if tipo == "Parcelamento" and valor_total:
            total_texto = f"  •  Total {self.formatar_moeda(valor_total)}"

        info = QLabel(
            f"📅 {self.formatar_data(vencimento)}   "
            f"📂 {categoria}  •  "
            f"📄 {tipo}{parcela_texto}{total_texto}"
        )
        info.setObjectName("infoDespesaLista")
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

        btn_pago.setObjectName("btnPagarDespesaLista")
        btn_pago.setToolTip("Pagar ou reabrir\n\nMarca a despesa como paga ou desfaz o pagamento, voltando a conta para aberto.")
        btn_pago.setFixedSize(82, 24)

        btn_editar = QPushButton("✏  Editar")
        btn_editar.setObjectName("btnEditarDespesaLista")
        btn_editar.setToolTip("Editar despesa\n\nAltera descrição, valor, vencimento ou outras informações desta despesa.")
        btn_editar.setFixedSize(82, 24)
        btn_editar.clicked.connect(lambda _, d=despesa: self.editar(d))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnExcluirDespesaLista")
        btn_excluir.setToolTip("Excluir despesa\n\nRemove esta despesa do LFinance após confirmação.")
        btn_excluir.setFixedSize(36, 24)
        btn_excluir.clicked.connect(lambda _, id=id_despesa, d=descricao: self.excluir(id, d))

        detalhes.addWidget(info, 1)
        detalhes.addWidget(status_label)
        detalhes.addWidget(btn_pago)
        detalhes.addWidget(btn_editar)
        detalhes.addWidget(btn_excluir)

        card_layout.addLayout(topo)
        card_layout.addLayout(detalhes)

        card.mouseDoubleClickEvent = lambda evento, d=despesa: self.editar(d)
        card.setToolTip("Dê dois cliques para editar esta despesa")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("Despesas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Veja, edite, pague ou exclua suas despesas")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nova = QPushButton("↓  Nova despesa")
        btn_nova.setObjectName("btnDespesa")
        btn_nova.setToolTip("Nova despesa\\n\\nCadastre uma conta a pagar, boleto ou compromisso futuro. Ela ficará pendente até ser marcada como paga.")
        btn_nova.clicked.connect(self.nova_despesa)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_nova)

        self.layout_principal.addLayout(topo)

        despesas = self.ordenar_despesas(listar_despesas())

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        abertas = sum(1 for d in despesas if self.separar_despesa(d)[9] != "paga")
        pagas = sum(1 for d in despesas if self.separar_despesa(d)[9] == "paga")
        resumo = QLabel(f"{len(despesas)} despesa(s) cadastrada(s)  •  {abertas} em aberto  •  {pagas} paga(s)")
        resumo.setObjectName("cardInfo")
        painel_layout.addWidget(resumo)

        total_aberto = sum(float(self.separar_despesa(d)[2] or 0) for d in despesas if self.separar_despesa(d)[9] != "paga")
        total_pago = sum(float(p[3] or 0) for p in listar_pagamentos())
        totais = QLabel(
            f"Em aberto: {self.formatar_moeda(total_aberto)}  •  "
            f"Pago no histórico: {self.formatar_moeda(total_pago)}  •  "
            f"Total: {self.formatar_moeda(total_aberto + total_pago)}"
        )
        totais.setObjectName("cardInfo")
        painel_layout.addWidget(totais)

        area = QScrollArea()
        area.setObjectName("areaDespesas")
        area.setWidgetResizable(True)

        conteudo = QWidget()
        conteudo.setAttribute(Qt.WA_StyledBackground, True)
        conteudo.setStyleSheet("background-color: transparent;")

        lista_layout = QVBoxLayout(conteudo)
        lista_layout.setContentsMargins(0, 0, 8, 0)
        lista_layout.setSpacing(12)

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada.")
            vazio.setObjectName("cardInfo")
            lista_layout.addWidget(vazio)
        else:
            for despesa in despesas:
                lista_layout.addWidget(self.criar_card_despesa(despesa))

        lista_layout.addStretch()
        area.setWidget(conteudo)

        painel_layout.addWidget(area, 1)
        self.layout_principal.addWidget(painel, 1)

    def nova_despesa(self):
        janela = NovaDespesa()
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

    def editar(self, despesa):
        janela = NovaDespesa(despesa)

        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def confirmar_exclusao_despesa_paga(self):
        from PySide6.QtWidgets import QMessageBox

        caixa = QMessageBox(self)
        caixa.setWindowTitle("Excluir despesa paga")
        caixa.setText("Esta despesa já foi paga.")
        caixa.setInformativeText(
            "Ela já foi considerada no saldo do sistema.\n\n"
            "Escolha se deseja manter o saldo atual ou estornar este pagamento."
        )
        caixa.setIcon(QMessageBox.Warning)

        btn_manter = caixa.addButton("Manter saldo", QMessageBox.YesRole)
        btn_estornar = caixa.addButton("Estornar pagamento", QMessageBox.DestructiveRole)
        btn_cancelar = caixa.addButton("Cancelar", QMessageBox.NoRole)

        caixa.setStyleSheet("""
            QMessageBox { background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid #ef4444; border-radius: 10px; }
            QLabel { color: #d7dcf0; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 170px; }
            QPushButton:hover { background-color: #ef4444; border: 1px solid #ef4444; }
        """)

        caixa.setMinimumSize(760, 280)
        btn_manter.setMinimumWidth(180)
        btn_estornar.setMinimumWidth(210)
        btn_cancelar.setMinimumWidth(180)

        caixa.exec()
        clicado = caixa.clickedButton()
        if clicado == btn_manter:
            return "manter_saldo"
        if clicado == btn_estornar:
            return "estornar"
        return "cancelar"

    def excluir(self, id_despesa, descricao="esta despesa"):
        despesa = buscar_despesa_por_id(id_despesa)
        status = str(despesa[-1]).lower() if despesa else ""

        if status == "paga":
            escolha = self.confirmar_exclusao_despesa_paga()
            if escolha == "cancelar":
                return
            if escolha == "manter_saldo":
                excluir_despesa(id_despesa)
            else:
                excluir_despesa_com_historico(id_despesa)
        else:
            janela = ConfirmacaoExclusaoDespesa(descricao)
            if not janela.exec():
                return
            excluir_despesa(id_despesa)

        self.montar_tela()
        if self.ao_alterar:
            self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

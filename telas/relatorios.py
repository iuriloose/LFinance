from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt

from banco.banco import (
    listar_despesas,
    listar_receitas,
    listar_gastos,
    listar_pagamentos,
)


class TelaRelatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.mes_referencia = date.today().replace(day=1)
        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: Segoe UI;
            }

            QLabel#tituloRelatorio {
                color: #ffffff;
                font-size: 31px;
                font-weight: 800;
            }

            QLabel#subtituloRelatorio {
                color: #a8b3c7;
                font-size: 14px;
                padding-right: 8px;
            }

            QLabel#periodoRelatorio {
                color: #ffffff;
                font-size: 15px;
                font-weight: 800;
                padding: 9px 14px;
                border-radius: 11px;
                background-color: rgba(30, 41, 59, 0.72);
                border: 1px solid #26364e;
            }

            QLabel#secaoRelatorio {
                color: #ffffff;
                font-size: 19px;
                font-weight: 800;
            }

            QLabel#textoSuave {
                color: #a8b3c7;
                font-size: 13px;
            }

            QLabel#textoNormal {
                color: #d7dcf0;
                font-size: 13px;
            }

            QLabel#cardTituloRelatorio {
                color: #a8b3c7;
                font-size: 13px;
            }

            QLabel#cardValorRelatorio {
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
            }

            QLabel#cardInfoRelatorio {
                color: #cbd5e1;
                font-size: 12px;
            }

            QLabel#valorVerde {
                color: #22c55e;
                font-size: 17px;
                font-weight: 800;
            }

            QLabel#valorAzul {
                color: #60a5fa;
                font-size: 17px;
                font-weight: 800;
            }

            QLabel#valorLaranja {
                color: #f59e0b;
                font-size: 17px;
                font-weight: 800;
            }

            QLabel#valorVermelho {
                color: #ef4444;
                font-size: 17px;
                font-weight: 800;
            }

            QLabel#itemTitulo {
                color: #ffffff;
                font-size: 14px;
                font-weight: 800;
            }

            QLabel#itemInfo {
                color: #cbd5e1;
                font-size: 12px;
            }

            QLabel#itemValor {
                color: #ffffff;
                font-size: 15px;
                font-weight: 800;
            }

            QFrame#cardBase {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 33, 50, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #26364e;
                border-radius: 16px;
            }

            QFrame#cardReceitaRelatorio {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(16, 65, 40, 0.96),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #22c55e;
                border-radius: 16px;
            }

            QFrame#cardPagoRelatorio {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(74, 48, 11, 0.96),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #f59e0b;
                border-radius: 16px;
            }

            QFrame#cardPendenteRelatorio {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(79, 24, 24, 0.96),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #ef4444;
                border-radius: 16px;
            }

            QFrame#cardSaldoRelatorio {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 46, 83, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #1e88ff;
                border-radius: 16px;
            }

            QFrame#linhaResumo {
                background-color: rgba(15, 23, 42, 0.54);
                border: 1px solid #26364e;
                border-radius: 12px;
            }

            QFrame#itemLista {
                background-color: rgba(15, 23, 42, 0.54);
                border: 1px solid #25364f;
                border-radius: 12px;
            }

            QFrame#barraFundo {
                background-color: #0f172a;
                border: 1px solid #26364e;
                border-radius: 8px;
            }

            QFrame#barraVerde {
                background-color: #22c55e;
                border-radius: 7px;
            }

            QFrame#barraLaranja {
                background-color: #f59e0b;
                border-radius: 7px;
            }

            QFrame#barraVermelha {
                background-color: #ef4444;
                border-radius: 7px;
            }

            QPushButton#btnAtualizarRelatorio, QPushButton#btnMesRelatorio, QPushButton#btnMesAtualRelatorio {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                padding: 10px 18px;
                border-radius: 11px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2563eb;
            }

            QPushButton#btnAtualizarRelatorio:hover, QPushButton#btnMesRelatorio:hover, QPushButton#btnMesAtualRelatorio:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnMesRelatorio {
                padding: 9px 12px;
                border: 1px solid #334155;
                min-width: 54px;
            }

            QPushButton#btnMesAtualRelatorio {
                padding: 9px 12px;
                border: 1px solid #334155;
                min-width: 154px;
            }

            QPushButton#btnAtualizarRelatorio {
                min-width: 142px;
            }

            QScrollArea#areaRelatorios {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaRelatorios > QWidget > QWidget {
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
        """)

    def limpar_tela(self):
        layout = self.layout()
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
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

    def formatar_moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m")
        except Exception:
            return data or "-"

    def nome_mes(self, data):
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return f"{meses[data.month - 1]} de {data.year}"

    def converter_data(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d").date()
        except Exception:
            return None

    def texto_status(self, data):
        hoje = date.today()
        if data is None:
            return "Sem data"
        if data < hoje:
            return "Atrasada"
        if data == hoje:
            return "Hoje"
        if data == hoje + timedelta(days=1):
            return "Amanhã"
        return f"Em {(data - hoje).days} dias"

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa

        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def dados_mes(self):
        hoje = date.today()
        inicio_mes = self.mes_referencia.replace(day=1)

        if inicio_mes.month == 12:
            fim_mes = inicio_mes.replace(year=inicio_mes.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = inicio_mes.replace(month=inicio_mes.month + 1, day=1) - timedelta(days=1)

        despesas_mes = []
        pendentes_mes = []
        atrasadas = []
        parcelamentos_abertos = []

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
                valor_total,
                status,
            ) = self.separar_despesa(despesa)

            data = self.converter_data(vencimento)
            if data is None:
                continue

            item = {
                "id": id_despesa,
                "descricao": descricao,
                "valor": float(valor or 0),
                "data": data,
                "data_texto": self.formatar_data(vencimento),
                "categoria": categoria,
                "tipo": tipo,
                "status": status,
                "situacao": self.texto_status(data),
                "parcela_atual": parcela_atual,
                "total_parcelas": total_parcelas,
                "valor_total": valor_total,
            }

            if inicio_mes <= data <= fim_mes:
                despesas_mes.append(item)
                if status == "aberta":
                    pendentes_mes.append(item)

            if status == "aberta" and inicio_mes <= data <= fim_mes and data < hoje:
                atrasadas.append(item)

            if (
                status == "aberta"
                and tipo == "Parcelamento"
                and inicio_mes <= data <= fim_mes
            ):
                parcelamentos_abertos.append(item)

        receitas_mes = []
        for receita in listar_receitas():
            id_receita, descricao, valor, data_recebimento, categoria, observacao = receita
            data = self.converter_data(data_recebimento)
            if data and inicio_mes <= data <= fim_mes:
                receitas_mes.append({
                    "id": id_receita,
                    "descricao": descricao,
                    "valor": float(valor or 0),
                    "data": data,
                    "data_texto": self.formatar_data(data_recebimento),
                    "categoria": categoria,
                    "tipo": "Receita",
                })

        gastos_mes = []
        for gasto in listar_gastos():
            id_gasto, descricao, valor, data_gasto, categoria, observacao = gasto
            data = self.converter_data(data_gasto)
            if data and inicio_mes <= data <= fim_mes:
                gastos_mes.append({
                    "id": id_gasto,
                    "descricao": descricao,
                    "valor": float(valor or 0),
                    "data": data,
                    "data_texto": self.formatar_data(data_gasto),
                    "categoria": categoria,
                    "tipo": "Gasto",
                })

        pagamentos_mes = []
        for pagamento in listar_pagamentos():
            if len(pagamento) >= 10:
                id_pagamento, id_despesa, descricao, valor, data_pagamento, categoria, tipo, parcela_atual, total_parcelas, forma_pagamento = pagamento
            else:
                id_pagamento, id_despesa, descricao, valor, data_pagamento, categoria, tipo, parcela_atual, total_parcelas = pagamento
                forma_pagamento = "Não informado"
            data = self.converter_data(data_pagamento)
            if data and inicio_mes <= data <= fim_mes:
                pagamentos_mes.append({
                    "id": id_pagamento,
                    "id_despesa": id_despesa,
                    "descricao": descricao,
                    "valor": float(valor or 0),
                    "data": data,
                    "data_texto": self.formatar_data(data_pagamento),
                    "categoria": categoria,
                    "tipo": tipo,
                    "parcela_atual": parcela_atual,
                    "total_parcelas": total_parcelas,
                    "forma_pagamento": forma_pagamento,
                })

        total_receitas = sum(item["valor"] for item in receitas_mes)
        total_gastos = sum(item["valor"] for item in gastos_mes)
        total_pagamentos = sum(item["valor"] for item in pagamentos_mes)
        total_pago = total_gastos + total_pagamentos
        total_pendente = sum(item["valor"] for item in pendentes_mes)
        total_atrasado = sum(item["valor"] for item in atrasadas)
        saldo_mes = total_receitas - total_pago

        return {
            "inicio_mes": inicio_mes,
            "fim_mes": fim_mes,
            "receitas": receitas_mes,
            "gastos": gastos_mes,
            "pagamentos": pagamentos_mes,
            "despesas_mes": despesas_mes,
            "pendentes": sorted(pendentes_mes, key=lambda item: item["data"]),
            "atrasadas": sorted(atrasadas, key=lambda item: item["data"]),
            "parcelamentos": sorted(parcelamentos_abertos, key=lambda item: item["data"]),
            "total_receitas": total_receitas,
            "total_gastos": total_gastos,
            "total_pagamentos": total_pagamentos,
            "total_pago": total_pago,
            "total_pendente": total_pendente,
            "total_atrasado": total_atrasado,
            "saldo_mes": saldo_mes,
        }

    def criar_card_resumo(self, objeto, icone, titulo, valor, info):
        card = QFrame()
        card.setObjectName(objeto)
        card.setMinimumHeight(96)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("cardValorRelatorio")
        lbl_icone.setFixedWidth(42)
        lbl_icone.setAlignment(Qt.AlignCenter)

        textos = QVBoxLayout()
        textos.setSpacing(2)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTituloRelatorio")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("cardValorRelatorio")

        lbl_info = QLabel(info)
        lbl_info.setObjectName("cardInfoRelatorio")

        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_valor)
        textos.addWidget(lbl_info)

        layout.addWidget(lbl_icone)
        layout.addLayout(textos, 1)

        return card

    def criar_linha_resumo(self, titulo, valor, info, objeto_valor):
        linha = QFrame()
        linha.setObjectName("linhaResumo")
        linha.setMinimumHeight(58)

        layout = QHBoxLayout(linha)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        textos = QVBoxLayout()
        textos.setSpacing(1)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("itemTitulo")

        lbl_info = QLabel(info)
        lbl_info.setObjectName("itemInfo")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName(objeto_valor)
        lbl_valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        textos.addWidget(lbl_titulo)
        textos.addWidget(lbl_info)

        layout.addLayout(textos, 1)
        layout.addWidget(lbl_valor)

        return linha

    def criar_item_lista(self, item, cor_valor="itemValor"):
        card = QFrame()
        card.setObjectName("itemLista")
        card.setMinimumHeight(58)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel(item.get("descricao", "-"))
        titulo.setObjectName("itemTitulo")

        detalhes = QLabel(f"📅 {item.get('data_texto', '-')}   •   📂 {item.get('categoria', '-')}   •   {item.get('tipo', '-')}")
        detalhes.setObjectName("itemInfo")
        detalhes.setWordWrap(True)

        valor = QLabel(self.formatar_moeda(item.get("valor", 0)))
        valor.setObjectName(cor_valor)
        valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        valor.setMinimumWidth(110)

        textos.addWidget(titulo)
        textos.addWidget(detalhes)

        layout.addLayout(textos, 1)
        layout.addWidget(valor)

        return card

    def criar_secao_lista(self, titulo, itens, cor_valor="itemValor", limite=5):
        caixa = QFrame()
        caixa.setObjectName("cardBase")
        caixa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        linha_titulo = QHBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("secaoRelatorio")

        total = sum(float(item.get("valor", 0) or 0) for item in itens)
        lbl_resumo = QLabel(f"{len(itens)} item(ns) • {self.formatar_moeda(total)}")
        lbl_resumo.setObjectName("textoSuave")
        lbl_resumo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        linha_titulo.addWidget(lbl_titulo)
        linha_titulo.addStretch()
        linha_titulo.addWidget(lbl_resumo)
        layout.addLayout(linha_titulo)

        if not itens:
            vazio = QLabel("Nenhum lançamento neste mês.")
            vazio.setObjectName("textoSuave")
            layout.addWidget(vazio)
        else:
            for item in itens[:limite]:
                layout.addWidget(self.criar_item_lista(item, cor_valor))

            if len(itens) > limite:
                extra = QLabel(f"+ {len(itens) - limite} lançamento(s) além destes.")
                extra.setObjectName("textoSuave")
                layout.addWidget(extra)

        return caixa

    def criar_barra(self, percentual, objeto_barra):
        fundo = QFrame()
        fundo.setObjectName("barraFundo")
        fundo.setFixedHeight(16)

        layout = QHBoxLayout(fundo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        barra = QFrame()
        barra.setObjectName(objeto_barra)
        barra.setFixedHeight(14)

        espaco = QFrame()
        espaco.setStyleSheet("background-color: transparent; border: none;")

        percentual = max(0, min(100, int(percentual)))
        layout.addWidget(barra, percentual)
        layout.addWidget(espaco, 100 - percentual)

        return fundo

    def montar_tela(self):
        if self.layout() is None:
            principal = QVBoxLayout(self)
            principal.setContentsMargins(28, 22, 28, 20)
            principal.setSpacing(14)
        else:
            self.limpar_tela()
            principal = self.layout()

        dados = self.dados_mes()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        bloco_titulo = QVBoxLayout()
        bloco_titulo.setSpacing(4)

        titulo = QLabel("📊 Relatórios")
        titulo.setObjectName("tituloRelatorio")
        titulo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        subtitulo = QLabel("Resumo financeiro por mês, com entradas, valores pagos e contas em aberto")
        subtitulo.setObjectName("subtituloRelatorio")
        subtitulo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        subtitulo.setWordWrap(True)
        subtitulo.setMinimumHeight(34)

        bloco_titulo.addWidget(titulo)
        bloco_titulo.addWidget(subtitulo)

        controles = QHBoxLayout()
        controles.setSpacing(10)
        controles.setAlignment(Qt.AlignRight | Qt.AlignTop)

        btn_anterior = QPushButton("‹")
        btn_anterior.setObjectName("btnMesRelatorio")
        btn_anterior.setFixedSize(58, 52)
        btn_anterior.clicked.connect(self.mes_anterior)

        periodo = QLabel(self.nome_mes(self.mes_referencia))
        periodo.setObjectName("periodoRelatorio")
        periodo.setAlignment(Qt.AlignCenter)
        periodo.setFixedSize(170, 52)

        btn_proximo = QPushButton("›")
        btn_proximo.setObjectName("btnMesRelatorio")
        btn_proximo.setFixedSize(58, 52)
        btn_proximo.clicked.connect(self.mes_proximo)

        btn_mes_atual = QPushButton("Mês atual")
        btn_mes_atual.setObjectName("btnMesAtualRelatorio")
        btn_mes_atual.setFixedSize(154, 52)
        btn_mes_atual.clicked.connect(self.voltar_mes_atual)

        btn_atualizar = QPushButton("↻ Atualizar")
        btn_atualizar.setObjectName("btnAtualizarRelatorio")
        btn_atualizar.setFixedSize(142, 52)
        btn_atualizar.clicked.connect(self.recarregar)

        controles.addWidget(btn_anterior)
        controles.addWidget(periodo)
        controles.addWidget(btn_proximo)
        controles.addWidget(btn_mes_atual)
        controles.addWidget(btn_atualizar)

        topo.addLayout(bloco_titulo, 1)
        topo.addLayout(controles, 0)
        principal.addLayout(topo)

        area = QScrollArea()
        area.setObjectName("areaRelatorios")
        area.setWidgetResizable(True)

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(14)

        cards = QGridLayout()
        cards.setSpacing(12)

        cards.addWidget(self.criar_card_resumo(
            "cardReceitaRelatorio", "💵", "Receitas do mês",
            self.formatar_moeda(dados["total_receitas"]),
            f"{len(dados['receitas'])} entrada(s)"
        ), 0, 0)

        cards.addWidget(self.criar_card_resumo(
            "cardPagoRelatorio", "✅", "Pago no mês",
            self.formatar_moeda(dados["total_pago"]),
            f"{len(dados['pagamentos'])} conta(s) + {len(dados['gastos'])} gasto(s)"
        ), 0, 1)

        cards.addWidget(self.criar_card_resumo(
            "cardPendenteRelatorio", "📌", "A pagar",
            self.formatar_moeda(dados["total_pendente"]),
            f"{len(dados['pendentes'])} pendente(s) • {len(dados['atrasadas'])} atrasada(s)"
        ), 0, 2)

        cards.addWidget(self.criar_card_resumo(
            "cardSaldoRelatorio", "💰", "Saldo do mês",
            self.formatar_moeda(dados["saldo_mes"]),
            "Receitas - valores já pagos"
        ), 0, 3)

        layout.addLayout(cards)

        painel = QFrame()
        painel.setObjectName("cardBase")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 18)
        painel_layout.setSpacing(12)

        secao = QLabel("Resumo do mês")
        secao.setObjectName("secaoRelatorio")
        painel_layout.addWidget(secao)

        painel_layout.addWidget(self.criar_linha_resumo(
            "Entradas", self.formatar_moeda(dados["total_receitas"]),
            "Total recebido no mês", "valorVerde"
        ))
        painel_layout.addWidget(self.criar_linha_resumo(
            "Valores já pagos", self.formatar_moeda(dados["total_pago"]),
            "Contas pagas + gastos realizados", "valorLaranja"
        ))
        painel_layout.addWidget(self.criar_linha_resumo(
            "Ainda falta pagar", self.formatar_moeda(dados["total_pendente"]),
            "Contas em aberto com vencimento neste mês", "valorVermelho"
        ))

        total_compromisso = dados["total_pago"] + dados["total_pendente"]
        resultado_previsto = dados["total_receitas"] - total_compromisso
        painel_layout.addWidget(self.criar_linha_resumo(
            "Resultado previsto", self.formatar_moeda(resultado_previsto),
            "Receitas menos valores pagos e pendentes do mês",
            "valorVerde" if resultado_previsto >= 0 else "valorVermelho"
        ))

        resultado_previsto = dados["total_receitas"] - total_compromisso
        percentual_pago = 0 if total_compromisso <= 0 else (dados["total_pago"] / total_compromisso) * 100
        percentual_pendente = 0 if total_compromisso <= 0 else (dados["total_pendente"] / total_compromisso) * 100

        lbl_andamento = QLabel("Andamento dos compromissos do mês")
        lbl_andamento.setObjectName("textoNormal")
        painel_layout.addWidget(lbl_andamento)

        painel_layout.addWidget(self.criar_barra(percentual_pago, "barraVerde"))

        info_andamento = QLabel(
            f"Pago: {int(percentual_pago)}%   •   Pendente: {int(percentual_pendente)}%   •   Total previsto: {self.formatar_moeda(total_compromisso)}"
        )
        info_andamento.setObjectName("textoSuave")
        painel_layout.addWidget(info_andamento)

        layout.addWidget(painel)

        listas = QGridLayout()
        listas.setSpacing(12)

        listas.addWidget(self.criar_secao_lista(
            "Últimas receitas", sorted(dados["receitas"], key=lambda item: item["data"], reverse=True), "valorVerde", 4
        ), 0, 0)
        listas.addWidget(self.criar_secao_lista(
            "Contas pagas", sorted(dados["pagamentos"], key=lambda item: item["data"], reverse=True), "valorAzul", 4
        ), 0, 1)
        listas.addWidget(self.criar_secao_lista(
            "Gastos realizados", sorted(dados["gastos"], key=lambda item: item["data"], reverse=True), "valorLaranja", 4
        ), 1, 0)
        listas.addWidget(self.criar_secao_lista(
            "Próximas contas", dados["pendentes"], "valorVermelho", 4
        ), 1, 1)
        listas.addWidget(self.criar_secao_lista(
            "Contas atrasadas", dados["atrasadas"], "valorVermelho", 4
        ), 2, 0)
        listas.addWidget(self.criar_secao_lista(
            "Parcelamentos em aberto", dados["parcelamentos"], "valorAzul", 4
        ), 2, 1)

        layout.addLayout(listas)

        rodape = QLabel("Use as setas para navegar entre os meses. O relatório considera os lançamentos do período selecionado.")
        rodape.setObjectName("textoSuave")
        layout.addWidget(rodape)

        area.setWidget(conteudo)
        principal.addWidget(area, 1)

    def mes_anterior(self):
        ano = self.mes_referencia.year
        mes = self.mes_referencia.month - 1
        if mes == 0:
            mes = 12
            ano -= 1
        self.mes_referencia = date(ano, mes, 1)
        self.montar_tela()

    def mes_proximo(self):
        ano = self.mes_referencia.year
        mes = self.mes_referencia.month + 1
        if mes == 13:
            mes = 1
            ano += 1
        self.mes_referencia = date(ano, mes, 1)
        self.montar_tela()

    def voltar_mes_atual(self):
        self.mes_referencia = date.today().replace(day=1)
        self.montar_tela()

    def recarregar(self):
        self.montar_tela()

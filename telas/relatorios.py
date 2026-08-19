from datetime import date, datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGridLayout, QSizePolicy, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter, QPen

from banco.banco import (
    listar_despesas,
    listar_receitas,
    listar_gastos,
    listar_pagamentos_detalhados,
)

from banco.valores_receber import listar_valores_receber


class GraficoBarrasInterativo(QWidget):
    """Gráfico vertical compacto com barras clicáveis por mês e categoria."""

    def __init__(self, meses, series, ao_clicar, parent=None):
        super().__init__(parent)
        self.meses = meses
        self.series = series
        self.ao_clicar = ao_clicar
        self.barras = []
        self.setObjectName("graficoBarrasRelatorio")
        self.setFixedHeight(224)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setToolTip("Clique em uma barra para ver os lançamentos.")

    @staticmethod
    def formatar_eixo(valor):
        if valor >= 1000:
            return f"R$ {valor / 1000:.1f} mil".replace(".", ",")
        return f"R$ {valor:.0f}"

    def paintEvent(self, evento):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#111827"))
        self.barras = []
        if not self.meses or not self.series:
            painter.setPen(QColor("#a8b3c7"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Ainda não há gastos para comparar.")
            return

        maximo = max(
            [float(valor or 0) for serie in self.series for valor in serie["valores"]] or [1]
        )
        area = QRectF(62, 14, max(120, self.width() - 80), max(110, self.height() - 52))
        grupos = len(self.meses)
        quantidade_series = len(self.series)
        largura_grupo = area.width() / max(grupos, 1)

        # Alterna faixas sutis para separar visualmente cada competência.
        for indice_mes in range(grupos):
            faixa = QRectF(
                area.left() + indice_mes * largura_grupo,
                area.top(),
                largura_grupo,
                area.height() + 28,
            )
            cor_faixa = "#12213a" if indice_mes % 2 == 0 else "#182b46"
            painter.fillRect(faixa, QColor(cor_faixa))

        painter.setPen(QPen(QColor("#334155"), 1))
        for nivel in range(5):
            y = area.bottom() - (area.height() * nivel / 4)
            painter.drawLine(area.left(), y, area.right(), y)
            if nivel in (0, 2, 4):
                painter.setPen(QColor("#718096"))
                painter.drawText(
                    QRectF(0, y - 9, 56, 18),
                    Qt.AlignRight | Qt.AlignVCenter,
                    self.formatar_eixo(maximo * nivel / 4),
                )
                painter.setPen(QPen(QColor("#334155"), 1))
        espacamento = 3
        largura_barra = max(
            6, (largura_grupo - 18 - (quantidade_series - 1) * espacamento) / max(quantidade_series, 1)
        )

        for indice_mes, mes in enumerate(self.meses):
            inicio = area.left() + indice_mes * largura_grupo + 9
            centro = area.left() + indice_mes * largura_grupo + largura_grupo / 2
            painter.setPen(QColor("#a8b3c7"))
            painter.drawText(
                QRectF(inicio, area.bottom() + 7, max(20, largura_grupo - 18), 20),
                Qt.AlignHCenter | Qt.AlignTop,
                mes["rotulo"],
            )
            for indice_serie, serie in enumerate(self.series):
                valor = float(serie["valores"][indice_mes] or 0)
                if valor <= 0:
                    continue
                altura = 0 if maximo <= 0 else area.height() * valor / maximo
                x = inicio + indice_serie * (largura_barra + espacamento)
                y = area.bottom() - altura
                retangulo = QRectF(x, y, largura_barra, altura)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(serie["cor"]))
                painter.drawRoundedRect(retangulo, 3, 3)
                self.barras.append((retangulo, mes, serie, valor))

    def mouseMoveEvent(self, evento):
        for retangulo, mes, serie, valor in self.barras:
            if retangulo.contains(evento.position()):
                texto = f"{serie['nome']} • {mes['rotulo']}: R$ {valor:,.2f}"
                self.setToolTip(texto.replace(",", "X").replace(".", ",").replace("X", "."))
                return
        self.setToolTip("Clique em uma barra para ver os lançamentos.")
        super().mouseMoveEvent(evento)

    def mouseReleaseEvent(self, evento):
        for retangulo, mes, serie, valor in self.barras:
            if retangulo.contains(evento.position()):
                self.ao_clicar(mes, serie, valor)
                evento.accept()
                return
        super().mouseReleaseEvent(evento)


class TelaRelatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.mes_referencia = date.today().replace(day=1)
        self._colunas_cartoes = None
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
                font-size: 21px;
                font-weight: 800;
            }

            QLabel#cardInfoRelatorio {
                color: #cbd5e1;
                font-size: 11px;
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
                padding: 0;
                border: 1px solid #334155;
                min-width: 42px;
                max-width: 42px;
            }

            QPushButton#btnMesAtualRelatorio {
                padding: 0 10px;
                border: 1px solid #334155;
                min-width: 126px;
                max-width: 126px;
            }

            QPushButton#btnAtualizarRelatorio {
                padding: 0 10px;
                min-width: 128px;
                max-width: 128px;
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

    @staticmethod
    def texto_quantidade(quantidade, singular, plural=None):
        palavra = singular if quantidade == 1 else (plural or f"{singular}s")
        return f"{quantidade} {palavra}"

    def separar_despesa(self, despesa):
        if len(despesa) == 10:
            return despesa

        if len(despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def dados_mes(self, referencia=None):
        hoje = date.today()
        inicio_mes = (referencia or self.mes_referencia).replace(day=1)

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

            if status == "aberta" and tipo == "Parcelamento":
                atual = int(parcela_atual or 1)
                total = int(total_parcelas or atual)
                restantes = max(total - atual + 1, 1)
                valor_parcela = float(valor or 0)
                item["parcelas_restantes"] = restantes
                item["valor_restante"] = round(valor_parcela * restantes, 2)
                item["valor_exibicao"] = item["valor_restante"]
                item["info_extra"] = f"Parcela {atual}/{total} • {restantes} restante(s) • próxima em {item['data_texto']}"
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

        # Valores a receber continuam fora das receitas até que sejam realmente
        # confirmados. Assim, o relatório mostra o planejamento sem inflar o
        # saldo realizado do mês.
        valores_receber_mes = []
        valores_receber_atrasados = []
        for valor_receber in listar_valores_receber("ativos"):
            (
                id_valor,
                pagador,
                descricao,
                _valor,
                data_prevista,
                categoria,
                _recorrente,
                _status,
                _observacao,
                _recebido,
                restante,
                situacao,
                frequencia,
            ) = valor_receber
            data = self.converter_data(data_prevista)
            if data is None:
                continue

            item = {
                "id": id_valor,
                "descricao": descricao,
                "pagador": pagador,
                "valor": float(restante or 0),
                "valor_exibicao": float(restante or 0),
                "data": data,
                "data_texto": self.formatar_data(data_prevista),
                "categoria": categoria,
                "tipo": "A receber",
                "situacao": situacao,
                "info_extra": (
                    f"{pagador}  •  {self.formatar_data(data_prevista)}  •  "
                    f"{frequencia.capitalize()}"
                ),
            }
            if inicio_mes <= data <= fim_mes:
                valores_receber_mes.append(item)
            if situacao == "atrasado":
                valores_receber_atrasados.append(item)

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
        for pagamento in listar_pagamentos_detalhados():
            (
                id_pagamento, id_despesa, descricao, valor, data_pagamento,
                categoria, tipo, parcela_atual, total_parcelas,
                forma_pagamento, valor_original, acrescimo, desconto,
                observacao,
            ) = pagamento
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
                    "valor_original": float(valor_original or valor or 0),
                    "acrescimo": float(acrescimo or 0),
                    "desconto": float(desconto or 0),
                    "observacao": observacao,
                })

        total_receitas = sum(item["valor"] for item in receitas_mes)
        total_gastos = sum(item["valor"] for item in gastos_mes)
        total_pagamentos = sum(item["valor"] for item in pagamentos_mes)
        total_acrescimos = sum(item["acrescimo"] for item in pagamentos_mes)
        total_descontos = sum(item["desconto"] for item in pagamentos_mes)
        total_pago = total_gastos + total_pagamentos
        total_pendente = sum(item["valor"] for item in pendentes_mes)
        total_atrasado = sum(item["valor"] for item in atrasadas)
        total_a_receber = sum(item["valor"] for item in valores_receber_mes)
        total_a_receber_atrasado = sum(item["valor"] for item in valores_receber_atrasados)
        saldo_mes = total_receitas - total_pago
        total_parcelamentos = sum(item.get("valor_restante", 0) for item in parcelamentos_abertos)
        resultado_previsto = total_receitas - (total_pago + total_pendente)
        resultado_planejado = resultado_previsto + total_a_receber

        return {
            "inicio_mes": inicio_mes,
            "fim_mes": fim_mes,
            "receitas": receitas_mes,
            "valores_receber": valores_receber_mes,
            "valores_receber_atrasados": sorted(valores_receber_atrasados, key=lambda item: item["data"]),
            "gastos": gastos_mes,
            "pagamentos": pagamentos_mes,
            "despesas_mes": despesas_mes,
            "pendentes": sorted(pendentes_mes, key=lambda item: item["data"]),
            "atrasadas": sorted(atrasadas, key=lambda item: item["data"]),
            "parcelamentos": sorted(parcelamentos_abertos, key=lambda item: item["data"]),
            "total_receitas": total_receitas,
            "total_gastos": total_gastos,
            "total_pagamentos": total_pagamentos,
            "total_acrescimos": total_acrescimos,
            "total_descontos": total_descontos,
            "total_pago": total_pago,
            "total_pendente": total_pendente,
            "total_atrasado": total_atrasado,
            "total_a_receber": total_a_receber,
            "total_a_receber_atrasado": total_a_receber_atrasado,
            "saldo_mes": saldo_mes,
            "total_parcelamentos": total_parcelamentos,
            "resultado_previsto": resultado_previsto,
            "resultado_planejado": resultado_planejado,
        }

    def criar_card_resumo(self, objeto, icone, titulo, valor, info):
        card = QFrame()
        card.setObjectName(objeto)
        card.setFixedHeight(76)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("cardValorRelatorio")
        lbl_icone.setFixedWidth(30)
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

    def mostrar_detalhes_ajustes(self, itens, titulo, campo, rotulo_campo):
        janela = QDialog(self)
        janela.setWindowTitle(titulo)
        janela.resize(900, 470)
        janela.setModal(True)
        janela.setStyleSheet("""
            QDialog { background-color: #0f1726; }
            QLabel { color: #ffffff; font-family: 'Segoe UI'; }
            QLabel#tituloDetalhes { font-size: 22px; font-weight: 800; }
            QLabel#resumoDetalhes { color: #a8b3c7; font-size: 13px; }
            QTableWidget { background-color: #111c2e; color: #ffffff; border: 1px solid #26364e; gridline-color: #26364e; font-size: 12px; }
            QHeaderView::section { background-color: #1e293b; color: #ffffff; border: 0; border-right: 1px solid #334155; padding: 8px; font-weight: 700; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #475569; border-radius: 8px; min-height: 38px; padding: 0 22px; font-weight: 700; }
            QPushButton:hover { background-color: #334155; }
        """)

        layout = QVBoxLayout(janela)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloDetalhes")
        total = sum(float(item.get(campo, 0) or 0) for item in itens)
        lbl_resumo = QLabel(
            f"{len(itens)} pagamento(s)  •  Total: {self.formatar_moeda(total)}"
        )
        lbl_resumo.setObjectName("resumoDetalhes")
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_resumo)

        tabela = QTableWidget(len(itens), 6)
        tabela.setHorizontalHeaderLabels([
            "Data", "Conta", "Valor original", "Total pago",
            rotulo_campo, "Observação"
        ])
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setAlternatingRowColors(True)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

        for linha, item in enumerate(sorted(itens, key=lambda i: i["data"], reverse=True)):
            valores = [
                item.get("data_texto", ""),
                item.get("descricao", ""),
                self.formatar_moeda(item.get("valor_original", 0)),
                self.formatar_moeda(item.get("valor", 0)),
                self.formatar_moeda(item.get(campo, 0)),
                item.get("observacao", "") or "—",
            ]
            for coluna, valor in enumerate(valores):
                tabela.setItem(linha, coluna, QTableWidgetItem(str(valor)))

        layout.addWidget(tabela, 1)
        botoes = QHBoxLayout()
        botoes.addStretch()
        fechar = QPushButton("Fechar")
        fechar.clicked.connect(janela.accept)
        botoes.addWidget(fechar)
        layout.addLayout(botoes)
        janela.exec()

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

        detalhe_base = f"📅 {item.get('data_texto', '-')}   •   📂 {item.get('categoria', '-')}   •   {item.get('tipo', '-')}"
        if item.get("info_extra"):
            detalhe_base = item["info_extra"]
        detalhes = QLabel(detalhe_base)
        detalhes.setObjectName("itemInfo")
        detalhes.setWordWrap(True)

        valor = QLabel(self.formatar_moeda(item.get("valor_exibicao", item.get("valor", 0))))
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

        total = sum(float(item.get("valor_exibicao", item.get("valor", 0)) or 0) for item in itens)
        lbl_resumo = QLabel(
            f"{self.texto_quantidade(len(itens), 'item')} • {self.formatar_moeda(total)}"
        )
        lbl_resumo.setObjectName("textoSuave")
        lbl_resumo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        linha_titulo.addWidget(lbl_titulo)
        linha_titulo.addStretch()
        linha_titulo.addWidget(lbl_resumo)
        layout.addLayout(linha_titulo)

        if not itens:
            vazio = QLabel("Nenhum registro para exibir.")
            vazio.setObjectName("textoSuave")
            layout.addWidget(vazio)
        else:
            for item in itens[:limite]:
                layout.addWidget(self.criar_item_lista(item, cor_valor))

            if len(itens) > limite:
                quantidade_extra = len(itens) - limite
                extra = QLabel(
                    f"+ {self.texto_quantidade(quantidade_extra, 'lançamento')} além "
                    f"{'deste' if quantidade_extra == 1 else 'destes'}."
                )
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

    def referencia_mes_anterior(self):
        ano = self.mes_referencia.year
        mes = self.mes_referencia.month - 1
        if mes == 0:
            ano, mes = ano - 1, 12
        return date(ano, mes, 1)

    def criar_janela_detalhes_lancamentos(self, titulo, itens, texto_vazio="Nenhum lançamento neste período."):
        janela = QDialog(self)
        janela.setWindowTitle(titulo)
        janela.setModal(True)
        janela.setMinimumWidth(700)
        janela.setSizeGripEnabled(True)
        janela.setStyleSheet("""
            QDialog { background-color: #0f1726; }
            QLabel { color: #ffffff; font-family: 'Segoe UI'; }
            QLabel#tituloDetalhes { font-size: 22px; font-weight: 800; }
            QLabel#resumoDetalhes { color: #a8b3c7; font-size: 13px; }
            QLabel#totalDetalhes { color: #22c55e; font-size: 18px; font-weight: 800; }
            QFrame#resumoDetalhesPainel { background-color: #152238; border: 1px solid #26364e; border-radius: 9px; }
            QTableWidget { background-color: #111c2e; color: #ffffff; border: 1px solid #26364e; gridline-color: #26364e; font-size: 13px; alternate-background-color: #162238; selection-background-color: #1d4ed8; selection-color: #ffffff; }
            QTableWidget::item { color: #ffffff; padding: 6px; border-bottom: 1px solid #26364e; }
            QTableWidget::item:alternate { background-color: #162238; color: #ffffff; }
            QHeaderView::section { background-color: #1e293b; color: #ffffff; border: 0; border-right: 1px solid #334155; padding: 8px; font-weight: 700; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #475569; border-radius: 8px; min-height: 38px; padding: 0 22px; font-weight: 700; }
            QPushButton:hover { background-color: #334155; }
        """)
        layout = QVBoxLayout(janela)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloDetalhes")
        layout.addWidget(lbl_titulo)

        total = sum(float(item.get("valor", 0) or 0) for item in itens)
        painel = QFrame()
        painel.setObjectName("resumoDetalhesPainel")
        painel_layout = QHBoxLayout(painel)
        painel_layout.setContentsMargins(14, 10, 14, 10)
        painel_layout.setSpacing(12)
        quantidade = QLabel(f"{len(itens)} lançamento(s) neste detalhe")
        quantidade.setObjectName("resumoDetalhes")
        valor_total = QLabel(self.formatar_moeda(total))
        valor_total.setObjectName("totalDetalhes")
        valor_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        painel_layout.addWidget(quantidade)
        painel_layout.addStretch()
        painel_layout.addWidget(valor_total)
        layout.addWidget(painel)

        tabela = QTableWidget(len(itens), 5)
        tabela.setObjectName("tabelaDetalhesRelatorio")
        tabela.setHorizontalHeaderLabels(["Data", "Descrição", "Categoria", "Tipo", "Valor"])
        tabela.verticalHeader().setVisible(False)
        tabela.verticalHeader().setDefaultSectionSize(35)
        tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        tabela.setSelectionMode(QTableWidget.NoSelection)
        tabela.setFocusPolicy(Qt.NoFocus)
        tabela.setAlternatingRowColors(True)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tabela.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        for linha, item in enumerate(sorted(itens, key=lambda registro: registro.get("data", date.min), reverse=True)):
            valores = [
                item.get("data_texto", "-"),
                item.get("descricao", "-"),
                item.get("categoria", "-") or "-",
                item.get("tipo", "-") or "-",
                self.formatar_moeda(item.get("valor", 0)),
            ]
            for coluna, valor in enumerate(valores):
                item_tabela = QTableWidgetItem(str(valor))
                if coluna == 4:
                    item_tabela.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tabela.setItem(linha, coluna, item_tabela)
        if not itens:
            tabela.setRowCount(1)
            tabela.setSpan(0, 0, 1, 5)
            item_vazio = QTableWidgetItem(texto_vazio)
            item_vazio.setTextAlignment(Qt.AlignCenter)
            tabela.setItem(0, 0, item_vazio)

        linhas_visiveis = max(1, min(len(itens), 7))
        tabela.setFixedHeight(40 + linhas_visiveis * 35 + 3)
        layout.addWidget(tabela)

        botoes = QHBoxLayout()
        botoes.addStretch()
        fechar = QPushButton("Fechar")
        fechar.clicked.connect(janela.accept)
        botoes.addWidget(fechar)
        layout.addLayout(botoes)
        janela.resize(790, min(560, 175 + tabela.height()))
        return janela

    def mostrar_detalhes_lancamentos(self, titulo, itens, texto_vazio="Nenhum lançamento neste período."):
        self.criar_janela_detalhes_lancamentos(titulo, itens, texto_vazio).exec()
    def ultimos_meses_relatorio(self, quantidade=6):
        meses = []
        referencia = self.mes_referencia
        for _ in range(quantidade):
            meses.append(referencia)
            mes = referencia.month - 1
            ano = referencia.year
            if mes == 0:
                ano, mes = ano - 1, 12
            referencia = date(ano, mes, 1)
        return list(reversed(meses))

    def criar_grafico_historico_categorias(self):
        meses_referencia = self.ultimos_meses_relatorio()
        dados_por_mes = [self.dados_mes(mes) for mes in meses_referencia]
        totais_categoria = {}
        itens_por_mes = []

        for dados in dados_por_mes:
            grupos = {}
            for item in dados["pagamentos"] + dados["gastos"]:
                categoria = item.get("categoria") or "Sem categoria"
                grupos.setdefault(categoria, []).append(item)
                totais_categoria[categoria] = totais_categoria.get(categoria, 0) + float(item.get("valor", 0) or 0)
            itens_por_mes.append(grupos)

        categorias_principais = [
            categoria for categoria, _total in sorted(
                totais_categoria.items(), key=lambda grupo: grupo[1], reverse=True
            )[:3]
        ]
        tem_outras = len(totais_categoria) > len(categorias_principais)
        categorias = list(categorias_principais)
        if tem_outras:
            categorias.append("Outras categorias")

        cores = ["#3b82f6", "#ef4444", "#a855f7", "#14b8a6"]
        series = []
        for indice, categoria in enumerate(categorias):
            valores, conjuntos = [], []
            for grupos in itens_por_mes:
                if categoria == "Outras categorias":
                    itens = [
                        item
                        for nome, grupo in grupos.items()
                        if nome not in categorias_principais
                        for item in grupo
                    ]
                else:
                    itens = grupos.get(categoria, [])
                conjuntos.append(itens)
                valores.append(sum(float(item.get("valor", 0) or 0) for item in itens))
            series.append({
                "nome": categoria,
                "cor": cores[indice % len(cores)],
                "valores": valores,
                "conjuntos": conjuntos,
            })

        caixa = QFrame()
        caixa.setObjectName("cardBase")
        caixa.setFixedHeight(316)
        caixa.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)

        linha_titulo = QHBoxLayout()
        titulo = QLabel("Gastos por categoria")
        titulo.setObjectName("secaoRelatorio")
        descricao = QLabel("Últimos 6 meses • clique em uma barra para detalhar")
        descricao.setObjectName("textoSuave")
        descricao.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        linha_titulo.addWidget(titulo)
        linha_titulo.addStretch()
        linha_titulo.addWidget(descricao)
        layout.addLayout(linha_titulo)

        legenda = QHBoxLayout()
        legenda.setSpacing(14)
        for serie in series:
            item_legenda = QLabel(f"■ {serie['nome']}")
            item_legenda.setStyleSheet(f"color: {serie['cor']}; font-size: 12px; font-weight: 700;")
            legenda.addWidget(item_legenda)
        legenda.addStretch()
        layout.addLayout(legenda)

        meses = [
            {"data": mes, "rotulo": self.nome_mes(mes).split(" de ")[0][:3]}
            for mes in meses_referencia
        ]

        def abrir_detalhes(mes, serie, _valor):
            indice = meses.index(mes)
            itens = serie["conjuntos"][indice]
            titulo_detalhe = f"{serie['nome']} — {self.nome_mes(mes['data'])}"
            self.mostrar_detalhes_lancamentos(titulo_detalhe, itens)

        grafico = GraficoBarrasInterativo(meses, series, abrir_detalhes, caixa)
        layout.addWidget(grafico)
        return caixa

    def criar_resumo_comparacao(self, dados_atual, dados_anterior):
        diferenca = dados_atual["total_pago"] - dados_anterior["total_pago"]
        if diferenca > 0:
            texto = f"Você gastou {self.formatar_moeda(diferenca)} a mais que no mês anterior."
            cor = "valorVermelho"
        elif diferenca < 0:
            texto = f"Você gastou {self.formatar_moeda(abs(diferenca))} a menos que no mês anterior."
            cor = "valorVerde"
        else:
            texto = "Seus gastos ficaram iguais aos do mês anterior."
            cor = "valorAzul"
        caixa = QFrame()
        caixa.setObjectName("linhaResumo")
        layout = QHBoxLayout(caixa)
        layout.setContentsMargins(16, 9, 16, 9)
        titulo = QLabel("Comparação mensal")
        titulo.setObjectName("itemTitulo")
        resultado = QLabel(texto)
        resultado.setObjectName(cor)
        resultado.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(titulo)
        layout.addWidget(resultado, 1)
        return caixa

    def criar_planejamento_compacto(self, dados):
        caixa = QFrame()
        caixa.setObjectName("linhaResumo")
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)
        titulo = QLabel("Planejamento do mês")
        titulo.setObjectName("itemTitulo")
        resumo = QLabel(
            f"A pagar: {self.formatar_moeda(dados['total_pendente'])}  •  "
            f"A receber previsto: {self.formatar_moeda(dados['total_a_receber'])}  •  "
            f"Saldo planejado: {self.formatar_moeda(dados['resultado_planejado'])}"
        )
        resumo.setObjectName("valorVerde" if dados["resultado_planejado"] >= 0 else "valorVermelho")
        resumo.setWordWrap(True)
        layout.addWidget(titulo)
        layout.addWidget(resumo)
        return caixa

    def criar_alertas(self, dados):
        alertas = []
        if dados["total_atrasado"] > 0:
            alertas.append(f"Contas atrasadas: {self.formatar_moeda(dados['total_atrasado'])}")
        if dados["total_a_receber_atrasado"] > 0:
            alertas.append(f"Valores a receber atrasados: {self.formatar_moeda(dados['total_a_receber_atrasado'])}")
        if dados["total_acrescimos"] > 0:
            alertas.append(f"Juros e multas pagos: {self.formatar_moeda(dados['total_acrescimos'])}")
        if not alertas:
            return None
        caixa = QFrame()
        caixa.setObjectName("cardPendenteRelatorio")
        layout = QHBoxLayout(caixa)
        layout.setContentsMargins(12, 8, 12, 8)
        titulo = QLabel("Atenção")
        titulo.setObjectName("itemTitulo")
        texto = QLabel("  •  ".join(alertas))
        texto.setObjectName("textoNormal")
        texto.setWordWrap(True)
        layout.addWidget(titulo)
        layout.addWidget(texto, 1)
        return caixa

    def quantidade_colunas_cartoes(self, largura=None):
        largura_util = self.width() if largura is None else largura
        return 2 if largura_util < 1250 else 4

    def montar_tela(self):
        if self.layout() is None:
            principal = QVBoxLayout(self)
            principal.setContentsMargins(28, 18, 28, 16)
            principal.setSpacing(10)
        else:
            self.limpar_tela()
            principal = self.layout()

        dados = self.dados_mes()
        dados_anterior = self.dados_mes(self.referencia_mes_anterior())

        topo = QHBoxLayout()
        topo.setSpacing(14)
        bloco_titulo = QVBoxLayout()
        bloco_titulo.setSpacing(2)
        titulo = QLabel("📊 Relatórios")
        titulo.setObjectName("tituloRelatorio")
        subtitulo = QLabel("Entenda rapidamente o que entrou, saiu e mudou no seu mês.")
        subtitulo.setObjectName("subtituloRelatorio")
        bloco_titulo.addWidget(titulo)
        bloco_titulo.addWidget(subtitulo)

        controles = QHBoxLayout()
        controles.setSpacing(7)
        controles.setContentsMargins(0, 0, 0, 0)
        btn_anterior = QPushButton("‹")
        btn_anterior.setObjectName("btnMesRelatorio")
        btn_anterior.setFixedSize(42, 40)
        btn_anterior.setToolTip("Ver mês anterior")
        btn_anterior.clicked.connect(self.mes_anterior)
        periodo = QLabel(self.nome_mes(self.mes_referencia))
        periodo.setObjectName("periodoRelatorio")
        periodo.setAlignment(Qt.AlignCenter)
        periodo.setFixedSize(164, 40)
        btn_proximo = QPushButton("›")
        btn_proximo.setObjectName("btnMesRelatorio")
        btn_proximo.setFixedSize(42, 40)
        btn_proximo.setToolTip("Ver próximo mês")
        btn_proximo.clicked.connect(self.mes_proximo)
        btn_mes_atual = QPushButton("Mês atual")
        btn_mes_atual.setObjectName("btnMesAtualRelatorio")
        btn_mes_atual.setFixedSize(126, 40)
        btn_mes_atual.clicked.connect(self.voltar_mes_atual)
        btn_atualizar = QPushButton("↻ Atualizar")
        btn_atualizar.setObjectName("btnAtualizarRelatorio")
        btn_atualizar.setFixedSize(128, 40)
        btn_atualizar.clicked.connect(self.recarregar)
        for controle in (btn_anterior, periodo, btn_proximo, btn_mes_atual, btn_atualizar):
            controles.addWidget(controle)

        topo.addLayout(bloco_titulo, 1)
        topo.addLayout(controles)
        principal.addLayout(topo)

        area = QScrollArea()
        area.setObjectName("areaRelatorios")
        area.setWidgetResizable(True)
        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(10)

        colunas_cartoes = self.quantidade_colunas_cartoes()
        self._colunas_cartoes = colunas_cartoes
        cards = QGridLayout()
        cards.setObjectName("cardsRelatorios")
        cards.setHorizontalSpacing(10)
        cards.setVerticalSpacing(8)
        for coluna in range(colunas_cartoes):
            cards.setColumnStretch(coluna, 1)
        itens_cartoes = [
            self.criar_card_resumo(
                "cardReceitaRelatorio", "💵", "Receitas", self.formatar_moeda(dados["total_receitas"]),
                self.texto_quantidade(len(dados["receitas"]), "entrada", "entradas") + " no mês",
            ),
            self.criar_card_resumo(
                "cardPagoRelatorio", "✅", "Gastos", self.formatar_moeda(dados["total_pago"]),
                "Contas pagas e gastos do dia",
            ),
            self.criar_card_resumo(
                "cardSaldoRelatorio", "💰", "Saldo realizado", self.formatar_moeda(dados["saldo_mes"]),
                "Entradas menos valores já pagos",
            ),
            self.criar_card_resumo(
                "cardSaldoRelatorio" if dados["resultado_previsto"] >= 0 else "cardPendenteRelatorio",
                "📈" if dados["resultado_previsto"] >= 0 else "📉",
                "Saldo previsto", self.formatar_moeda(dados["resultado_previsto"]),
                "Considera as contas pendentes deste mês",
            ),
        ]
        for indice, cartao in enumerate(itens_cartoes):
            cards.addWidget(cartao, indice // colunas_cartoes, indice % colunas_cartoes)
        layout.addLayout(cards)

        alerta = self.criar_alertas(dados)
        if alerta is not None:
            layout.addWidget(alerta)

        layout.addWidget(self.criar_grafico_historico_categorias())
        layout.addWidget(self.criar_resumo_comparacao(dados, dados_anterior))
        layout.addWidget(self.criar_planejamento_compacto(dados))

        rodape = QLabel(
            "Clique nas barras para abrir os lançamentos. Valores previstos a receber não entram no saldo realizado."
        )
        rodape.setObjectName("textoSuave")
        layout.addWidget(rodape)
        layout.addStretch()

        area.setWidget(conteudo)
        area.verticalScrollBar().setValue(0)
        principal.addWidget(area, 1)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        colunas = self.quantidade_colunas_cartoes()
        if self._colunas_cartoes is not None and colunas != self._colunas_cartoes:
            QTimer.singleShot(0, self.montar_tela)

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

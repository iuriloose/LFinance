"""Controles reutilizáveis para navegar entre competências mensais."""

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


MESES = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)


def nome_mes(referencia):
    return f"{MESES[referencia.month - 1]} de {referencia.year}"


def mover_mes(referencia, deslocamento):
    indice = referencia.year * 12 + referencia.month - 1 + deslocamento
    ano, mes_zero = divmod(indice, 12)
    return date(ano, mes_zero + 1, 1)


def periodo_mes(referencia):
    inicio = referencia.replace(day=1)
    return inicio, mover_mes(inicio, 1)


def pertence_ao_mes(data_texto, referencia):
    """Informa se uma data ISO (AAAA-MM-DD) pertence ao mês selecionado."""
    if not data_texto:
        return False
    inicio, proximo = periodo_mes(referencia)
    return inicio.isoformat() <= str(data_texto) < proximo.isoformat()


class FiltroMensal(QWidget):
    """Barra compacta de mês com navegação anterior, próxima e mês atual."""

    def __init__(self, titulo, referencia, ao_anterior, ao_proximo, ao_atual, parent=None):
        super().__init__(parent)
        self.setObjectName("filtroMensal")
        self.setStyleSheet("""
            QWidget#filtroMensal { background-color: #111c2d; border: 1px solid #2b405d; border-radius: 9px; }
            QLabel#tituloFiltroMensal { color: #e2e8f0; font-size: 13px; font-weight: 700; background: transparent; border: none; }
            QLabel#periodoFiltroMensal { color: #ffffff; background-color: #1a2940; border: 1px solid #344a68; border-radius: 8px; font-family: "Segoe UI"; font-size: 13px; font-weight: 700; padding: 0 14px; }
            QPushButton#btnNavegarMes { color: #ffffff; background-color: #1e293b; border: 1px solid #475569; border-radius: 8px; font-size: 18px; font-weight: 700; }
            QPushButton#btnNavegarMes:hover { background-color: #334155; border-color: #60a5fa; }
            QPushButton#btnMesAtual { color: #dbeafe; background-color: #10243a; border: 1px solid #3b82f6; border-radius: 8px; font-size: 12px; font-weight: 700; padding: 0 14px; }
            QPushButton#btnMesAtual:hover { background-color: #16415d; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        texto = QLabel(titulo)
        texto.setObjectName("tituloFiltroMensal")
        anterior = QPushButton("‹")
        anterior.setObjectName("btnNavegarMes")
        anterior.setFixedSize(34, 32)
        anterior.setToolTip("Ver mês anterior")
        anterior.clicked.connect(ao_anterior)
        periodo = QLabel(nome_mes(referencia))
        periodo.setObjectName("periodoFiltroMensal")
        periodo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        periodo.setFixedSize(156, 32)
        proximo = QPushButton("›")
        proximo.setObjectName("btnNavegarMes")
        proximo.setFixedSize(34, 32)
        proximo.setToolTip("Ver próximo mês")
        proximo.clicked.connect(ao_proximo)
        atual = QPushButton("Mês atual")
        atual.setObjectName("btnMesAtual")
        atual.setFixedHeight(32)
        atual.setToolTip("Voltar para o mês atual")
        atual.clicked.connect(ao_atual)

        layout.addWidget(texto)
        layout.addStretch(1)
        layout.addWidget(anterior)
        layout.addWidget(periodo)
        layout.addWidget(proximo)
        layout.addWidget(atual)

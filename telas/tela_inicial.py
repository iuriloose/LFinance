from datetime import date

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame
)

from componentes.cards import CardResumo
from telas.nova_despesa import NovaDespesa
from banco.banco import listar_despesas, somar_despesas_abertas, contar_despesas_atrasadas


class TelaInicial(QWidget):
    def __init__(self, ao_salvar_despesa=None):
        super().__init__()
        self.ao_salvar_despesa = ao_salvar_despesa
        self.montar_tela()

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 24)
        layout.setSpacing(24)

        topo = QHBoxLayout()

        textos = QVBoxLayout()
        titulo = QLabel("Bom dia, Iuri 👋")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Aqui está o resumo da sua vida financeira")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_despesa = QPushButton("↓  Nova despesa")
        btn_despesa.setObjectName("btnDespesa")
        btn_despesa.clicked.connect(self.abrir_nova_despesa)

        btn_receita = QPushButton("↑  Nova receita")
        btn_receita.setObjectName("btnReceita")

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_despesa)
        topo.addWidget(btn_receita)

        layout.addLayout(topo)

        total_despesas = somar_despesas_abertas()
        atrasadas = contar_despesas_atrasadas(date.today().isoformat())

        cards = QHBoxLayout()
        cards.setSpacing(18)

        cards.addWidget(CardResumo("Saldo atual", "R$ 0,00", "receitas em breve"))
        cards.addWidget(CardResumo("Receitas do mês", "R$ 0,00", "em breve"))
        cards.addWidget(CardResumo("Despesas abertas", f"R$ {total_despesas:.2f}".replace(".", ","), "total em aberto"))
        cards.addWidget(CardResumo("Contas atrasadas", str(atrasadas), "vencidas e não pagas"))

        layout.addLayout(cards)

        painel = QFrame()
        painel.setObjectName("card")

        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(24, 22, 24, 22)
        painel_layout.setSpacing(10)

        titulo_lista = QLabel("📅 Últimas despesas")
        titulo_lista.setObjectName("cardValor")
        titulo_lista.setStyleSheet("font-size: 22px;")

        painel_layout.addWidget(titulo_lista)

        despesas = listar_despesas()

        if not despesas:
            vazio = QLabel("Nenhuma despesa cadastrada ainda.")
            vazio.setObjectName("cardInfo")
            painel_layout.addWidget(vazio)
        else:
            for despesa in despesas[:6]:
                _, descricao, valor, vencimento, categoria, tipo, status = despesa
                texto = f"{vencimento}  •  {descricao}  •  R$ {valor:.2f}  •  {categoria}  •  {status}"
                texto = texto.replace(".", ",")

                linha = QLabel(texto)
                linha.setObjectName("linhaDespesa")
                painel_layout.addWidget(linha)

        painel_layout.addStretch()
        layout.addWidget(painel)

    def abrir_nova_despesa(self):
        janela = NovaDespesa()
        if janela.exec() and self.ao_salvar_despesa:
            self.ao_salvar_despesa()
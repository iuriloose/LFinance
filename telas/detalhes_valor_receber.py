from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from banco.valores_receber import (
    buscar_valor_receber_por_id,
    cancelar_valor_receber,
    desfazer_ultimo_recebimento,
    listar_recebimentos_valor,
)
from componentes.dialogo_confirmacao import confirmar_acao
from componentes.tabela_registros import TabelaRegistros


def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data):
    partes = str(data).split("-")
    if len(partes) == 3:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return str(data)


class DetalhesValorReceber(QDialog):
    def __init__(self, id_valor, parent=None):
        super().__init__(parent)
        self.id_valor = id_valor
        self.valor_receber = buscar_valor_receber_por_id(id_valor)
        self.setWindowTitle("Detalhes do valor a receber")
        self.resize(720, 560)
        self.setMinimumSize(620, 500)
        self.setModal(True)
        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog { background-color: #0f1726; }
            QLabel {
                color: #d7dcf0;
                font: 12px 'Segoe UI';
                background: transparent;
            }
            QLabel#tituloDetalhes {
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#subtituloDetalhes {
                color: #94a3b8;
                font-size: 14px;
            }
            QLabel#rotuloResumo {
                color: #94a3b8;
                font-size: 13px;
            }
            QLabel#valorResumo {
                color: #ffffff;
                font-size: 15px;
                font-weight: 800;
            }
            QFrame#cardDetalhes {
                background: #131d2e;
                border: 1px solid #2a3a52;
                border-radius: 9px;
            }
            QPushButton {
                min-height: 38px;
                border-radius: 8px;
                padding: 0 16px;
                color: #ffffff;
                font-weight: 700;
            }
            QPushButton#fechar {
                background: #1f2937;
                border: 1px solid #475569;
            }
            QPushButton#desfazer {
                background: #78350f;
                border: 1px solid #f59e0b;
            }
            QPushButton#cancelarSaldo {
                background: #7f1d1d;
                border: 1px solid #ef4444;
            }
        """)

    def montar_tela(self):
        atual = self.valor_receber
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        titulo = QLabel(atual[2])
        titulo.setObjectName("tituloDetalhes")
        subtitulo = QLabel(f"{atual[1]}  •  {atual[5]}")
        subtitulo.setObjectName("subtituloDetalhes")
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        recorrencia = {"unico": "Único", "quinzenal": "Quinzenal", "mensal": "Mensal"}.get(
            atual[12] if len(atual) > 12 else ("mensal" if atual[6] else "unico"),
            "Único",
        )
        situacao = {
            "em_aberto": "Em aberto",
            "parcial": "Parcial",
            "atrasado": "Atrasado",
            "recebido": "Recebido",
            "cancelado": "Cancelado",
        }[atual[11]]

        card = QFrame()
        card.setObjectName("cardDetalhes")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(22, 16, 22, 16)
        card_layout.setSpacing(28)
        campos = (
            (("Previsto", formatar_moeda(atual[3])), ("Recebido", formatar_moeda(atual[9]))),
            (("Restante", formatar_moeda(atual[10])), ("Previsão", formatar_data(atual[4]))),
            (("Situação", situacao), ("Frequência", recorrencia)),
        )
        for coluna in campos:
            coluna_layout = QVBoxLayout()
            coluna_layout.setSpacing(12)
            for rotulo, valor in coluna:
                campo_layout = QVBoxLayout()
                campo_layout.setSpacing(3)
                rotulo_label = QLabel(rotulo)
                rotulo_label.setObjectName("rotuloResumo")
                valor_label = QLabel(valor)
                valor_label.setObjectName("valorResumo")
                campo_layout.addWidget(rotulo_label)
                campo_layout.addWidget(valor_label)
                coluna_layout.addLayout(campo_layout)
            card_layout.addLayout(coluna_layout, 1)
        layout.addWidget(card)

        historico_titulo = QLabel("Histórico de recebimentos")
        historico_titulo.setStyleSheet(
            "color: #ffffff; font-size: 15px; font-weight: 800;"
        )
        layout.addWidget(historico_titulo)

        recebimentos = listar_recebimentos_valor(self.id_valor)
        tabela = TabelaRegistros(
            ["Data", "Valor", "Observação"],
            larguras={0: 120, 1: 145},
            coluna_flexivel=2,
            altura_linha=36,
        )
        if not recebimentos:
            tabela.mostrar_vazio("Nenhum recebimento registrado.")
        else:
            for _id, valor, data, observacao, _receita_id in recebimentos:
                tabela.adicionar_linha(
                    [formatar_data(data), formatar_moeda(valor), observacao or "—"]
                )
        layout.addWidget(tabela, 1)

        botoes = QHBoxLayout()
        if recebimentos:
            desfazer = QPushButton("Desfazer último")
            desfazer.setObjectName("desfazer")
            desfazer.setToolTip(
                "Remove o último recebimento e a Receita vinculada a ele."
            )
            desfazer.clicked.connect(self.desfazer)
            botoes.addWidget(desfazer)

        if atual[11] in {"em_aberto", "parcial", "atrasado"}:
            cancelar_saldo = QPushButton("Cancelar saldo restante")
            cancelar_saldo.setObjectName("cancelarSaldo")
            cancelar_saldo.setToolTip(
                "Encerra somente o valor ainda pendente e preserva o que já foi recebido."
            )
            cancelar_saldo.clicked.connect(self.cancelar_saldo)
            botoes.addWidget(cancelar_saldo)

        botoes.addStretch()
        fechar = QPushButton("Fechar")
        fechar.setObjectName("fechar")
        fechar.clicked.connect(self.reject)
        botoes.addWidget(fechar)
        layout.addLayout(botoes)

    def desfazer(self):
        if not confirmar_acao(
            "Desfazer recebimento",
            "O último recebimento e a Receita criada por ele serão removidos.\n\n"
            "Deseja continuar?",
            "Desfazer recebimento",
            self,
        ):
            return
        sucesso, mensagem = desfazer_ultimo_recebimento(self.id_valor)
        if not sucesso:
            QMessageBox.warning(self, "Não foi possível desfazer", mensagem)
            return
        self.accept()

    def cancelar_saldo(self):
        if not confirmar_acao(
            "Cancelar saldo restante",
            "O valor que ainda falta receber será encerrado.\n"
            "Os recebimentos já registrados continuarão em Receitas.\n\n"
            "Deseja continuar?",
            "Cancelar saldo",
            self,
            "#dc2626",
        ):
            return
        sucesso, mensagem = cancelar_valor_receber(self.id_valor)
        if not sucesso:
            QMessageBox.warning(self, "Não foi possível cancelar", mensagem)
            return
        self.accept()

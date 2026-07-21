from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import Qt

from banco.banco import listar_receitas, excluir_receita
from componentes.tabela_registros import TabelaRegistros, criar_botao_acao
from telas.nova_receita import NovaReceita


class ConfirmacaoExclusaoReceita(QDialog):
    def __init__(self, descricao):
        super().__init__()

        self.setWindowTitle("Excluir receita")
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

        titulo = QLabel("Excluir receita")
        titulo.setObjectName("tituloConfirmacao")

        texto = QLabel("Tem certeza que deseja excluir esta receita?")
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


class TelaReceitas(QWidget):
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
            QFrame#cardReceitaLista {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18, 49, 34, 0.98),
                    stop:1 rgba(12, 23, 38, 0.98)
                );
                border: 1px solid #223149;
                border-left: 4px solid #22c55e;
                border-radius: 9px;
            }

            QFrame#cardReceitaLista:hover {
                border: 1px solid #22c55e;
                background-color: rgba(20, 55, 40, 0.98);
            }

            QLabel#tituloReceitaLista {
                color: #ffffff;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#valorReceitaLista {
                color: #ffffff;
                font-size: 16px;
                font-weight: 900;
            }

            QLabel#infoReceitaLista {
                color: #d7dcf0;
                font-size: 12px;
            }

            QPushButton#btnEditarReceitaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnEditarReceitaLista:hover {
                background-color: rgba(37, 99, 235, 0.24);
                border: 1px solid #60a5fa;
            }

            QPushButton#btnExcluirReceitaLista {
                background-color: rgba(30, 41, 59, 0.78);
                color: #ffffff;
                border: 1px solid #7f1d1d;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 14px;
                min-height: 24px;
            }

            QPushButton#btnExcluirReceitaLista:hover {
                background-color: rgba(127, 29, 29, 0.34);
                border: 1px solid #ef4444;
            }

            QScrollArea#areaReceitas {
                border: none;
                background-color: transparent;
            }

            QScrollArea#areaReceitas > QWidget > QWidget {
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

    def formatar_data(self, data):
        partes = data.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data

    def formatar_moeda(self, valor):
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def criar_card_receita(self, receita):
        id_receita, descricao, valor, data_recebimento, categoria, observacao = receita

        card = QFrame()
        card.setObjectName("cardReceitaLista")
        card.setMinimumHeight(72)
        card.setMaximumHeight(78)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 12, 8)
        card_layout.setSpacing(5)

        topo = QHBoxLayout()
        topo.setSpacing(10)

        titulo = QLabel(descricao)
        titulo.setObjectName("tituloReceitaLista")

        valor_label = QLabel(self.formatar_moeda(valor))
        valor_label.setObjectName("valorReceitaLista")
        valor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        topo.addWidget(titulo, 1)
        topo.addWidget(valor_label)

        detalhes = QHBoxLayout()
        detalhes.setSpacing(8)

        extra = f"  •  📝 {observacao}" if observacao else ""
        info = QLabel(f"📅 {self.formatar_data(data_recebimento)}   📂 {categoria}{extra}")
        info.setObjectName("infoReceitaLista")
        info.setWordWrap(False)

        btn_editar = QPushButton("✏  Editar")
        btn_editar.setObjectName("btnEditarReceitaLista")
        btn_editar.setToolTip("Editar receita\n\nAltera descrição, valor, data ou observação desta receita.")
        btn_editar.setFixedSize(82, 24)
        btn_editar.clicked.connect(lambda _, r=receita: self.editar(r))

        btn_excluir = QPushButton("🗑")
        btn_excluir.setObjectName("btnExcluirReceitaLista")
        btn_excluir.setToolTip("Excluir receita\n\nRemove esta receita do LFinance após confirmação.")
        btn_excluir.setFixedSize(36, 24)
        btn_excluir.clicked.connect(lambda _, id=id_receita, d=descricao: self.excluir(id, d))

        detalhes.addWidget(info, 1)
        detalhes.addWidget(btn_editar)
        detalhes.addWidget(btn_excluir)

        card_layout.addLayout(topo)
        card_layout.addLayout(detalhes)

        card.mouseDoubleClickEvent = lambda evento, r=receita: self.editar(r)
        card.setToolTip("Dê dois cliques para editar esta receita")

        return card

    def montar_tela(self):
        self.limpar_tela()

        topo = QHBoxLayout()
        topo.setSpacing(16)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("Receitas")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Veja, edite ou exclua suas entradas de dinheiro")
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nova = QPushButton("↑  Nova receita")
        btn_nova.setObjectName("btnReceita")
        btn_nova.setToolTip("Nova receita\\n\\nRegistre uma entrada de dinheiro, como salário, venda, comissão ou outro recebimento.")
        btn_nova.clicked.connect(self.nova_receita)

        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(btn_nova)

        self.layout_principal.addLayout(topo)

        receitas = listar_receitas()

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        total_receitas = sum(float(receita[2] or 0) for receita in receitas)
        resumo = QLabel(
            f"{len(receitas)} receita(s) cadastrada(s)  •  "
            f"Total recebido: {self.formatar_moeda(total_receitas)}"
        )
        resumo.setObjectName("cardInfo")
        painel_layout.addWidget(resumo)

        tabela = TabelaRegistros(
            ["Data", "Descrição", "Categoria", "Observação", "Valor", "Ação"],
            larguras={0: 105, 2: 150, 3: 220, 4: 135, 5: 165},
            coluna_flexivel=1,
        )
        if not receitas:
            tabela.mostrar_vazio("Nenhuma receita cadastrada.")
        else:
            for receita in receitas:
                id_receita, descricao, valor, data_recebimento, categoria, observacao = receita
                linha = tabela.adicionar_linha(
                    [
                        self.formatar_data(data_recebimento),
                        descricao,
                        categoria or "—",
                        observacao or "—",
                        self.formatar_moeda(valor),
                        "",
                    ],
                    dados=receita,
                    colunas_esquerda=(1, 3),
                )
                btn_editar = criar_botao_acao(
                    "Editar",
                    lambda _, r=receita: self.editar(r),
                    "#3b82f6",
                    72,
                    "Editar esta receita",
                )
                btn_excluir = criar_botao_acao(
                    "🗑",
                    lambda _, id=id_receita, d=descricao: self.excluir(id, d),
                    "#ef4444",
                    36,
                    "Excluir esta receita",
                )
                tabela.definir_acoes(linha, [btn_editar, btn_excluir])
            tabela.cellDoubleClicked.connect(
                lambda linha, _coluna: self.editar(tabela.item(linha, 0).data(Qt.UserRole))
            )

        painel_layout.addWidget(tabela, 1)
        self.layout_principal.addWidget(painel, 1)

    def nova_receita(self):
        janela = NovaReceita()
        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def editar(self, receita):
        janela = NovaReceita(receita)
        if janela.exec():
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def excluir(self, id_receita, descricao="esta receita"):
        janela = ConfirmacaoExclusaoReceita(descricao)

        if janela.exec():
            excluir_receita(id_receita)
            self.montar_tela()
            if self.ao_alterar:
                self.ao_alterar()

    def recarregar(self):
        self.montar_tela()

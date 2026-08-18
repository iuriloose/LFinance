from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from banco.valores_receber import (
    buscar_valor_receber_por_id,
    desfazer_ultimo_recebimento,
    excluir_valor_receber,
    listar_valores_receber,
)
from componentes.tabela_registros import TabelaRegistros, criar_botao_acao
from telas.detalhes_valor_receber import DetalhesValorReceber
from telas.novo_valor_receber import NovoValorReceber
from telas.receber_valor import ReceberValor


class TelaValoresReceber(QWidget):
    def __init__(self, ao_alterar=None):
        super().__init__()
        self.ao_alterar = ao_alterar
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(36, 30, 36, 24)
        self.layout_principal.setSpacing(16)
        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QComboBox#filtroValores {
                background: #151f31;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 10px;
                min-height: 27px;
                min-width: 170px;
                font-size: 12px;
            }
            QComboBox#filtroValores::drop-down {
                border: none;
                width: 26px;
            }
            QPushButton#btnNovoValor {
                background-color: #10263a;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 12px;
                min-height: 42px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: 800;
            }
            QPushButton#btnNovoValor:hover {
                background-color: #075985;
                border-color: #7dd3fc;
            }
            QLabel#resumoValores {
                color: #d7dcf0;
                font-size: 13px;
            }
            QLabel#ajudaValores {
                color: #7dd3fc;
                font-size: 11px;
            }
        """)

    @staticmethod
    def formatar_data(data):
        partes = str(data).split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return str(data)

    @staticmethod
    def formatar_moeda(valor):
        return (
            f"R$ {float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    @staticmethod
    def texto_situacao(situacao):
        return {
            "em_aberto": ("Em aberto", "#22c55e"),
            "parcial": ("Parcial", "#f59e0b"),
            "atrasado": ("Atrasado", "#ef4444"),
            "recebido": ("Recebido", "#22c55e"),
            "cancelado": ("Cancelado", "#94a3b8"),
        }[situacao]

    def limpar_tela(self):
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self.limpar_layout(item.layout())

    def montar_tela(self, filtro_preferido=None):
        filtro_atual = filtro_preferido or "ativos"
        if filtro_preferido is None and hasattr(self, "filtro"):
            filtro_atual = self.filtro.currentData() or "ativos"
        self.limpar_tela()

        topo = QHBoxLayout()
        textos = QVBoxLayout()
        textos.setSpacing(4)
        titulo = QLabel("Valores a receber")
        titulo.setObjectName("titulo")
        subtitulo = QLabel(
            "Acompanhe salários, comissões e valores que ainda vão entrar"
        )
        subtitulo.setObjectName("subtitulo")
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        novo = QPushButton("+  Novo valor a receber")
        novo.setObjectName("btnNovoValor")
        novo.setToolTip(
            "Cadastre um dinheiro previsto. Ele só entrará no saldo quando for recebido."
        )
        novo.clicked.connect(self.novo)
        topo.addLayout(textos)
        topo.addStretch()
        topo.addWidget(novo)
        self.layout_principal.addLayout(topo)

        painel = QFrame()
        painel.setObjectName("card")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(12)

        todos = listar_valores_receber("todos")
        ativos = [
            item
            for item in todos
            if item[11] in {"em_aberto", "parcial", "atrasado"}
        ]
        atrasados = [item for item in todos if item[11] == "atrasado"]
        total_restante = sum(item[10] for item in ativos)
        total_recebido = sum(item[9] for item in todos)

        linha_resumo = QHBoxLayout()
        resumo = QLabel(
            f"{len(ativos)} ativo(s)  •  {len(atrasados)} atrasado(s)  •  "
            f"A receber: {self.formatar_moeda(total_restante)}  •  "
            f"Já recebido: {self.formatar_moeda(total_recebido)}"
        )
        resumo.setObjectName("resumoValores")

        self.filtro = QComboBox()
        self.filtro.setObjectName("filtroValores")
        self.filtro.addItem("Em aberto", "ativos")
        self.filtro.addItem("Atrasados", "atrasados")
        self.filtro.addItem("Recebidos", "recebidos")
        self.filtro.addItem("Cancelados", "cancelados")
        self.filtro.addItem("Todos", "todos")
        indice = self.filtro.findData(filtro_atual)
        self.filtro.setCurrentIndex(max(indice, 0))
        self.filtro.currentIndexChanged.connect(self.recarregar)

        linha_resumo.addWidget(resumo)
        linha_resumo.addStretch()
        linha_resumo.addWidget(QLabel("Mostrar:"))
        linha_resumo.addWidget(self.filtro)
        painel_layout.addLayout(linha_resumo)

        ajuda = QLabel(
            "Valores pendentes não alteram o saldo da Tela inicial. "
            "Use Desfazer para cancelar somente o último recebimento."
        )
        ajuda.setObjectName("ajudaValores")
        ajuda.setWordWrap(True)
        painel_layout.addWidget(ajuda)

        valores = listar_valores_receber(filtro_atual)
        self.tabela = TabelaRegistros(
            [
                "Previsão",
                "Pessoa / empresa",
                "Descrição",
                "Categoria",
                "Situação",
                "Total",
                "Restante",
                "Ação",
            ],
            larguras={
                0: 100,
                2: 190,
                3: 125,
                4: 90,
                5: 115,
                6: 120,
                7: 244,
            },
            coluna_flexivel=1,
            colunas_ocultar_compacto=(2, 3, 5),
            limite_compacto=950,
        )
        if not valores:
            self.tabela.mostrar_vazio("Nenhum valor encontrado neste filtro.")
        else:
            for item in valores:
                texto_status, cor_status = self.texto_situacao(item[11])
                linha = self.tabela.adicionar_linha(
                    [
                        self.formatar_data(item[4]),
                        item[1],
                        item[2],
                        item[5],
                        texto_status,
                        self.formatar_moeda(item[3]),
                        self.formatar_moeda(item[10]),
                        "",
                    ],
                    dados=item,
                    cores={4: cor_status},
                    tooltips={
                        1: item[1],
                        2: item[2],
                        3: item[8] or item[5],
                    },
                )
                botoes = []
                if item[11] in {"em_aberto", "parcial", "atrasado"}:
                    botoes.append(
                        criar_botao_acao(
                            "Receber",
                            lambda _, valor=item: self.receber(valor),
                            "#22c55e",
                            68,
                            "Registrar recebimento total ou parcial",
                        )
                    )
                    botoes.append(
                        criar_botao_acao(
                            "Editar",
                            lambda _, valor=item: self.editar(valor),
                            "#3b82f6",
                            58,
                            "Editar este valor a receber",
                        )
                    )
                if item[9] > 0:
                    botoes.append(
                        criar_botao_acao(
                            "Desfazer",
                            lambda _, id_valor=item[0], descricao=item[2]: self.desfazer_ultimo(
                                id_valor, descricao
                            ),
                            "#f59e0b",
                            78,
                            "Desfazer o último recebimento e a Receita vinculada",
                        )
                    )
                botoes.append(
                    criar_botao_acao(
                        "Ver",
                        lambda _, id_valor=item[0]: self.detalhes(id_valor),
                        "#38bdf8",
                        42,
                        "Ver detalhes e histórico",
                    )
                )
                if item[9] <= 0 and item[11] not in {"recebido", "cancelado"}:
                    botoes.append(
                        criar_botao_acao(
                            "🗑",
                            lambda _, id_valor=item[0], descricao=item[2]: self.excluir(
                                id_valor, descricao
                            ),
                            "#ef4444",
                            34,
                            "Excluir este valor",
                        )
                    )
                self.tabela.definir_acoes(linha, botoes)

            self.tabela.cellDoubleClicked.connect(
                lambda linha, _coluna: self.detalhes(
                    self.tabela.item(linha, 0).data(Qt.UserRole)[0]
                )
            )

        painel_layout.addWidget(self.tabela, 1)
        self.layout_principal.addWidget(painel, 1)

    def notificar_alteracao(self):
        if self.ao_alterar:
            self.ao_alterar()

    def novo(self):
        if NovoValorReceber(parent=self).exec():
            self.montar_tela()
            self.notificar_alteracao()

    def editar(self, valor):
        if NovoValorReceber(valor, self).exec():
            self.montar_tela()
            self.notificar_alteracao()

    def receber(self, valor):
        if ReceberValor(valor, self).exec():
            atualizado = buscar_valor_receber_por_id(valor[0])
            filtro = "recebidos" if atualizado and atualizado[11] == "recebido" else "ativos"
            self.montar_tela(filtro)
            self.notificar_alteracao()

    def desfazer_ultimo(self, id_valor, descricao):
        resposta = QMessageBox.question(
            self,
            "Desfazer último recebimento",
            f'O último recebimento de "{descricao}" e a Receita vinculada a ele serão removidos.\n\n'
            "Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return
        sucesso, mensagem = desfazer_ultimo_recebimento(id_valor)
        if not sucesso:
            QMessageBox.warning(self, "Não foi possível desfazer", mensagem)
            return
        self.montar_tela("ativos")
        self.notificar_alteracao()

    def detalhes(self, id_valor):
        if DetalhesValorReceber(id_valor, self).exec():
            self.montar_tela()
            self.notificar_alteracao()

    def excluir(self, id_valor, descricao):
        resposta = QMessageBox.question(
            self,
            "Excluir valor a receber",
            f'Deseja excluir "{descricao}"?\n\nEsta ação não poderá ser desfeita.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return
        sucesso, mensagem = excluir_valor_receber(id_valor)
        if not sucesso:
            QMessageBox.warning(self, "Não foi possível excluir", mensagem)
            return
        self.montar_tela()
        self.notificar_alteracao()

    def recarregar(self, *_):
        self.montar_tela()

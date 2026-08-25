"""Controles e regras de interface para categorias financeiras."""

from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QMessageBox, QPushButton, QVBoxLayout,
)

from banco.banco import (
    listar_categorias,
    listar_categorias_ocultas,
    ocultar_categoria,
    registrar_categoria_personalizada,
    restaurar_categoria,
)


ESTILO_DIALOGO_CATEGORIAS = """
    QDialog { background-color: #0f1117; }
    QLabel { color: #f5f5f5; font-family: 'Segoe UI'; font-size: 13px; }
    QLabel#tituloCategorias { font-size: 20px; font-weight: 800; }
    QLabel#ajudaCategorias { color: #a8b3c7; }
    QLineEdit, QListWidget {
        background-color: #181d29; color: #ffffff; border: 1px solid #334155;
        border-radius: 8px; padding: 7px 9px; font-size: 13px;
    }
    QListWidget::item { padding: 6px; }
    QListWidget::item:selected { background-color: #1d4ed8; }
    QPushButton {
        background-color: #202638; color: #ffffff; border: 1px solid #475569;
        border-radius: 8px; min-height: 32px; padding: 0 14px; font-weight: 700;
    }
    QPushButton:hover { background-color: #334155; }
    QPushButton#categoriaConfirmar { background-color: #2563eb; border-color: #3b82f6; }
    QPushButton#categoriaConfirmar:hover { background-color: #3b82f6; }
    QPushButton#categoriaRemover { background-color: #7f1d1d; border-color: #ef4444; }
    QPushButton#categoriaRemover:hover { background-color: #b91c1c; }
"""


def configurar_combo_categoria(combo, categoria_atual=""):
    """Prepara um seletor explícito de categorias disponíveis."""
    categoria_atual = (categoria_atual or "").strip()
    combo.clear()
    combo.addItems(listar_categorias())
    combo.setEditable(False)
    combo.setMaxVisibleItems(12)
    combo.setPlaceholderText("Selecione uma categoria")
    combo.setToolTip("Clique para abrir a lista de categorias")
    combo.setAccessibleName("Categoria")

    if categoria_atual:
        indice = combo.findText(categoria_atual)
        if indice < 0:
            # Preserva a categoria histórica ao editar um lançamento antigo.
            combo.addItem(categoria_atual)
            indice = combo.count() - 1
        combo.setCurrentIndex(indice)
    else:
        combo.setCurrentIndex(-1)


def salvar_categoria_do_combo(combo):
    """Valida a categoria escolhida e a mantém disponível para os próximos usos."""
    categoria = combo.currentText().strip()
    if not categoria:
        raise ValueError("Escolha uma categoria ou crie uma nova.")
    return registrar_categoria_personalizada(categoria)


def _atualizar_combo(combo, categoria_atual=None):
    atual = categoria_atual if categoria_atual is not None else combo.currentText()
    configurar_combo_categoria(combo, atual)


def abrir_dialogo_nova_categoria(parent, combo):
    """Solicita uma categoria nova e a seleciona no formulário atual."""
    janela = QDialog(parent)
    janela.setWindowTitle("Nova categoria")
    janela.setModal(True)
    janela.setFixedSize(410, 205)
    janela.setStyleSheet(ESTILO_DIALOGO_CATEGORIAS)

    layout = QVBoxLayout(janela)
    layout.setContentsMargins(22, 20, 22, 18)
    layout.setSpacing(10)

    titulo = QLabel("Criar nova categoria")
    titulo.setObjectName("tituloCategorias")
    ajuda = QLabel("Ex.: Bebidas, Lanche, Compras na internet.")
    ajuda.setObjectName("ajudaCategorias")
    campo = QLineEdit()
    campo.setPlaceholderText("Nome da categoria")

    botoes = QHBoxLayout()
    botoes.addStretch()
    cancelar = QPushButton("Cancelar")
    confirmar = QPushButton("Adicionar")
    confirmar.setObjectName("categoriaConfirmar")
    botoes.addWidget(cancelar)
    botoes.addWidget(confirmar)

    def salvar():
        try:
            categoria = registrar_categoria_personalizada(campo.text())
        except ValueError as erro:
            QMessageBox.warning(janela, "Categoria", str(erro))
            campo.setFocus()
            return
        _atualizar_combo(combo, categoria)
        janela.accept()

    cancelar.clicked.connect(janela.reject)
    confirmar.clicked.connect(salvar)
    campo.returnPressed.connect(salvar)

    layout.addWidget(titulo)
    layout.addWidget(ajuda)
    layout.addWidget(campo)
    layout.addStretch()
    layout.addLayout(botoes)
    campo.setFocus()
    janela.exec()


def abrir_gerenciador_categorias(parent, combo):
    """Permite ocultar/restaurar categorias sem mudar lançamentos existentes."""
    janela = QDialog(parent)
    janela.setWindowTitle("Gerenciar categorias")
    janela.setModal(True)
    janela.setFixedSize(510, 470)
    janela.setStyleSheet(ESTILO_DIALOGO_CATEGORIAS)

    layout = QVBoxLayout(janela)
    layout.setContentsMargins(22, 20, 22, 18)
    layout.setSpacing(10)

    titulo = QLabel("Gerenciar categorias")
    titulo.setObjectName("tituloCategorias")
    ajuda = QLabel(
        "Remover da lista não altera contas, gastos ou relatórios já registrados. "
        "Você pode restaurar uma categoria depois."
    )
    ajuda.setObjectName("ajudaCategorias")
    ajuda.setWordWrap(True)

    disponiveis_titulo = QLabel("Categorias disponíveis")
    lista_disponiveis = QListWidget()
    lista_disponiveis.setObjectName("listaCategoriasDisponiveis")
    ocultas_titulo = QLabel("Categorias removidas da lista")
    lista_ocultas = QListWidget()
    lista_ocultas.setObjectName("listaCategoriasOcultas")

    remover = QPushButton("Remover da lista")
    remover.setObjectName("categoriaRemover")
    restaurar = QPushButton("Restaurar categoria")
    fechar = QPushButton("Fechar")

    def atualizar_listas():
        lista_disponiveis.clear()
        lista_disponiveis.addItems(listar_categorias())
        lista_ocultas.clear()
        lista_ocultas.addItems(listar_categorias_ocultas())
        remover.setEnabled(lista_disponiveis.count() > 0)
        restaurar.setEnabled(lista_ocultas.count() > 0)

    def remover_categoria():
        item = lista_disponiveis.currentItem()
        if not item:
            QMessageBox.information(janela, "Categorias", "Escolha uma categoria disponível primeiro.")
            return
        categoria = item.text()
        caixa = QMessageBox(janela)
        caixa.setWindowTitle("Remover categoria da lista")
        caixa.setText(f"Remover “{categoria}” da lista de categorias?")
        caixa.setInformativeText(
            "As contas e gastos que já usam essa categoria não serão alterados. "
            "Você poderá restaurá-la depois."
        )
        caixa.setIcon(QMessageBox.Question)
        confirmar = caixa.addButton("Remover da lista", QMessageBox.AcceptRole)
        caixa.addButton("Cancelar", QMessageBox.RejectRole)
        caixa.exec()
        if caixa.clickedButton() != confirmar:
            return
        ocultar_categoria(categoria)
        _atualizar_combo(combo)
        atualizar_listas()

    def restaurar_categoria_selecionada():
        item = lista_ocultas.currentItem()
        if not item:
            QMessageBox.information(janela, "Categorias", "Escolha uma categoria removida primeiro.")
            return
        categoria = item.text()
        restaurar_categoria(categoria)
        _atualizar_combo(combo)
        atualizar_listas()

    remover.clicked.connect(remover_categoria)
    restaurar.clicked.connect(restaurar_categoria_selecionada)
    fechar.clicked.connect(janela.accept)

    acoes = QHBoxLayout()
    acoes.addWidget(remover)
    acoes.addWidget(restaurar)
    acoes.addStretch()
    acoes.addWidget(fechar)

    layout.addWidget(titulo)
    layout.addWidget(ajuda)
    layout.addWidget(disponiveis_titulo)
    layout.addWidget(lista_disponiveis, 1)
    layout.addWidget(ocultas_titulo)
    layout.addWidget(lista_ocultas, 1)
    layout.addLayout(acoes)
    atualizar_listas()
    janela.exec()


def adicionar_acoes_categoria(layout_categoria, combo, parent):
    """Adiciona controles claros para abrir, criar e organizar categorias."""
    acoes = QHBoxLayout()
    acoes.setSpacing(4)

    ver_lista = QPushButton("⌄ Lista")
    ver_lista.setObjectName("btnListaCategorias")
    ver_lista.setToolTip("Abrir a lista de categorias")
    ver_lista.setAccessibleName("Ver lista de categorias")
    ver_lista.setFixedWidth(64)

    nova = QPushButton("+ Nova")
    nova.setObjectName("btnNovaCategoria")
    nova.setToolTip("Criar e selecionar uma nova categoria")
    nova.setAccessibleName("Criar nova categoria")
    nova.setFixedWidth(64)

    gerenciar = QPushButton("Gerenciar")
    gerenciar.setObjectName("btnGerenciarCategorias")
    gerenciar.setToolTip("Remover ou restaurar categorias da lista")
    gerenciar.setAccessibleName("Gerenciar categorias")
    gerenciar.setFixedWidth(80)

    ver_lista.clicked.connect(combo.showPopup)
    nova.clicked.connect(lambda: abrir_dialogo_nova_categoria(parent, combo))
    gerenciar.clicked.connect(lambda: abrir_gerenciador_categorias(parent, combo))

    acoes.addWidget(ver_lista)
    acoes.addWidget(nova)
    acoes.addWidget(gerenciar)
    acoes.addStretch()
    layout_categoria.addLayout(acoes)
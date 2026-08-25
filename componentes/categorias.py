"""Utilitários para categorias escolhidas ou criadas pelo usuário."""

from PySide6.QtWidgets import QComboBox

from banco.banco import listar_categorias, registrar_categoria_personalizada


def configurar_combo_categoria(combo, categoria_atual=""):
    """Prepara um seletor que também aceita uma categoria nova."""
    combo.clear()
    combo.addItems(listar_categorias())
    combo.setEditable(True)
    combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    combo.setMaxVisibleItems(12)
    combo.setCurrentText((categoria_atual or "").strip())
    if combo.lineEdit():
        combo.lineEdit().setPlaceholderText("Escolha ou digite uma nova categoria")


def salvar_categoria_do_combo(combo):
    """Valida e registra a categoria escolhida para os próximos lançamentos."""
    return registrar_categoria_personalizada(combo.currentText())
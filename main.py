import sys

from PySide6.QtWidgets import QApplication

from banco.banco import criar_tabelas
from telas.tela_inicial import TelaInicial


criar_tabelas()

app = QApplication(sys.argv)

janela = TelaInicial()
janela.show()

sys.exit(app.exec())
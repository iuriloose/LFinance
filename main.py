import sys

from PySide6.QtWidgets import QApplication

from banco.banco import criar_tabelas
from telas.principal import TelaPrincipal


criar_tabelas()

app = QApplication(sys.argv)

janela = TelaPrincipal()
janela.show()

sys.exit(app.exec())
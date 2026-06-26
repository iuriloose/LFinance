import sys

from PySide6.QtWidgets import QApplication

from telas.tela_inicial import TelaInicial


app = QApplication(sys.argv)

janela = TelaInicial()
janela.show()

sys.exit(app.exec())
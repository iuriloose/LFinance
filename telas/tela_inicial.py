from PySide6.QtWidgets import QMainWindow


class TelaInicial(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LFinance")
        self.resize(1200, 720)
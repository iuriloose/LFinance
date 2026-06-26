from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy


class CardResumo(QFrame):
    def __init__(self, titulo, valor, info):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitulo")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("cardValor")

        lbl_info = QLabel(info)
        lbl_info.setObjectName("cardInfo")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        layout.addStretch()
        layout.addWidget(lbl_info)
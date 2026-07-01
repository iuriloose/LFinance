from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy


class CardResumo(QFrame):
    def __init__(self, titulo, valor, info=""):
        super().__init__()

        self.setObjectName("card")
        self.setMinimumHeight(92)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(4)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitulo")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("cardValor")
        lbl_valor.setStyleSheet("font-size: 26px;")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)

        if info:
            lbl_info = QLabel(info)
            lbl_info.setObjectName("cardInfo")
            lbl_info.setStyleSheet("font-size: 13px;")
            layout.addWidget(lbl_info)
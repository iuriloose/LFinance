import ctypes
import os

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QWidget


def aplicar_barra_titulo_escura(widget):
    if os.name != "nt" or widget is None:
        return

    try:
        hwnd = int(widget.winId())
        valor = ctypes.c_int(1)

        for atributo in (20, 19):
            resultado = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                atributo,
                ctypes.byref(valor),
                ctypes.sizeof(valor),
            )
            if resultado == 0:
                break
    except Exception:
        pass


class TemaJanelasWindows(QObject):
    def eventFilter(self, objeto, evento):
        if (
            os.name == "nt"
            and evento.type() == QEvent.Show
            and isinstance(objeto, QWidget)
            and objeto.isWindow()
        ):
            QTimer.singleShot(
                0,
                lambda janela=objeto: aplicar_barra_titulo_escura(janela),
            )

        return False


def instalar_tema_janelas(app):
    filtro = TemaJanelasWindows(app)
    app.installEventFilter(filtro)
    return filtro

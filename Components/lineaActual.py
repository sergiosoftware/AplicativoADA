from PyQt5.QtWidgets import QLabel, QStatusBar


class lineaActual(QStatusBar):
    def __init__(self):
        super(lineaActual, self).__init__()
        self.posicionActual = "Fila: %s, Columna: %s"
        self.fila_columna=QLabel(self.posicionActual % (0,0))
        self.addWidget(self.fila_columna)

    # Actualizar la posicion del cursor
    def actualizarCursor(self, fila, columna):
        self.fila_columna.setText(self.posicionActual % (fila, columna))


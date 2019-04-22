from Controllers.notacionAnalisis import *
import Components.panelCodigo as panelC
from Components.frameArbol import *
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


class terminalAPP(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        #Referenciado en la GUIPrincipal para construir el analizadorSemantico
        self.panel = panelC.panelCodigo()
        #Referenciado en la GUIPrincipal para construir el analizadorSemantico
        self.terminal = QTextEdit()
        #Referenciado en la GUIPrincipal para construir el analizadorSemantico
        self.estado = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.append(etiquetaRoja + "Terminal APP" + cierreEtiqueta)
        self.estado.setReadOnly(True)
        self.estado.append(etiquetaRoja + 'Variables' + cierreEtiqueta)
        fuenteAPP = QFont('Ubuntu Mono')
        fuenteAPP.setPointSize(10)
        fuenteAPP.setBold(True)
        self.estado.setFont(fuenteAPP)
        fuenteAPP.setPointSize(10)
        self.terminal.setFont(fuenteAPP)
        self.canvas = frameArbol()
        disenoAncho = QHBoxLayout()
        disenoAlto = QVBoxLayout()
        disenoAlto.addWidget(self.estado)
        disenoAlto.addWidget(self.canvas)
        disenoGeneral = QVBoxLayout()
        disenoGeneral.addWidget(self.panel)
        disenoGeneral.addStretch()
        disenoGeneral.addWidget(self.terminal)
        disenoGeneral.addStretch()
        disenoAncho.addLayout(disenoGeneral)
        disenoAncho.addLayout(disenoAlto)
        disenoAncho.setAlignment(QtCore.Qt.AlignHCenter)
        self.setLayout(disenoAncho)










from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsTextItem,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QGraphicsTextItem)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QMouseEvent as eventoRaton
from Controllers.controlAmbientes import *

# Control de arbol de ejecuciones (ambientes) en cuanto a sus componentes
class frameArbol(QGraphicsView):
    def __init__(self):
        super(frameArbol, self).__init__()
        # Inicializar el arbol de entornos
        self.arbolEntornos = None
        # Definir la ubicacion inicial en el cuadro de dibujo
        self.y = 50
        # Definir el cuadro de dibujo haciendo uso de librerias externas
        self.panelDibujo = QGraphicsScene()
        # Asignar el panelDibujo como escena principal del frame del arbol
        self.setScene(self.panelDibujo)

    # Indicar en que momento se debe repintar el canvas principal
    def drawA(self):
        self.panelDibujo.clear()
        self.graficar()

    # Proceso para graficar el arbol, incluyendo sus ambientes(nodos) y sus aristas
    def graficar(self):
        raiz = self.arbolEntornos.getRaiz()
        self.y = 50
        self.graficarArbol(raiz, 10, self.y)
        self.graficarAristas(raiz)

    # Sobrescribir el metodo mousePressEvent de la libreria QGraphicsView
    def mousePressEvent(self, event: eventoRaton) -> None:
        # Capturar las coordenadas sobre las que se realizo el evento
        coordenadaX = event.pos().x()
        coordenadaY = event.pos().y()
        # Ubicar el evento en la escena definida
        ubicacion = self.mapToScene(event.pos())
        # Obtener la reiz del arbol
        raiz = self.arbolEntornos.getRaiz()
        if (raiz!=None):
            # Se crea para poder operar el ambiente, tener acceso a el
            ambienteN = QRect(int(ubicacion.x()), int(ubicacion.y()), raiz.dimension, raiz.dimension)
            self.verificarNodo(raiz, ambienteN)

    # Verificar relacion panel-ambiente
    def verificarNodo(self, ambienteActual, ambienteBuscar):
        # Verificar si el ambienteActual buscado es el ambienteActual con el evento mouse
        if ambienteActual.dibujarN.intersects(ambienteBuscar):
            # Informacion del ambienteBuscar (ambienteActual)zz
            mensaje = QMessageBox()
            mensaje.setIcon(QMessageBox.Information)
            mensaje.setText("Ambiente: " + str(ambienteActual.contenido))
            mensaje.exec_()
            return True
        else:
            # Realizar la busqueda en todos los ambientes (nodos) restantes
            for i in ambienteActual.hijos:
                self.verificarNodo(i, ambienteBuscar)

    # Graficar el arbol generado
    def graficarArbol(self, ambiente, posX, posY):
        # Crear los esquemas ara utilizar la libreria
        nodo1 = QPen(Qt.black)
        nodo2 = QPen(Qt.green)
        # Asignar coordenada X y Y al nuevo ambiente
        ambiente.x = posX
        ambiente.y = self.y
        # Crear un modelo de ambiente (nodo)
        ambiente.dibujarN = QRect(ambiente.x, ambiente.y, ambiente.dimension, ambiente.dimension)
        # Definir si el ambiente esta activo para marcarlo con color diferente a los demas
        if ambiente.nActivo:
            self.panelDibujo.addEllipse(ambiente.x, ambiente.y, ambiente.dimension, ambiente.dimension, nodo2)
        else:
            self.panelDibujo.addEllipse(ambiente.x, ambiente.y, ambiente.dimension, ambiente.dimension, nodo1)

        # Informacion que tendra el ambiente

        cadena = QGraphicsTextItem()
        cadena.setPlainText(str(ambiente.nombre))
        cadena.setPos(QPointF(ambiente.x + 2, ambiente.y - 3))
        posX += 50

        # Graficar los hijos del ambiente actual
        for i in ambiente.hijos:
            self.y += 40
            self.graficarArbol(i,posX, self.y)

    # Graficar las aristas del arbol
    def graficarAristas(self,ambiente):
        linea1 = QPen(Qt.black)
        puntoIni = ambiente.dimension / 2
        for i in ambiente.hijos:
            posXInicial = ambiente.x + ambiente.dimension + 5
            posYInicial = ambiente.y + ambiente.dimension - 5
            posYFinal = i.y + puntoIni
            self.panelDibujo.addLine(ambiente.x + ambiente.dimension, posYInicial, posXInicial, posYInicial )
            self.panelDibujo.addLine(posXInicial, posYInicial, posXInicial, posYFinal, linea1)
            self.panelDibujo.addLine(posXInicial, posYFinal, i.x, posYFinal, linea1)
            self.graficarAristas(i)

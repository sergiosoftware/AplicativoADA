from PyQt5.QtCore import QRectF,QRect

# Ambiente de ejecucion, denotado como un nodo


class ambiente:
    def __init__(self, nombre, contenido):
        self.nombre = nombre
        self.x = 0
        self.y = 0
        self.dimension = 20
        self.nActivo = False
        self.contenido = contenido
        self.hijos = []
        self.temporales = {}
        # Variable de hiloControl sobre el ambiente (Nodo) seleccionado
        self.dibujarN = QRect(self.x, self.y, self.dimension, self.dimension)

    # Agregar un nuevo ambiente
    def agregarNodo(self, ambienteN):
        self.hijos.append(ambienteN)

    # Cantidad de hijos de un nodo
    def getNumHijos(self):
        return len(self.hijos)

    # Consultar si un nodo es una hoja
    def nodoHoja(self):
        return len(self.hijos) == 0

    # Inicializar mostrar el arbol de ejecuciones
    def mostrarArbolE(self):
        self.mostrarArbol(True)

    def mostrarArbol(self, numeroHijo):
        cadena = "└── " if numeroHijo else "├── "
        print("" + cadena + str(self.nombre))
        posicion = len(self.hijos) - 1
        cadena = "    " if numeroHijo else "│   "
        for i in range(0, posicion):
            self.hijos[i].mostrarArbol(""+cadena, False)
        if len(self.hijos) > 0:
            self.hijos[posicion].mostrarArbol(""+cadena, True)

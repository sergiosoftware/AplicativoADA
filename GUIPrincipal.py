'''librerias y archivos importados'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsTextItem, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5 import uic
import Components.terminalAPP as terAPP
import Components.lineaActual as linA
from Controllers.analizadorLexico import *
import Controllers.analizadorSintacticoSemantico as Semantico
from Controllers.notacionAnalisis import *
from Components.graficosEjecuciones import *
import threading


''' GUI principal donde se realiza toda la gestion del aplicativo'''


class GUIPrincipal(QMainWindow):
    def __init__(self):
        # Constructor para el paramtero que recibe la clase GUIPrincipal
        QMainWindow.__init__(self)
        # Inicializar el frame general diseñado en QtDesigner
        uic.loadUi("framegeneral.ui", self)
        '''Referenciar la clase terminalAPP, la cual cumplira con el papel
         de panel dentro del aplicativo, es decir, la terminal donde se recibe
         la informacion del usuario '''
        self.mainGeneral = terAPP.terminalAPP()
        # Asignar la mainGeneral como el principal componente del aplicativo
        self.setCentralWidget(self.mainGeneral)
        # Crear una instancia del analizador lexico para realizar los analisis
        self.analizadorLexico = Lexico()
        # Control del valor del nodo en el que se encuentra la ejecucion, util para la gestion de ambientes
        self.estadoActual = 0
        # Control de las graficas que se pueden general durante la ejecucion
        self.graficasTiempos = {}
        # Control de las ejecuciones que se han realizado durante el analisis del codigo
        self.ejecucion = 0
        # Cargar el Analizador sintactico y analizadorSemantico
        self.analizadorSemantico = Semantico.sintacticoSemantico(self.mainGeneral.estado, self.mainGeneral.terminal,
                                                                 self.mainGeneral.panel)
        # Control del desarrollo del analizador analizadorSemantico del aplicativo
        self.hiloControl = threading.Thread()
        # Control de la linea de ejecuion actual
        self.lineaActual = linA.lineaActual()
        self.setStatusBar(self.lineaActual)
        # Atributos de la GUI en px (x,y,ancho,alto) corresponden a la aparacion de la ventana y su dimension
        self.setGeometry(000, 000, 1350, 700)
        # Asignar los assets al frame general
        self.CargarIcono()
        # Asignar las acciones a cada componente del frame general
        self.CargarFunciones()
        # Asignar una barra de herramientas con las pricipales funciones al frame general
        self.cargarAsignarHerramientas()

    # Identifica la linea (numero) y posicion dado un estado
    def ControlLinea(self):
        x = self.mainGeneral.panel.getCursorPosition()
        self.lineaActual.actualizarCursor(x[0], x[1])

    # Definir assets para el framework general, se sobrescriben los originales del QtDesigner
    def CargarIcono(self):
        # Archivos
        self.btnNuevo.setIcon(QIcon('assets/imagenes/Agregar.png'))
        self.btnAbrir.setIcon(QIcon('assets/imagenes/Ingresar.png'))
        self.btnGuardar.setIcon(QIcon('assets/imagenes/Descargar.png'))
        self.btnSalir.setIcon(QIcon('assets/imagenes/Cancelar.png'))
        # Opciones
        self.btnFijar.setIcon(QIcon('assets/imagenes/Fijar.png'))
        self.btnLexer.setIcon(QIcon('assets/imagenes/Lexer.png'))
        self.btnContinuar.setIcon(QIcon('assets/imagenes/Siguiente.png'))
        self.btnPausar.setIcon(QIcon('assets/imagenes/Pausar.png'))
        self.btnLimpiarTerminal.setIcon(QIcon('assets/imagenes/Bin.png'))
        self.btnLimpiarVariable.setIcon(QIcon('assets/imagenes/BinVariable.png'))
        self.btnIniciar.setIcon(QIcon('assets/imagenes/BanderaVerde.png'))
        self.btnCancelar.setIcon(QIcon('assets/imagenes/BanderaRoja.png'))
        # Herramientas
        self.btnBreakpoints.setIcon(QIcon('assets/imagenes/Ubicacion.png'))
        self.btnTiempos.setIcon(QIcon('assets/imagenes/Grafica.png'))
        self.btnArbol.setIcon(QIcon('assets/imagenes/Pintar.png'))
        # Acerca de
        self.btnInformacion.setIcon(QIcon('assets/imagenes/Informacion.png'))

    # Definir las funciones para cada boton del framework general indicados en la barra de herramientas
    def CargarFunciones(self):
        self.mainGeneral.panel.cursorPositionChanged.connect(self.ControlLinea)
        # Archivos
        self.btnNuevo.triggered.connect(self.archivoNuevo)
        self.btnAbrir.triggered.connect(self.archivoAbrir)
        self.btnGuardar.triggered.connect(self.archivoGuardar)
        self.btnSalir.triggered.connect(self.archivoSalir)
        # Opciones
        self.btnFijar.triggered.connect(self.opcionesFijarLinea)
        # self.btnLexer.triggered.connect()
        self.btnContinuar.triggered.connect(self.opcionesContinuar)
        self.btnPausar.triggered.connect(self.opcionesPausar)
        self.btnLimpiarTerminal.triggered.connect(self.opcionesLimpiarTerminal)
        # self.btnLimpiarVariable.triggered.connect()
        self.btnIniciar.triggered.connect(self.opcionesIniciar)
        self.btnCancelar.triggered.connect(self.opcionesCancelar)
        # Herramientas
        self.btnBreakpoints.triggered.connect(self.herramientaBreakpoint)
        self.btnTiempos.triggered.connect(self.herramientasTiempos)
        # self.btnArbol.triggered.connect()
        # Acerca de
        self.btnInformacion.triggered.connect(self.acercadeInformacion)

    # Restaurar panel para empezar un nuevo analisis de codigo
    def archivoNuevo(self):
        self.mainGeneral.panel.clear()

    # Cargar archivo en el panel para realizar analisis
    def archivoAbrir(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "",
                                                      "All Files (*);;Python Files (*.py)", options=options)
            #filename = QFileDialog.getOpenFileName(self,'open File')
            print (fileName)
            f = open(fileName,'r')
            filedata = f.read()
            self.mainGeneral.panel.setText(filedata)
            f.close()
        except FileNotFoundError:
            print("Error al cargar el archivo :(")

    # Guardar los datos del panel en un archivo
    def archivoGuardar(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "",
                                                      "All Files (*);;Text Files (*.txt)", options=options)
            #filename = QFileDialog.getSaveFileName(self,'Save File')
            f = open(fileName,'w')
            filedata = self.mainGeneral.panel.text()
            f.write(filedata)
            f.close()
        except FileNotFoundError:
            print("Error al guardar el archivo :(")

    # Salir del aplicativo
    def archivoSalir(self):
        self.opcionesCancelar()
        sys.exit()

    # Posicion donde se ubica el cursor para fijar la linea
    def opcionesFijarLinea(self):
        posicion = self.mainGeneral.panel.getPosicion()
        self.mainGeneral.terminal.append(etiquetaRoja + "Linea x : "+str(posicion[0])+" Linea y : "+str(posicion[1])+ cierreEtiqueta)

    ''' Avanzar linea en el panel durante el analisis del codigo
        se toma el ambiente(nodo) actual y se ubica la raiz del arbol de ejecuciones
        se hace el recorrido desde la raiz hasta el ambiente (nodo) actual'''
    def opcionesContinuar(self):
        print('llega a alguna cosa')
        posicion = self.mainGeneral.panel.getPosicionCursor()
        print(self.mainGeneral.panel.getPosicionCursor())
        datos = self.posicionCursor(posicion)
        if(self.analizadorSemantico != None):
            print('alguna cosa')
            if self.analizadorSemantico.vActual != None:
                print('alguna cosa 2')
                self.mainGeneral.estado.clear()
                self.informarValores(self.analizadorSemantico.vActual)
                print('alguna cosa 3')
            nodoA = self.analizadorSemantico.aActual
            raiz = self.analizadorSemantico.arbolAmbientes.getRaiz()
            encontrarN = self.analizadorSemantico.arbolAmbientes.buscarN(nodoA, raiz)
            print('alguna cosa 4')
            encontrarN.nActivo = True
            print('alguna cosa 4.1')
            self.mainGeneral.canvas.arbolEntornos = self.analizadorSemantico.arbolAmbientes
            print('alguna cosa 4.2')
            self.mainGeneral.canvas.drawA()
            print('alguna cosa 5')
            encontrarN.nActivo = False
            self.analizadorSemantico.pasoActual = False
            print('alguna cosa 6')

    # Obtener posicion del cursor dada una linea
    def posicionCursor(self,linea):
        return self.mainGeneral.panel.text(linea[0])

    # Pausar la ejecucion del programa
    def opcionesPausar(self):
        print ("Sin desarrollar")

    # Limpiar el canvas del terminal
    def opcionesLimpiarTerminal(self):
        self.mainGeneral.terminal.clear()

    # Iniciar el proceso de analisis lexico y sintactico
    def opcionesIniciar(self):
        if (not self.hiloControl.isAlive()):
            posision = posision = self.mainGeneral.panel.getPosicionCursor()
            linea = str(self.posicionCursor(posision))
            cadena = self.mainGeneral.panel.text()
            self.analizadorLexico.setTerminal(self.mainGeneral.terminal)
            lMarcadas = self.mainGeneral.panel.getLineasMarcadas()
            # Iniciar analisis sintactico cadena a cadena
            self.analizadorSemantico.iniciarSemanticoSintactico()
            # Evitar el uso de variables que no son del analisis actual
            self.analizadorSemantico.reiniciarVariables()
            self.hiloControl = threading.Thread(target=self.analizadorSemantico.iniciarAnalisis, args=(cadena,lMarcadas,))
            self.hiloControl.start()
            self.mainGeneral.canvas.panelDibujo.clear()
        else:
            mensaje = QMessageBox()
            mensaje.setIcon(QMessageBox.Information)
            mensaje.setText("Ejecución en curso")
            mensaje.exec_()

    # Cancelar la ejecucion del aplicativo
    def opcionesCancelar(self):
        self.analizadorSemantico.detener = True
        self.analizadorSemantico.pasoActual = False
        self.mainGeneral.panel.setCursorPosition(0,0)

    # Lineas marcadas y sus ejecuciones (numero)
    def herramientaBreakpoint(self):
        mensaje = QMessageBox()
        mensaje.setIcon(QMessageBox.Warning)
        mensaje.setText("Seleccionar el número de linea, asi\nse establecera un nuevo punto de corte."
                    "\n\nLa terminal indica información sobre estos puntos, asi:\n\n"
                    "1). El primer valor corresponde a la linea\n"+
                    "2). El segundo valor las veces que paso por ese punto")
        mensaje.exec_()
        lineasMarcadas = self.analizadorSemantico.lMarcadas
        self.mainGeneral.terminal.append(str(lineasMarcadas))


    # Obtener una grafica con los tiempos de ejecucion
    def herramientasTiempos(self):
        self.graficasTiempos = self.analizadorSemantico.ctEjecucion
        self.graficasBreakpoint = self.analizadorSemantico.ctEjecucionB
        self.mainGeneral.terminal.append(str(self.graficasTiempos))
        pintarGrafica = graficosEjecuciones(self.graficasTiempos, self.graficasBreakpoint)


    # Informacion general
    def acercadeInformacion(self):
        mensaje = QMessageBox()
        mensaje.setIcon(QMessageBox.Information)
        mensaje.setText("Aplicativo ADA \n Sergio Cardona \n Sebastian Saldarriaga")
        mensaje.exec_()


    # Asignar las acciones a cada boton del frame general para mostrar una barra de herramientas alterna
    def cargarAsignarHerramientas(self):
        self.Barra.addAction(self.btnNuevo)
        self.Barra.addAction(self.btnAbrir)
        self.Barra.addAction(self.btnGuardar)
        self.Barra.addSeparator()
        self.Barra.addAction(self.btnFijar)
        self.Barra.addAction(self.btnLexer)
        self.Barra.addAction(self.btnContinuar)
        self.Barra.addAction(self.btnPausar)
        self.Barra.addSeparator()
        self.Barra.addAction(self.btnIniciar)
        self.Barra.addAction(self.btnCancelar)
        self.Barra.addSeparator()
        self.Barra.addAction(self.btnInformacion)
        self.Barra.addAction(self.btnLimpiarTerminal)
        # self.Barra.addAction(self.actionClearEst)
        self.Barra.addAction(self.btnBreakpoints)
        self.Barra.addAction(self.btnArbol)
        self.Barra.addAction(self.btnTiempos)

    # Reiniciar el panel donde se indican las variables de la ejecucion
    def reiniciarVariables(self):
        self.mainGeneral.estado.clear()

    # informacion sobre las variables de una ejecucion
    def informarValores(self, variables):
        for i,j in variables.items():
            if type(j[0]) == tuple:
                self.mainGeneral.estado.append(etiquetaAzulO + "Variable: " + cierreEtiqueta + etiquetaVerde + str(i) + cierreEtiqueta +
                                               etiquetaAzulO + "Almacenados :" + str(j[0][0]) + cierreEtiqueta + " Dimension " + str(j[0][1]))
                self.mainGeneral.estado.append(etiquetaAzulO + "Valores " + str(j[1]) + cierreEtiqueta)
            else:
                self.mainGeneral.estado.append(etiquetaAzulO + "Variable: " + cierreEtiqueta + etiquetaVerde + str(i) + cierreEtiqueta +
                                               etiquetaAzulO + "Tipo "+str(j[0]) + cierreEtiqueta)
                if (j[0] == 'GRAPH'):
                    self.mainGeneral.estado.append(etiquetaAzulO + "Ambientes " + str(j[1].nodes()) + cierreEtiqueta)
                    self.mainGeneral.estado.append(etiquetaAzulO + "Costos " + str(j[1].edges()) + cierreEtiqueta)
                else:
                    self.mainGeneral.estado.append(etiquetaAzulO + "Informacion "+ str(j[1]) + cierreEtiqueta)

    # Tokens del analisis del codigo
    def tokensCodigo(self, cadena):
        if self.actionLexer.isChecked():
            self.mainGeneral.terminal.append("Revisado")
            # en caso de ser necesario se debe hacer uso del init de la calse analizadorLexico
            #self.analizadorLexico.analizar(cadena, self.mainGeneral.estado)
        else:
            self.mainGeneral.terminal.append("Sin revisar")


''' Carga y ejecucion de todos los componentes'''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    frameP = GUIPrincipal()
    frameP.show()
    app.setWindowIcon(QIcon('assets/imagenes/icon.png'))
    app.exec_()

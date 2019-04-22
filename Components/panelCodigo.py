import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import QsciScintilla, QsciAPIs, QsciLexerPascal
from PyQt5.QtWidgets import QApplication
from Controllers.analizadorLexico import *
# Control del panel donde se gestiona el codigo ingresado por el usuario
class panelCodigo(QsciScintilla):
    # Control de la linea marcada, activa en 1
    CONTROL_LINEA_MARCADA = 1
    def __init__(self,parent=None):
        super(panelCodigo, self).__init__(parent)
        # Definir propiedades graficas
        fuente = QFont()
        fuente.setFamily('Roboto')
        fuente.setFixedPitch(True)
        fuente.setPointSize(8)
        self.setFont(fuente)
        self.setMarginsFont(fuente)
        fuenteEditor = QFontMetrics(fuente)
        self.setMarginsFont(fuente)
        self.setMarginWidth(0,fuenteEditor.width("00000")-15)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#E0E0E0"))
        self.setMarginSensitivity(1,True)
        # Ocultar scrollbar inferior
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        # Dimension del panel donde se edita el codigo
        self.setMinimumSize(600, 360)
        # funcion(señal) para la linea marcada------tengo dudas de su funcionamiento
        self.marginClicked.connect(self.asignarBreak)
        # Icono que se mostrara en la linea marcada
        self.markerDefine(QsciScintilla.Rectangle, self.CONTROL_LINEA_MARCADA)
        self.setMarkerBackgroundColor(QColor("#F90000"),self.CONTROL_LINEA_MARCADA)
        # Dar valor a los caracteres especiales
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Identificar la linea donde se encuentra la ejecucion
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#00ff22"))

        # Funciones para identar las lineas del editor de codigo
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)

        # Resaltado y fuente del lexer
        self.lexer = QsciLexerPascal()
        self.lexer.setDefaultFont(fuente)

        # Autocompletar haciendo uso de la API Qsci
        api = QsciAPIs(self.lexer)
        self.palabrasGramatica(api) #flta
        api.prepare()
        # Asignar colores a las keywords de la gramatica
        self.asignarColores() #falta
        self.setLexer(self.lexer)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        # Lineas marcadas
        self.controlLineasM = []

    # Asignar breackpoints a la linea marcada
    def asignarBreak(self, nmargin, nline, modifiers):
        #SI LA LINEA YA ESTA MARCADA SE BORRA DE LAS
        #LINEAS MARACADAS, SI NO, SE ADICIONA
        print("sdfsdfsdfsdfsd")
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.CONTROL_LINEA_MARCADA) # se agrega el breackpoint al editor para visualizarlo
            if self.controlLineasM.__contains__(nline):
                self.controlLineasM.remove(nline)#se agrega el breackpoint al aplicativo
        else:
            #se desmarca el breackpoint
            self.markerAdd(nline, self.CONTROL_LINEA_MARCADA)
            if not self.controlLineasM.__contains__(nline):
                self .controlLineasM.append(nline)

    # Obtener las palabras definidas en la gramatica para autocompletar el codigo del edito
    def palabrasGramatica(self, asignarAPI):
        analizadorLex = Lexico()
        keywords = analizadorLex.consultarPalabras()
        for i in keywords:
            asignarAPI.add(i)

    # Asignar colores a las palabras reservadas para que se diferencien en el codigo
    def asignarColores(self):
        self.lexer.setColor(QColor('#F44336'), QsciLexerPascal.Number)
        self.lexer.setColor(QColor('#34495e'), QsciLexerPascal.Keyword)
        self.lexer.setColor(QColor('#42A5F5'), QsciLexerPascal.SingleQuotedString)
        self.lexer.setColor(QColor('#F06292'), QsciLexerPascal.Operator)
        self.lexer.setColor(QColor('#3498db'), QsciLexerPascal.Character)


    # Retornar la posicion del cursos con una funcion de QsciSCintilla
    def getPosicionCursor(self):
        return self.getCursorPosition()

    # Modificar la poscion del cursor
    def setPosicionCursor(self):
        posicionN = self.getPosicionCursor()
        self.setCursorPosition(posicionN[0],posicionN[1])

    # Retornar las lineas marcadas de la estructura controlLineasM
    def getLineasMarcadas(self):
        return self.controlLineasM



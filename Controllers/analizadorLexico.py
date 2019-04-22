# importar librerias necesarias para la implementacion del proyecto
# ply.lex nos permitira construir el analizador lexico
import Controllers.ply.lex as lex
import Controllers.notacionAnalisis as resaltado
import sys


''' clase donde tendremos definidas reglas, tokens, funciones, etc.
De acuerdo a la gramatica definida y a las restricciones de la libreria PLY '''


class Lexico:
    # Constructor para la clase
    def __init__(self):
        self.lexer = None
        # palabras reservadas de la gramatica
        # se hace uso de un diccionario donde la llave corresponde a la palabra reservada y el
        # valor corresponde al token definido en la gramatica
        self.reservadas = {
            # ZONA DE DECLARACION
            'BEGIN': 'BEGIN',
            'END': 'END',
            'VAR': 'VAR',
            # TIPOS DE DATOS
            'INTEGER': 'INTEGER',
            'DOUBLE': 'DOUBLE',
            'STRING': 'STRING',
            'BOOLEAN': 'BOOLEAN',
            # CICLOS Y BUCLES
            'FOR': 'FOR',
            'WHILE': 'WHILE',
            'REPEAT': 'REPEAT',
            # CONDICIONALES
            'IF': 'IF',
            'ELSE': 'ELSE',
            # SUBRUTINAS - PROCEDIMIENTOS Y FUNCIONES
            'PROCEDURE': 'PROCEDURE',
            'FUNCTION': 'FUNCTION',
            # MODO DE LOS PARAMTEROS DE LAS SUBRUTINAS
            'E': 'MODOVALOR',
            'ES': 'MODOREFERENCIA',
            # FUNCIONES ESPECIALES
            'CALL': 'CALL',
            'MOD': 'MOD',
            'FLOOR': 'FLOOR',
            'CEIL': 'CEIL',
            'DIV': 'DIV',
            # OPERADORES LOGICOS
            'AND': 'AND',
            'OR': 'OR',
            'NOT': 'NOT',
            'NULL': 'NULL',
            'T': 'TRUE',
            'F': 'FALSE',
            # ESTRUCTURAS DE DATOS
            'STACK': 'STACK',
            'QUEUE': 'QUEUE',
            'LIST': 'LIST',
            'GRAPH': 'GRAPH',
            # SUBRUTINAS DE LAS ESTRUCUTRAS DE DATOS
            'LENGTH': 'LENGTH',
            'RECORD': 'RECORD',
            'TO': 'TO',
            'DO': 'DO',
            # OPERACIONES EXTRAS
            'WRITELN': 'WRITELN',
            'THEN': 'THEN',
            'UNTIL': 'UNTIL',
            'STR': 'STR',
            'RETURN': 'RETURN'
        }

        # producciones definidas por una expresion regular
        self.tokens = [
            # DECLARACION
            'COMENTARIO',
            'ID',
            'ASIGNACION',
            # TIPOS DE DATOS
            'DOUBLEVAL',
            'INTEGERVAL',
            'STRINGVAL',
            # OPERACIONES ELEMENTALES
            'MAS',
            'MENOS',
            'POR',
            'DIVIDIR',
            # CARACTERES ESPECIALES
            'PA',
            'PC',
            'PUNTO',
            'PUNTOCOMA',
            'COMA',
            'DOSPUNTOS',
            # OPERADORES RELACIONALES
            'MENOR',
            'MENORIGUAL',
            'MAYOR',
            'MAYORIGUAL',
            'IGUAL',
            'DIFERENTE',
            # ESTRUCTURAS DE DATOS
            'ARRAY',
            'SUBARRAY'
        ] + list(self.reservadas.values())

    # Procedimiento para consultarPalabras terminales de la gramatica
    def consultarPalabras(self):
        return self.reservadas.keys()

    # Definicion de la produccion de los tokens definidos, por
    # restriccion de la libreria se debe tener la estructura t_NOMBRE
    t_ASIGNACION = r'\<--'
    t_MAS = r'\+'
    t_MENOS = r'\-'
    t_POR = r'\*'
    t_DIVIDIR = r'\/'
    t_PA = r'\('
    t_PC = r'\)'
    t_PUNTO = r'\.'
    t_PUNTOCOMA = r'\;'
    t_COMA = r'\,'
    t_DOSPUNTOS = r'\:'
    t_MENOR = r'\<'
    t_MENORIGUAL = r'\<\='
    t_MAYOR = r'\>'
    t_MAYORIGUAL = r'\>\='
    t_IGUAL = r'\='
    t_DIFERENTE = r'\<\>'
    t_ARRAY = r'\[\d+\]'
    t_SUBARRAY = r'\[\d+\s*\.\.\s*\d+\]'

    # Procedimientos para definir las expresiones regulares de los
    # tokens que lo requieren, por restriccion de la libreria,
    # la firma de los procedimientos debe ser t_XXX y debe recibir
    # un parametro que denotara el token
    def t_COMENTARIO(self, t):
        # no importa los caracteres que se incluyan
        r'\#.*'
        pass

    def t_ID(self, t):
        # cadenas que incluyen caracteres desde la a hasta la z
        # y digitos del 0 al 9
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reservadas.get(t.value, 'ID')
        # retorna la produccion del ID
        return t

    def t_DOUBLEVAL(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        # retorna el digito con parte decimal
        return t

    def t_INTEGERVAL(self, t):
        r'\d+'
        t.value = int(t.value)
        # retorna la combinacion de digitos sin parte de decimal
        return t

    def t_STRINGVAL(self, t):
        r'\"(\s*\w*\_*\+*\-*\.*\,*\€*\!*\@*\#*\$*\%*\^*\**\(*\)*\;*\:*\\*\/*\|*\<*\>*\!*\¡*\?*\¿*\}*\{*\~*)*\"'
        t.value = str(t.value)
        # retorna los caracteres combinados como una unica cadena
        return t

    # Procedimientos especiales requeridos por la libreria para su
    # correcto funcionamiento

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += len(t.value)

    # tokens que no seran tenidos en cuenta en caso de encontrarlos
    # para el caso son la tabulacion y space
    t_ignore = ' \t'

    # Definir una instancia de la terminal para ser parametrizada

    terminal = None
    # Definir la instancia creada como una variable global

    def setTerminal(self, term):
        global terminal
        terminal = term

    # Procedimiento para capturar todos los tokens que no se encuentran
    # definidos en la gramatica y pueden ser interpretados como error
    # lrojo_rojo se interpreta como una linea con estado de error para realizar el analisis

    def t_error(self, t):
        print("Caracter invalido '%s'" % t.value[0], file=sys.stderr)
        terminal.append(resaltado.etiquetaRoja + "Caracter invalido '%s'" % str(t.value[0]) + resaltado.cierreEtiqueta)
        t.lexer.skip(1)

    # Procedimiento para iniicalizar el analizador
    # **kwargs se usa porque se desea manejar argumentos con nombre en una funcion

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Procedimiento de prueba para el analizador
    # su implementacion no se refleja en el comportamiento del analizador

    def test(self, alg):
        self.lexer.input(alg)
        while True:
            termino = self.lexer.token()
            if not termino:
                break
            print (termino)

#if __name__ == "__main__":
 #   lexico = Lexico()
#
 #   data2 ='''
  #       VAR \n
   #         x : INTEGER [5]; \n
    #        y : STACK; \n
     #       m : QUEUE; \n
      #      a : LIST; \n
       #     d : GRAPH; \n
        #    b : INTEGER; \n
         #   c : STRING; \n
          #  e : BOOLEAN; \n
           # f : DOUBLE; \n
        #BEGIN \n
         #   e <-- STR("HOLA"); \n
          #  x <-- 5; \n
        #END \n'''
#
#
 #   lexico.build()
  #  lexico.test(data2)

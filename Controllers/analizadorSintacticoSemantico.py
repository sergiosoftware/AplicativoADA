# importar librerias necesarias para la implementacion del proyecto
# ply.yacc nos permitira construir el analizador sintactico

from Controllers.analizadorLexico import *
import Controllers.ply.yacc as yacc
import queue as queue
import networkx as netx
import time
from Controllers.notacionAnalisis import *
from Controllers.controlAmbientes import *

'''Clase donde definimos las reglas para el analisis sintactico y analizadorSemantico
 de los algoritmos'''
class sintacticoSemantico:
    # Constructor de la clase
    # param terminal tendra la funcion de consola de la aplicacion, veremos informacion
    # param editor hiloControl del paso a paso de la ejecucion del codigo que se esta analizando
    def __init__(self,area = None, terminal = None, editor = None):
        # Definir una instancia del analizador lexico para realizar verificaciones
        self.lexer = Lexico()
        # tokens definidos en el analizador lexico
        self.tokens = self.lexer.tokens
        # identificador de la linea en la que se encuentra el analisis del codigo
        self.pasoActual = False
        # Palabras(funciones) rservadas definidas en la gramatica para el lenguaje
        self.pfReservadas = ['GET_P', 'GET_Q', 'GET', 'WIDTH', 'DEEP', 'DEQUEUE', 'POP', 'SIZE', 'SIZE_QUEUE', 'SIZE_STACK']
        # Palabras(procedimientos) reservadas definidas en la gramatica para el lenguaje
        self.ppReservadas = ['ADD', 'ENQUEUE', 'PUSH', 'SORT', 'ADD_NODE', 'ADD_EDGE', 'REMOVE',
                                          'REMOVE_NODE',
                                          'REMOVE_TRANS', 'TO_LIST']
        # Tipos de datos que se manejaran en el lenguaje, tambien basados en la gramatica
        self.tdLenguaje = {int: 'INTEGER', str: 'STRING', float: 'DOUBLE', bool: 'BOOLEAN'}
        # Control de la variables con su valor y tipo
        self.vGlobales = {}
        # Control de la variable que se encuentra en analisis
        self.vActual = None
        # Control de las funciones ingresadas por el usuario
        self.fUsuario = {}
        # Control de los procedimientos ingresados por el usuario
        self.pUsuario = {}
        # Control de registros ingresados por el usuario
        self.rUsuario = {}
        # Control de la ejecucion del analisis
        self.detener = False
        # Control de las lineas marcadas por el usuario
        self.lMarcadas = {}
        # Control del ambiente(nodo) de ejecucion
        self.aActual = 0
        # Control del arbol de ambientes
        self.arbolAmbientes = controlAmbientes()
        # Control de los ambientes generados
        self.ambientesG = 0
        # Control del tiempo de ejecucion
        self.tiempoE = 0
        # Control de los tiempos de ejecucion individuales (reales)
        self.ctEjecucion = {}
        # Control de los tiempos de ejecucion individuales (teoricos) y sus breakpoints
        self.ctEjecucionB = {}
        # Control de acciones generales
        self.contador = 0
        # Asignar los parametros recibidos en el constructor
        self.area = area
        self.terminal = terminal
        self.editor = editor
        self.t = None


    # Iniciar analisis sintactico y Semantico
    def iniciarAnalisis(self,texto,linea):
        for i in linea:
            self.lMarcadas[i+1] = 0
        self.lexer.build()
        self.semsin.parse(texto, tracking=True, lexer=self.lexer.lexer)

    # Recursos para analisis Semantico y sintactico haciendo uso de las librerias ply
    def iniciarSemanticoSintactico(self):
        self.semsin=yacc.yacc(module=self)

    # Asignar a las variables sus valores iniciales
    def reiniciarVariables(self):
        # identificador de la linea en la que se encuentra el analisis del codigo
        self.pasoActual = False
        # Control de la variables con su valor y tipo
        self.vGlobales = {}
        # Control de la variable que se encuentra en analisis
        self.vActual = None
        # Control de las funciones ingresadas por el usuario
        self.fUsuario = {}
        # Control de los procedimientos ingresados por el usuario
        self.pUsuario = {}
        # Control de registros ingresados por el usuario
        self.rUsuario = {}
        # Control de la ejecucion del analisis
        self.detener = False
        # Control de las lineas marcadas por el usuario
        self.lMarcadas = {}
        # Control del ambiente(nodo) de ejecucion
        self.aActual = 0
        # Control de acciones generales
        self.contador += 1
        # Control del tiempo de ejecucion
        self.tiempoE = 0
        # Control del arbol de ambientes
        self.arbolAmbientes = controlAmbientes()
        # Control de los ambientes generados
        self.ambientesG = 0

    # Estructurar los condicionales de acuerdo a la gramatica definida y sus respectivas reglas
    def estructurarCondiciones(self, valorRecibido, variablesDefinidas: {}, padreAmbiente=0):
        cad_eval = ''
        lista_condicion = valorRecibido.split(',')  # separo por coma en una lista los valores que entran
        # print(lista_condicion)
        lista_oplog = ['<', '>', '<=', '>=', 'and', 'or', '!=', '=']  # lista con los operadores logicos

        for i in lista_condicion:  # recorro la lista cad_temp
            if i not in lista_oplog:  # si no esta en los operadores e por que es un id o valorRecibido exlicito
                val_temp = self.convertirVarValor(i, variablesDefinidas, padreAmbiente)  # obtengo el valorRecibido de la cadena
                # print(val_temp)
                cad_eval += str(val_temp)  # la concateno en la cadena que vamos a devolver para evaluar
            else:
                # si esta en los operadores logicos
                if i == '=':  # si es igual =
                    cad_eval += '=='  # concateno ==
                elif i == 'and' or i == 'or':
                    cad_eval += ' ' + i + ' '  # si es and u or concateno espacios y en medio la operacio
                    # si no hago esto queda la cadena pegada y no se puede evaluar
                else:
                    cad_eval += i  # en otro caso simplemente concateno el operador
        # print(cad_eval)
        return cad_eval  # devuelvo la cadena lista para ser evaluada

    # Estructuras las funciones ingresadas por el usuario en el editor
    def estructurarFunciones(self, valorRecibido, variablesDefinidas, padreAmbiente=0):
        # valorRecibido
        # ('sumar', 'True,&i&,&sumpar&')
        variables_funcion = {}  # variablesDefinidas que le pasaremos a la funcion
        funcion_temp = ()
        nombre_funcion = valorRecibido[0]  # Obtenemos el nombre de la funcion
        # si es una funcion reservada del lenguaje
        if nombre_funcion.upper() in self.pfReservadas:

            parametros_pasados = valorRecibido[1]

            if nombre_funcion == 'GET_P':
                pila = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'STACK'):  # ees porque es el primer parametro
                                pila = temp_var[1]


                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de obtener sin remover STACK en una variable diferente a una STACK",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener sin remover STACK en una variable diferente a una STACK" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, no se puede realizar una operacion de operacion de obtener sin remover en un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede realizar una operacion de operacion de obtener sin remover en un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    if (len(pila) == 0):
                        print(
                            "Error semantico, no se puede obtener sin remover sobre una pila vacia " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede obtener sin remover sobre una pila vacia " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
                    else:
                        retorno = pila.pop()  # sacamos
                        pila.append(retorno)  # ingresamos nuevamente por la izquierda
                        retorno = eval(retorno)  # y retornamos
                        return retorno

                else:
                    print(
                        "Error sintaxicosemantico, la funcion obtener sin remover STACK solo recive la pila",
                        file=sys.stderr)

                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion obtener sin remover STACK solo recive la pila" + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)

            elif nombre_funcion == 'POP':
                pila = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'STACK'):  # ees porque es el primer parametro
                                pila = temp_var[1]


                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de pop en una variable diferente a una STACK",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de pop en una variable diferente a una STACK" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, no se puede realizar una operacion de operacion de pop en un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede realizar una operacion de operacion de pop en un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    if (len(pila) == 0):
                        print(
                            "Error semantico, no se puede pop sobre una pila vacia " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede pop sobre una pila vacia " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
                    else:
                        retorno = pila.pop()  # sacamos
                        return eval(retorno)

                else:
                    print(
                        "Error sintaxicosemantico, la funcion pop solo recive la pila",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion pop solo recive la pila" + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)


            elif nombre_funcion == 'DEQUEUE':
                cola = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'QUEUE'):  # ees porque es el primer parametro
                                cola = temp_var[1]


                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de deseencolar en una variable diferente a una QUEUE",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de deseencolar en una variable diferente a una QUEUE" + cierreEtiqueta)
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, eno se puede realizar una operacion de desencolar en un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, eno se puede realizar una operacion de desencolar en un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    if (len(cola) == 0):
                        print(
                            "Error semantico, no se puede desencolar sobre una cola vacia " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede desencolar sobre una cola vacia " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
                    else:
                        retorno = cola.popleft()  # recordar mirar lo que hemos encolado
                        retorno = eval(retorno)
                        return retorno

                else:
                    print(
                        "Error sintaxicosemantico, la funcion desencolar solo recive dos parametros, la cola y el valorRecibido a encolar ",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion desencolar solo recive dos parametros, la cola y el valorRecibido a encolar " + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)


            elif nombre_funcion == 'GET_Q':
                cola = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'QUEUE'):  # ees porque es el primer parametro
                                cola = temp_var[1]


                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de obtener sin remover QUEUE en una variable diferente a una QUEUE",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener sin remover QUEUE en una variable diferente a una QUEUE" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, no se puede realizar una operacion de operacion de obtener sin remover en un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede realizar una operacion de operacion de obtener sin remover en un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    if (len(cola) == 0):
                        print(
                            "Error semantico, no se puede obtener sin remover QUEUE sobre una cola vacia " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede obtener sin remover QUEUE sobre una cola vacia " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
                    else:
                        retorno = cola.popleft()  # sacamos
                        cola.appendleft(retorno)  # ingresamos nuevamente por la izquierda
                        retorno = eval(retorno)  # y retornamos
                        return retorno

                else:
                    print(
                        "Error sintaxicosemantico, la funcion obtener sin remover solo recive la cola",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion obtener sin remover solo recive la cola" + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)

            elif nombre_funcion == 'SIZE_QUEUE':
                cola = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'QUEUE'):  # ees porque es el primer parametro
                                cola = temp_var[1]

                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de obtener longitud de cola en una variable diferente a una QUEUE",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener longitud de cola en una variable diferente a una QUEUE" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, eno se puede realizar una operacion de obtener longitud de cola sobre un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener longitud de cola sobre un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    return len(cola)

                else:
                    print(
                        "Error sintaxicosemantico, la funcion tamaño de cola solo recive la cola ",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion tamaño de cola solo recive la cola " + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)
            elif nombre_funcion == 'SIZE_STACK':
                pila = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            tipo_var = temp_var[0]

                            if (tipo_var == 'STACK'):  # ees porque es el primer parametro
                                pila = temp_var[1]

                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de obtener longitud de pila en una variable diferente a una STACK",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener longitud de pila en una variable diferente a una STACK" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, eno se puede realizar una operacion de obtener longitud de pila sobre un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, eno se puede realizar una operacion de obtener longitud de pila sobre un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    return len(pila)

                else:
                    print(
                        "Error sintaxicosemantico, la funcion tamaño de pila solo recive la pila ",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion tamaño de pila solo recive la pila " + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)
            elif nombre_funcion == 'SIZE':
                lista_arreglo = ''

                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                # print(lista_parametros)

                # Recordar optimizar
                if len(lista_parametros) == 1:
                    if lista_parametros[0].find('&') != -1:  # si la encontro es porque es una variable
                        temp_var_name = lista_parametros[0].replace("&", "")  # quitamos el ampersand
                        if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                            temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                            if (type(temp_var[0]) == tuple):  # porque puede ser un arreglo
                                tipo_var = 'ARRAY'
                            else:
                                tipo_var = temp_var[0]

                            if (tipo_var == 'LIST' or tipo_var == 'ARRAY'):  # ees porque es el primer parametro
                                lista_arreglo = temp_var[1]

                            else:
                                print(
                                    "Error semantico, no se puede realizar una operacion de obtener longitud  en una variable diferente a una LIST o un ARRAY",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener longitud  en una variable diferente a una LIST o un ARRAY" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            print(
                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    else:
                        print(
                            "Error semantico, eno se puede realizar una operacion de obtener longitud sobre un escalar " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, eno se puede realizar una operacion de obtener longitud sobre un escalar " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # termino el for
                    # encolamos
                    return len(lista_arreglo)

                else:
                    print(
                        "Error sintaxicosemantico, la funcion tamaño de LIST o ARRAY solo recive la lista o el arreglo ",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion tamaño de LIST o ARRAY solo recive la lista o el arreglo " + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)
            elif nombre_funcion == 'GET':
                lista = ''
                valor_indice = ''
                lista_parametros = parametros_pasados.split(",")
                # print(lista_parametros)
                if len(lista_parametros) == 2:
                    indice = 0
                    for m in range(0, len(lista_parametros)):
                        if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                            temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                            if temp_var_name in variablesDefinidas.keys():  # si esta en la tabla de variablesDefinidas de contexto
                                temp_var = variablesDefinidas[temp_var_name]  # entonces la sacamos

                                tipo_var = temp_var[0]

                                if (tipo_var == 'LIST' and indice == 0):  # ees porque es el primer parametro
                                    lista = temp_var[1]
                                elif indice == 1:  # esporque es el segundo parametro
                                    if (tipo_var != 'INTEGER'):
                                        print(
                                            "Error semantico, no se puede realizar una operacion de obtener, con un indice diferente a un INTEGER ",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener, con un indice diferente a un INTEGER " + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_indice = temp_var[1]

                                else:
                                    print(
                                        "Error semantico, no se puede realizar una operacion get en una variable diferente a una LIST",
                                        file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, no se puede realizar una operacion get en una variable diferente a una LIST" + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                            else:
                                print(
                                    "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion,
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_funcion + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:

                            if (indice == 0):
                                print(
                                    "Error semantico, se esperaba una variable de tipo LIST, no un escalar",
                                    file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, se esperaba una variable de tipo LIST, no un escalar" + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                            else:
                                if (type(eval(lista_parametros[m])) != int):
                                    print(
                                        "Error semantico, no se puede realizar una operacion de obtener, con un indice diferente a un INTEGER ",
                                        file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, no se puede realizar una operacion de obtener, con un indice diferente a un INTEGER " + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                                else:
                                    valor_indice = int(lista_parametros[m])
                        indice += 1

                    # termino el for
                    try:
                        retorno = eval(lista[valor_indice])  # adicionamos
                        return retorno
                    except IndexError as e:
                        print(
                            "Error semantico, esa posicion no existe en la lista " + str(e),
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, esa posicion no existe en la lista " + str(e) + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
                else:
                    print(
                        "Error sintaxicosemantico, la funcion get de LIST de la lista no tiene el numero de parametros correctos ",
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error sintaxicosemantico, la funcion get de LIST de la lista no tiene el numero de parametros correctos" + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)


        # sino, es una funcion creada por el usuario
        elif nombre_funcion in self.fUsuario.keys():
            self.ambientesG += 1
            x = self.ambientesG

            # print("agrego ambiente",self.arbolito.add2(x, padreAmbiente,"Funcion :" +str(nombre_funcion)))
            # print("Ambiente : ",x," Padre :",padreAmbiente)

            parametros_pasados = valorRecibido[1]

            funcion_temp = self.fUsuario[nombre_funcion]  # obtenemos la funcion

            # print(funcion_temp)

            parametros_esperado = funcion_temp[0]

            parametros_esperado = parametros_esperado.split('-')

            parametros_esperado_organizado = []
            for n in parametros_esperado:
                temp_p = n.split(',')
                parametros_esperado_organizado.append(temp_p)

            # print(parametros_esperado_organizado)

            # [['E', 'INTEGER', 'n1'], ['E', 'INTEGER', 'n2'], ['ES', 'INTEGER', 'n3']]
            tabla_funcion = funcion_temp[1]
            lista_parametros = parametros_pasados.split(",")
            for m in range(0, len(lista_parametros)):
                if lista_parametros[m].find('&') != -1:
                    temp_var_name = lista_parametros[m].replace("&", "")
                    if temp_var_name in variablesDefinidas.keys():
                        temp_var = variablesDefinidas[temp_var_name]
                        if parametros_esperado_organizado[m][0] == 'E':  # sacamos el tipo de parametros que recibe
                            nombre_variable = parametros_esperado_organizado[m][2]
                            tipo_variable = parametros_esperado_organizado[m][1]

                            if temp_var[0] == tipo_variable:
                                if temp_var[0] not in self.tdLenguaje.values():  # si es una estructura de datos
                                    print(
                                        "Los tipos de estrucutras de datos se deben pasar por referencia")
                                    self.terminal.append(
                                        etiquetaAmarilla + "Los tipos de estrucutras de datos se pasan por referencia" + cierreEtiqueta)

                                # variablesDefinidas[i] = [tipo, valorRecibido]
                                variables_funcion[nombre_variable] = [tipo_variable,
                                                                      temp_var[1]]  # enviamos la variable


                            else:
                                print(
                                    "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                    + " y se encontro con " + str(temp_var[0]), file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                    + " y se encontro con " + str(temp_var[0]) + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)

                        else:  # por referencia
                            nombre_variable = parametros_esperado_organizado[m][2]
                            tipo_variable = parametros_esperado_organizado[m][1]

                            if temp_var[0] == tipo_variable:
                                variables_funcion[nombre_variable] = temp_var  # enviamos la variable

                            else:
                                print(
                                    "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                    + " y se encontro con " + str(temp_var[0]), file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                    + " y se encontro con " + str(temp_var[0]) + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)

                    else:
                        print(
                            "Error semantico, esta variable no esta definida en el alcance de esta funcion " + nombre_funcion,
                            file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de esta funcion " + nombre_funcion + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                else:
                    if parametros_esperado_organizado[m][0] == 'E':
                        variable_pasada = lista_parametros[m]
                        try:
                            variable_pasada = eval(variable_pasada)
                            nombre_variable = parametros_esperado_organizado[m][2]
                            tipo_variable = parametros_esperado_organizado[m][1]
                            if (type(variable_pasada) in self.tdLenguaje.keys()):
                                tipo_variable_pasada = self.tdLenguaje[type(variable_pasada)]
                                if (tipo_variable_pasada == tipo_variable):
                                    variables_funcion[nombre_variable] = [tipo_variable,
                                                                          variable_pasada]  # creamos una variable
                                else:
                                    print(
                                        "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                        + " y se encontro con " + str(variable_pasada), file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                        + " y se encontro con " + str(variable_pasada) + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                        except Exception as e:
                            print(
                                "Error semantico, no se permite este tipo de parametros en la funcion " + nombre_funcion + " " + variable_pasada + " " + str(
                                    e), file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, no se permite este tipo de parametros en la funcion " + nombre_funcion + " " + variable_pasada + " " + str(
                                    e) + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)
                    else:
                        print("Error semantico, un escalar no se puede pasar por referencia ", file=sys.stderr)
                        self.terminal.append(
                            etiquetaRoja + "Error semantico, un escalar no se puede pasar por referencia " + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)
            # print(funcion_temp[1])
            # print(funcion_temp)
            print("agrego ambiente", self.arbolAmbientes.agregarAmbiente(self.ambientesG, padreAmbiente, "Funcion : " + str(
                nombre_funcion) + "\nParametros pasados " + str(variables_funcion)))

            print("Ambiente : ", self.ambientesG, " Padre : ", padreAmbiente)
            retorno = self.algPrincipal(funcion_temp[1], variables_funcion, self.ambientesG)
            # print(variables_funcion)

            return retorno
        else:
            print("Error semantico, la funcion  " + nombre_funcion + " no esta definida", file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Error semantico, la funcion  " + nombre_funcion + " no esta definida" + cierreEtiqueta)
            self.reiniciarVariables()
            exit(1)

    # intercambiar el nombre de la variable por su valo
    def convertirVarValor(self, valorRecibido, variablesDefinidas, padreAmbiente=0):
        # print(valorRecibido)
        # si es una tupla entonces se esta asignando una funcion
        if type(valorRecibido) == tuple:

            return self.estructurarFunciones(valorRecibido, variablesDefinidas, padreAmbiente)

        else:
            valor_return = ''
            try:  # si ahi algun probmea con eval retornamos un error

                valor_return = eval(valorRecibido)

                # print(valor_return)
                return valor_return
            except Exception as e:
                valor_temp = valorRecibido
                i = 0
                tipo = ''
                while i < len(valorRecibido):
                    if (valorRecibido[i] == '&'):
                        temp_pos = ''  # aqui guardaremos lo que reemplazaremos luego en la cadena
                        temp_pos += valorRecibido[i]
                        variable_temp = ''
                        j = i + 1
                        while valorRecibido[j] != '&':
                            temp_pos += valorRecibido[j]
                            j = j + 1
                        temp_pos += valorRecibido[j]
                        variable_temp = temp_pos.replace("&", "")  # quitamos los anpersant
                        i = i + j + 1
                        if variable_temp.find("[") != -1:

                            variable_temp = variable_temp.replace("]", "")  # si es un arreglo quitamos ]
                            list_variable = variable_temp.split("[")  # como nos queda [ espliteamos por ese
                            var_name = list_variable[0]
                            indice = int(list_variable[1])

                            if var_name in variablesDefinidas.keys():
                                var = variablesDefinidas[var_name]
                                tipo = var[0][0]
                                tamano = var[0][1]
                                valor_lista = var[1]

                                if (indice < tamano):
                                    if (tipo in ("STRING", "INTEGER", "DOUBLE")):

                                        valor_temp = valor_temp.replace(temp_pos, str(valor_lista[indice]))
                                    else:
                                        print(
                                            "Error semantico, operacion no permitida con este tipo de datos " + tipo,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, operacion no permitida con este tipo de datos " + tipo + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:
                                    print("Error semantico, se desbordo el arreglo " + var_name, file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, se desbordo el arreglo " + var_name + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                            else:
                                print("Error semantico, no existe esta variable" + var_name, file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no existe esta variable" + var_name + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:  # es porque es una variable normnal
                            var_name = variable_temp
                            if var_name in variablesDefinidas.keys():
                                var = variablesDefinidas[var_name]
                                tipo = var[0]
                                if (tipo in ("INTEGER", "DOUBLE")):

                                    valor_var = var[1]
                                    valor_temp = valor_temp.replace(temp_pos, str(valor_var))
                                elif tipo == "STRING":
                                    valor_var = var[1]
                                    valor_var = "\"" + valor_var + "\""  # le concatenamos las comillas para que no tengamos problemas al operarlo con eval
                                    valor_temp = valor_temp.replace(temp_pos, str(valor_var))

                                else:
                                    print("Error semantico, operacion no permitida con este tipo de datos " + tipo,
                                          file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, operacion no permitida con este tipo de datos " + tipo + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                            else:
                                print("Error semantico, no existe esta variable " + var_name, file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no existe esta variable " + var_name + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)

                    else:
                        i = i + 1

                try:  # si ahi algun probmea con eval retornamos un error
                    valor_return = eval(valor_temp)

                except Exception as e:
                    print(
                        "Error semantico, no se puede realizar esta operacion compruebe los tipos que esta pasando " + valor_temp,
                        file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error semantico, no se puede realizar esta operacion compruebe los tipos que esta pasando " + valor_temp + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)
                # print(valor_temp)
                # print(valor_return)
                # print(type(valor_return))
                return valor_return

    '''Definir todas las producciones de acuerdo a la estructura de la gramtica
    y de acuerdo a lo establecido en analizador lexico, cada funcion recibe un parametro p,
    el cual corresponde a una regla semantica'''
    def p_bloqueP(self,p):
        # Por convencion de la libreria, se debe tener la misma estructura de las reglas definidas en la gramatica
        # p[0] -> nombreproduccion, p[1] -> token1, p[2] ->  resultado de la produccion
        'bloqueP : declaracionPrincipal bloque'
        # Guardar la regla en una tabla general
        self.tablaDatos = p[2]
        # Se genera el ambiente (nodo) inicial(raiz)
        self.arbolAmbientes.agregarRaiz(self.ambientesG, "ROOT")
        self.algPrincipal(self.tablaDatos, self.vGlobales, self.ambientesG)
        self.terminal.append("Analizado en: "+str(self.tiempoE))
        # Guardar el tiempo de la ejecucion para realizar las posteriores graficas
        self.ctEjecucion[self.contador] = self.tiempoE
        acumular = 0
        for i in self.lMarcadas.values():
            acumular += i
        # Guardar los breakpoint para graficas y otras operaciones
        self.ctEjecucionB[self.contador] = acumular
        exit(0)

    def p_bloque(self,p):
        'bloque : BEGIN bloqueContenido END'
        p[0] = p[2]

    def p_bloqueFuncion(self,p):
        'bloqueFuncion : BEGIN bloqueContenido retorno END'
        p[0] = [p[2], p[3],p.lineno(1)]

    def p_retorno_valor(self,p):
        'retorno : RETURN valor PUNTOCOMA'
        p[0] = ('retorno', p[2], p.lineno(1))

    def p_bloqueContenido_si(self,p):
        'bloqueContenido : si bloqueContenido'
        p[0] = (('si', p[1]), p[2], p.lineno(1))
        # print(p.lineno(1))

    def p_bloqueContenido_para(self,p):
        'bloqueContenido : para bloqueContenido'
        p[0] = (('para', p[1]), p[2], p.lineno(1))

    def p_bloqueContenido_mientras(self,p):
        'bloqueContenido : mientras bloqueContenido'
        p[0] = (('mientras', p[1]), p[2], p.lineno(1))

    def p_bloqueContenido_repeat(self,p):
        'bloqueContenido : repetir bloqueContenido'
        p[0] = (('repetir', p[1]), p[2], p[1][2])  # para que empieze desde el until

    def p_bloqueContenido_escribir(self,p):
        'bloqueContenido : escribir bloqueContenido'
        p[0] = (('escribir', p[1]), p[2], p.lineno(1))

    def p_bloqueContenido_asignar(self,p):
        'bloqueContenido : asignar bloqueContenido'
        p[0] = (('asignar', p[1]), p[2], p.lineno(1))

    def p_bloqueContenido_llamar_procedure(self,p):
        'bloqueContenido : llamarProcedure  bloqueContenido'
        p[0] = (('llamarProcedimiento', p[1]), p[2], p.lineno(1))

    def p_bloqueContenido_empty(self,p):
        'bloqueContenido : empty'
        p[0] = 'omitaBloque'

    def p_escribir(self,p):
        'escribir : WRITELN PA par PC PUNTOCOMA'
        p[0] = p[3]

    def p_para(self,p):
        'para : FOR ID ASIGNACION toFor TO toFor DO bloque'
        p[0] = (p[2], p[4], p[6], p[8])

    def p_to_for_id(self,p):
        'toFor : ID'
        p[0] = "&" + str(p[1]) + "&"

    def p_to_for_integer(self,p):
        'toFor : INTEGERVAL'
        p[0] = str(p[1])

    def p_mientras(self,p):
        'mientras : WHILE PA condicion PC DO bloque'
        p[0] = (p[3], p[6])

    def p_repetir(self,p):
        'repetir : REPEAT bloqueContenido UNTIL PA condicion PC'
        p[0] = (p[5], p[2], p.lineno(3))

    def p_si(self,p):
        'si : IF PA condicion PC THEN bloque sino'
        p[0] = (p[3], p[6], p[7])

    def p_sino_bloq(self,p):
        'sino : ELSE bloque'
        p[0] = p[2]

    def p_sino_empty(self,p):
        'sino : empty'
        p[0] = 'omitaSino'

    # NO SE NECESITA POR EL MOMENTO HACER ALGO SEMANTICO AQUI TAL VEZ

    def p_declaracionPrincipal(self,p):
        'declaracionPrincipal : VAR  declaracion especiales'

    def p_especiales_registro(self,p):
        'especiales : registro especiales'

    def p_especiales_funcion(self,p):
        'especiales : funcion especiales'

    def p_especiales_procedimiento(self,p):
        'especiales : procedimiento especiales'

    def p_parametros_mdoval_id(self,p):
        'parametros : MODOVALOR tipo ID'
        if p[2] == 'ARRAY':
            print("Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista",
                  file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista" + cierreEtiqueta)
            exit(-1)
        p[0] = p[1] + "," + p[2] + "," + p[3]

    def p_parametros_mdoref_id(self,p):
        'parametros : MODOREFERENCIA tipo ID'
        if p[2] == 'ARRAY':
            print("Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista",
                  file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista" + cierreEtiqueta)
            self.reiniciarVariables()
            exit(-1)
        p[0] = p[1] + "," + p[2] + "," + p[3]

    def p_parametros_mdoval_id_parm(self,p):
        'parametros : MODOVALOR tipo ID COMA parametros'
        if p[2] == 'ARRAY':
            print("Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista",
                  file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista" + cierreEtiqueta)
            self.reiniciarVariables()
            exit(-1)
        p[0] = p[1] + "," + p[2] + "," + p[3] + "-" + p[5]

    def p_parametros_mdoref_id_parm(self,p):
        'parametros : MODOREFERENCIA tipo ID COMA parametros'
        if p[2] == 'ARRAY':
            print("Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista",
                  file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Error semantico, no se permiten arreglos como parametros de una funcion, en su lugar use una lista" + cierreEtiqueta)
            self.reiniciarVariables()
            exit(-1)
        p[0] = p[1] + "," + p[2] + "," + p[3] + "-" + p[5]

    def p_funcion(self,p):
        'funcion : FUNCTION ID PA parametros PC bloqueFuncion'
        valor_id = p[2]

        if valor_id in self.vGlobales.keys() or valor_id in self.fUsuario.keys() or valor_id in self.pUsuario or valor_id in self.rUsuario:
            print("Error semantico, usted ya uso este identificador " + valor_id, file=sys.stderr)
            self.terminal.append(etiquetaRoja + "Error semantico, usted ya uso este identificador " + valor_id + cierreEtiqueta)
        else:
            self.fUsuario[valor_id] = (p[4], p[6], p.lineno(1))

    def p_procedimiento(self,p):
        'procedimiento : PROCEDURE ID PA parametros PC bloque'
        valor_id = p[2]

        if valor_id in self.vGlobales.keys() or valor_id in self.fUsuario.keys() or valor_id in self.pUsuario or valor_id in self.rUsuario:
            print("Error semantico, usted ya uso este identificador " + valor_id, file=sys.stderr)
            self.terminal.append(etiquetaRoja + "Error semantico, usted ya uso este identificador " + valor_id + cierreEtiqueta)
        else:
            self.pUsuario[valor_id] = (p[4], p[6], p.lineno(1))

    def p_registro_declar(self,p):
        'registro : RECORD ID BEGIN declaracionReg END'
        valor_id = p[2]

        if valor_id in self.vGlobales.keys() or valor_id in self.fUsuario.keys() or valor_id in self.pUsuario or valor_id in self.rUsuario:
            print("Error semantico, usted ya uso este identificador " + valor_id, file=sys.stderr)
            self.terminal.append(etiquetaRoja + "Error semantico, usted ya uso este identificador " + valor_id + cierreEtiqueta)
        else:
            self.rUsuario[valor_id] = p[4]

    def p_declaracionreg_variablereg(self,p):
        'declaracionReg : variableReg declaracionReg'
        if (p[2] != None):
            p[0] = p[1] + "-" + p[2]
        else:
            p[0] = p[1]

    def p_declaracionreg_empty(self,p):
        'declaracionReg : empty'

    def p_variablereg_tipo(self,p):
        'variableReg : nombresV DOSPUNTOS tipo PUNTOCOMA'
        nombres = p[1] + ":" + p[3]

        p[0] = nombres

    def p_variablereg_array(self,p):
        'variableReg : nombresV DOSPUNTOS tipo ARRAY PUNTOCOMA'
        nombres = p[1] + ":" + p[3] + ",ARRAY"
        p[0] = nombres

    def p_declaracion_variable(self,p):
        'declaracion : variable declaracion'

    def p_declaracion_empty(self,p):
        'declaracion : empty'

    def p_variable_tipo(self,p):
        'variable : nombresV DOSPUNTOS tipo PUNTOCOMA'
        list_variables = p[1].split(",")
        for i in list_variables:
            if i in self.vGlobales:  # recorremos solo las llaves
                print("Error semantico, ya definio previamente la variable " + i, file=sys.stderr)
                self.terminal.append(etiquetaRoja + "Error semantico, ya definio previamente la variable " + i + cierreEtiqueta)
                self.reiniciarVariables()
                exit(1)
            else:
                valor_defect = 0
                if p[3] == 'BOOLEAN':
                    valor_defect = False
                elif p[3] == 'INTEGER':
                    valor_defect = 0
                elif p[3] == 'STRING':
                    valor_defect = ""
                elif p[3] == 'DOUBLE':
                    valor_defect = 0.0
                elif p[3] == 'LIST' or p[3] == 'STACK':
                    valor_defect = []
                    # recordar que se usa es como una pila, o lista pero depende de lcaso
                    # https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks
                elif p[3] == 'QUEUE':
                    valor_defect = queue.deque()

                elif p[3] == 'GRAPH':
                    valor_defect = netx.Graph()  # creamos un grafo

                    # http://networkx.readthedocs.io/en/networkx-1.11/reference/introduction.html

                self.vGlobales[i] = [p[3],
                                         valor_defect]  # guardamos la varaible, donde tenemos el tipo, y el valor p[3] es el tipo

    def p_variable_array(self,p):
        'variable : nombresV DOSPUNTOS tipo ARRAY PUNTOCOMA'
        list_variables = p[1].split(",")
        for i in list_variables:
            if i in self.vGlobales:  # recorremos solo las llaves
                print("Error semantico, ya definidio previamente la variable " + i, file=sys.stderr)
                self.terminal.append(etiquetaRoja + "Error semantico, ya definidio previamente la variable " + i + cierreEtiqueta)
                self.reiniciarVariables()
                exit(1)
            else:
                p[4] = p[4].replace("[", "")
                p[4] = p[4].replace("]", "")
                p[4] = int(p[4])  # indice

                arreglo = []
                for j in range(0, p[4]):
                    arreglo.append(0)
                self.vGlobales[i] = [(p[3], p[4]), arreglo]
                # guardamos la variable, donde tenemos el tipo, y el valor p[3] es el tipo
                # En este caso tenemos que tener cuidado de si lo que ahi dentro es una tupla o no

    def p_nombresV_id(self,p):
        'nombresV : ID'
        p[0] = p[1]

    def p_nombresV_nom(self,p):
        'nombresV : ID COMA nombresV'
        p[0] = p[1] + "," + p[3]

    def p_tipo_integer(self,p):
        'tipo : INTEGER'
        p[0] = p[1]

    def p_tipo_double(self,p):
        'tipo : DOUBLE'
        p[0] = p[1]

    def p_tipo_string(self,p):
        'tipo : STRING'
        p[0] = p[1]

    def p_tipo_boolean(self,p):
        'tipo : BOOLEAN'
        p[0] = p[1]

    def p_tipo_array(self,p):
        'tipo : ARRAY'
        p[0] = p[1]

    def p_tipo_stack(self,p):
        'tipo : STACK'
        p[0] = p[1]

    def p_tipo_queue(self,p):
        'tipo : QUEUE'
        p[0] = p[1]

    def p_tipo_list(self,p):
        'tipo : LIST'
        p[0] = p[1]

    def p_tipo_graph(self,p):
        'tipo : GRAPH'
        p[0] = p[1]

    def p_tipo_id(self,p):  # una variable es de tipo registro
        'tipo : ID'
        p[0] = p[1]

    def p_especiales_empty(self,p):
        'especiales : empty'

    def p_asignar_arregloIdOp(self,p):
        'asignar : arregloID ASIGNACION operacion PUNTOCOMA'
        p[0] = (p[1], p[3])

    def p_asignar_arreglofunction(self,p):
        'asignar : arregloID ASIGNACION llamarFunction PUNTOCOMA'
        p[0] = (p[1], p[3])

    def p_asignar_arregloIdNull(self,p):
        'asignar : arregloID ASIGNACION NULL PUNTOCOMA'
        p[0] = (p[1], 'NULL')

    def p_asignar_record(self,p):
        'asignar : asignacionRecord'
        p[0] = p[1]

    def p_asignacion_record_oper(self,p):
        'asignacionRecord : idRecord ASIGNACION operacion PUNTOCOMA'
        p[0] = (p[1], p[3])

    def p_idRecord_rec(self,p):
        'idRecord : ID PUNTO idRecord2'
        p[0] = p[1] + "." + p[3]

    def p_idRecord2_ID(self,p):
        'idRecord2 : ID'
        p[0] = p[1]

    def p_arregloID_id(self,p):
        'arregloID : ID'
        p[0] = p[1]

    def p_arregloID_array(self,p):
        'arregloID : ID ARRAY'
        var_name = p[1]

        p[2] = p[2].replace("[", "")  # organizamos los valores dentro del arreglo, para obtener el indice
        p[2] = p[2].replace("]", "")
        p[2] = int(p[2])
        indice = p[2]  # sacamos el indice al que se le va asignar algo en el arreglo

        p[0] = (var_name, indice)  # retornamos el indice con la variable

    def p_operacion_par(self,p):
        'operacion : par'
        p[0] = p[1]

    def p_operacion_subarray(self,p):
        'operacion : SUBARRAY'
        p[0] = p[1]

    def p_par_opmath(self,p):
        'par : opmath'
        p[0] = p[1]

    def p_par_parAux(self,p):
        'par : PA par PC parAux'

        p[0] = '(' + str(p[2]) + ')' + str(p[4])

    def p_parAux_mathsymbol(self,p):
        'parAux : mathsymbol par'
        p[0] = p[1] + p[2]

    def p_parAux_empty(self,p):
        'parAux : empty'
        p[0] = ''

    def p_condicion(self,p):
        'condicion : negacion par comparar par continuidad'
        if (p[1] != None):
            if (p[5] != None):
                p[0] = p[1] + "," + p[2] + "," + p[3] + "," + p[4] + "," + p[5]
            else:
                p[0] = p[1] + "," + p[2] + "," + p[3] + "," + p[4]
        else:
            if (p[5] != None):
                p[0] = p[2] + "," + p[3] + "," + p[4] + "," + p[5]
            else:
                p[0] = p[2] + "," + p[3] + "," + p[4]

    def p_continuidad_condicion(self,p):
        'continuidad : oplogico condicion'
        p[0] = p[1] + ',' + p[2]

    def p_continuidad_empty(self,p):
        'continuidad : empty'

    def p_comparar_mayor(self,p):
        'comparar : MAYOR'
        p[0] = '>'

    def p_comparar_menor(self,p):
        'comparar : MENOR'
        p[0] = '<'

    def p_comparar_mayor_igual(self,p):
        'comparar : MAYORIGUAL'
        p[0] = '>='

    def p_comparar_menor_igual(self,p):
        'comparar : MENORIGUAL'
        p[0] = '<='

    def p_comparar_igual(self,p):
        'comparar : IGUAL'
        p[0] = '='

    def p_comparar_diferente(self,p):
        'comparar : DIFERENTE'
        p[0] = '!='

    def p_oplogico_and(self,p):
        'oplogico : AND'
        p[0] = 'and'

    def p_oplogico_or(self,p):
        'oplogico : OR'
        p[0] = 'or'

    def p_negacion_not(self,p):
        'negacion : NOT'
        p[0] = 'not'

    def p_negacion_empty(self,p):
        'negacion : empty'

    def p_opmath_valor(self,p):
        'opmath : valor'
        p[0] = str(p[1])

    def p_opmath_mathsymbol(self,p):
        'opmath : valor mathsymbol par'

        p[0] = str(p[1]) + p[2] + str(p[3])

    def p_mathsymbol_mas(self,p):
        'mathsymbol : MAS'
        p[0] = '+'

    def p_mathsymbol_menos(self,p):
        'mathsymbol : MENOS'
        p[0] = '-'

    def p_mathsymbol_por(self,p):
        'mathsymbol : POR'
        p[0] = '*'

    def p_mathsymbol_dividir(self,p):
        'mathsymbol : DIVIDIR'
        p[0] = '/'

    def p_mathsymbol_div(self,p):
        'mathsymbol : DIV'
        p[0] = '//'

    def p_mathsymbol_mod(self,p):
        'mathsymbol : MOD'
        p[0] = '%'

    def p_techo(self,p):
        'techo : CEIL PA opmath PC'
        p[0] = "math.ceil(" + p[3] + ")"

    def p_piso(self,p):
        'piso : FLOOR PA opmath PC'
        p[0] = "math.floor(" + p[3] + ")"

    def p_valor_arregloid(self,p):
        'valor : arregloID'
        if type(p[1]) == tuple:

            p[0] = "&" + str(p[1][0]) + "[" + str(p[1][1]) + "]&"
        else:
            p[0] = "&" + str(p[1]) + "&"

    def p_valor_integerval(self,p):
        'valor : INTEGERVAL'
        p[0] = p[1]

    def p_valor_doubleval(self,p):
        'valor : DOUBLEVAL'
        p[0] = p[1]

    def p_valor_stringval(self,p):
        'valor : STRINGVAL'
        p[0] = p[1]

    def p_valor_true(self,p):
        'valor : TRUE'
        p[0] = True

    def p_valor_false(self,p):
        'valor : FALSE'
        p[0] = False

    def p_valor_techo(self,p):
        'valor : techo'
        p[0] = p[1]

    def p_valor_piso(self,p):
        'valor : piso'
        p[0] = p[1]

    def p_valor_longitud(self,p):
        'valor : longitud'
        p[0] = p[1]

    def p_valor_conversion_cad(self,p):
        'valor : conversionCad'
        p[0] = p[1]

    def p_conversion_cad(self,p):
        'conversionCad : STR PA opmath PC'
        p[0] = "str(" + p[3] + ")"

    def p_longitud(self,p):
        'longitud : LENGTH PA STRINGVAL PC'
        # p[3] = p[3].replace("\"","")
        p[0] = "" + str(len(p[3]))

    def p_llamar_procedure_valoresCall(self,p):
        'llamarProcedure : CALL PROCEDURE ID PA valoresCall PC PUNTOCOMA'
        p[0] = (p[3], p[5])  # si es una tupla es porque es un llamado a una funcion

    def p_llamar_procedure_vacio(self,p):
        'llamarProcedure : CALL PROCEDURE ID PA error PC PUNTOCOMA'
        print(
            "Errror de Sintaxis, los procedimientos necesitan parametros ya que estos actuan como las variables usadas en el procedimiento",
            file=sys.stderr)
        self.terminal.append(
            etiquetaRoja + "Errror de Sintaxis, los procedimientos necesitan parametros ya que estos actuan como las variables usadas en el procedimiento" + cierreEtiqueta)
        self.reiniciarVariables()
        exit(1)

    def p_llamar_function_valoresCall(self,p):
        'llamarFunction : CALL FUNCTION ID PA valoresCall PC'
        p[0] = (p[3], p[5])  # si es una tupla es porque es un llamado a una funcion

    def p_llamar_function_vacio_error(self,p):
        'llamarFunction : CALL FUNCTION ID PA error PC'
        print(
            "Errror de Sintaxis, las funciones necesitan parametros ya que estos actuan como las variables usadas en la funcion",
            file=sys.stderr)
        self.terminal.append(
            etiquetaRoja + "Errror de Sintaxis, las funciones necesitan parametros ya que estos actuan como las variables usadas en la funcion" + cierreEtiqueta)
        self.reiniciarVariables()
        exit(1)

    def p_valoresCall_valor(self,p):
        'valoresCall : valor'
        if (str(p[1]).find("[") != -1):
            print(
                "Errror de Sintaxis, no es permitido pasar arreglos, con llamado a indice como parametro ",
                file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Errror de Sintaxis, no es permitido pasar arreglos, con llamado a indice como parametro " + cierreEtiqueta)
            self.reiniciarVariables()
            exit(1)
        else:
            p[0] = str(p[1])

    def p_valoresCall_varios(self,p):
        'valoresCall : valor COMA valoresCall'
        if (str(p[1]).find("[") != -1):
            print(
                "Errror de Sintaxis, no es permitido pasar arreglos, con llamado a indice como parametro ",
                file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Errror de Sintaxis, no es permitido pasar arreglos, con llamado a indice como parametro " + cierreEtiqueta)
            self.reiniciarVariables()
            exit(1)
        else:
            p[0] = str(p[1]) + "," + p[3]

    def p_empty(self,p):
        'empty : '
        pass

    def p_longitud_error(self,p):
        'longitud : LENGTH PA error PC'
        print("Tipo de dato invalido, se esperaba una cadena", file=sys.stderr)
        self.terminal.append(etiquetaRoja + "Tipo de dato invalido, se esperaba una cadena" + cierreEtiqueta)

    def p_error(self,p):
        if (p != None):
            print("Errror de Sintaxis en la linea " + str(p.lineno) + " en el token " + str(p.value), file=sys.stderr)
            self.terminal.append(
                etiquetaRoja + "Errror de Sintaxis en la linea " + str(p.lineno) + " en el token " + str(p.value) + cierreEtiqueta)
        else:
            print("Errror de Sintaxis", file=sys.stderr)
            self.terminal.append(etiquetaRoja + "Errror de Sintaxis" + cierreEtiqueta)
        self.reiniciarVariables()
        exit(1)

    '''Algoritmo principal con toda la logica para la ejecucion del aplicativo,
    su funcionamiento se basa en generar tuplas con instrucciones derivadas de 
    una tupla general donde se tienen todas las instrucciones'''
    #def run(self,tabla, variables: {},padre = 0)
    def algPrincipal(self, tablaDatos, variablesEntorno: {}, padreAmbiente=0):
        # avanzar = True # para que lo vuelva true cada ves que dentre a run
        # print(tabla_principal[1])
        # print(len(tabla_principal[0]))
        # print(tabla[1][1])
        # print(len(tabla[1][1][1]))
        # movemos el ambiente
        self.ambiente_actual = padreAmbiente
        print(self.ambiente_actual)


        while self.pasoActual == True:
            x = 1  # esto es para que no me saque error porque el while no tiene nada
        # print("Avanzo") # cuando es false entonces imprime esto y sigue con el proceso

        if (self.detener == True): # detenemos el programa
            self.reiniciarVariables()  # limpiamos variables antes se salir
            exit(1)

        self.pasoActual = True # lo hacemos true para que se detenga en la siguiente ejecucion

        self.vActual = None


        time.sleep(1)
        if type(tablaDatos) == list:
            # area.append("Funcion")
            # mostrar_variables(variables)
            self.algPrincipal(tablaDatos[0], variablesEntorno, self.ambientesG)
            return self.algPrincipal((tablaDatos[1]), variablesEntorno,self.ambientesG)  # retornamos
        else:
            if tablaDatos[0][0] == 'asignar':
                iniciot = time.time()
                self.vActual = variablesEntorno

                #self.mostrar_variables(variables)

                #rint("\nEntro a assig")
                # area.append("Asignar")

                # time.sleep(1)
                asig = tablaDatos[0][1]
                if type(asig[0]) == tuple:  # si es una tupla es porque lo ahi dentro es un diccionario
                    var_name = asig[0][0]
                    if var_name in variablesEntorno.keys():
                        var = variablesEntorno[var_name]

                        var_indice_max = var[0][1]  # tamaño del arreglo
                        var_indice = asig[0][1]
                        if var_indice > var_indice_max:
                            print("Error semantico, se desbordo el arreglo " + var_name, file=sys.stderr)
                            self.terminal.append(etiquetaRoja + "Error semantico, se desbordo el arreglo " + var_name + cierreEtiqueta)
                        else:
                            tipo_var = var[0][0]
                            valor = asig[1]

                            valor = self.convertirVarValor(valor, variablesEntorno,padreAmbiente)  # organizamos el valor
                            tipo_valor = type(valor)
                            tipo_valor = self.tdLenguaje[tipo_valor]
                            if (tipo_valor == tipo_var):
                                var_value = var[1]
                                var_value[var_indice] = valor

                                # print(valor)

                                # print("Asigancion Arreglo : "+str(tabla[2]))
                                self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                                #print(tabla[2])
                                if tablaDatos[2] in self.lMarcadas.keys():
                                    self.lMarcadas[tablaDatos[2]] += 1


                                fint = time.time()
                                #self.tiempito = (fint-iniciot)
                                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                            else:
                                print("Error semantico, no puede asginar a un " + tipo_var + " un " + tipo_valor,
                                      file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no puede asginar a un " + tipo_var + " un " + tipo_valor + cierreEtiqueta)
                                exit(1)
                                # var.insert(var_indice,)

                    else:
                        print("Error semantico, esta variable no existe " + var_name, file=sys.stderr)
                        self.terminal.append(etiquetaRoja + "Error semantico, esta variable no existe " + var_name + cierreEtiqueta)
                else:
                    var_name = asig[0]
                    if var_name in variablesEntorno.keys():
                        var = variablesEntorno[var_name]
                        tipo_var = var[0]
                        if tipo_var in ("INTEGER", "DOUBLE", "STRING"):  # el tipo debe hacer parte de esto

                            valor = asig[1]
                            valor = self.convertirVarValor(valor, variablesEntorno, padreAmbiente)
                            tipo_valor = type(valor)
                            tipo_valor = self.tdLenguaje[tipo_valor]
                            if (tipo_valor == tipo_var):
                                var[1] = valor

                                # print(valor)
                                # print("Asigancion Normal : " + str(tabla[2]))
                                self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                                #print(tabla[2])
                                if tablaDatos[2] in self.lMarcadas.keys():
                                    self.lMarcadas[tablaDatos[2]] += 1

                                fint = time.time()
                                self.tiempoE = (fint - iniciot)
                                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                            else:
                                print("Error semantico, no puede asginar a un " + tipo_var + " un " + tipo_valor,
                                      file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, no puede asginar a un " + tipo_var + " un " + tipo_valor + cierreEtiqueta)
                        else:
                            print("Error semantico, no se puede operar con este tipo de datos " + tipo_var,
                                  file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error semantico, no se puede operar con este tipo de datos " + tipo_var + cierreEtiqueta)
                            exit(1)

            elif tablaDatos[0][0] == 'si':
                iniciot = time.time()
                # area.append("If")
                # mostrar_variables(variables)
                # mostrar_variables(variables)
                # print("entro a un si")
                # print(tabla)   #('si',(condicion,contenidoBloque,sino),contenidoBloque)
                primera_parte_si = tablaDatos[0][1]  # lo que contiene el si (condicion,contenidoBloque,sino)
                # print(primera_parte_si)
                condicion_temp = primera_parte_si[0]  # saco la condicion
                # print(type(condicion_temp))
                cad_eval = self.estructurarCondiciones(condicion_temp, variablesEntorno, padreAmbiente)  # organizo la condicion , para esto agrege una coma en la produccion condicion
                # que deriva en continuidad
                # print(cad_eval)


                result_cond = eval(cad_eval)  # evaluo la cadena y lo guardo el resultado de la condicion
                # print(result_cond)

                if result_cond:  # utilizo la condicion
                    # print("cumple condicion")
                    # print("Sentencia Si: " + str(tabla[2]))
                    self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                    if tablaDatos[2] in self.lMarcadas.keys():
                        self.lMarcadas[tablaDatos[2]] += 1

                    fint = time.time()
                    self.tiempoE = (fint-iniciot)
                    self.algPrincipal(primera_parte_si[1], variablesEntorno, padreAmbiente)  ## ejecuto el metodo con lo que viene dentro del si es decir contenidoBloque
                else:
                    # en caso de que no se cumpla la condicion
                    # print("no cumple condicion")
                    # print("Sentencia Si no: " + str(tabla[2]))
                    fint = time.time()
                    self.tiempoE = (fint - iniciot)
                    self.algPrincipal(primera_parte_si[2], variablesEntorno, padreAmbiente)  ## ejecuto el metodo con lo que tiene el sino contenidoSino

                fint = time.time()
                self.tiempoE = (fint - iniciot)

                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)  ##llamo el metodo con el hermano derecho es decir con el bloqueContenido externo


            elif tablaDatos[0][0] == 'mientras':
                iniciot = time.time()
                # area.append("While")
                # mostrar_variables(variables)
                # mostrar_variables(variables)
                # print("entro a while")
                # print(tabla) #('while',(condicion,bloque dentro del while),bloque despues del while)
                primera_parte_mientras = tablaDatos[0][
                    1]  # obtengo (condicion,bloqueContenidodento del while,bloqueContenido depues while)
                # print(primera_parte_mientras)
                condicion_temp = primera_parte_mientras[0]  # obtengo la condicion
                cad_eval = self.estructurarCondiciones(condicion_temp, variablesEntorno, padreAmbiente)  ## llamo a organizar condicion
                # print(cad_eval)
                result_cond = eval(cad_eval)  # evaluo la condicion
                while result_cond:
                    self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                    if tablaDatos[2] in self.lMarcadas.keys():
                        self.lMarcadas[tablaDatos[2]] += 1
                    self.algPrincipal(primera_parte_mientras[1], variablesEntorno, padreAmbiente)  # ejecuto el metodo con el bloque contenido que esta dentro del while
                    cad_eval = self.estructurarCondiciones(condicion_temp, variablesEntorno, padreAmbiente)  # reorganizo la condicion, funciona como actualizar la condicion
                    # print(cad_eval)
                    result_cond = eval(cad_eval)  # evaluo la condicon que reorganize para que la tome el while
                    # print("Sentencia Mientras: " + str(tabla[2]))

                    # print(variables['i'][1])
                    # print(cad_eval)
                    # result_cond = eval(cad_eval)
                    # print(result_cond)

                fint = time.time()
                self.tiempoE = (fint - iniciot)

                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)
            elif tablaDatos[0][0] == 'para':
                iniciot = time.time()
                # area.append("For")
                # mostrar_variables(variables)
                # print("entro a un para")
                # print(tabla) #('para',(var,inicio,fin,(('asignar',(var,valor),bloquedepues de asignar)),bloque despues de for))
                segunda_parte_para = tablaDatos[0][1]  # (var,inicio,fin,bloquedentro del for)
                # print(segunda_parte_para)
                var_key = segunda_parte_para[0]  # obtengo la variable
                if (var_key in variablesEntorno.keys()):
                    inicio = self.convertirVarValor(segunda_parte_para[1], variablesEntorno, padreAmbiente)  # obtengo el inicio
                    limite = self.convertirVarValor(segunda_parte_para[2], variablesEntorno, padreAmbiente)  # obtengo el fin, lo envaluamos por si nos envian una variable

                    if (type(limite) != int):
                        print("Error semantico, el limite del for debe ser un entero", file=sys.stderr)
                        self.terminal.append(etiquetaRoja + "Error semantico, el limite del for debe ser un entero" + cierreEtiqueta)
                        self.reiniciarVariables()
                        exit(1)

                    # print('inicio : '+str(inicio)+'limite : '+str(limite))

                    # variables[var_key][1] = int(inicio)

                    for i in range(inicio, limite):  # construyo un for desde inicio hasta fin
                        variablesEntorno[var_key][
                            1] = i  # a la variable que va a estar en el for le asigno lo que hay en i para que vaya
                        # cambiando su estado
                        # print("Sentencia Para: " + str(tabla[2]))
                        self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                        if tablaDatos[2] in self.lMarcadas.keys():
                            self.lMarcadas[tablaDatos[2]] += 1
                        # print(variables[var_key])
                        self.algPrincipal(segunda_parte_para[3], variablesEntorno, padreAmbiente)  # ejecuto el metodo con el bloque que esta dentro del for

                    fint = time.time()
                    self.tiempoE = (fint - iniciot)

                    self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)  # ejecuto lo que hay en el bloque despues del for
                else:
                    print("Error semantico, no existe esta variable" + var_key, file=sys.stderr)
                    self.terminal.append(etiquetaRoja + "Error semantico, no existe esta variable" + var_key + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)
                    # print(var)
            elif tablaDatos[0][0] == 'repetir':
                iniciot = time.time()
                # area.append("Repeat")
                # mostrar_variables(variables)
                # (('repetir', ('condicion', bloqueCOntenido_repetir), bloqueContenido_despuesRepetir)
                segunda_parte_repetir = tablaDatos[0][1]
                condicion = segunda_parte_repetir[0]

                self.algPrincipal(segunda_parte_repetir[1], variablesEntorno, padreAmbiente)

                cad_eval = self.estructurarCondiciones(condicion, variablesEntorno, padreAmbiente)
                # print("condicion ---- " + str(cad_eval))

                result_cond = eval(cad_eval)

                while (result_cond):
                    self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                    if tablaDatos[2] in self.lMarcadas.keys():
                        self.lMarcadas[tablaDatos[2]] += 1
                    self.algPrincipal(segunda_parte_repetir[1], variablesEntorno, padreAmbiente)

                    cad_eval = self.estructurarCondiciones(condicion, variablesEntorno, padreAmbiente)
                    # print(cad_eval)
                    result_cond = eval(cad_eval)

                fint = time.time()
                self.tiempoE = (fint - iniciot)

                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

            elif tablaDatos[0][0] == 'escribir':
                iniciot = time.time()
                # ('escribir', '"Hola mundo"'),
                valor = tablaDatos[0][1]
                valor_evaluado = self.convertirVarValor(valor, variablesEntorno, padreAmbiente)
                valor_evaluado = str(valor_evaluado)

                self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                if tablaDatos[2] in self.lMarcadas.keys():
                    self.lMarcadas[tablaDatos[2]] += 1

                #print(">>>> " + valor_evaluado)

                self.terminal.append(etiquetaAzulClaro + "Output" + cierreEtiqueta + etiquetaVerde + valor_evaluado + cierreEtiqueta)
                # print("Sentencia escribir: " + str(tabla[2]))
                fint = time.time()
                self.tiempoE = (fint - iniciot)
                self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)


            elif tablaDatos[0][0] == 'llamarProcedimiento':
                # ('llamarProcedimiento', ('sumatoria', '1,10,&sumRes&')
                # area.append("Procedure")
                # mostrar_variables(variables
                iniciot = time.time()
                variables_procedimientos = {}
                # print(tabla[0])
                nombre_procedure_llamado = tablaDatos[0][1][0]

                parametros_pasados = tablaDatos[0][1][1]

                # print(procedimientos)
                # print("Sentencia call procedure: " + str(tabla[2]))
                self.editor.setCursorPosition(tablaDatos[2] - 1, 0)
                if tablaDatos[2] in self.lMarcadas.keys():
                    self.lMarcadas[tablaDatos[2]] += 1
                self.vActual = variablesEntorno

                #si es un procedimiento reservado
                if nombre_procedure_llamado.upper() in self.ppReservadas:
                    if nombre_procedure_llamado == 'ENQUEUE':
                        cola = ''
                        valor_encolar = ''
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 2:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'QUEUE' and indice == 0):  # ees porque es el primer parametro
                                            cola = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a las colas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a las colas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_encolar = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion de encolar en una variable diferente a una QUEUE",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion de encolar en una variable diferente a una QUEUE" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo QUEUE, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo QUEUE, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_encolar = lista_parametros[m]
                                indice += 1

                            # termino el for
                            # encolamos
                            cola.append(valor_encolar)  # encolamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                        else:
                            print(
                                "Error sintaxicosemantico, la funcion encolar solo recive dos parametros, la cola y el valor a encolar ",
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error sintaxicosemantico, la funcion encolar solo recive dos parametros, la cola y el valor a encolar " + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)
                    elif nombre_procedure_llamado == 'PUSH':
                        pila = ''
                        valor_apilar = ''
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 2:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'STACK' and indice == 0):  # ees porque es el primer parametro
                                            pila = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a las pilas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a las pilas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_apilar = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion push en una variable diferente a una STACK",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion push en una variable diferente a una STACK" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo STACK, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo STACK, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_apilar = lista_parametros[m]
                                indice += 1

                            # termino el for

                            pila.append(valor_apilar)  # apilamos
                            fint = time.time()
                            self.tiempoE = (fint-iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                        else:
                            print(
                                "Error sintaxicosemantico, la funcion push solo recive dos parametros, la pila y el valor a añadir ",
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error sintaxicosemantico, la funcion push solo recive dos parametros, la pila y el valor a añadir " + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)
                    elif nombre_procedure_llamado == 'ADD':
                        lista = ''
                        valor_adicionar = ''
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 2:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'LIST' and indice == 0):  # ees porque es el primer parametro
                                            lista = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a las listas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a las listas solo se les puede insertar tipos primitivos de datos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_adicionar = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion add en una variable diferente a una LIST",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion add en una variable diferente a una LIST" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo LIST, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo LIST, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_adicionar = lista_parametros[m]
                                indice += 1

                            # termino el for
                            lista.append(valor_adicionar)  # adicionamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                        else:
                            print(
                                "Error sintaxicosemantico, la funcion add solo recive dos parametros, la lista y el valor a añadir ",
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error sintaxicosemantico, la funcion add solo recive dos parametros, la lista y el valor a añadir " + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)

                    elif nombre_procedure_llamado == 'REMOVE':
                        lista = ''
                        valor_remover = 0
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 2:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'LIST' and indice == 0):  # ees porque es el primer parametro
                                            lista = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a las listas solo se les puede remover datos de tipo primitivos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a las listas solo se les puede remover datos de tipo primitivos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_remover = temp_var[1]
                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion remove en una variable diferente a una LIST",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion remove en una variable diferente a una LIST" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo LIST, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo LIST, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_remover = lista_parametros[m]
                                indice += 1

                            # termino el for
                            lista.remove(valor_remover)  # adicionamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                        else:
                            print(
                                "Error sintaxicosemantico, la funcion remove solo recive dos parametros, la cola y el valor a encolar ",
                                file=sys.stderr)
                            exit(1)
                    elif nombre_procedure_llamado == 'SORT':
                        lista = ''
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 1:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'LIST' and indice == 0):  # ees porque es el primer parametro
                                            lista = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion sort en una variable diferente a una LIST",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion sort en una variable diferente a una LIST" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo LIST, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            "Error semantico, se esperaba una variable de tipo LIST, no un escalar")
                                        self.reiniciarVariables()
                                        exit(1)
                                indice += 1

                            # termino el for
                            lista.sort()  # adicionamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)

                        else:
                            print(
                                "Error sintaxicosemantico, la funcion sort, solo recibe un parametro que es la lista a ordenar ",
                                file=sys.stderr)
                            self.terminal.append(
                                "Error sintaxicosemantico, la funcion sort, solo recibe un parametro que es la lista a ordenar ")
                            self.reiniciarVariables()
                            exit(1)
                    elif nombre_procedure_llamado == 'ADD_NODE':
                        grafo = ''
                        valor_nodo = 0
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 2:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'GRAPH' and indice == 0):  # ees porque es el primer parametro
                                            grafo = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a los grafos solo se les puede añadir nodos de tipo primitivos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a los grafos solo se les puede añadir nodos de tipo primitivos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_nodo = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion add_node en una variable diferente a un GRPAH",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion add_node en una variable diferente a un GRPAH" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo GRAPH, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo GRAPH, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    else:
                                        valor_nodo = lista_parametros[m]
                                indice += 1

                            # termino el for
                            grafo.add_node(valor_nodo)  # adicionamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)
                        else:
                            print(
                                "Error sintaxicosemantico, la funcion add_node solo recive dos parametros, el grafo y el valor a añadir ",
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error sintaxicosemantico, la funcion add_node solo recive dos parametros, el grafo y el valor a añadir " + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)
                    elif nombre_procedure_llamado == 'ADD_EDGE':
                        grafo = ''
                        valor_nodo_origen = 0
                        valor_nodo_destino = 0
                        valor_nodo_peso = 0.0
                        lista_parametros = parametros_pasados.split(",")
                        # print(lista_parametros)
                        if len(lista_parametros) == 4:
                            indice = 0
                            for m in range(0, len(lista_parametros)):
                                if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                                    temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                                    if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                        temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                        tipo_var = temp_var[0]

                                        if (tipo_var == 'GRAPH' and indice == 0):  # ees porque es el primer parametro
                                            grafo = temp_var[1]
                                        elif indice == 1:  # esporque es el segundo parametro
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a los grafos solo tiene nodos de tipo primitivos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a los grafos solo tiene nodos de tipo primitivos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_nodo_origen = temp_var[1]
                                        elif indice == 2:
                                            if (tipo_var not in self.tdLenguaje.values()):
                                                print(
                                                    "Error semantico, a los grafos solo tiene nodos de tipo primitivos, nada de arreglos o estructuras de datos",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a los grafos solo tiene nodos de tipo primitivos, nada de arreglos o estructuras de datos" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_nodo_destino = temp_var[1]
                                        elif indice == 3:
                                            if (tipo_var == 'DOUBLE'):
                                                print(
                                                    "Error semantico, a los grafos solo puede tener pesos de tipo DOUBLE en las aristas",
                                                    file=sys.stderr)
                                                self.terminal.append(
                                                    etiquetaRoja + "Error semantico, a los grafos solo puede tener pesos de tipo DOUBLE en las aristas" + cierreEtiqueta)
                                                self.reiniciarVariables()
                                                exit(1)
                                            else:
                                                valor_nodo_peso = temp_var[1]

                                        else:
                                            print(
                                                "Error semantico, no se puede realizar una operacion add_edge en una variable diferente a un GRPAH",
                                                file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, no se puede realizar una operacion add_edge en una variable diferente a un GRPAH" + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                    else:
                                        print(
                                            "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                else:  # es porque no es una variable, sino un valor normal

                                    if (indice == 0):
                                        print(
                                            "Error semantico, se esperaba una variable de tipo GRAPH, no un escalar",
                                            file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba una variable de tipo GRAPH, no un escalar" + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                                    elif (indice == 1):
                                        valor_nodo_origen = lista_parametros[m]

                                    elif (indice == 2):
                                        valor_nodo_destino = lista_parametros[m]

                                    elif (indice == 3):
                                        valor_nodo_peso = lista_parametros[m]
                                indice += 1

                            # termino el for
                            grafo.add_edge(valor_nodo_origen, valor_nodo_destino, weight=valor_nodo_peso)  # adicionamos
                            fint = time.time()
                            self.tiempoE = (fint - iniciot)
                            self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)
                        else:
                            print(
                                "Error sintaxicosemantico, la funcion add_trans solo recibe dos parametros, el grafo y el valor a añadir ",
                                file=sys.stderr)
                            self.terminal.append(
                                etiquetaRoja + "Error sintaxicosemantico, la funcion add_trans solo recive dos parametros, el grafo y el valor a añadir " + cierreEtiqueta)
                            self.reiniciarVariables()
                            exit(1)
                #sino, es un procedimiento creado por el usuario
                elif nombre_procedure_llamado in self.pUsuario.keys():  # verificamos si esta en la tabla de procedimientos
                    self.ambientesG += 1
                    iniciot = time.time()
                    # {'sumatoria': ('E,INTEGER,numero1-E,INTEGER,numero2-ES,INTEGER,resultado', (('para', ('numero', 0, 'numero2', (('asignar', ('resultado', '&resultado&+&numero&')), 'omitaBloque'))), 'omitaBloque'))}
                    procedimiento_llamado = self.pUsuario[nombre_procedure_llamado]  # obtenemos el procedimiento
                    parametros_esperado = procedimiento_llamado[0]  # obtenemos los parametros esperados

                    parametros_esperado = parametros_esperado.split('-')  # spliteamos los parametros

                    parametros_esperado_organizado = []
                    for n in parametros_esperado:
                        temp_p = n.split(',')
                        parametros_esperado_organizado.append(temp_p)
                    tabla_procedimiento = procedimiento_llamado[1]
                    lista_parametros = parametros_pasados.split(",")
                    for m in range(0, len(lista_parametros)):
                        if lista_parametros[m].find('&') != -1:  # si la encontro es porque es una variable
                            temp_var_name = lista_parametros[m].replace("&", "")  # quitamos el ampersand
                            if temp_var_name in variablesEntorno.keys():  # si esta en la tabla de variables de contexto
                                temp_var = variablesEntorno[temp_var_name]  # entonces la sacamos

                                if parametros_esperado_organizado[m][
                                    0] == 'E':  # sacamos el tipo de parametros que recibe # sacamos el tipo de parametro que recibe
                                    nombre_variable = parametros_esperado_organizado[m][
                                        2]  # obtenemos el nombre de la variable
                                    tipo_variable = parametros_esperado_organizado[m][
                                        1]  # obtenemos el tipo de variable

                                    if temp_var[0] == tipo_variable:  # si los tipos corresponden
                                        if temp_var[
                                            0] not in self.tdLenguaje.values():  # si es una estructura de datos # miramos si es una estuctura de datos
                                            print(
                                                "Los tipos de estructuras de datos se pasan por referencia")
                                            self.terminal.append(
                                                etiquetaAmarilla + "Los tipos de estructuras de datos se pasan por referencia" + cierreEtiqueta)
                                        variables_procedimientos[nombre_variable] = [tipo_variable, temp_var[1]]  # enviamos la variable
                                    else:
                                        print(
                                            "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                            + " y se encontro con " + str(temp_var[0]), file=sys.stderr)
                                        self.terminal.append(
                                            etiquetaRoja + "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                            + " y se encontro con " + str(temp_var[0]) + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)

                                else:  # por referencia
                                    nombre_variable = parametros_esperado_organizado[m][2]
                                    tipo_variable = parametros_esperado_organizado[m][1]

                                    if temp_var[0] == tipo_variable:
                                        variables_procedimientos[nombre_variable] = temp_var  # enviamos la variable
                                    else:
                                        print(
                                            "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                            + " y se encontro con " + str(temp_var[0]), file=sys.stderr)
                                        self.terminal.append(etiquetaRoja +
                                                        "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                                        + " y se encontro con " + str(temp_var[0]) + cierreEtiqueta)
                                        self.reiniciarVariables()
                                        exit(1)
                            else:
                                print(
                                    "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado,
                                    file=sys.stderr)
                                self.terminal.append(etiquetaRoja +
                                                "Error semantico, esta variable no esta definida en el alcance de este procedimiento " + nombre_procedure_llamado + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)
                        else:
                            if parametros_esperado_organizado[m][0] == 'E':
                                variable_pasada = lista_parametros[m]

                                try:
                                    variable_pasada = eval(variable_pasada)
                                    nombre_variable = parametros_esperado_organizado[m][2]
                                    tipo_variable = parametros_esperado_organizado[m][1]
                                    if (type(variable_pasada) in self.tdLenguaje.keys()):
                                        tipo_variable_pasada = self.tdLenguaje[type(variable_pasada)]
                                        if (tipo_variable_pasada == tipo_variable):
                                            variables_procedimientos[nombre_variable] = [tipo_variable,
                                                                                         variable_pasada]  # creamos una variable
                                        else:
                                            print(
                                                "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                                + " y se encontro con " + str(variable_pasada), file=sys.stderr)
                                            self.terminal.append(
                                                etiquetaRoja + "Error semantico, se esperaba un parametro de tipo  " + tipo_variable + " en el parametro " + nombre_variable
                                                + " y se encontro con " + str(variable_pasada) + cierreEtiqueta)
                                            self.reiniciarVariables()
                                            exit(1)
                                except Exception as e:
                                    print(
                                        "Error semantico, no se permite este tipo de parametros " + variable_pasada + " " + str(
                                            e), file=sys.stderr)
                                    self.terminal.append(
                                        etiquetaRoja + "Error semantico, no se permite este tipo de parametros " + variable_pasada + " " + str(
                                            e) + cierreEtiqueta)
                                    self.reiniciarVariables()
                                    exit(1)
                            else:
                                print("Error semantico, un escalar no se puede pasar por referencia ", file=sys.stderr)
                                self.terminal.append(
                                    etiquetaRoja + "Error semantico, un escalar no se puede pasar por referencia " + cierreEtiqueta)
                                self.reiniciarVariables()
                                exit(1)

                    # print(procedimiento_llamado[1])
                    fint = time.time()
                    self.tiempoE = (fint - iniciot)

                    print("agrego ambiente", self.arbolAmbientes.agregarAmbiente(self.ambientesG, padreAmbiente, "Procedimiento : " + str(
                        nombre_procedure_llamado) + "\nParametros pasados " + str(variables_procedimientos)))

                    print("Ambiente : ", self.ambientesG, " Padre : ", padreAmbiente)

                    self.algPrincipal(procedimiento_llamado[1], variables_procedimientos,self.ambientesG)
                    self.algPrincipal(tablaDatos[1], variablesEntorno, padreAmbiente)  # llamamos lo que sigue
                else:
                    print("Error semantico, Este procedimiento no existe  " + nombre_procedure_llamado, file=sys.stderr)
                    self.terminal.append(
                        etiquetaRoja + "Error semantico, Este procedimiento no existe  " + nombre_procedure_llamado + cierreEtiqueta)
                    self.reiniciarVariables()
                    exit(1)


            elif tablaDatos[0] == 'retorno':  # esto se cumple cuando es una funcion
                # ('retorno', '&n3&')
                iniciot = time.time()
                # print("ENTRO A RETORNO")
                valor = self.convertirVarValor(tablaDatos[1], variablesEntorno, padreAmbiente)
                #self.editor.setCursorPosition(tabla[2] - 1, 0)
                #print(tabla)
                fint = time.time()
                self.tiempoE = (fint - iniciot)
                if tablaDatos[2] in self.lMarcadas.keys():
                    self.lMarcadas[tablaDatos[2]] += 1
                return valor


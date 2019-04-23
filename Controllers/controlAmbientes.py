from Controllers.ambiente import *

# Control del arbol de ambientes, la raiz corresponde al ambiente inicial de ejecucion
class controlAmbientes():
    def __init__(self):
        # La raiz del arbol se toma como el ambiente inicial de la ejecucion
        self.raiz= None

    # Set y Get para la raiz del arbol
    def setRaiz(self,raiz):
        self.raiz=raiz

    def getRaiz(self):
        return self.raiz


    # Agregar hijos en el nivel 0 (raiz) y nivel 1
    def agregarRaiz(self, ambienteN, valor):
        nodoTemporal = ambiente(ambienteN, valor)
        if self.raiz == None:
            self.setRaiz(nodoTemporal)
        else:
            self.getRaiz().agregarNodo(nodoTemporal, valor)

    # Agregar hijos desde el nivel 2 en adelante
    def agregarAmbiente(self,ambienteN, padre, valor):
        if self.getRaiz() == None:
            return False
        nodoTemporal = self.buscarN(padre,self.getRaiz())
        if nodoTemporal != None:
            aux = ambiente(ambienteN,valor)
            nodoTemporal.agregarNodo(aux)
            return True
        return False

    # Buscar nodo en el arbol de ejecucion
    def buscarN(self,nodo,arbol):
        if arbol == None:
            return None
        if arbol.nombre == nodo:
            return arbol
        for i in arbol.hijos:
            aux = self.buscarN(nodo,i)
            if aux != None:
                return  aux
        return None

    # Inicicalizar el recorrer y mostrar el arbol de ejecuciones (ambientes)
    def recorrerArbolE(self):
        return self.recorrerMostrarArbolE(self.getRaiz())

    # Recorrer y mostrar el arbol de ejecuciones (ambientes)
    def recorrerMostrarArbolE(self, arbol):
        if arbol!=None:
            cadena = arbol.nombre+ " "
            for i in arbol.hijos:
                cadena+=self.recorrerMostrarArbolE(i)
            return x
        return ""

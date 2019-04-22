import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as graficar
import numpy as generar

# Graficar los tiempos de ejecucion
class graficosEjecuciones():
    def __init__(self,tiempos,breakpoints):
        # Obtner las ejecuciones realizadas
        self.ejeRealizadas = list(tiempos.keys())
        # Asignar los valores a la coordenada Y, la cual se grafica con la libreria numpy
        coordenadaY = generar.arange(len(self.ejeRealizadas))
        # Obtner una copia de los parametros recibidos
        self.tiemposT = list(tiempos.values())
        self.breakpointsT = list(breakpoints.values())
        # Estilo con el cual se realizaran las graficas
        graficar.style.use("ggplot")
        # Inicializacion de la grafica 1
        graficar.subplot(1,2,1)
        # Indicar que se hace uso de un grafico de barras
        graficar.barh(coordenadaY, self.tiemposT, align="center")
        # Valores limite de cada coordenada
        graficar.yticks(coordenadaY, self.ejeRealizadas)
        # Nombre de la coordenada x grafica 1
        graficar.xlabel("Tiempo")
        # Titulo de la grafica 1
        graficar.title("Tiempos de ejecución")
        # Inicializacion de la grafica 2
        graficar.subplot(1,2,2)
        # Titulo de la grafica 2
        graficar.title("Tiempos teóricos")
        # Nombre de la coordenada x grafica 2
        graficar.xlabel("Tiempos reales")
        # Nombre de la coordenada y grafica 2
        graficar.ylabel("Tiempos teóricos")
        # Valores de la coordenada x grafica 2
        valorX = generar.array(self.tiemposT)
        # Valores de la coordenada y grafica 2
        valorY = generar.array(self.breakpointsT)
        # Graficar cada coordenada en la grafica 2
        graficar.plot(valorX,valorY)
        # Mostrar las graficas de los tiempos
        graficar.show()

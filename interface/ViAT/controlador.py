# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:36:21 2020

@author: veroh
"""

#from Modelo import Biosenal
from vista import ViAT
import sys
from PyQt5.QtWidgets import QApplication
#%%
"""
Esta clase lleva a cabo la ejecucin del programa
"""
class Principal(object):
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=ViAT()
#        self.__mi_biosenal=Biosenal()
#        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
#        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())
#%%
"""
Esta clase realiza el enlace entre los 3 cdigos para el correcto funcionamiento del programa
"""
#class Coordinador(object):
#    def __init__(self,vista,biosenal):
#        self.__mi_vista=vista
#        self.__mi_biosenal=biosenal
#    def recibirDatosSenal(self,data):
#        self.__mi_biosenal.asignarDatos(data)
#    def devolverDatosSenal(self,x_min,x_max):
#        return self.__mi_biosenal.devolver_segmento(x_min,x_max)
#    def escalarSenal(self,x_min,x_max,escala):
#        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala)

# Se ejecuta el programa   
p=Principal()
p.main()
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:36:21 2020

@author: veroh
"""

from view import ViAT
import sys
from PyQt5.QtWidgets import QApplication,QScrollArea
from model import Model
#%%
class Principal(object):
    def __init__(self):  
#        scroll_area = QScrollArea()
        self.__app=QApplication(sys.argv)
        self.__view=ViAT()
        self.sistema = Model();
        self.mi_coordinador = Controller(self.__view,self.sistema)
        self.__view.asignarControlador(self.mi_coordinador);
    def main(self):
        self.__view.show()
        sys.exit(self.__app.exec_())


class Controller(object):
    def __init__(self, view, sistema):
        self.__view = view;
        self.sistema = sistema;
        
    def detectarDispositivo(self):
        return self.sistema.puertos(); 

    def crearCarpeta(self,codigo,nombre,apellidos,estatura,peso,observaciones):
        self.sistema.crearCarpeta(codigo,nombre,apellidos,estatura,peso,observaciones)
        
#    def guardar_datos(self,codigo,nombre,apellidos,estatura,peso,observaciones):
#        self.base_datos.guardado(codigo,nombre,apellidos,estatura,peso,observaciones)
        
        
    def returnLastData(self):
        return self.sistema.returnLastData();
    
    def startData(self):
        self.sistema.startData();
    
    def stopData(self):
        self.sistema.stopData();
        print('Stop Data Controlador')
    

        
#%%
if __name__ == "__main__":
    controller = Principal();
    controller.main();
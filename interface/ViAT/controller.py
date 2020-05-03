# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:36:21 2020

@author: veroh
"""

from view import ViAT
import sys
from PyQt5.QtWidgets import QApplication, QScrollArea
from model import Model
import os
# %%


class Principal(object):
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__view = ViAT()
        self.system = Model()
        self.my_controller = Controller(self.__view, self.system)
        self.__view.assignController(self.my_controller)

    def main(self):
        self.__view.show()
        sys.exit(self.__app.exec_())


class Controller(object):
    def __init__(self, view, system):
        self.__view = view
        self.system = system

    def detectarDispositivo(self):
        return self.system.puertos()

    def crearCarpeta(self, codigo, nombre, apellidos, estatura, peso, observaciones):
        self.system.crearCarpeta(
            codigo, nombre, apellidos, estatura, peso, observaciones)

    def returnLastData(self):
        return self.system.returnLastData()
    
    def returnLastZ(self):
        return self.system.returnLastZ()
    
    def startDevice(self):
        self.system.startDevice()

    def startData(self):
        self.system.startData()

    def stopData(self):
        self.system.stopData()
        print('Stop Data Controlador')

    def startZ(self):
        self.system.startZ()

    def stopZ(self):
        self.system.stopZ()
        print('Stop Z Controlador')


# %%
if __name__ == "__main__":
#    os.system("randData.py")
    controller = Principal()
    controller.main()

# -*- coding: utf-8 -*-
"""
Created on 2020

@author: Verónica Henao Isaza
"""

from view import ViAT
import sys
from PyQt5.QtWidgets import QApplication, QScrollArea
from model import Model
import os

from sys import argv
from sys import exit
from PyQt5.QtWidgets import QApplication

from view import DataBase
from view import LoadRegistration

# In[]
class Principal(object):
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.__view = ViAT()
        self.system = Model("ViAT","subject")
        self.my_controller = Controller(self.__view, self.system)
        self.__controlador = Controlador(self.__view, self.system)
        self.__view.assignController(self.my_controller)
        self.__view.asignar_controlador(self.__controlador)
    def main(self):
        self.__view.show()
        sys.exit(self.__app.exec_())


class Controller(object):
    def __init__(self, view, system):
        self.__view = view
        self.system = system
  
    def returnLastData(self):
        return self.system.returnLastData()
    
    def returnLastZ(self):
        return self.system.returnLastZ()
    
    def returnLastStimulus(self):
        return self.system.returnLastStimulus()
       
    def startDevice(self):
        self.system.startDevice()

    def startData(self):
        self.system.startData()

    def stopData(self):
        self.system.stopData()
        print('Stop Data Controlador')
    
    def stopDevice(self):
        self.system.stopDevice()
        print('Stop Device Controlador')

    def startZ(self):
        self.system.startZ()

    def stopZ(self):
        self.system.stopZ()
        print('Stop Z Controlador')
    
    def startStimulus(self):
        self.system.startStimulus()

    def stopStimulus(self):
        self.system.stopStimulus()
        
# In[]
class Controlador:
    def __init__(self, view,system):
        self.__view = view
        self.system = system
   
    def mostrar(self, controlador):
        self.integrantes= DataBase()
        self.integrantes.asignar_controlador(controlador)
        self.integrantes.show()
    
    def agregar_datos(self, datos):
        return self.system.add_into_collection_one(datos)
           
    def obtener_integrantes(self):
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_many({}, proj)
    
    def buscar_integrantes(self, buscar):
        consult = {"cc":{"$regex": buscar}}
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_many(consult, proj)
    
    def obtener_uno(self, buscar):
        consult = {"cc":buscar}
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_one(consult, proj)
    
    def borrar(self, dato):
        consult = {"cc": dato}
        self.system.delete_data(consult)
        
    
        
        
        

# %%
if __name__ == "__main__":
#    os.system("randData.py")
    controller = Principal()
    controller.main()

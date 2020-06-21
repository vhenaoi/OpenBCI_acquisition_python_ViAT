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
import subprocess


# In[]
class Principal(object):
    def __init__(self):
        cmd = r'C:\Program Files\MongoDB\Server\4.2\bin\mongod.exe'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=0x08000000)
        process.wait()
        self.__app = QApplication(sys.argv)
        self.__view = ViAT()
        self.system = Model("ViAT","subject")
        self.my_controller = Controller(self.__view, self.system)
        self.__controlador = Controlador(self.__view, self.system)
        self.__view.assignController(self.my_controller)
        self.__view.assign_controller(self.__controlador)
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
        
    def defineLocation(self):
        self.system.defineLocation()
        
    def laplace_controller(self,laplace1,laplace2,laplace3):
        self.system.laplace(laplace1,laplace2,laplace3)
        
    def ReceiveData(self,data):
        self.system.init_assign_data(data)
        
    def returnDataSenal(self,x_min,x_max):
        return self.system.return_segment(x_min,x_max)
    
    def scaleSignal(self,x_min,x_max,escala):
        return self.system.signal_scale(x_min,x_max,escala)
        
# In[]
class Controlador:
    def __init__(self, view,system):
        self.__view = view
        self.system = system
   
    def see(self, controlador):
        self.integrantes= DataBase()
        self.integrantes.assign_controller(controlador)
        self.integrantes.show()
    
    def add_data(self, datos):
        return self.system.add_into_collection_one(datos)
           
    def get_integrants(self):
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_many({}, proj)
    
    def search_integrantes(self, buscar):
        consult = {"cc":{"$regex": buscar}}
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_many(consult, proj)
    
    def get_one(self, buscar):
        consult = {"cc":buscar}
        proj = {"_id":0, "d":1,"nombre":1,"apellidos":1, "cc":1, "sexo":1,
                "dominante":1,"gafas":1,"snellen":1,"corregida":1,
                "estimulo":1,"edad":1,"tiempo":1,"rp":1,"ubicacion":1}
        return self.system.search_one(consult, proj)
    
    def delete(self, dato):
        consult = {"cc": dato}
        self.system.delete_data(consult)
        
    
        
        
        

# %%
if __name__ == "__main__":
#    os.system("randData.py")
    controller = Principal()
    controller.main()

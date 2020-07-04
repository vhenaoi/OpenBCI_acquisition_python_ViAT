# -*- coding: utf-8 -*-
"""
Created on 2020

@author: Verónica Henao Isaza
"""
from PyQt5.QtWidgets import QApplication
import sys

from view import ViAT
from model import Model
import subprocess

# from PySide2 import QtWidgets
# from PySide2 import QtCore
# from PySide2 import QtGui
# from PySide2.QtUiTools import QUiLoader
# from PySide2.QtWidgets import QApplication
# from PySide2.QtCore import QFile, QIODevice

# In[]


class Principal(object):
    '''
    It determines what processes the model must perform when the user interacts
    with the system, and then communicates the results to the eye. It simply 
    takes an order from the view and sends it to the controller, so the 
    functions in this module refer to the same functions that are in the model.
    The controller is made up of 3 classes:
        • Main: Start the MongoDB database server in an application thread, 
        start the application and define the variables of the view and 
        the model. Enter the view and model to each of the controllers and 
        assign the controllers to use in the view.
        • Controller: Manages all the functions related to the data received
        from the device and the signals graphed on the interface.
        • Controller: Manages all the functions related to the subjects 
        database and the interaction with MongoDB.
    '''

    def __init__(self):
        cmd = r'C:\Program Files\MongoDB\Server\4.2\bin\mongod.exe'
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, creationflags=0x08000000)
        process.wait()
        self.__app = QApplication(sys.argv)
        self.__view = ViAT()
        self.system = Model("ViAT", "subject")
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

    def stopDevice(self):
        self.system.stopDevice()
        print('Stop Device Controlador')

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

    def startStimulus(self):
        self.system.startStimulus()

    def stopStimulus(self):
        self.system.stopStimulus()

    def newLocation(self, location):
        self.system.newLocation(location)

    def location(self):
        return self.system.location()

    def laplace_controller(self, laplace1, laplace2, laplace3):
        self.system.laplace(laplace1, laplace2, laplace3)


# In[]
class Controlador:
    def __init__(self, view, system):
        self.__view = view
        self.system = system

    def add_data(self, datos):
        return self.system.add_into_collection_one(datos)

    def get_integrants(self):
        proj = {"_id": 0, "d": 1, "nombre": 1, "apellidos": 1, "cc": 1, "sexo": 1,
                "dominante": 1, "gafas": 1, "snellen": 1, "corregida": 1,
                "estimulo": 1, "edad": 1, "tiempo": 1, "rp": 1, "ubicacion": 1}
        return self.system.search_many({}, proj)

    def search_integrantes(self, buscar):
        consult = {"cc": {"$regex": buscar}}
        proj = {"_id": 0, "d": 1, "nombre": 1, "apellidos": 1, "cc": 1, "sexo": 1,
                "dominante": 1, "gafas": 1, "snellen": 1, "corregida": 1,
                "estimulo": 1, "edad": 1, "tiempo": 1, "rp": 1, "ubicacion": 1}
        return self.system.search_many(consult, proj)

    def get_one(self, buscar):
        consult = {"cc": buscar}
        proj = {"_id": 0, "d": 1, "nombre": 1, "apellidos": 1, "cc": 1, "sexo": 1,
                "dominante": 1, "gafas": 1, "snellen": 1, "corregida": 1,
                "estimulo": 1, "edad": 1, "tiempo": 1, "rp": 1, "ubicacion": 1}
        return self.system.search_one(consult, proj)

    def delete(self, dato):
        consult = {"cc": dato}
        self.system.delete_data(consult)

    def ReceiveData(self, data):
        self.system.assign_data(data)

    def returnDataSenal(self, x_min, x_max):
        return self.system.return_segment(x_min, x_max)

    def scaleSignal(self, x_min, x_max, escala):
        return self.system.signal_scale(x_min, x_max, escala)

    def file_location(self, i, cc):
        return self.system.file_location(i, cc)


# %%
if __name__ == "__main__":
    # os.system("randData.py")
    controller = Principal()
    controller.main()

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


    def clinicalhistoryInformation(self,idAnswer,nameAnswer,lastnameAnswer,ccAnswer,sexAnswer,
                     eyeAnswer,ageAnswer,glassesAnswer,snellenAnswer,
                     CorrectionAnswer,stimulusAnswer,timeAnswer,responsibleAnswer):
        self.system.clinicalhistoryInformation(idAnswer,nameAnswer,lastnameAnswer,ccAnswer,
                                 sexAnswer,eyeAnswer,ageAnswer,glassesAnswer,
                                 snellenAnswer,CorrectionAnswer,stimulusAnswer,
                                 timeAnswer,responsibleAnswer)
    def webclinicalhistoryInformation(self):
        self.system.webclinicalhistoryInformation()
        
    def searchClinicalhistory(self):
        self.system.searchClinicalhistory()
    
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
        
    
        
        
        

# %%
if __name__ == "__main__":
#    os.system("randData.py")
    controller = Principal()
    controller.main()

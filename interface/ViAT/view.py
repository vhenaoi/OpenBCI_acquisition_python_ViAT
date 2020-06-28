'''View ViAT
Created on 2020

@author: Verónica Henao Isaza

WorkerSignals: Defines the signals available from a running worker thread.
    
Worker: Inherits from QRunnable to handler worker thread setup,
        signals and wrap-up.
    
    By: https://www.learnpyqt.com/courses/concurrent-execution
    /multithreading-pyqt-applications-qthreadpool/
    
    
ViAT: Initial user view, allows you to record or view patient data
    
LoadRegistration: View of the data required by each patient
    
DataAcquisition: Visualization of the electrode configuration, the impedance of
                 each one and the verification of connected devices.
    
AcquisitionSignal: It allows to acquire the signal and the mark, under visual 
                    stimulation
    
DataBase: Allows you to view current information in the database

'''

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QMessageBox, QDialog
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QProgressBar, QPushButton, QLCDNumber
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.Qt import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import scipy.io as sio
import numpy as np
from scipy.signal import welch
import pandas as pd
import wmi
from Stimulation_Acuity import Stimulus
from randData import RandData
import os
import pygame
import time
import traceback
import sys
from pylsl import StreamInfo, StreamOutlet
from pylsl import StreamInlet, resolve_stream
from datetime import datetime
import csv
import subprocess
import errno
import pyqtgraph as pg
from datetime import datetime
import random

#from PySide2 import QtWidgets 
#from PySide2 import QtCore 
#from PySide2 import QtGui 
#from PySide2.QtUiTools import QUiLoader
#from PySide2.QtWidgets import QApplication
#from PySide2.QtCore import QFile, QIODevice
# In[]
class WorkerSignals(QObject):
    '''
    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal() # with no data to indicate when the task is complete
    error = pyqtSignal(tuple) # which receives a tuple of Exception type, 
                              # Exception value and formatted traceback.
    result = pyqtSignal(object) # receiving any object type from the executed function.
    progress = pyqtSignal(int)

# In[]
class Worker(QRunnable):
    '''
    Worker thread

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()  # Done

# In[]
class ViAT(QtWidgets.QMainWindow):
    '''First user view
    
    Load a .ui type view designed in Qt designer
    
    :setup: this function contains the condition to move to the other views
    '''
    def __init__(self):
        super(ViAT, self).__init__()
        #The designed view is exported in qt designer
        loadUi('ViAT.ui', self)
#        QFile("ViAT.ui")
        self.setWindowTitle('Inicio')
        self.setWindowIcon(QtGui.QIcon('icono.png')) #window icon
        self.setup() 
        self.show()

    def assignController(self, controller):
        # create connection to controller
        self.my_controller = controller
        
    def assign_controller(self, controlador):
        self.__controlador = controlador

    def setup(self):
        self.startRegistration.clicked.connect(self.loadRegistration)
        self.patientData.clicked.connect(self.loadData)
        self.exit.clicked.connect(self.end)
        pixmap = QtGui.QPixmap('Logo.png')
        self.logo.setPixmap(pixmap)

    def loadRegistration(self):
        self.__registry = LoadRegistration(self,self.__controlador,self.my_controller)
        self.__registry.show()
        self.hide()

    def loadData(self):
        self.__registry = DataBase(self,self.__controlador,self.my_controller)
        self.__registry.show()
        self.hide()

    def end(self):
        self.hide()
        exit()

# In[]
class LoadRegistration(QtWidgets.QDialog):
    def __init__(self, LR, controlador , controller):
        super(LoadRegistration, self).__init__()
        loadUi("Agregardatos.ui", self)
#        QFile("Agregardatos.ui")
        self.setup()
        self.setWindowTitle('Base de datos')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.__parentLoadRegistration = LR
        self.__controlador = controlador
        self.my_controller = controller
        self.__loc = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
#        self.__loc = os.getcwd()
        
    def setup(self):
        self.btn_search.clicked.connect(self.find)
        self.btn_add.clicked.connect(self.add)
        self.btn_show.clicked.connect(self.see)
        self.back.clicked.connect(self.loadStart)
        self.next.clicked.connect(self.dataAcquisition)
        self.btn_update.clicked.connect(self.upgrade)
        self.btn_update.setEnabled(False)
        self.next.setEnabled(False)
        self.save.clicked.connect(self.location)
        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        pixmap2 = QtGui.QPixmap('save.png')
        self.savelogo.setPixmap(pixmap2)
        self.snellen.setPlaceholderText("20/20")
        self.correction.setPlaceholderText("NaN")
        self.time.setPlaceholderText("NaN")
        
    def assign_controller(self, controlador):
        self.__controlador = controlador
        
    def location(self):
        self.my_controller.defineLocation()
    
    def upgrade(self):
        if not (self.d.text() and self.nombre.text() and
                self.apellidos.text() and self.cc.text() and 
                self.snellen.text() and self.correction.text()  and 
                self.edad.text() and self.time.text() and self.rp.text()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Todos los campos deben estar diligenciados")
            msg.setWindowTitle("Alerta!")
            x = msg.exec_()
        else:
            if self.sexo.currentIndex() == 0:
                self.sex = 'Femenino'
            else:
                self.sex = 'Masculino'
            if self.dominante.currentIndex() == 0:
                self.domi = 'Derecho'
            else:
                self.domi = 'Izquierdo'
            if self.glasses.currentIndex() == 0:
                self.glass = 'No'
            else:
                self.glass = 'Si'
            if self.stimulus.currentIndex() == 0:
                self.stimu = 'Vernier'
            else:
                 self.stimu = 'Grating'
            data = {
                    "d":self.d.text(),
        			"nombre":self.nombre.text(),
        			"apellidos": self.apellidos.text(),
        			"cc":self.cc.text(),
                    "sexo":(self.sex),
                    "dominante":(self.domi),
        			"gafas":(self.glass),
        			"snellen":(self.snellen.text()),
        			"corregida":(self.correction.text()),
        			"estimulo":(self.stimu),
        			"edad":(self.edad.text()),
        			"tiempo":(self.time.text()),
        			"rp":(self.rp.text()),
                    "ubicacion":(str(self.__loc))
                    }
    
            band = self.__controlador.add_data(data)
            if band == True:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Información Actualizada")
                msg.show()
            self.activate()
    def deactivate(self):
       self.nombre.setEnabled(False)
       self.apellidos.setEnabled(False)
       self.d.setEnabled(False)
       self.cc.setEnabled(False)
       self.sexo.setEnabled(False)
       self.dominante.setEnabled(False)
       self.btn_search.setEnabled(False)
       self.btn_update.setEnabled(True)
       

        
    def find(self):
        find = self.cc.text()
        result = self.__controlador.get_one(find)
        if result != False:
            self.show_info(result)
            self.deactivate()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Información no encontrada")
            msg.show()
            
            self.activate()
        self.next.setEnabled(True)
            
    def activate(self):
        self.nombre.setEnabled(True)
        self.apellidos.setEnabled(True)
        self.cc.setEnabled(True)
        self.sexo.setEnabled(True)
        self.d.setEnabled(True)
        self.dominante.setEnabled(True)
        self.glasses.setEnabled(True)
        self.snellen.setEnabled(True)
        self.correction.setEnabled(True)
        self.stimulus.setEnabled(True)
        self.edad.setEnabled(True)
        self.time.setEnabled(True)
        self.rp.setEnabled(True)
        self.btn_add.setEnabled(True)
        self.d.setText("")
        self.nombre.setText("")
        self.apellidos.setText("")
        self.cc.setText("")
        self.cc.setText("")
        self.snellen.setPlaceholderText("20/20")
        self.snellen.setText("")
        self.correction.setPlaceholderText("NaN")
        self.correction.setText("")
        self.edad.setText("")
        self.time.setPlaceholderText("NaN")
        self.time.setText("")
        self.rp.setText("")
    
    def show_info(self, result):
        info = result
        print(info)
        self.d.setText(info[0])
        self.nombre.setText(info[1])
        self.apellidos.setText(str(info[2]))
        self.cc.setText(str(info[3]))
        if str(info[4]) == 'Femenino':
            self.sexo.setCurrentIndex(0)
        else:
            self.sexo.setCurrentIndex(1)
        if str(info[5]) == 'Derecho':
            self.dominante.setCurrentIndex(0) 
        else:
            self.dominante.setCurrentIndex(1)
        if str(info[6]) == 'Si':
            self.glasses.setCurrentIndex(1)
        else:
            self.glasses.setCurrentIndex(0)
        self.snellen.setText(str(info[7]))
        self.correction.setText(str(info[8]))
        if str(info[9]) == 'Vernier':
            self.stimulus.setCurrentIndex(0)     
        self.edad.setText(str(info[10]))
        self.time.setText(str(info[11]))
        self.rp.setText(str(info[12]))
        self.btn_add.setEnabled(False)
            
    def add(self):
        if not (self.d.text() and self.nombre.text() and
                self.apellidos.text() and self.cc.text() and 
                self.snellen.text() and self.correction.text()  and 
                self.edad.text() and self.time.text() and self.rp.text()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Todos los campos deben estar diligenciados")
            msg.setWindowTitle("Alerta!")
            x = msg.exec_()
        else:
            if self.sexo.currentIndex() == 0:
                self.sex = 'Femenino'
            else:
                self.sex = 'Masculino'
            if self.dominante.currentIndex() == 0:
                self.domi = 'Derecho'
            else:
                self.domi = 'Izquierdo'
            if self.glasses.currentIndex() == 0:
                self.glass = 'No'
            else:
                self.glass = 'Si'
            if self.stimulus.currentIndex() == 0:
                self.stimu = 'Vernier'
            else:
                 self.stimu = 'Grating'
            data = {
                "d":self.d.text(),
    			"nombre":self.nombre.text(),
    			"apellidos": self.apellidos.text(),
    			"cc":self.cc.text(),
                "sexo":(self.sex),
                "dominante":(self.domi),
    			"gafas":(self.glass),
    			"snellen":(self.snellen.text()),
    			"corregida":(self.correction.text()),
    			"estimulo":(self.stimu),
    			"edad":(self.edad.text()),
    			"tiempo":(self.time.text()),
    			"rp":(self.rp.text()),
                "ubicacion":(str(self.__loc))
                }

            
            band = self.__controlador.add_data(data)
            if band == True:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Información Agregada")
                msg.show()
            self.activate()
        self.next.setEnabled(True)
        
    def see(self):
            self.__registry = DataBase(self,self.__controlador,self.my_controller)
            self.__registry.show()
            self.hide()
        
    def loadStart(self):
        self.__parentLoadRegistration.show()
        self.hide()

    def dataAcquisition(self):
        self.__registry = DataAcquisition(self, self.my_controller)
        self.__registry.show()
        self.hide()

# In[]
class DataAcquisition(QtWidgets.QMainWindow):
    '''Electrodes and devices
    
        Verify that the application can continue with the registration
    
        :setup: This function allows to:
                1. Initiate communication with OpenBCI
                2. Verify the existence of a second connected display 
                to show stimulation
                3. Observe the impedance at each electrode
                
        :param variable controller: allows me to communicate with the model 
        through the controller
    '''
    #Contains restrictions to follow the actions in an orderly manner
    def __init__(self, DA, controller):
        super(DataAcquisition, self).__init__()
        #The designed view is exported in qt designer
        loadUi('Adquisicion.ui', self)
#        QFile('Adquisicion.ui')
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.__parentDataAcquisition = DA
        self.threadpool = QThreadPool() #creating a group of threads in qt
        self.my_controller = controller

    def setup(self):
        self.back.clicked.connect(self.loadStart)
        self.infoAdquisition.clicked.connect(self.info)
        self.next.setEnabled(False)
        self.StopZ.setEnabled(False)
        self.detectDevice.setEnabled(False)
        self.startDevice.clicked.connect(self.Startdevice)
        self.FCz.setEnabled(False)
        self.Oz.setEnabled(False)
        self.O1.setEnabled(False)
        self.PO7.setEnabled(False)
        self.O2.setEnabled(False)
        self.PO8.setEnabled(False)
        self.PO3.setEnabled(False)
        self.PO4.setEnabled(False)
        self.GND.clicked.connect(self.startMeasurement)
        self.REF.clicked.connect(self.startMeasurement)
        self.FCz.clicked.connect(self.startMeasurement)
        self.PO3.clicked.connect(self.startMeasurement)
        self.PO4.clicked.connect(self.startMeasurement)
        self.PO7.clicked.connect(self.startMeasurement)
        self.PO8.clicked.connect(self.startMeasurement)
        self.O1.clicked.connect(self.startMeasurement)
        self.O2.clicked.connect(self.startMeasurement)
        self.Oz.clicked.connect(self.startMeasurement)
        
        pixmap = QtGui.QPixmap('M.png')
        self.mounting.setPixmap(pixmap)
        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        
    def info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Comience identificando que el dispositivo esta conectado y que puede comenzar a adquirir los datos, se abrirá una ventana negra en la cual se muestran los datos adquiridos, presione 'Miminizar' y a continuación verifique que la pantalla de estimulación se encuentra conectada y ahora, para verificar la impedancia presione cualquiera de los electrodos de la configuración. Antes de pasar a la siguiente etapa recuerde detener la medición de la impedancia ")
        msg.setWindowTitle("Ayuda")
        x = msg.exec_()
        
    def loadStart(self):
        self.__parentDataAcquisition.show()
        self.hide()

    def executeAcquisition(self):
        self.next.setEnabled(False) #Revisar genera delay
        self.__registry = AcquisitionSignal(self, self.my_controller)
        self.__registry.show()
        self.hide()
        
        
    def returnLastZ(self):
        return self.my_controller.returnLastZ()

    def startMeasurement(self):
        self.my_controller.startZ()
        self.StopZ.setEnabled(True)
        self.StopZ.clicked.connect(self.StopMeasurement)
        
        print("Iniciar medicion")
        self.timer = QtCore.QTimer(self) #creating a time thread
        self.timer.timeout.connect(self.printZ)
        self.timer.start(22)  # speed in milliseconds discriminated by human eye


    def fGND(self):
        self.GND.setEnabled(False)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Verifique la conexion del electrodo")
        msg.setWindowTitle("Alerta!")
        x = msg.exec_()

    def fREF(self):
        self.REF.setEnabled(False)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Verifique la conexion del electrodo")
        msg.setWindowTitle("Alerta!")
        x = msg.exec_()
        
    def printZ(self):
        Z = self.returnLastZ()
        self.impedanceFCZ.display(Z[0])
        self.impedanceOZ.display(Z[1])
        self.impedanceO1.display(Z[2])
        self.impedancePO7.display(Z[3])
        self.impedanceO2.display(Z[4])
        self.impedancePO8.display(Z[5])
        self.impedancePO3.display(Z[6])
        self.impedancePO4.display(Z[7])
    
    def StopMeasurement(self):
        self.timer.stop()
        self.my_controller.stopZ()
        print("detener impedancia")
        self.next.setEnabled(True)
        self.next.clicked.connect(self.executeAcquisition)

    def Startdevice(self):
        #use worker function explained at startup
        self.worker = Worker(self.execute_this_fn)
        self.worker.signals.result.connect(self.print_output)  # s
        self.worker.signals.finished.connect(self.thread_complete)
        self.worker.signals.progress.connect(self.progress_fn)  # n
        # Execute
        self.threadpool.start(self.worker)
        
        
        self.detectDevice.setEnabled(True)
        self.startDevice.setEnabled(False)
        self.detectDevice.clicked.connect(self.device)
        
    def device(self):
       
        self.FCz.setEnabled(True)
        self.Oz.setEnabled(True)
        self.O1.setEnabled(True)
        self.PO7.setEnabled(True)
        self.O2.setEnabled(True)
        self.PO8.setEnabled(True)
        self.PO3.setEnabled(True)
        self.PO4.setEnabled(True)
        self.my_controller.startData()

        ##Allows to detect if there is a second screen connected
#        obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)
#        displays = [x for x in obj if 'DISPLAY' in str(x)]
#        num=len(displays)
#        if num==3:
#            self.next.setEnabled(True)
#            self.next.clicked.connect(self.executeAcquisition)
#        else:
#            msg = QMessageBox()
#            msg.setIcon(QMessageBox.Warning)
#            msg.setText("Debe conectar una segunda pantalla para poder iniciar la adquisición")
#            msg.setWindowTitle("Alerta!")
#            num=0
#            x = msg.exec_()
        self.detectDevice.setEnabled(False)
       
    def progress_fn(self, n):
        pass

    def execute_this_fn(self, progress_callback):
        self.my_controller.startDevice()
        

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

# In[]
class AcquisitionSignal(QtWidgets.QMainWindow):
    '''
        This module allows to start the visual stimulation, and allows 
        to visualize the acquired signals in real time.

        It is divided into two sections:
        
        1. The first view allows you to start and restart the stimulus. 
        Disconnecting the device will observe the results of the subject 
        that has been registered
        2. The second part only allows to view the signals in real time
    
        :param variable controller: allows me to communicate with the model 
        through the controller    
    '''
    def __init__(self, AS, controller):
        super(AcquisitionSignal, self).__init__()
        #The designed view is exported in qt designer
        loadUi('Adquisicion_accion.ui', self)
#        QFile('Adquisicion_accion.ui')
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.counter = 0
        self.__parentAcquisitionSignal = AS
        self.threadpool = QThreadPool() #creating a group of threads in qt
        print("Multithreading with maximum %d threads" %
        self.threadpool.maxThreadCount())
        self.timer = QTimer()  #creating a time thread
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.my_controller = controller
        self.step = 0
        

    def setup(self):
        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        self.play.clicked.connect(self.startPlay)
        self.stop.setEnabled(False)
#        self.patientData.clicked.connect(self.loadData)
        self.back.clicked.connect(self.loadStart)
        self.exit.clicked.connect(self.end)
        self.playGraph.clicked.connect(self.startGraph)
        self.stopGraph.clicked.connect(self.haltGraph)
        self.adquisitionInfo.clicked.connect(self.info)
        self.stopDevice.clicked.connect(self.stopProcess)
        self.display.clicked.connect(self.displaysignal)
    
    def closeData(self,data):
        data.close()
        
        
    def info(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("En la parte superior encontrara dos pestañas, la de inicio, en la que se encuentra actualmente y la de visualización, en la cual podra observar la señal adquirida en tiempo real. Primero debe presionar el botón inicio en la pestaña actual, luego, pase a la pestaña de visualización y presione 'visualiza', en la primera pestaña podra observar una barra de proceso que le anunciara que el estimulo esta a punto de presentarse. Al terminar podra visualizar los resultados de la estimulación en esta misma pestaña, para visualizar resultados anteriores o de otro pacientes, dirijase a 'Base de datos pacientes'  ")
        msg.setWindowTitle("Ayuda")
        x = msg.exec_()

    def startPlay(self):
        self.ban = True
        self.stop.setEnabled(True)
        self.stop.clicked.connect(self.stopEnd)
        self.play.setEnabled(False)
        try:
            pygame.init()
            # Any other args, kwargs are passed to the run function
            self.worker = Worker(self.execute_this_fn)
            self.play.setEnabled(False)
            pygame.quit()
            self.worker.signals.result.connect(self.print_output)  # s
            self.worker.signals.finished.connect(self.thread_complete)
            self.worker.signals.progress.connect(self.progress_fn)  # n
            # Execute
            self.threadpool.start(self.worker)
        except:
            pygame.quit()

    def progress_fn(self, n):
        pass


    def execute_this_fn(self, progress_callback):
        veces=0
        while veces<10 and self.ban is True:
            time.sleep(veces) #increment one second when entering while
            value = self.alert.value()
            if value < 100:
                value = value + 10 #progress bar
                self.alert.setValue(value)
            else:
                self.timer.stop()
            veces=veces+1
#        time.sleep(15)  # if the while is not used for the progress bar
        if self.ban is True:
            self.my_controller.startStimulus()
            self.my_controller.stopStimulus()
        else:
            pass


    
    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("COMPLETE!")

    def stopEnd(self):#Reset
        self.play.setEnabled(True)
        pygame.quit()
        self.alert.setValue(0)

    def loadData(self):
        self.__registry = DataBase(self,self.__controlador,self.my_controller)
        self.__registry.show()
        self.hide()

    def loadStart(self):
        self.__parentAcquisitionSignal.show()
        self.hide()
    
    def end(self):
        self.hide()
        exit()

    def recurring_timer(self):
        pass

    def returnLastData(self):
        return self.my_controller.returnLastData()
    
    def stopProcess(self):
        self.my_controller.stopDevice()   
    
    def graphData(self):
        ''' This function allows to graph and save the registry data
            data arrives from the model, where it is acquired by the device 
            and configured, passes through the controller before reaching the view
            The date is also saved to have control of the acquisition and to
            be able to carry out the processing with the marks associated with the stimulus.
        '''
        if self.welch.currentIndex() == 0:
            c = 0
            pen=('#208A8A')
        elif self.welch.currentIndex() == 1:
            c = 1
            pen=('#CD10B4')
        elif self.welch.currentIndex() == 2:
            c = 2
            pen=('#1014CD')
        elif self.welch.currentIndex() == 3:
            c = 3
            pen=('#10CD14')
        elif self.welch.currentIndex() == 4:
            c = 4
            pen=('#F7FB24')
        elif self.welch.currentIndex() == 5:
            c = 5
            pen=('#FBB324')
        elif self.welch.currentIndex() == 6:
            c = 6
            pen=('#E53923')
        else:
            c = 7
            pen=('#806123')
        
        self.my_controller.laplace_controller(self.laplace1.currentIndex(),self.laplace2.currentIndex(),self.laplace3.currentIndex())
        data, Powers, freq, laplace, Plaplace, flaplace = self.returnLastData()
       
        data = data - np.mean(data, 0)
        if data.ndim == 0:
            print("Lista vacia")
            return
        self.welchPlot.clear()
        self.welchPlot.plot(x=freq,y=Powers[c,:],pen=pen)
        self.welchPlot.repaint()
        self.welchLaplace.clear()
        self.welchLaplace.plot(x=flaplace,y=Plaplace[0,:], pen=('#0D6B9D'))
        self.welchLaplace.repaint()
        self.viewSignalOz.clear()
        self.viewSignalOz.plot(np.round(data[1, :], 1), pen=('#CD10B4'))
        self.viewSignalOz.repaint()
        self.viewSignalO1.clear()
        self.viewSignalO1.plot(np.round(data[2, :], 1), pen=('#1014CD'))
        self.viewSignalO1.repaint()
        self.viewSignalPO7.clear()
        self.viewSignalPO7.plot(np.round(data[3, :], 1), pen=('#10CD14'))
        self.viewSignalPO7.repaint()
        self.viewSignalO2.clear()
        self.viewSignalO2.plot(np.round(data[4, :], 1), pen=('#F7FB24'))
        self.viewSignalO2.repaint()
        self.viewSignalPO8.clear()
        self.viewSignalPO8.plot(np.round(data[5, :], 1), pen=('#FBB324'))
        self.viewSignalPO8.repaint()
        self.viewSignalPO3.clear()
        self.viewSignalPO3.plot(np.round(data[6, :], 1), pen=('#E53923'))
        self.viewSignalPO3.repaint()
        self.viewSignalPO4.clear()
        self.viewSignalPO4.plot(np.round(data[7, :], 1), pen=('#806123'))
        self.viewSignalPO4.repaint()


    def startGraph(self):
        '''
        call the data in the controller
        '''
        self.my_controller.startData()
        self.stopDevice.setEnabled(False)

        print("Iniciar senal")
        self.timer = QtCore.QTimer(self)
        # timer.setSingleShot(True)
        self.timer.timeout.connect(self.graphData)
        self.timer.start(22)  # milisegundos ojo humano
        # print(self.timer.isActive())

    def haltGraph(self):
        self.timer.stop()
        self.ban = False 
        self.my_controller.stopData()
        self.stopDevice.setEnabled(True)
        print("detener senal")
        
        
    def displaysignal(self):
        self.__registry = GraphicalInterface(self,self.__controlador, self.my_controller)
        self.__registry.show()
        self.hide()
        
    
# In[]
        
class DataBase(QDialog):
    def __init__(self, DB,controlador , controller):
        super(DataBase, self).__init__()
        loadUi("Buscardatos.ui", self)
#        QFile("Buscardatos.ui")
        self.setWindowTitle('Base de datos')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.setup_TreeWidget()
        self.__parentDataBase = DB
        self.__controlador = controlador
        self.my_controller = controller
        
    def setup_TreeWidget(self):
    		self.table.setStyleSheet('Background-color:rgba(255, 215, 255,20);')
    		self.table.setColumnWidth(0, 150)
    		self.table.setColumnWidth(1, 110)
    		self.table.setColumnWidth(2, 110)
    		self.table.setColumnWidth(3, 110)
    		self.table.setColumnWidth(4, 110)
    		self.table.setColumnWidth(5, 110)
            
    def assign_controller(self, controlador):
        self.__controlador = controlador
    
    def setup(self):
        self.line_search.setPlaceholderText("Cedula del sujeto")
        self.btn_show.clicked.connect(self.show_everything)
        self.btn_search.clicked.connect(self.find)
        self.table.itemDoubleClicked.connect(self.dbclick)
        self.back.clicked.connect(self.loadStart)
        self.display.clicked.connect(self.displaysignal)

        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        
    def show_everything(self):
        results = self.__controlador.get_integrants()
        self.see(results)
        
            
    def find(self):
    		find = self.line_search.text()
    		self.line_search.setText("")
    		self.line_search.setPlaceholderText("Cedula del sujeto")
    		results = self.__controlador.search_integrantes(find)
    		self.see(results)
            
    def see(self, results):
        self.table.clear()
        for result in results:
            item = QTreeWidgetItem(self.table)
            for i in range(14):
                item.setText(i,str(result[i]))
                        
    def dbclick(self):
        if self.options.currentIndex() == 0:
            data = self.table.currentItem()
            buttonReply = QMessageBox.question(self, 'Borrar información', 
    			u"¿Desea eliminar a %s de la lista de sujetos?"%data.text(0), 
    			QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.__controlador.delete(data.text(0))
                self.show_everything()
            if buttonReply == QMessageBox.No:
                pass
            if buttonReply == QMessageBox.Cancel:
                pass
        else:
            data = self.table.currentItem()
            buttonReply = QMessageBox.question(self, 'Buscar información',
                u"¿Desea ir a la ubicación del registro de %s?"%data.text(0),
                QMessageBox.Yes | QMessageBox.No)
            path = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
            path = os.path.realpath(path)
            if buttonReply == QMessageBox.Yes:
                os.startfile(path)
            if buttonReply == QMessageBox.No:
                pass
            if buttonReply == QMessageBox.Cancel:
                pass

    def loadStart(self):
        self.__parentDataBase.show()
        self.hide()
    
    def displaysignal(self):
        self.__registry = GraphicalInterface(self,self.__controlador)
        self.__registry.show()
        self.hide()
        
    	
# In[]

class GraphicalInterface(QtWidgets.QMainWindow):
    def __init__(self, IG, controlador):
        super(GraphicalInterface,self).__init__(IG)
        loadUi ('visualizacion.ui',self)
        self.setup()
        self.show()
        
        self.__x_min=0
        self.__x_max=0
        self.setWindowTitle('Visualización')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup_TreeWidget()
        self.__parentGraphicInterface = IG
        self.__controlador = controlador
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup(self): 
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.campo_grafico.setLayout(layout)
#        self.campo_grafico.setCentralWidget(layout)
        
        self.btn_load.clicked.connect(self.load_signal)
        self.btn_ahead.clicked.connect(self.forward_signal)
        self.btn_behind.clicked.connect(self.delay_signal)
        self.btn_increase.clicked.connect(self.increase_signal)
        self.btn_decrease.clicked.connect(self.decrease_signal)    
        self.btn_leave.clicked.connect(self.toclose)
        self.btn_ahead.setEnabled(False)
        self.btn_behind.setEnabled(False)
        self.btn_increase.setEnabled(False)
        self.btn_decrease.setEnabled(False)
        self.line_search.setPlaceholderText("Cedula del sujeto")
        self.btn_search.clicked.connect(self.find)
        self.table.itemDoubleClicked.connect(self.dbclick)
        self.back.clicked.connect(self.loadStart)
        self.btn_show.clicked.connect(self.show_everything)

        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
                 
        
    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t,s)
    # Mtodo para graficar la seal
    def graph_data(self,datos):
        # Se limpia el campo donde se grafica la seal para evitar que queden superpuestas 
        self.ax.cla()
#        self.figure = plt.figure()
#        self.canvas = FigureCanvas(self.figure)
#        self.ax = self.figure.add_subplot(111)
#        layout = QVBoxLayout()
#        layout.addWidget(self.canvas)
#        self.campo_grafico.setLayout(layout)
        
        print(datos.shape)
        for c in range(datos.shape[0]):
            self.ax.plot(datos[c,:]+c*10)
        self.ax.set_xlabel("Muestras")
        self.ax.set_ylabel("Voltaje (uV)")
        self.ax.set_title('Registro EEG - Visualización ViAT')
        
        self.canvas.draw()
    def setup_TreeWidget(self):
    		self.table.setStyleSheet('Background-color:rgba(255, 215, 255,20);')
    		self.table.setColumnWidth(0, 150)
    		self.table.setColumnWidth(1, 110)
    		self.table.setColumnWidth(2, 110)
    		self.table.setColumnWidth(3, 110)
    		self.table.setColumnWidth(4, 110)
    		self.table.setColumnWidth(5, 110)    
    # Mtodo para cerrar el programa
    def toclose(self):
        self.close()
    # Asignacin de controlador para hacer la conexin en el modelo MVC
    def assign_controller(self,controlador):
        self.__controlador=controlador
    # Mtodo para adelantar la seal un segundo en el tiempo. Esto corresponde a 2000 puntos en la seal
    def forward_signal(self):
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000
        self.graph_data(self.__controlador.returnDataSenal(self.__x_min,self.__x_max))
    # Mtodo para atrasar la seal un segundo en el tiempo. Esto corresponde a 2000 puntos en la seal
    def delay_signal(self):
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.graph_data(self.__controlador.returnDataSenal(self.__x_min,self.__x_max))
    # Mtodo para aumentar la amplitud de la seal
    def increase_signal(self):
        self.graph_data(self.__controlador.scaleSignal(self.__x_min,self.__x_max,2))
    # Mtodo para disminuir la amplitud de la seal
    def decrease_signal(self):
        self.graph_data(self.__controlador.scaleSignal(self.__x_min,self.__x_max,0.5))
    # Mtodo de cargar la seal a la vista
    def load_signal(self):
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir seal","","Todos los archivos (*);;Archivos csv (*.csv)*")
        if archivo_cargado != "":
            d = pd.read_csv(archivo_cargado, header=None)
#            d = pd.read_csv(archivo_cargado,';')
#            d = d.drop([9], axis=1)
#            d = d.drop([0], axis=1)
#            d = d.drop([0], axis=0)
            d = d.values
            d = d[0:8,:]*100000
            d[1] = d[1,:] - d[0,:]
            d[2] = d[2,:] - d[0,:]
            d[3] = d[3,:] - d[0,:]
            d[4] = d[4,:] - d[0,:]
            d[5] = d[5,:] - d[0,:]
            d[6] = d[6,:] - d[0,:]
            d[7] = d[7,:] - d[0,:]
            print(d.size/250)
            senal_continua = d
            self.__senal=senal_continua
            self.__controlador.ReceiveData(senal_continua)
            self.__x_min=0
            self.__x_max=2000
            self.graph_data(self.__controlador.returnDataSenal(self.__x_min,self.__x_max))
            self.btn_ahead.setEnabled(True)
            self.btn_behind.setEnabled(True)
            self.btn_increase.setEnabled(True)
            self.btn_decrease.setEnabled(True)
            
    def show_everything(self):
        results = self.__controlador.get_integrants()
        self.see(results)
        
            
    def find(self):
    		find = self.line_search.text()
    		self.line_search.setText("")
    		self.line_search.setPlaceholderText("Cedula del sujeto")
    		results = self.__controlador.search_integrantes(find)
    		self.see(results)
            
    def see(self, results):
        self.table.clear()
        for result in results:
            item = QTreeWidgetItem(self.table)
            for i in range(14):
                item.setText(i,str(result[i]))
                        
    def dbclick(self):
            data = self.table.currentItem()
            buttonReply = QMessageBox.question(self, 'Buscar información',
                u"¿Desea ir a la ubicación del registro de %s?"%data.text(0),
                QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                path = self.__controlador.file_location(data.text(0),data.text(3))
                archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir senal", path,"Todos los archivos (*);;Archivos csv (*.csv)*")
                if archivo_cargado != "":
                    d = pd.read_csv(archivo_cargado, header=None)
#                    d = pd.read_csv(archivo_cargado,';')
#                    d = d.T
#                    d = d.drop([9], axis=1)
#                    d = d.drop([0], axis=1)
#                    d = d.drop('Unnamed: 0', axis=0)
                    d = d.values
                    d = d[0:8,:]*100000
                    d[1] = d[1,:] - d[0,:]
                    d[2] = d[2,:] - d[0,:]
                    d[3] = d[3,:] - d[0,:]
                    d[4] = d[4,:] - d[0,:]
                    d[5] = d[5,:] - d[0,:]
                    d[6] = d[6,:] - d[0,:]
                    d[7] = d[7,:] - d[0,:]
                    print(d.size/250)
                    senal_continua = d
                    self.__senal=senal_continua
                    self.__controlador.ReceiveData(senal_continua)
                    self.__x_min=0
                    self.__x_max=2000
                    self.graph_data(self.__controlador.returnDataSenal(self.__x_min,self.__x_max))
                    self.btn_ahead.setEnabled(True)
                    self.btn_behind.setEnabled(True)
                    self.btn_increase.setEnabled(True)
                    self.btn_decrease.setEnabled(True)
            if buttonReply == QMessageBox.No:
                pass
            if buttonReply == QMessageBox.Cancel:
                pass

    def loadStart(self):
        self.__parentGraphicInterface.show()
        self.hide()
        

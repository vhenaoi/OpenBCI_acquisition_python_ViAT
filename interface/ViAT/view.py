from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QMessageBox, QDialog
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy.io as sio
import numpy as np
from scipy.signal import welch
import pandas as pd 
from PyQt5.QtGui import QIcon, QPixmap
import wmi
from Stimulation_Acuity import Stimulus
import os
from PyQt5.QtWidgets import QWidget, QProgressBar, QPushButton, QApplication, QLCDNumber
from PyQt5.QtCore import QBasicTimer
import pygame
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from impedance import Impedance

import time
import traceback, sys

import pygame
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from datetime import datetime
import csv

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)    
class Worker(QRunnable):
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
            self.signals.result.emit(result)# Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class ViAT(QMainWindow):
    def __init__(self):
        super(ViAT,self).__init__()
        loadUi ('ViAT.ui',self)
        self.setWindowTitle('Inicio')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
    
    def asignarControlador(self,controlador):
        self.mi_controlador = controlador;
        
        
    def setup(self):
        self.startRegistration.clicked.connect(self.loadRegistration)
        self.patientData.clicked.connect(self.loadData)
        self.exitStar.clicked.connect(self.end)
        pixmap = QPixmap('Logo.png')
        self.logo.setPixmap(pixmap)
    def loadRegistration(self):
        self.__registry=LoadRegistration(self,self.mi_controlador)
        self.__registry.show()
        self.hide()
    def loadData(self):
        self.__registry=DataBase(self)
        self.__registry.show()
        self.hide()
    def end(self):
        pass

class LoadRegistration(QMainWindow):
    def __init__(self,LR,controlador):
        super(LoadRegistration,self).__init__()
        loadUi ('Registro-HistoriaClinica.ui',self)
        self.setWindowTitle('Registro')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
        self.mi_controlador = controlador
        
        self.__parentLoadRegistration = LR
    def setup(self):
        self.back.clicked.connect(self.loadStart)
        self.next.clicked.connect(self.dataAcquisition)
        pixmap = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap)
    def clinicalhistoryInformation(self):
        pass
    def loadStart(self):
        self.__parentLoadRegistration.show()
        self.hide()
#    def dataAcquisition(self):
#        msg = QMessageBox(self.LoadRegistration)
#        pass
#    def dataAcquisition(self):
#        self.__registry=DataAcquisition(self)
#        self.__registry.show()
#        self.hide()
    def dataAcquisition(self):
#        if not (self.idAnswer.text() and self.nameAnswer.text() and
#                self.lastnameAnswer.text() and self.responsibleAnswer.text() and self.ccAnswer.text()):
#            msg = QMessageBox()
#            msg.setIcon(QMessageBox.Warning)
#            msg.setText("Todos los campos marcados con * deben estar diligenciados")
#            msg.setWindowTitle("Alerta!")
#            x = msg.exec_()
#        else:
        self.__registry=DataAcquisition(self,self.mi_controlador)
        self.__registry.show()
        self.hide()

class DataAcquisition(QMainWindow):
    def __init__(self, DA,controlador):
        super(DataAcquisition,self).__init__()
        loadUi ('Adquisicion.ui',self)
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()        
        self.__parentDataAcquisition = DA
        self.z()
        self.impedanceFCZ.display(self.S[1][0])
        self.impedanceOZ.display(self.S[1][1])
        self.impedanceO1.display(self.S[1][2])
        self.impedancePO7.display(self.S[1][3])
        self.impedanceO2.display(self.S[1][4])
        self.impedancePO8.display(self.S[1][5])
        self.impedancePO3.display(self.S[1][6])
        self.impedancePO4.display(self.S[1][7])
        self.mi_controlador = controlador

        
    def setup(self):
        self.back.clicked.connect(self.loadStart)
        self.next.setEnabled(False)
        self.detectDevice.clicked.connect(self.device)
        self.FCz.setEnabled(False)
        self.Oz.setEnabled(False)
        self.O1.setEnabled(False)
        self.PO7.setEnabled(False)
        self.O2.setEnabled(False)
        self.PO8.setEnabled(False)
        self.PO3.setEnabled(False)
        self.PO4.setEnabled(False)
        self.GND.clicked.connect(self.fGND)
        self.REF.clicked.connect(self.fREF)
        self.FCz.clicked.connect(self.fFCz)
        self.PO3.clicked.connect(self.fPO3)
        self.PO4.clicked.connect(self.fPO4)
        self.PO7.clicked.connect(self.fPO7)
        self.PO8.clicked.connect(self.fPO8)
        self.O1.clicked.connect(self.fO1)
        self.O2.clicked.connect(self.fO2)
        self.Oz.clicked.connect(self.fOz)
        
        pixmap = QPixmap('M.png')
        self.mounting.setPixmap(pixmap)
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
    
    def z(self):
        Z = Impedance()
        self.S = Z.sample()
                 
    def loadStart(self):
        self.__parentDataAcquisition.show()
        self.hide()
    def executeAcquisition(self):
        self.__registry=AcquisitionSignal(self,self.mi_controlador)
        self.__registry.show()
        self.hide() 
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
    def fFCz(self):
        #GRAY
        self.z()
#        self.FCz.setEnabled(False)
        self.impedanceFCZ.display(self.S[1][0]) 
    def fOz(self):
        #PURPLE
        self.z()
#        self.Oz.setEnabled(False)
        self.impedanceOZ.display(self.S[1][1])
    def fO1(self):
        #BLUE
        self.z()
#        self.O1.setEnabled(False)
        self.impedanceO1.display(self.S[1][2])
    def fPO7(self):
        #GREEN
        self.z()
#        self.PO7.setEnabled(False)
        self.impedancePO7.display(self.S[1][3])
    def fO2(self):
        #YELLOW
        self.z()
#        self.O2.setEnabled(False)
        self.impedanceO2.display(self.S[1][4])
    def fPO8(self):
        #ORANGE
        self.z()
#        self.PO8.setEnabled(False)
        self.impedancePO8.display(self.S[1][5])
    def fPO3(self):
        #RED
        self.z()
#        self.PO3.setEnabled(False)
        self.impedancePO3.display(self.S[1][6]) 
    def fPO4(self):
        #BROWN
        self.z()
#        self.PO4.setEnabled(False)
        self.impedancePO4.display(self.S[1][7])  
   
          
    def device(self):
        self.FCz.setEnabled(True)
        self.Oz.setEnabled(True)
        self.O1.setEnabled(True)
        self.PO7.setEnabled(True)
        self.O2.setEnabled(True)
        self.PO8.setEnabled(True)
        self.PO3.setEnabled(True)
        self.PO4.setEnabled(True)
        self.next.setEnabled(True)
        self.next.clicked.connect(self.executeAcquisition)
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
                 #Necesito un WHILE   

#        from PyQt5.QtWidgets import QMessageBox
#        detectado = self.mi_controlador.detectarDispositivo();
#        if (detectado):
#            msg = QMessageBox(self.ventana_principal)
#            msg.setIcon(QMessageBox.Information)
#            msg.setText("El dispositivo ha sido detectado")
#            msg.setWindowTitle("Información")
#            msg.show()
            
        self.detectDevice.setEnabled(True)
            
#        else:
#            msg = QMessageBox(self.ventana_principal)
#            msg.setIcon(QMessageBox.Warning)
#            msg.setText("El dispositivo no ha sido detectado o no se encuentra conectado")
#            msg.setWindowTitle("Alerta!")
#            msg.show()
#            self.boton_iniciar.setEnabled(False)

class AcquisitionSignal(QMainWindow):
    def __init__(self, AS,controlador):
        super(AcquisitionSignal,self).__init__()
        loadUi ('Adquisicion_accion.ui',self)
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
#        self.step = 0
        self.counter = 0
        self.__parentAcquisitionSignal = AS
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.mi_controlador = controlador

    def setup(self):
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        self.play.clicked.connect(self.startPlay)
        self.stop.clicked.connect(self.stopEnd)
        self.patientData.clicked.connect(self.loadData)
        self.back.clicked.connect(self.loadStart)
        self.exitStar.clicked.connect(self.end)
        self.playGraph.clicked.connect(self.starGraph)
        self.stopGraph.clicked.connect(self.haltGraph)
    def startPlay(self):
        self.play.setEnabled(False)
        try:
            pygame.init()
            self.worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
            self.play.setEnabled(False)
            pygame.quit()
            self.worker.signals.result.connect(self.print_output)#s
            self.worker.signals.finished.connect(self.thread_complete)
            self.worker.signals.progress.connect(self.progress_fn)#n
            # Execute
            self.threadpool.start(self.worker)
        except:
            pygame.quit()
        
    def progress_fn(self, n):
        pass

    def execute_this_fn(self, progress_callback):
        estimulo = Stimulus()       
        estimulo.starStimulus()
 
    def print_output(self,s):
        print(s)
    
        
    def thread_complete(self):
        print("THREAD COMPLETE!")
    def stopEnd(self):
        self.play.setEnabled(True)
        pygame.quit()
#        self.threadpool.destroyed
    def loadData(self):
        self.__registry=DataBase(self)
        self.__registry.show()
        self.hide()
    def loadStart(self):
        self.__parentAcquisitionSignal.show()
        self.hide()
    def end(self):
        pass
    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.play.setText('Iniciar')
            return
        self.step +=1
        self.alert.setValue(self.step)
    def recurring_timer(self):
        pass
       
    def returnLastData(self):
        return self.mi_controlador.returnLastData();
    
    def graphData(self):
        data,Powers,freq = self.returnLastData();
        data = data - np.mean(data,0);
        if data.ndim == 0:
            print("Lista vacia")
            return
#        self.viewSignalFCz.clear();
#        self.viewSignalFCz.plot(np.round(data[0,:],1),pen=('silver'))
#        self.viewSignalFCz.repaint();
        self.viewSignalOz.clear();
        self.viewSignalOz.plot(np.round(data[0,:],1),pen=('#CD10B4'))
        self.viewSignalOz.repaint();
        self.viewSignalO1.clear();
        self.viewSignalO1.plot(np.round(data[0,:],2),pen=('#1014CD'))
        self.viewSignalO1.repaint();
        self.viewSignalPO7.clear();
        self.viewSignalPO7.plot(np.round(data[0,:],3),pen=('#10CD14'))
        self.viewSignalPO7.repaint();
        self.viewSignalO2.clear();
        self.viewSignalO2.plot(np.round(data[0,:],4),pen=('#F7FB24'))
        self.viewSignalO2.repaint();
        self.viewSignalPO8.clear();
        self.viewSignalPO8.plot(np.round(data[0,:],5),pen=('#FBB324'))
        self.viewSignalPO8.repaint();
        self.viewSignalPO4.clear();
        self.viewSignalPO4.plot(np.round(data[0,:],6),pen=('#806123'))
        self.viewSignalPO4.repaint();
        self.viewSignalPO3.clear();
        self.viewSignalPO3.plot(np.round(data[0,:],7),pen=('#E53923'))
        self.viewSignalPO3.repaint();

    def starGraph(self):
        self.mi_controlador.startData()

        print("Iniciar senal")
        self.timer = QtCore.QTimer(self);
        #timer.setSingleShot(True)
        self.timer.timeout.connect(self.graphData)
        self.timer.start(22)#milisegundos ojo humano
        #print(self.timer.isActive())      
    
    def haltGraph(self):
        self.timer.stop()
        self.mi_controlador.stopData();
        print("detener senal")        

        
        
    

class DataBase(QMainWindow):
    def __init__(self, DB):
        super(DataBase,self).__init__()
        loadUi ('Adquisicion_datos.ui',self)
        self.setWindowTitle('Base de datos')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
#        self.__controller = c
        self.__parentDataBase = DB
    def setup(self):
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        self.behind.clicked.connect(self.delaySignal)
        self.before.clicked.connect(self.forwardSignal)
        self.patientAcquisition.clicked.connect(self.dataAcquisition)
        self.back.clicked.connect(self.loadStart)
        self.exitStar.clicked.connect(self.end)
    def delaySignal(self):
        pass
    def forwardSignal(self):
        pass
    def dataAcquisition(self):
        self.__registry=DataAcquisition(self)
        self.__registry.show()
        self.hide()
    def loadStart(self):
        self.__parentDataBase.show()
        self.hide()
    def end(self):
        pass

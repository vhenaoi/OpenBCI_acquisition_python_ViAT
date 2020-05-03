'''View ViAT

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
#from Server import Server
from randData import RandData
import os
from PyQt5.QtWidgets import QWidget, QProgressBar, QPushButton, QApplication, QLCDNumber
from PyQt5.QtCore import QBasicTimer
import pygame
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#from impedance import Impedance

import time
import traceback
import sys

import pygame
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from pylsl import StreamInlet, resolve_stream
from datetime import datetime
import csv
import subprocess


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


class ViAT(QMainWindow):
    '''First user view
    
    Load a .ui type view designed in Qt designer
    
    :setup: this function contains the condition to move to the other views
    '''
    def __init__(self):
        super(ViAT, self).__init__()
        loadUi('ViAT.ui', self)
        self.setWindowTitle('Inicio')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()

    def assignController(self, controller):
        self.my_controller = controller

    def setup(self):
        self.startRegistration.clicked.connect(self.loadRegistration)
        self.patientData.clicked.connect(self.loadData)
        self.exit.clicked.connect(self.end)
        pixmap = QPixmap('Logo.png')
        self.logo.setPixmap(pixmap)

    def loadRegistration(self):
        self.__registry = LoadRegistration(self, self.my_controller)
        self.__registry.show()
        self.hide()

    def loadData(self):
        self.__registry = DataBase(self)
        self.__registry.show()
        self.hide()

    def end(self):
        self.hide()
        exit()

        


class LoadRegistration(QMainWindow):
    '''Take data
    
        Allows you to collect basic information from patients or subjects
    
        :setup: this function contains the condition to move to the other views
        
        :clinicalhistoryInformation: Compare the data entered in the database to 
        autocomplete the stationary fields
        
        :dataAcquisition: Check that the fields are completely filled
    '''
    def __init__(self, LR, controller):
        super(LoadRegistration, self).__init__()
        loadUi('Registro-HistoriaClinica.ui', self)
        self.setWindowTitle('Registro')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
        self.my_controller = controller

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
        self.__registry = DataAcquisition(self, self.my_controller)
        self.__registry.show()
        self.hide()


class DataAcquisition(QMainWindow):
    '''Electrodes and devices
    
        Verify that the application can continue with the registration
    
        :setup: this function contains the condition to move to the other views
    '''
    
    def __init__(self, DA, controller):
        super(DataAcquisition, self).__init__()
        loadUi('Adquisicion.ui', self)
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
        self.__parentDataAcquisition = DA
        self.threadpool = QThreadPool()
        self.my_controller = controller

    def setup(self):
        self.back.clicked.connect(self.loadStart)
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
        
        pixmap = QPixmap('M.png')
        self.mounting.setPixmap(pixmap)
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)

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
        self.timer = QtCore.QTimer(self)
        # timer.setSingleShot(True)
        self.timer.timeout.connect(self.printZ)
        self.timer.start(22)  # milisegundos ojo humano
        # print(self.timer.isActive())

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

    def fFCz(self):
        # GRAY
        pass


    def fOz(self):
        # PURPLE
        pass

    def fO1(self):
        # BLUE
        pass


    def fPO7(self):
        # GREEN
        pass


    def fO2(self):
        # YELLOW
        pass


    def fPO8(self):
        # ORANGE
        pass


    def fPO3(self):
        # RED
        pass

    def fPO4(self):
        # BROWN
        pass
    def Startdevice(self):
        self.worker = Worker(self.execute_this_fn)
        self.worker.signals.result.connect(self.print_output)  # s
        self.worker.signals.finished.connect(self.thread_complete)
        self.worker.signals.progress.connect(self.progress_fn)  # n
        # Execute
        self.threadpool.start(self.worker)
        
        
        self.detectDevice.setEnabled(True)
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

        # print(self.timer.isActive())
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
        # Necesito un WHILE

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
        
    def progress_fn(self, n):
        pass

    def execute_this_fn(self, progress_callback):
#        servidor = Server()
#        servidor.port()
#        data = RandData()
#        data.sample()
        try:
            Rand=subprocess.call('start /wait python randData.py', shell=True)
        except KeyboardInterrupt:
            Rand.terminate()
            
        self.my_controller.startDevice()
        

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")


class AcquisitionSignal(QMainWindow):
    def __init__(self, AS, controller):
        super(AcquisitionSignal, self).__init__()
        loadUi('Adquisicion_accion.ui', self)
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QIcon('icono.png'))
        self.setup()
        self.show()
#        self.step = 0
        self.counter = 0
        self.__parentAcquisitionSignal = AS
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" %
              self.threadpool.maxThreadCount())
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.my_controller = controller

    def setup(self):
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        self.play.clicked.connect(self.startPlay)
        self.stop.clicked.connect(self.stopEnd)
        self.patientData.clicked.connect(self.loadData)
        self.back.clicked.connect(self.loadStart)
        self.exit.clicked.connect(self.end)
        self.playGraph.clicked.connect(self.startGraph)
        self.stopGraph.clicked.connect(self.haltGraph)

    def startPlay(self):
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
        time.sleep(15)
        estimulo = Stimulus()
        estimulo.start_stimulus()

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def stopEnd(self):
        self.play.setEnabled(True)
        pygame.quit()
#        self.threadpool.destroyed

    def loadData(self):
        self.__registry = DataBase(self)
        self.__registry.show()
        self.hide()

    def loadStart(self):
        self.__parentAcquisitionSignal.show()
        self.hide()
    
    def end(self):
        self.hide()
        exit()

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.play.setText('Iniciar')
            return
        self.step += 1
        self.alert.setValue(self.step)

    def recurring_timer(self):
        pass

    def returnLastData(self):
        return self.my_controller.returnLastData()

    def graphData(self):
        data, Powers, freq = self.returnLastData()
        data = data - np.mean(data, 0)
        if data.ndim == 0:
            print("Lista vacia")
            return
        self.viewSignalOz.clear()
        self.viewSignalOz.plot(np.round(data[0, :], 1), pen=('#CD10B4'))
        self.viewSignalOz.repaint()
        self.viewSignalO1.clear()
        self.viewSignalO1.plot(np.round(data[0, :], 2), pen=('#1014CD'))
        self.viewSignalO1.repaint()
        self.viewSignalPO7.clear()
        self.viewSignalPO7.plot(np.round(data[0, :], 3), pen=('#10CD14'))
        self.viewSignalPO7.repaint()
        self.viewSignalO2.clear()
        self.viewSignalO2.plot(np.round(data[0, :], 4), pen=('#F7FB24'))
        self.viewSignalO2.repaint()
        self.viewSignalPO8.clear()
        self.viewSignalPO8.plot(np.round(data[0, :], 5), pen=('#FBB324'))
        self.viewSignalPO8.repaint()
        self.viewSignalPO4.clear()
        self.viewSignalPO4.plot(np.round(data[0, :], 6), pen=('#806123'))
        self.viewSignalPO4.repaint()
        self.viewSignalPO3.clear()
        self.viewSignalPO3.plot(np.round(data[0, :], 7), pen=('#E53923'))
        self.viewSignalPO3.repaint()

    def startGraph(self):
        self.my_controller.startData()

        print("Iniciar senal")
        self.timer = QtCore.QTimer(self)
        # timer.setSingleShot(True)
        self.timer.timeout.connect(self.graphData)
        self.timer.start(22)  # milisegundos ojo humano
        # print(self.timer.isActive())

    def haltGraph(self):
        self.timer.stop()
        self.my_controller.stopData()
        print("detener senal")


class DataBase(QMainWindow):
    def __init__(self, DB):
        super(DataBase, self).__init__()
        loadUi('Adquisicion_datos.ui', self)
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
        self.exit.clicked.connect(self.end)
        self.stopDevice.clicked.connect(self.stopData)

    def delaySignal(self):
        pass
    
    def stopData(self):
        pass

    def forwardSignal(self):
        pass

    def dataAcquisition(self):
        self.__registry = DataAcquisition(self)
        self.__registry.show()
        self.hide()

    def loadStart(self):
        self.__parentDataBase.show()
        self.hide()

    def end(self):
        self.hide()
        exit()
        

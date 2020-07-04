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
from PyQt5 import QtCore, QtWidgets, QtGui
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
import errno
import pyqtgraph as pg
from datetime import datetime
import random

# from PySide2 import QtWidgets
# from PySide2 import QtCore
# from PySide2 import QtGui
# from PySide2.QtUiTools import QUiLoader
# from PySide2.QtWidgets import QApplication
# from PySide2.QtCore import QFile, QIODevice

'''
Manages how data is displayed in the graphical interface by means of the 
commands it sends to the controller and the data it returns from the
 operations performed on the model.
It is composed of 6 views designed in QtDesigner and by 8 classes that 
control each of the views and two additional ones for the control of threads 
for the processes that are carried out simultaneously
'''
# In[]


class WorkerSignals(QtCore.QObject):
    '''
    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()  # with no data to indicate when the task is complete
    # which receives a tuple of Exception type,
    error = QtCore.pyqtSignal(tuple)
    # Exception value and formatted traceback.
    # receiving any object type from the executed function.
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)

# In[]


class Worker(QtCore.QRunnable):
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

    @QtCore.pyqtSlot()
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

    Run the main ViAT.ui view with the menu to scroll through the application.
        1. Start registration: Go to view 2.
        2. Patient database: Lets you go to view 6
        3. Exit: Exit the application.
    '''

    def __init__(self):
        super(ViAT, self).__init__()
        # The designed view is exported in qt designer
        loadUi('ViAT.ui', self)
#        QFile("ViAT.ui")
        self.setWindowTitle('Inicio')
        self.setWindowIcon(QtGui.QIcon('icono.png'))  # window icon
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
        self.__registry = LoadRegistration(
            self, self.__controlador, self.my_controller)
        self.__registry.show()
        self.hide()

    def loadData(self):
        self.__registry = DataBase(
            self, self.__controlador, self.my_controller)
        self.__registry.show()
        self.hide()

    def end(self):
        self.hide()
        self.my_controller.stopDevice()
        exit()

# In[]


class LoadRegistration(QtWidgets.QDialog):
    '''
    Run the AddData.ui view (Figure 2). It has the function of creating and
    managing a database of each subject registered with the ViAT tool.
     :setup: This function allows to:
        1. Free writing fields
        2. Verification button
        3. Drop-down menu buttons
        4. It allows the user to have the autonomy to choose the location of
            the files resulting from the stimulation (Registration, marks,
            processing with multitaper and processing with time frequency)
        5. Allows the user to navigate to the database to search for a subject
            view 5
        6. It allows adding a subject, after completing all the fields.
        7. When verifying a subject from the database, allow them to be
            manipulated and updated with the “Update” button. If you want to
            delete any of the records, you must go to the database and confirm
            this action.
        8. Lets you go to the next view.
        9. It is the help button
    '''

    def __init__(self, LR, controlador, controller):
        super(LoadRegistration, self).__init__()
        loadUi("Agregardatos.ui", self)
        # QFile("Agregardatos.ui")
        self.setup()
        self.setWindowTitle('Base de datos')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.show()
        self.__parentLoadRegistration = LR
        self.__controlador = controlador
        self.my_controller = controller
        self.__locR, self.__locP = self.my_controller.location()

    def setup(self):
        self.btn_search.clicked.connect(self.find)
        self.btn_add.clicked.connect(self.add)
        self.btn_show.clicked.connect(self.see)
        self.back.clicked.connect(self.loadStart)
        self.next.clicked.connect(self.dataAcquisition)
        self.btn_update.clicked.connect(self.upgrade)
        self.infoAdquisition.clicked.connect(self.info)
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

    def info(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Diríjase al campo de CC y digite la cédula del sujeto a registrar, para verificar que no se encuentre ya en la base de datos, si no está llene todos los campos presentados a continuación y presione agregar, en el botón 'definir ubicación‘ podrá modificar la ubicación donde desea que quede guardado el registro, al finalizar presione el botón 'Siguiente'. Si el sujeto ya se encuentra en la base de datos y desea modificar un campo, presione 'Actualizar'. Si desea observar todos los sujetos en la base de datos presione 'Mostrar Pacientes'. Para volver al menú anterior presione 'Atrás'.")
        msg.setWindowTitle("Ayuda")
        x = msg.exec_()

    def assign_controller(self, controlador):
        self.__controlador = controlador

    def location(self):
        location = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.my_controller.newLocation(location)

    def upgrade(self):
        if not (self.d.text() and self.nombre.text() and
                self.apellidos.text() and self.cc.text() and
                self.snellen.text() and self.correction.text() and
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
                "d": self.d.text(),
                "nombre": self.nombre.text(),
                "apellidos": self.apellidos.text(),
                "cc": self.cc.text(),
                "sexo": (self.sex),
                "dominante": (self.domi),
                "gafas": (self.glass),
                "snellen": (self.snellen.text()),
                "corregida": (self.correction.text()),
                "estimulo": (self.stimu),
                "edad": (self.edad.text()),
                "tiempo": (self.time.text()),
                "rp": (self.rp.text()),
                "ubicacion": (str(self.__locR))
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
                self.snellen.text() and self.correction.text() and
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
                "d": self.d.text(),
                "nombre": self.nombre.text(),
                "apellidos": self.apellidos.text(),
                "cc": self.cc.text(),
                "sexo": (self.sex),
                "dominante": (self.domi),
                "gafas": (self.glass),
                "snellen": (self.snellen.text()),
                "corregida": (self.correction.text()),
                "estimulo": (self.stimu),
                "edad": (self.edad.text()),
                "tiempo": (self.time.text()),
                "rp": (self.rp.text()),
                "ubicacion": (str(self.__locR))
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
        self.__registry = DataBase(
            self, self.__controlador, self.my_controller)
        self.__registry.show()
        self.hide()

    def loadStart(self):
        self.__parentLoadRegistration.show()
        self.hide()

    def dataAcquisition(self):
        self.__registry = DataAcquisition(
            self, self.__controlador, self.my_controller)
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

        Run the Acquisition.ui view. It has the function of
        preparing the registration, locating the user, observing the suggested
        electrode assembly (10-10), measuring the impedance of each positioned
        electrode, connecting the device and verifying the second screen in
        which the stimulus will be presented.
    '''
    # Contains restrictions to follow the actions in an orderly manner

    def __init__(self, DA, controlador, controller):
        super(DataAcquisition, self).__init__()
        # The designed view is exported in qt designer
        loadUi('Adquisicion.ui', self)
        # QFile('Adquisicion.ui')
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.__parentDataAcquisition = DA
        self.threadpool = QThreadPool()  # creating a group of threads in qt
        self.my_controller = controller
        self.__controlador = controlador
        self.banDataAcquisition = 0

    def setup(self):
        self.back.clicked.connect(self.loadStart)
        self.infoAdquisition.clicked.connect(self.info)
        self.next.setEnabled(False)
        self.StopZ.setEnabled(False)
        self.detectDevice.setEnabled(False)
        self.startDevice.clicked.connect(self.Startdevice)
        self.next.clicked.connect(self.executeAcquisition)
        self.StopZ.clicked.connect(self.StopMeasurement)
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
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Comience identificando que el dispositivo está conectado y que puede comenzar a adquirir los datos, se abrirá una ventana negra la cual le anuncia que se ha comenzado la adquisición, presione 'Minimizar' y a continuación verifique que la pantalla de estimulación se encuentra conectada. Para verificar la impedancia presione cualquiera de los electrodos de la configuración. Antes de pasar a la siguiente etapa recuerde detener la medición de la impedancia.")
        msg.setWindowTitle("Ayuda")
        x = msg.exec_()

    def loadStart(self):
        self.__parentDataAcquisition.show()
        self.hide()

    def executeAcquisition(self):
        if self.banDataAcquisition == True:
            self.next.setEnabled(False)  # Revisar genera delay
            self.__registry = AcquisitionSignal(
                self, self.__controlador, self.my_controller)
            self.__registry.show()
            self.hide()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(
                "Detenga la medición de la impedancia antes de continuar")
            msg.setWindowTitle("Alerta!")
            x = msg.exec_()

    def returnLastZ(self):
        return self.my_controller.returnLastZ()

    def startMeasurement(self):
        self.my_controller.startZ()
        self.StopZ.setEnabled(True)

        print("Iniciar medicion")
        self.timer = QtCore.QTimer(self)  # creating a time thread
        self.timer.timeout.connect(self.printZ)
        # speed in milliseconds discriminated by human eye
        self.timer.start(22)

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
        self.banDataAcquisition = 1
        self.timer.stop()
        self.my_controller.stopZ()
        print("detener impedancia")
        self.next.setEnabled(True)

    def Startdevice(self):
        # use worker function explained at startup
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

        # Allows to detect if there is a second screen connected
        obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)
        displays = [x for x in obj if 'DISPLAY' in str(x)]
        num = len(displays)
        if num == 3:
            self.next.setEnabled(True)
            self.next.clicked.connect(self.executeAcquisition)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(
                "Debe conectar una segunda pantalla para poder iniciar la adquisición")
            msg.setWindowTitle("Alerta!")
            num = 0
            x = msg.exec_()
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

    def __init__(self, AS, controlador, controller):
        super(AcquisitionSignal, self).__init__()
        # The designed view is exported in qt designer
        loadUi('Adquisicion_accion.ui', self)
        # QFile('Adquisicion_accion.ui')
        self.setWindowTitle('Adquisición')
        self.setWindowIcon(QtGui.QIcon('icono.png'))
        self.setup()
        self.show()
        self.counter = 0
        self.__parentAcquisitionSignal = AS
        self.threadpool = QThreadPool()  # creating a group of threads in qt
        print("Multithreading with maximum %d threads" %
              self.threadpool.maxThreadCount())
        self.timer = QTimer()  # creating a time thread
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.my_controller = controller
        self.__controlador = controlador
        self.step = 0

    def setup(self):
        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
        self.play.clicked.connect(self.startPlay)
        self.stop.setEnabled(False)
        self.back.clicked.connect(self.loadStart)
        self.exit.clicked.connect(self.end)
        self.playGraph.clicked.connect(self.startGraph)
        self.stopGraph.clicked.connect(self.haltGraph)
        self.adquisitionInfo.clicked.connect(self.info)
        self.stopDevice.clicked.connect(self.stopProcess)
        self.display.setEnabled(True)
        self.display.clicked.connect(self.displaysignal)

    def closeData(self, data):
        data.close()

    def info(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("En la parte superior encontrará dos pestañas, cargar estimulación, en la que se encuentra actualmente y la de visualización, en la cual podrá observar la señal adquirida en tiempo real. Primero debe presionar el botón inicio en la pestaña actual, luego, pase a la pestaña de visualización y presione 'visualizar’, en la primera pestaña podrá observar una barra de proceso que le anunciara que el estímulo está a punto de presentarse. En esta pestaña podrá interactuar con la señal aplicando el método de Welch a cada uno de los canales o modificando la configuración de Laplace según el interés del registro. Podrá reiniciar el estímulo las veces que sea necesario sin necesidad de detener la adquisición. En la parte inferior podrá observar 4 botones que le permiten ir a la vista anterior, desconectar el dispositivo de adquisición, visualizar las señales adquiridas previamente o salir del programa.")
        msg.setWindowTitle("Ayuda")
        x = msg.exec_()

    def startPlay(self):
        self.ban = True
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
        veces = 0
        while veces < 10 and self.ban is True:
            time.sleep(veces)  # increment one second when entering while
            value = self.alert.value()
            if value < 100:
                value = value + 10  # progress bar
                self.alert.setValue(value)
            else:
                self.timer.stop()
            veces = veces+1
        # time.sleep(15)  # if the while is not used for the progress bar
        if self.ban is True:
            self.my_controller.startStimulus()
            self.my_controller.stopStimulus()
        else:
            pass

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("COMPLETE!")

    def stopEnd(self):  # Reset
        self.play.setEnabled(True)
        pygame.quit()
        self.alert.setValue(0)

    def loadStart(self):
        self.__parentAcquisitionSignal.show()
        self.hide()

    def end(self):
        self.hide()
        self.my_controller.stopDevice()
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
            pen = ('#208A8A')
        elif self.welch.currentIndex() == 1:
            c = 1
            pen = ('#CD10B4')
        elif self.welch.currentIndex() == 2:
            c = 2
            pen = ('#1014CD')
        elif self.welch.currentIndex() == 3:
            c = 3
            pen = ('#10CD14')
        elif self.welch.currentIndex() == 4:
            c = 4
            pen = ('#F7FB24')
        elif self.welch.currentIndex() == 5:
            c = 5
            pen = ('#FBB324')
        elif self.welch.currentIndex() == 6:
            c = 6
            pen = ('#E53923')
        else:
            c = 7
            pen = ('#806123')

        self.my_controller.laplace_controller(self.laplace1.currentIndex(
        ), self.laplace2.currentIndex(), self.laplace3.currentIndex())
        data, Powers, freq, laplace, Plaplace, flaplace = self.returnLastData()

        data = data - np.mean(data, 0)
        if data.ndim == 0:
            print("Lista vacia")
            return
        self.welchPlot.clear()
        self.welchPlot.plot(x=freq, y=Powers[c, :], pen=pen)
        self.welchPlot.repaint()
        self.welchLaplace.clear()
        self.welchLaplace.plot(x=flaplace, y=Plaplace[0, :], pen=('#0D6B9D'))
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
        self.display.setEnabled(False)

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
        self.stop.setEnabled(True)
        self.display.setEnabled(True)
        print("detener senal")

    def displaysignal(self):
        self.__registry = GraphicalInterface(self, self.__controlador)
        self.__registry.show()
        self.hide()


# In[]

class DataBase(QDialog):
    '''
    Run the SearchData.ui view.
    It has the function of displaying the subjects registered in the database.
    :setup: This function allows to:
        1. Allows to search a subject in the database by means of the
        registered ID number.
        2. It is a Menu that allows you to choose the function that you will
        have when you double-click on a subject in the database, allowing you
        to delete a record or route to the locally registered files of the
        selected subject.
        3. This button allows showing all the subjects in the local database
        created in MongoDB when executing the program.
        4. Lets you direct view 6, where previously registered signs are
        observed.
        5. Help button contains the following message: In the first field you
        find, you can type the CC of a subject to search for their information
        in the database, or press 'Show all' to view all the subjects present
        in the database . There is a drop-down menu below this field, this
        allows you to delete a subject from the database or direct the user
        to the subject's registry. In the button 'Visualize signals' you will
        go to the view that allows you to search and visualize previously
        acquired signals. To return to the previous menu press 'Back'.
        6. Back, this button allows you to return to the previous view,
        this can be; View 1 or 2. According to the use given by the user.
    '''

    def __init__(self, DB, controlador, controller):
        super(DataBase, self).__init__()
        loadUi("Buscardatos.ui", self)
        # QFile("Buscardatos.ui")
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
        self.line_search.setPlaceholderText("Cédula del sujeto")
        self.btn_show.clicked.connect(self.show_everything)
        self.btn_search.clicked.connect(self.find)
        self.table.itemDoubleClicked.connect(self.dbclick)
        self.back.clicked.connect(self.loadStart)
        self.display.clicked.connect(self.displaysignal)
        self.infoAdquisition.clicked.connect(self.info)

        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)

    def info(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("En el primer campo que encuentra podrá digitar la CC de un sujeto para buscar su información en la base de datos, o presionar 'Mostrar todo' para visualizar todos los sujetos presentes en la base de datos. Existe un menú desplegable debajo de este campo, este permite eliminar un sujeto de la base de datos o direccionar al usuario al registro del sujeto. En el botón 'Visualizar señales’ se dirigirá a la vista que le permite buscar y visualizar señales previamente adquiridas. Para volver al menú anterior presione 'Atrás'.")
        msg.setWindowTitle("Ayuda")

    def show_everything(self):
        results = self.__controlador.get_integrants()
        self.see(results)

    def find(self):
        find = self.line_search.text()
        self.line_search.setText("")
        self.line_search.setPlaceholderText("Cédula del sujeto")
        results = self.__controlador.search_integrantes(find)
        self.see(results)

    def see(self, results):
        self.table.clear()
        for result in results:
            item = QTreeWidgetItem(self.table)
            for i in range(14):
                item.setText(i, str(result[i]))

    def dbclick(self):
        if self.options.currentIndex() == 0:
            data = self.table.currentItem()
            buttonReply = QMessageBox.question(self, 'Borrar información',
                                               u"¿Desea eliminar a %s de la lista de sujetos?" % data.text(
                                                   0),
                                               QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.__controlador.delete(data.text(3))
                self.show_everything()
            if buttonReply == QMessageBox.No:
                pass
            if buttonReply == QMessageBox.Cancel:
                pass
        else:
            data = self.table.currentItem()
            buttonReply = QMessageBox.question(self, 'Buscar información',
                                               u"¿Desea ir a la ubicación del registro de %s?" % data.text(
                                                   0),
                                               QMessageBox.Yes | QMessageBox.No)
            path = self.__controlador.file_location(data.text(0), data.text(3))
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
        self.__registry = GraphicalInterface(self, self.__controlador)
        self.__registry.show()
        self.hide()


# In[]

class GraphicalInterface(QtWidgets.QMainWindow):
    '''
    Run the visualization.ui view.
    It has the function of displaying the signals registered with the ViAT
    software or the OpenViBE software.
     :setup: This function allows to:
        1. Menu. The signals acquired with OpenViBE have a different storage
        structure than the one acquired by ViAT, for this reason it is
        necessary for the user to specify what type the signal is before
        loading it.
        2. Load signal, opens the file explorer in the application folder
        and allows you to search for the record you want to observe.
        There is a folder called “Record” in the main folder, there you
        should find all the records made by ViAT unless you have changed the
        location of a record in View 2.
        3. They are buttons to interact with the displayed signal.
        They allow you to move the sign to the right or left and make a
        small zoom of it.
        4. It allows to search for a subject in the database and when it
        appears in the table and double-click, the user will go to the
        subject's records folder.
        5. Help button contains the following message: In this view you will
        be able to view signals previously registered by ViAT or in OpenViBE
        software, in the drop-down menu on the right choose the type of file
        to search and press 'Load signal'. The buttons at the bottom of this
        button allow you to scroll the signal in time and adjust the signal
        for better viewing. In the following field, you can interact with the
        database again by searching for a subject with your CC to visualize the
        signal in a more agile way. If you want to observe all the subjects in
        the database press 'Show Patients'. To return to the previous menu press
        'Back'.
        6. Back, this button allows you to return to the previous view,
        this can be; View 4 or 5. According to the use given by the user.
        7. Close the program.
    '''

    def __init__(self, IG, controlador):
        super(GraphicalInterface, self).__init__(IG)
        loadUi('visualizacion.ui', self)
        self.setup()
        self.show()

        self.__x_min = 0
        self.__x_max = 0
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
        self.line_search.setPlaceholderText("Cédula del sujeto")
        self.btn_search.clicked.connect(self.find)
        self.table.itemDoubleClicked.connect(self.dbclick)
        self.back.clicked.connect(self.loadStart)
        self.btn_show.clicked.connect(self.show_everything)
        self.infoAdquisition.clicked.connect(self.info)

        pixmap1 = QtGui.QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)

    def info(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("En esta vista podrá visualizar señales previamente registradas por ViAT o en el software OpenViBE, en el menú desplegable a la derecha elija el tipo de archivo que va a buscar y presione 'Cargar señal'. Los botones en la parte inferior de este botón le permiten desplazar la señal en el tiempo y realizar un ajuste de la señal para visualizarla mejor. En el campo siguiente podrá interactuar nuevamente con la base de datos buscando un sujeto con su CC para visualizar la señal de manera más ágil. Si desea observar todos los sujetos en la base de datos presione 'Mostrar Pacientes'. Para volver al menú anterior presione 'Atrás'.")
        msg.setWindowTitle("Ayuda")

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)

    # Graph signal
    def graph_data(self, datos):
        self.ax.cla()
#        print(datos.shape)
        for c in range(datos.shape[0]):
            self.ax.plot(datos[c, :]+c*10)
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
    # Close program

    def toclose(self):
        self.close()

    # Controller assignment to make connection in MVC model
    def assign_controller(self, controlador):
        self.__controlador = controlador

    # Advance the signal one second in time. This corresponds to 2000 points in the signal
    def forward_signal(self):
        self.__x_min = self.__x_min+2000
        self.__x_max = self.__x_max+2000
        self.graph_data(self.__controlador.returnDataSenal(
            self.__x_min, self.__x_max))

    # Delaying the signal one second in time. This corresponds to 2000 points in the signal
    def delay_signal(self):
        if self.__x_min < 2000:
            return
        self.__x_min = self.__x_min-2000
        self.__x_max = self.__x_max-2000
        self.graph_data(self.__controlador.returnDataSenal(
            self.__x_min, self.__x_max))

    # Increase signal amplitude
    def increase_signal(self):
        self.graph_data(self.__controlador.scaleSignal(
            self.__x_min, self.__x_max, 2))

    # Decrease signal amplitude
    def decrease_signal(self):
        self.graph_data(self.__controlador.scaleSignal(
            self.__x_min, self.__x_max, 0.5))

    # Load the signal in sight
    def load_signal(self):
        uploaded_file, _ = QFileDialog.getOpenFileName(
            self, "Abrir seal", "", "Todos los archivos (*);;Archivos csv (*.csv)*")
        if uploaded_file != "":
            if self.type.currentIndex() == 0:
                d = pd.read_csv(uploaded_file, header=None)
                d = d.values
                d = d[0:8, :]*100000
                d[1] = d[1, :] - d[0, :]
                d[2] = d[2, :] - d[0, :]
                d[3] = d[3, :] - d[0, :]
                d[4] = d[4, :] - d[0, :]
                d[5] = d[5, :] - d[0, :]
                d[6] = d[6, :] - d[0, :]
                d[7] = d[7, :] - d[0, :]
            else:
                d = pd.read_csv(uploaded_file, ';', header=None)
                d = d.drop([0], axis=0)
                d = d.T
                d = d.drop([9], axis=1)
                d = d.drop([0], axis=0)
                index = list(range(0, len(d[1])))
                d[0] = index
                d = d.set_index(d[0])
                d = d.drop([8], axis=0)
                d = d.astype(float)
                d = d.values
                d = d[0:8, :]*500
                d[0] = d[0, :]
                d[1] = d[1, :] + 1000
                d[2] = d[2, :] + 2000
                d[3] = d[3, :] + 3000
                d[4] = d[4, :] + 4000
                d[5] = d[5, :] + 5000
                d[6] = d[6, :] + 6000
                d[7] = d[7, :] + 7000

            print(d.size/250)
            senal_continua = d
            self.__senal = senal_continua
            self.__controlador.ReceiveData(senal_continua)
            self.__x_min = 0
            self.__x_max = 2000
            self.graph_data(self.__controlador.returnDataSenal(
                self.__x_min, self.__x_max))
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
                item.setText(i, str(result[i]))

    def dbclick(self):
        data = self.table.currentItem()
        buttonReply = QMessageBox.question(self, 'Buscar información',
                                           u"¿Desea ir a la ubicación del registro de %s?" % data.text(
                                               0),
                                           QMessageBox.Yes | QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            path = self.__controlador.file_location(data.text(0), data.text(3))
            uploaded_file, _ = QFileDialog.getOpenFileName(
                self, "Abrir senal", path, "Todos los archivos (*);;Archivos csv (*.csv)*")
            if uploaded_file != "":
                d = pd.read_csv(uploaded_file, ';', header=None)
                d = d.drop([0], axis=0)
                d = d.T
                d = d.drop([9], axis=1)
                d = d.drop([0], axis=0)
                index = list(range(0, len(d[1])))
                d[0] = index
                d = d.set_index(d[0])
                d = d.drop([8], axis=0)
                d = d.astype(float)
                d = d.values
                d = d[0:8, :]*500
                d[0] = d[0, :]
                d[1] = d[1, :] + 1000
                d[2] = d[2, :] + 2000
                d[3] = d[3, :] + 3000
                d[4] = d[4, :] + 4000
                d[5] = d[5, :] + 5000
                d[6] = d[6, :] + 6000
                d[7] = d[7, :] + 7000

                print(d.size/250)
                senal_continua = d
                self.__senal = senal_continua
                self.__controlador.ReceiveData(senal_continua)
                self.__x_min = 0
                self.__x_max = 2000
                self.graph_data(self.__controlador.returnDataSenal(
                    self.__x_min, self.__x_max))
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

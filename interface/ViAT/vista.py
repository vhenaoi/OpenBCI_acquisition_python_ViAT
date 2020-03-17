# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:18:13 2020

@author: veroh
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy.io as sio
import numpy as np
from scipy.signal import welch
import pandas as pd 
from PyQt5.QtGui import QIcon, QPixmap


class ViAT(QMainWindow):
    # Constructor con lanzador para la ventana
    def __init__(self):
        super(ViAT,self).__init__()
        loadUi ('ViAT.ui',self)
        self.setup()
        self.show()
    # Se configuran las señales y los slots de los botones.
    def setup(self):
        # Se establecen los slots de los botones presentes en la ventana principal del sistema
        self.iniciarRegistro.clicked.connect(self.cargarRegistro)
        self.datosPacientes.clicked.connect(self.cargarDatos)
        self.salirInicio.clicked.connect(self.salir)
        pixmap = QPixmap('Logo.png')
        self.logo.setPixmap(pixmap)
    def cargarRegistro(self):
        self.__registro=CargarRegistro(self)
        self.__registro.show()
        self.hide()
    def cargarDatos(self):
        pass
    def salir(self):
        pass

class CargarRegistro(QMainWindow):
    # Constructor con lanzador para la ventana
    def __init__(self, vp):
        super(CargarRegistro,self).__init__()
        loadUi ('Registro-HistoriaClinica.ui',self)
        self.setup()
        self.show()
        
        self.__ventanaPadre = vp
    # Se configuran las seales y los slots de los botones.
    def setup(self):
        # Se establecen los slots de los botones presentes en la ventana principal del sistema
        self.atras.clicked.connect(self.cargarInicio)
        self.siguiente.clicked.connect(self.adquisicionDatos)
        pixmap = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap)
    def infoHistoriaClinica(self):
        pass
    def cargarInicio(self):
        self.__ventanaPadre.show()
        self.hide()
    def adquisicionDatos(self):
        self.__registro=AdquisicionDatos(self)
        self.__registro.show()
        self.hide()

class AdquisicionDatos(QMainWindow):
    def __init__(self, vp):
        super(AdquisicionDatos,self).__init__()
        loadUi ('Adquisicion.ui',self)
        self.setup()
        self.show()
        
        self.__ventanaPadre = vp
    def setup(self):
        # Se establecen los slots de los botones presentes en la ventana principal del sistema
        self.atras.clicked.connect(self.cargarInicio)
        self.siguiente.clicked.connect(self.adquisicionAccion)
        pixmap = QPixmap('M.png')
        self.m.setPixmap(pixmap)
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
    def cargarInicio(self):
        self.__ventanaPadre.show()
        self.hide()
    def adquisicionAccion(self):
        self.__registro=AdquisicionSignal(self)
        self.__registro.show()
        self.hide()

class AdquisicionSignal(QMainWindow):
    def __init__(self, vp):
        super(AdquisicionDatos,self).__init__()
        loadUi ('Adquisicion_accion.ui',self)
        self.setup()
        self.show()
        
        self.__ventanaPadre = vp
    def setup(self):
        # Se establecen los slots de los botones presentes en la ventana principal del sistema
        self.atras.clicked.connect(self.cargarAdquisicion)
        pixmap = QPixmap('M.png')
        self.m.setPixmap(pixmap)
        pixmap1 = QPixmap('blanclogo.png')
        self.logo.setPixmap(pixmap1)
#    def infoHistoriaClinica(self):
#        pass
#    def cargarInicio(self):
#        self.__ventanaPadre.show()
#        self.hide()
#    def cargarAdquisicion(self):
#        pass
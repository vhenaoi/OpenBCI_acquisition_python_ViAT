'''
Created on 2020

@author: Verónica Henao Isaza

'''
import numpy as np
from pylsl import StreamInlet, resolve_stream
from linearFIR import filter_design
from nonlinear import hampelFilter
import scipy.signal as signal
import os
from datetime import datetime
import pandas as pd
from serial.tools import list_ports
import subprocess
from Stimulation_Acuity import Stimulus
from pymongo import MongoClient
from dataprocessing import Processing
from plot_stft import TimeFrequency
import pygame


class Model(object):
    '''
    It contains the data and the functionality of the application, that is, 
    it is responsible for performing the functions of updating, searching, 
    consulting, data processing.
    '''

    def __init__(self, name_db, name_collection, data=None):
        '''
        Receives: Name of the database, name of the collection of the database,
        data for graphics.
        Function: Make the connection to the mongo database,
        design the filters by calling filtDesign () and define the storage 
        locations of the files.
        '''

        MONGO_URI = "mongodb://localhost:27017/"
        self.__client = MongoClient(MONGO_URI)
        self.__db = self.__client[name_db]
        self.__collection = self.__db[name_collection]
        self.__fs = 250
        self.filtDesign()
        self.data = data
        print("se diseño el filtro")
        self.path_app = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT'
        self.cwd = self.path_app+'/'+'Records'
        self.processing = self.path_app+'/'+'Processing'
        if not np.all(data) == None:
            self.assign_data(data)
        else:
            self.__data = np.asarray([])

    def newLocation(self, location):
        '''
        Receive: The new location
        Function: Select the location of the new records to acquire
        '''

        if location != "":
            self.path_app = location
            print(self.path_app)
            self.cwd = location+'/'+'Records'
            self.processing = location+'/'+'Processing'
            if not os.path.isdir(self.cwd):
                os.mkdir(self.cwd)
                print(self.cwd)
            if not os.path.isdir(self.processing):
                os.mkdir(self.processing)
                print(self.processing)
        else:
            pass

    def location(self):
        '''
        Redefine the location of the new records to acquire
        '''

        return self.cwd, self.processing

    def startDevice(self):
        '''
        Start sending the data, use the subprocess.Popen function to start a
        new process without stopping the existing one.
        '''

        # servidor = Server()
        # servidor.port()
        # data = RandData()
        # data.sample()
        try:
            self.__process = subprocess.Popen('start python randData.py',
                                              shell=True, stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,)
            output = self.__process.communicate()[0].decode('utf-8')
            print(output)
            # if (Rand):
            # msg = QMessageBox(self.ventana_principal)
            # msg.setIcon(QMessageBox.Information)
            # msg.setText("El dispositivo ha sido detectado")
            # msg.setWindowTitle("Información")
            # msg.show()
            # else:
            # msg = QMessageBox(self.ventana_principal)
            # msg.setIcon(QMessageBox.Warning)
            # msg.setText("El dispositivo no ha sido detectado o no se encuentra conectado")
            # msg.setWindowTitle("Alerta!")
            # msg.show()
            # self.boton_iniciar.setEnabled(False)
        except KeyboardInterrupt:
            os.popen(
                r'TASKKILL /F /FI "WINDOWTITLE eq C:\Users\veroh\Anaconda3\python.exe"')

#        self.__channels = 8
#        self.__data = np.zeros((self.__channels, 2500))
#        self.streams_EEG = resolve_stream('type', 'EEG')

    def stopDevice(self):
        '''
        Stop sending the data and close the process.
        '''

        os.popen(
            r'TASKKILL /F /FI "WINDOWTITLE eq C:\Users\veroh\Anaconda3\python.exe"')

    def startData(self):
        '''
        Defines a matrix of zeros for the data with the number of channels
        and the number of samples.
        Use the resolve_stream function of the pylsl library to receive the
        data sent by the Server.py server or the randData.py data simulator.
        Using the StreamInlet object to receive transmission data 
        (and metadata) from the lab network, it takes the available 
        transmissions and finally does a pull_chunk () that extracts a chunk 
        of samples from the input.
        '''

        self.__channels = 8
        self.__data = np.zeros((self.__channels, 2500))
        self.streams_EEG = resolve_stream('type', 'EEG')
        self.__inlet = StreamInlet(self.streams_EEG[0], max_buflen=250)
        self.__inlet.pull_chunk()

    def stopData(self):
        '''
        Stops the action of receiving the data by closing the stream with 
        close_stream () and calls the dataprocessing.py and plot_stft.py
        processing modules
        '''

        if not os.path.isfile(self.cwd + '/' + str(self.p[0])+'_'+str(self.p[1])+'/'+self.date[0]+'/'+'Mark_'+self.p[0]+'_'+self.p[1]+'.csv'):
            pass
        else:
            maxV = Processing(self.p[0], self.p[1],
                              self.date[0], self.cwd, self.processing)
            maxV.run()
            TimeFre = TimeFrequency(
                self.p[0], self.p[1], self.date[0], self.cwd, self.processing)
            TimeFre.plot_stft()

        self.__inlet.close_stream()
        print('Stop Data Modelo')

    def startStimulus(self):
        '''
        call the stimulation module Stimulation_Acuity.py and start it.
        '''

        s = Stimulus(
            self.p[0], self.p[1], self.cwd + '/' + str(self.p[0])+'_'+str(self.p[1]))
        s.start_stimulus()

    def stopStimulus(self):
        '''
        Stops stimulation by closing the pygame.
        '''

        pygame.quit()

    def startZ(self):
        '''
        Start receiving data with StreamInlet to later find the impedance 
        of the data.
        '''

        self.__inlet = StreamInlet(self.streams_EEG[0], max_buflen=250)

    def stopZ(self):
        '''
        Close the reception of the data with close_stream at 
        the end of the reading of the impedance.
        '''

        self.__inlet.close_stream()
        print('Stop impedance')

    def readZ(self):
        '''
        Do a pull_sample () to take a value and perform the ohm-law operation.
        V = received rms voltage. i = device current = 6 nA
        Z = (V * √2) / i
        The value of Z is divided by 1000 before being presented in the view.
        '''

        sample, timestamp = self.__inlet.pull_sample()
        self.Z = []
        for i in range(0, 8):
            Z_i = ((sample[i])*np.sqrt(2))/(6*pow(10, -9))
            self.Z.append(Z_i/1000)

    def readData(self):
        '''
        Do a pull_chunk () to take a number of values and make a difference
        between the reference channel and each of the channels of interest.
        Create a Dataframe of each result to store it in a .csv file
        '''

        samples, timestamp = self.__inlet.pull_chunk()
        samples = np.transpose(np.asanyarray(samples))
        try:
            self.sh = samples.shape[1]
            self.s = samples
            self.__data = np.roll(self.__data, self.sh)
            self.__data[0, 0:self.sh] = samples[0, :]  # FCz
            self.__data[1, 0:self.sh] = samples[1, :] - \
                samples[0, :]  # Oz - FCz
            self.__data[2, 0:self.sh] = samples[2, :] - \
                samples[0, :]  # O1 - FCz
            self.__data[3, 0:self.sh] = samples[3, :] - \
                samples[0, :]  # PO7 - FCz
            self.__data[4, 0:self.sh] = samples[4, :] - \
                samples[0, :]  # O2  - FCz
            self.__data[5, 0:self.sh] = samples[5, :] - \
                samples[0, :]  # PO8 - FCz
            self.__data[6, 0:self.sh] = samples[6, :] - \
                samples[0, :]  # PO3 - FCz
            self.__data[7, 0:self.sh] = samples[7, :] - \
                samples[0, :]  # PO4 - FCz

        except:
            return

        self.__dataT = {'C1': samples[0, :],
                        'C2': self.__data[1, 0:self.sh],
                        'C3': self.__data[2, 0:self.sh],
                        'C4': self.__data[3, 0:self.sh],
                        'C5': self.__data[4, 0:self.sh],
                        'C6': self.__data[5, 0:self.sh],
                        'C7': self.__data[6, 0:self.sh],
                        'C8': self.__data[7, 0:self.sh]}
        now = datetime.now()
        self.date = (now.strftime("%m-%d-%Y"), now.strftime("%H-%M-%S"))
        # cwd = os.getcwd()
        loc = self.cwd + '/' + \
            str(self.p[0])+'_'+str(self.p[1]) + '/'+self.date[0]
        name = '/' + 'Record_'+str(self.p[0])+'_'+str(self.p[1])+'.csv'
        if not os.path.isdir(loc):
            os.mkdir(loc)
            header = True
        else:
            if os.path.isfile(loc + name):
                header = False
            else:
                header = True
        if not np.all(self.__data == 0):
            r = pd.DataFrame(self.__dataT, columns=[
                             'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'])
            d = str(self.date[1])
            r['H'] = pd.Series([d])
            r = r.fillna(0)
            r.to_csv(loc + name, mode='a', header=header, index=True, sep=';')

    def filtDesign(self):
        '''
        Design a low pass filter and a high pass filter
        '''

        order, self.lowpass = filter_design(
            self.__fs, locutoff=0, hicutoff=50, revfilt=0)
        order, self.highpass = filter_design(
            self.__fs, locutoff=5, hicutoff=0, revfilt=1)

    def filtData(self):
        '''
        Call the readData () function and use the filtfit function of
        scipy.signal to apply a filter to the received data in real time.
        '''

        self.readData()

        self.senal_filtrada_pasaaltas = signal.filtfilt(
            self.highpass, 1, self.__data)
        self.senal_filtrada_pasaaltas = hampelFilter(
            self.senal_filtrada_pasaaltas, 6)
        self.senal_filtrada_pasabandas = signal.filtfilt(
            self.lowpass, 1, self.senal_filtrada_pasaaltas)

        self.laplace_filtrada_pasaaltas = signal.filtfilt(
            self.highpass, 1, self.__laplace)
        self.laplace_filtrada_pasaaltas = hampelFilter(
            self.laplace_filtrada_pasaaltas, 6)
        self.laplace_filtrada_pasabandas = signal.filtfilt(
            self.lowpass, 1, self.laplace_filtrada_pasaaltas)

    def Pot(self):
        '''
        Apply the Welch method to the channel or user-defined configuration
        in the interface
        '''

        self.filtData()
        nblock = 250
        noverlap = nblock/2

        self.f, self.Pxx = signal.welch(self.senal_filtrada_pasabandas, self.__fs,
                                        nperseg=self.__fs*2, noverlap=noverlap)

        self.ftg, self.Pxxtg = signal.welch(self.__laplace,
                                            self.__fs, nperseg=self.__fs*2, noverlap=noverlap)

    def laplace(self, laplace1, laplace2, laplace3):
        '''
        Rec: From the drop-down menu of the graphical interface, take the
        values of the channels of interest.
        Func: Create an array to perform the Laplace operation with the 
        delivered values.
        '''

        self.readData()

        if laplace1 == 0:
            one = 1
        elif laplace1 == 1:
            one = 0
        elif laplace1 == 2:
            one = 2
        elif laplace1 == 3:
            one = 3
        elif laplace1 == 4:
            one = 4
        elif laplace1 == 5:
            one = 5
        elif laplace1 == 6:
            one = 6
        else:
            one = 7
        if laplace2 == 0:
            two = 2
        elif laplace2 == 1:
            two = 0
        elif laplace2 == 2:
            two = 1
        elif laplace2 == 3:
            two = 3
        elif laplace2 == 4:
            two = 4
        elif laplace2 == 5:
            two = 5
        elif laplace2 == 6:
            two = 6
        else:
            two = 7
        if laplace3 == 0:
            three = 4
        elif laplace3 == 1:
            three = 0
        elif laplace3 == 2:
            three = 1
        elif laplace3 == 3:
            three = 3
        elif laplace3 == 4:
            three = 2
        elif laplace3 == 5:
            three = 5
        elif laplace3 == 6:
            three = 6
        else:
            three = 7
        self.__laplace = np.zeros((1, 2500))
        self.__laplace = np.roll(self.__laplace, self.sh)
        self.__laplace[0, 0:self.sh] = (
            self.s[one, :]*2)-self.s[two, :]-self.s[three, :]

    def returnLastData(self):
        '''
        Run Pot () and return the values to the view to graph them.
        '''

        self.Pot()
        return (self.senal_filtrada_pasabandas, self.Pxx, self.f,
                self.laplace_filtrada_pasabandas, self.Pxxtg, self.ftg)  # [0:6,:]

    def returnLastZ(self):
        '''
        Run readZ () and return the values of the impedance.
        '''

        self.readZ()
        return self.Z

    def returnLastStimulus(self):
        '''
        Run readData ()
        '''

        self.readData()
        return

    def add_into_collection_one(self, data):
        '''
        Add a subject to the database
        '''

        self.__collection.insert_one(data)
        self.p = data['d'], data['cc']
        loc = self.cwd + '/' + str(self.p[0])+'_'+str(self.p[1])
        if not os.path.isdir(loc):
            os.mkdir(loc)
        else:
            pass
        return True

    def search_one(self, consult, proj):
        '''
        Search for a person from the database
        '''

        result = self.__collection.find_one(consult, proj)
        try:
            info_result = [result.get("d", None), result.get("nombre", None), result.get("apellidos", None),
                           result.get("cc", None), result.get(
                               "sexo", None), result.get("dominante", None),
                           result.get("gafas", None), result.get(
                               "snellen", None), result.get("corregida", None),
                           result.get("estimulo", None), result.get(
                               "edad", None), result.get("tiempo", None),
                           result.get("rp", None), result.get("ubicacion")]
            self.p = info_result[0], info_result[3]
            loc = self.cwd + '/' + str(self.p[0])+'_'+str(self.p[1])
            if not os.path.isdir(loc):
                os.mkdir(loc)
            else:
                pass
            return info_result
        except:
            return False

    def search_many(self, consult, proj, view=False):
        '''
        Returns the list of members of the database
        '''

        results = self.__collection.find(consult, proj)
        if view == True:
            for result in results:
                print(result)
        info_integrantes = list()
        for result in results:
            info = [result.get("d", None), result.get("nombre", None), result.get("apellidos", None),
                    result.get("cc", None), result.get(
                        "sexo", None), result.get("dominante", None),
                    result.get("gafas", None), result.get(
                        "snellen", None), result.get("corregida", None),
                    result.get("estimulo", None), result.get(
                        "edad", None), result.get("tiempo", None),
                    result.get("rp", None), result.get("ubicacion")]
            info_integrantes.append(info)
        return info_integrantes

    def delete_data(self, data):
        '''
        Delete a subject from the database
        '''

        self.__collection.delete_one(data)

    def assign_data(self, data):
        '''
        Deliver the data to be graphed from a .csv file
        '''
        self.__data = data

    def return_segment(self, x_min, x_max):
        '''
        Allow signal advance in time
        '''

        if x_min >= x_max:
            return None
        return self.__data[:, x_min:x_max]

    def signal_scale(self, x_min, x_max, escala):
        '''
        Allow to expand or decrease the signal
        '''

        copy_data = self.__data[:, x_min:x_max].copy()
        return copy_data*escala

    def file_location(self, i, cc):
        '''
        It allows to find a file of a certain subject.
        '''

        path_subject = self.cwd + '/' + str(i)+'_'+str(cc)
        return path_subject

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
import sys
from datetime import datetime
#import errno
import pandas as pd
import csv
from serial.tools import list_ports
import subprocess
import pymysql
from Stimulation_Acuity import Stimulus
from datetime import timezone
from pymongo import MongoClient




class Model(object):
    
    def __init__(self, name_db, name_collection):
        MONGO_URI = "mongodb://localhost:27017/"
        self.__client = MongoClient(MONGO_URI)
        self.__db = self.__client[name_db]
        self.__collection = self.__db[name_collection]        
        self.__fs = 250
        self.filtDesign()
        print("se diseño el filtro")       
        
               
    def startDevice(self):
        
#        servidor = Server()
#        servidor.port()
#        data = RandData()
#        data.sample()
        try:
            self.__process = subprocess.Popen('start python randData.py',
                                              shell=True,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,)
            output = self.__process.communicate()[0].decode('utf-8')
            print(output)
            
#            self.__Rand=subprocess.call('start /wait python randData.py', shell=True)
    #        if (Rand):
    #            msg = QMessageBox(self.ventana_principal)
    #            msg.setIcon(QMessageBox.Information)
    #            msg.setText("El dispositivo ha sido detectado")
    #            msg.setWindowTitle("Información")
    #            msg.show()
    #        else:
    #            msg = QMessageBox(self.ventana_principal)
    #            msg.setIcon(QMessageBox.Warning)
    #            msg.setText("El dispositivo no ha sido detectado o no se encuentra conectado")
    #            msg.setWindowTitle("Alerta!")
    #            msg.show()
    #            self.boton_iniciar.setEnabled(False)
        except KeyboardInterrupt:
            os.popen(r'TASKKILL /F /FI "WINDOWTITLE eq C:\Users\veroh\Anaconda3\python.exe"')
                
        
        self.__channels = 8
        self.__data = np.zeros((self.__channels, 2500))
        self.streams_EEG = resolve_stream('type', 'EEG')
        
    def stopDevice(self):
        os.popen(r'TASKKILL /F /FI "WINDOWTITLE eq C:\Users\veroh\Anaconda3\python.exe"')




    def startData(self):
        
        self.__channels = 8
        self.__data = np.zeros((self.__channels, 2500))
        self.streams_EEG = resolve_stream('type', 'EEG')
        self.__inlet = StreamInlet(self.streams_EEG[0], max_buflen=250)
        self.__inlet.pull_chunk()


         

    def stopData(self):
        
        self.__inlet.close_stream()
        print('Stop Data Modelo')
        
    def startStimulus(self):
        estimulo = Stimulus(self.p[0],self.p[1])
        estimulo.start_stimulus()
        

    def stopStimulus(self):
        pass
      

    def startZ(self):
        
        self.__inlet = StreamInlet(self.streams_EEG[0], max_buflen=250)
        

    def stopZ(self):
        
        self.__inlet.close_stream()
        print('Stop impedance')

    def readZ(self):
        
        sample, timestamp = self.__inlet.pull_sample()
        self.Z = []
        for i in range(0, 8):
            Z_i = ((sample[i])*np.sqrt(2))/(6*pow(10, -9))
            self.Z.append(Z_i/1000)
                 
        
    def readData(self):

        samples, timestamp = self.__inlet.pull_chunk()
        samples = np.transpose(np.asanyarray(samples))
        self.__laplace = np.zeros((1,2500))
        try:            
            self.__data = np.roll(self.__data, samples.shape[1])
            self.__laplace = np.roll(self.__laplace, samples.shape[1])
            print('sample',samples.shape)
            self.__data[0,0:samples.shape[1]] = samples[0,:] #FCz
            self.__data[1,0:samples.shape[1]] = samples[1,:] - samples[0,:]; #Oz - FCz
            self.__data[2,0:samples.shape[1]] = samples[2,:] - samples[0,:]; #O1 - FCz
            self.__data[3,0:samples.shape[1]] = samples[3,:] - samples[0,:]; #PO7 - FCz
            self.__data[4,0:samples.shape[1]] = samples[4,:] - samples[0,:]; #O2  - FCz
            self.__data[5,0:samples.shape[1]] = samples[5,:] - samples[0,:]; #PO8 - FCz
            self.__data[6,0:samples.shape[1]] = samples[6,:] - samples[0,:]; #PO3 - FCz
            self.__data[7,0:samples.shape[1]] = samples[7,:] - samples[0,:]; #PO4 - FCz
            self.__laplace[0,0:samples.shape[1]] = (samples[1,:]*2)-samples[2,:]-samples[4,:] #2Oz-O1-O2
        except:
            return

        self.__dataT = {'C1':samples[0,:],
                        'C2':self.__data[1,0:samples.shape[1]],
                        'C3':self.__data[2,0:samples.shape[1]],
                        'C4':self.__data[3,0:samples.shape[1]],
                        'C5':self.__data[4,0:samples.shape[1]],
                        'C6':self.__data[5,0:samples.shape[1]],
                        'C7':self.__data[6,0:samples.shape[1]],
                        'C8':self.__data[7,0:samples.shape[1]]}
        now = datetime.now()
        date = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
#        cwd = os.getcwd()
        cwd = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
        loc = cwd + '/'+date[0]       
        if not  os.path.isdir(loc):
            os.mkdir(loc)
            header=True
        else:
            header=False
        if not np.all(self.__data==0):
            r = pd.DataFrame(self.__dataT,columns=['C1','C2','C3','C4','C5','C6','C7','C8'])
            d = str(date[1])
            r['H']=pd.Series([d])
            r.to_csv(loc + '/'  + 'Record_'+str(self.p[0])+'_'+str(self.p[1])+'.csv' ,mode='a',header=header,index=False, sep=';')


    def filtDesign(self):
        order, self.lowpass = filter_design(
            self.__fs, locutoff=0, hicutoff=50, revfilt=0)
        order, self.highpass = filter_design(
            self.__fs, locutoff=5, hicutoff=0, revfilt=1)

    def filtData(self):
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
        self.filtData()
        nblock = 250
        noverlap = nblock/2;
                        
        self.f, self.Pxx = signal.welch(self.senal_filtrada_pasabandas, self.__fs,
                                        nperseg=self.__fs*2, noverlap=noverlap);
        
        self.ftg, self.Pxxtg = signal.welch(self.__laplace, 
            self.__fs, nperseg=self.__fs*2, noverlap=noverlap);
                            
        

    def returnLastData(self):        
        self.Pot()
        return (self.senal_filtrada_pasabandas, self.Pxx, self.f,
    self.laplace_filtrada_pasabandas, self.Pxxtg, self.ftg) # [0:6,:]
    
    def returnLastZ(self):
        self.readZ()
        return self.Z
    
    def returnLastStimulus(self):
        self.readData()
        return         
    
    def clinicalhistoryInformation(self, idAnswer,nameAnswer,lastnameAnswer,ccAnswer,
                     sexAnswer,eyeAnswer,ageAnswer,glassesAnswer,snellenAnswer,
                     CorrectionAnswer,stimulusAnswer,timeAnswer,
                     responsibleAnswer):

        if sexAnswer == 0:
            sexAnswer = 'Femenino'
        else:
            sexAnswer = 'Masculino'
        if eyeAnswer == 0:
            eyeAnswer = 'Derecho'
        else:
            eyeAnswer = 'Izquierdo'
        if glassesAnswer == 0:
            glassesAnswer = 'Si'
        else:
            glassesAnswer = 'No'
        if stimulusAnswer == 0:
            stimulusAnswer = 'Vernier'
        else:
             stimulusAnswer = 'Grating'
            
            
    def add_into_collection_one(self, data):
        self.__collection.insert_one(data)
        self.p = data['d'],data['cc']
        return True
    
    def add_into_collection_many(self, datas):
        self.__collection.insert_many(datas)
        print("Documentos agregados con éxito")
        
    def search_one(self, consult, proj):
        result = self.__collection.find_one(consult, proj)
        try:
            info_result = [result.get("d", None),result.get("nombre", None), result.get("apellidos", None), 
                           result.get("cc", None), result.get("sexo", None), result.get("dominante", None),
                           result.get("gafas", None),result.get("snellen", None),result.get("corregida", None),
                           result.get("estimulo", None),result.get("edad", None),result.get("tiempo", None),
                           result.get("rp", None),result.get("ubicacion")]
            self.p = info_result[0],info_result[3]
            return info_result
        except:
            return False
        
    def search_many(self, consult, proj, view=False):
        results = self.__collection.find(consult, proj)
        if view == True:
            for result in results:
                print(result)
        info_integrantes = list()
        for result in results:
            info = [result.get("d", None),result.get("nombre", None), result.get("apellidos", None), 
                    result.get("cc", None), result.get("sexo", None), result.get("dominante", None),
                    result.get("gafas", None),result.get("snellen", None),result.get("corregida", None),
                    result.get("estimulo", None),result.get("edad", None),result.get("tiempo", None),
                    result.get("rp", None),result.get("ubicacion")]
            info_integrantes.append(info)
        return info_integrantes
    def update_info(self, consult, data):
        self.__collection.update(consult, data)
        
    def delete_data(self, data):
        self.__collection.delete_one(data)
    
    def show_database(self):
        dbs = self.__client.list_database_names()
        for i in dbs:
            print(i)
        return dbs
    
    def show_collections(self):
        collections = self.db.list_collection_names()
        for collection in collections:
            print(collection)
        return collections
    
    def delete_collection(self, collection):
        self.__bd[collection].drop()
        
    def delete_db(self, db):
        self.__client[db].drop()

        
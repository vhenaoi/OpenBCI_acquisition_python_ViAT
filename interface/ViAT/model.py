import os
import csv
## Anexamos el directorio vista
#sys.path.append(r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\codigo_anestesia')

#import numpy as np
#from pyOpenBCI import OpenBCICyton
#from pylsl import StreamInfo, StreamOutlet
#from pylsl import StreamInlet, resolve_stream
#from serial.tools import list_ports
#from datetime import datetime
#from linearFIR import filter_design
#from nonlinear import hampelFilter
#from Server import Server
#import scipy.signal as signal
#serial_openBCI = 'DQ0081';

#import sys
from serial.tools import list_ports
## Anexamos el directorio vista
#sys.path.append(r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\codigo_anestesia')

import numpy as np
from pylsl import StreamInlet, resolve_stream
from linearFIR import filter_design
from nonlinear import hampelFilter
import scipy.signal as signal

class Model(object):
    
    @classmethod
    def puertos(self):
        self.lista_puertos = list_ports.comports();
        try:
            for i in range(len(self.lista_puertos)):
                ps = self.lista_puertos[i];
                if (i==len(self.lista_puertos)-1):
                    if (ps.serial_number[:5]=='DQ008'):
                        return True
            return False
        except:
            return False
            
    def __init__(self):
        self.__fs = 250;
        self.filtDesign();
        print("se diseño el filtro")
        
        self.__channels = 8
        self.__data = np.zeros((self.__channels - 2,2500))
        print("looking for an EEG stream...")
        self.__streams_EEG = resolve_stream('type', 'EEG')
        # create a new inlet to read from the stream
        # 
#        self.__inlet = StreamInlet(self.__streams_EEG[0],max_buflen=250)
#        
#        self.__inlet.pull_chunk()
        
    def startData(self):
        self.__inlet = StreamInlet(self.__streams_EEG[0],max_buflen=250)
        
        self.__inlet.pull_chunk()
    
    def stopData(self):
        self.__inlet.close_stream();
        print('Stop Data Modelo')
        
#    def saveData(self,data):
#        with open("prueba_almacenar.csv","a",newline='') as csvfile:
#            writer = csv.writer(csvfile, delimiter=',')
#            writer.writerows(self.__data)
#    
    def readData(self):
    
        #print(self.__inlet.samples_available())
        samples, timestamp = self.__inlet.pull_chunk()
        
#        with open(self.ruta,"a",newline='') as csvfile:
#                writer = csv.writer(csvfile, delimiter=',')
#                writer.writerows(samples)
        
        samples = np.transpose(np.asanyarray(samples));
        
        #print(samples.shape)
        
        #print(timestamp, sample[0])
        if (samples is None) or  (timestamp is None):
            return

        #for s in range(len(samples)):
        #    sample = samples[s]
            
        #self.__last_data = samples
            #print("EN modelo readData")
            #print(sample)
            #print(np.asarray(sample).shape)
        try:    
            self.__data = np.roll(self.__data,samples.shape[1]);
            
            
            #self.__data[:,0:samples.shape[1]] = samples
            
            #BIS
            self.__data[0,0:samples.shape[1]] = samples[2,:] - samples[1,:]; #F3 - Fz
            self.__data[1,0:samples.shape[1]] = samples[3,:] - samples[1,:]; #F4 - Fz
            
            #PRECUNEUS
            self.__data[2,0:samples.shape[1]] = samples[7,:] - samples[1,:]; #Pz - Fz
            self.__data[3,0:samples.shape[1]] = samples[4,:] - samples[1,:]; #Cz - Fz
            
            #SENSORIMOTOR
            self.__data[4,0:samples.shape[1]] = samples[5,:] - samples[3,:]; #C3 - F4
            self.__data[5,0:samples.shape[1]] = samples[6,:] - samples[2,:]; #C4 - F3
            
            #print(self.__data[0,:]);
            
        except:
            #print("Error en la resta");
            pass
        

    def filtDesign(self):
        order, self.lowpass = filter_design(self.__fs, locutoff = 0, hicutoff = 50, revfilt = 0);
        order, self.highpass = filter_design(self.__fs, locutoff = 5, hicutoff = 0, revfilt = 1);
    
    def filtData(self):
        self.readData()
        self.senal_filtrada_pasaaltas = signal.filtfilt(self.highpass, 1, self.__data);
        self.senal_filtrada_pasaaltas = hampelFilter(self.senal_filtrada_pasaaltas,6);
        self.senal_filtrada_pasabandas = signal.filtfilt(self.lowpass, 1, self.senal_filtrada_pasaaltas);
        
    
    def Pot(self):
        self.filtData();
        self.f,self.Pxx = signal.welch(self.senal_filtrada_pasabandas,self.__fs,nperseg=self.__fs*2, noverlap=self.__fs);
    
    def returnLastData(self):
        self.Pot()
        return self.senal_filtrada_pasabandas, self.Pxx, self.f;#[0:6,:]
        
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





class Model(object):

    def __init__(self):
        
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
        estimulo = Stimulus(self.__idAnswer,self.__ccAnswer) #The stimulus function is called for more information go to the stimulus
#        self.streams_Marks = resolve_stream('type', 'Markers')
#        self.__inlet_Marks = StreamInlet(self.streams_Marks[0])
#        self.__inlet_Marks.pull_chunk()
        estimulo.start_stimulus()
        

    def stopStimulus(self):
        pass
        
#        self.__inlet_Marks.close_stream()
#        print('Stop Data Modelo')
#        
        

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
#        try: 
#            sample_mark, timestamp = self.__inlet_Marks.pull_sample()
#        except:
#            sample_mark = None
        samples = np.transpose(np.asanyarray(samples))
#        print(sample_mark)
#        print(type(sample_mark))
#        if (samples is None) or (timestamp is None):
#            return
#        if (sample_mark is None):
#            sample_mark = [0]
#        print(sample_mark)
        try:            
            self.__data = np.roll(self.__data, samples.shape[1])
            self.__data[0,0:samples.shape[1]] = samples[0,:] #FCz
            self.__data[1,0:samples.shape[1]] = samples[1,:] - samples[0,:]; #Oz - FCz
            self.__data[2,0:samples.shape[1]] = samples[2,:] - samples[0,:]; #O1 - FCz
            self.__data[3,0:samples.shape[1]] = samples[3,:] - samples[0,:]; #PO7 - FCz
            self.__data[4,0:samples.shape[1]] = samples[4,:] - samples[0,:]; #O2  - FCz
            self.__data[5,0:samples.shape[1]] = samples[5,:] - samples[0,:]; #PO8 - FCz
            self.__data[6,0:samples.shape[1]] = samples[6,:] - samples[0,:]; #PO3 - FCz
            self.__data[7,0:samples.shape[1]] = samples[7,:] - samples[0,:]; #PO4 - FCz
#            if (sample_mark is not None):
#                Mark = sample_mark*samples.shape[1]
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
#        print(self.__dataT)
        now = datetime.now()
        date = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
        loc = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Registers'+ '/'+date[0]       
        if not  os.path.isdir(loc):
            os.mkdir(loc)
            header=True
        else:
            header=False
        if not np.all(self.__data==0):
            r = pd.DataFrame(self.__dataT,columns=['C1','C2','C3','C4','C5','C6','C7','C8'])
            timestamp = [datetime.fromtimestamp(x) for x in timestamp]
            r['H']=timestamp
            r.to_csv(loc + '/'  + 'Registry_'+str(self.__idAnswer)+'_'+str(self.__ccAnswer)+'.csv' ,mode='a',header=header,index=False, sep=';')
#            dateT =pd.DataFrame(date,columns=['D'])
#            dateT.to_csv(loc + '/'  + 'Registry_'+str(self.__idAnswer)+'_'+str(self.__ccAnswer)+'.csv' ,mode='a',header=False,index=False, sep=';')

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

    def Pot(self):
        self.filtData()
        self.f, self.Pxx = signal.welch(
            self.senal_filtrada_pasabandas, 
            self.__fs, nperseg=self.__fs*2, 
            noverlap=self.__fs)

    def returnLastData(self):        
        self.Pot()
        return self.senal_filtrada_pasabandas, self.Pxx, self.f # [0:6,:]
    
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

        History=pd.DataFrame()
        Subject=pd.DataFrame()
        Subjects=pd.DataFrame()
        self.__idAnswer = idAnswer
        self.__ccAnswer = ccAnswer
        self.__ageAnswer =ageAnswer
        self.__glassesAnswer = glassesAnswer
        self.__snellenAnswer = snellenAnswer
        self.__CorrectionAnswer = CorrectionAnswer
        now = datetime.now()
        self.__date = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
        path = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HistoriaClinicaViAT'
        path_Marks = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Marks'
        self.__path_Register = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Registers'
        if sexAnswer == 0:
            sexAnswer = 'Femenino'
        else:
            sexAnswer = 'Masculino'
        if eyeAnswer == 0:
            eyeAnswer = 'Derecho'
        else:
            eyeAnswer = 'Izquierdo'
        gen = pd.DataFrame({'id':[self.__idAnswer],
                            'nombre':[nameAnswer], 
                            'apellido':[lastnameAnswer], 
                            'cc':[self.__ccAnswer], 
                            'sexo':[sexAnswer],
                            'ojo dominante':[eyeAnswer]
                            })
        if glassesAnswer == 0:
            glassesAnswer = 'Si'
        else:
            glassesAnswer = 'No'
        if snellenAnswer == 0:
            snellenAnswer = '20/20'
        elif snellenAnswer == 1:
            snellenAnswer = '20/16'
        elif snellenAnswer == 2:
            snellenAnswer = '20/25'
        elif snellenAnswer == 3:
            snellenAnswer = '20/40'
        elif snellenAnswer == 4:
            snellenAnswer = '20/50'
        elif snellenAnswer == 5:
            snellenAnswer = '20/63'
        elif snellenAnswer == 6:
            snellenAnswer = '20/80'
        elif snellenAnswer == 7:
            snellenAnswer = '20/100'
        elif snellenAnswer == 8:
            snellenAnswer = '20/125'
        elif snellenAnswer == 9:
            snellenAnswer = '20/160'
        elif snellenAnswer == 10:
            snellenAnswer = '20/200'
        if CorrectionAnswer == 0:
            CorrectionAnswer = 'NaN'
        elif CorrectionAnswer == 1:
            CorrectionAnswer = '20/16'
        elif CorrectionAnswer == 2:
            CorrectionAnswer = '20/20'
        elif CorrectionAnswer == 3:
            CorrectionAnswer = '20/25'
        elif CorrectionAnswer == 4:
            CorrectionAnswer = '20/40'
        elif CorrectionAnswer == 5:
            CorrectionAnswer = '20/50'
        elif CorrectionAnswer == 6:
            CorrectionAnswer = '20/63'
        elif CorrectionAnswer == 7:
            CorrectionAnswer = '20/80'
        elif CorrectionAnswer == 8:
            CorrectionAnswer = '20/100'
        elif CorrectionAnswer == 9:
            CorrectionAnswer = '20/125'
        elif CorrectionAnswer == 10:
            CorrectionAnswer = '20/160'
        elif CorrectionAnswer == 11:
            CorrectionAnswer = '20/200'
        if stimulusAnswer == 0:
            stimulusAnswer = 'Vernier'
        else:
             stimulusAnswer = 'Grating'
            
        var = pd.DataFrame({'edad':[self.__ageAnswer],
                                     'gafas':[self.__glassesAnswer],
                                     'snellen':[self.__snellenAnswer],
                                     'snellen corregido':[self.__CorrectionAnswer],
                                     'estimulo':[stimulusAnswer],
                                     'tiempo de accidente visual':[timeAnswer],
                                     'responsable':[responsibleAnswer],
                                     'hora':[self.__date[1]],'Marca':[path_Marks+ '/' +'Mark_H_'+self.__date[1][0:2]+'.csv'],
                                             'Registro':[self.__path_Register+ '/' +'Registry_H_'+self.__date[1][0:2]+'.csv']
                                     })
        History = History.append(var)
        Subject = Subject.append(gen)
        Subjects = Subjects.append(gen)
        fijo = path + '/' +  self.__idAnswer + '_' + self.__ccAnswer
        if os.path.isdir(fijo):
            variable=(fijo + '/' + self.__date[0])
            Subjects.to_csv(path + '/'  + 'Subjects.csv' ,mode='a',header=False, index=False, sep=';')
            if os.path.isdir(variable):
                History.to_csv(variable + '/'  + 'History.csv' ,mode='a',header=False, index=False, sep=';')
            else:
                os.mkdir(variable)
                History.to_csv(variable + '/'  + 'History.csv' , index=False,sep=';')
        else:
            os.mkdir(fijo)
            variable=(fijo + '/' + self.__date[0])
            os.mkdir(variable)
            print('se creo el segundo directorio')
            print(variable)
            Subject.to_csv(fijo + '/'  + 'Suject.csv' , index=False, sep=';')
            History.to_csv(variable + '/'  + 'History.csv' ,index=False, sep=';')
            Subjects.to_csv(path + '/'  + 'Subjects.csv' ,mode='a',index=False, sep=';')
            
        
      
    def webclinicalhistoryInformation(self):
        ############### CONFIGURAR ESTO ###################
        idAnswer = self.__idAnswer
        ccAnswer = self.__ccAnswer
        ageAnswer = self.__ageAnswer
        glassesAnswer = self.__glassesAnswer
        snellenAnswer = self.__snellenAnswer
        CorrectionAnswer = self.__CorrectionAnswer
        date = self.__date
        path_Register = self.__path_Register
        # Abre conexion con la base de datos
        db = pymysql.connect(host="127.0.0.1",
                             user="root",
                             database="viat"
                             )
        ##################################################
        cursor = db.cursor()

        # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO registro(ID, CC,EDAD,GAFAS,AA,AL,AD,FECHA,REGISTROS) \
           VALUES ("+idAnswer,ccAnswer,ageAnswer,glassesAnswer,snellenAnswer,CorrectionAnswer,date,path_Register+")".format()
        try:
           # Execute the SQL command
           cursor.execute(sql)
#           cursor.execute("SELECT VERSION()")
           # Commit your changes in the database
           db.commit()
        except:
           # Rollback in case there is any error
           db.rollback()
        
        
        # desconectar del servidor
        db.close()
    
    def searchClinicalhistory(self):
        ############### CONFIGURAR ESTO ###################
        # Open database connection
        db = pymysql.connect(host="127.0.0.1",
                             user="root",
                             database="viat"
                             )
        ##################################################
        
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        
        # Prepare SQL query to READ a record into the database.
        sql = "SELECT * FROM registro \
        WHERE ID = 1134234371".format(0)
        
        # Execute the SQL command
        cursor.execute(sql)
        
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
           ID = row[0]
           CC = row[1]
           EDAD = row[2]
           GAFAS = row[3]
           AA = row[4]
           AL = row[5]
           AD = row[6]
           FECHA = row[7]
           REGISTROS =row[8]
           # Now print fetched result
           print (ID+CC+EDAD+GAFAS+AA+AL+AD+FECHA+REGISTROS.format(ID,CC,EDAD,GAFAS,AA,AL,AD,FECHA,REGISTROS))
        
        # disconnect from server
        db.close()
        
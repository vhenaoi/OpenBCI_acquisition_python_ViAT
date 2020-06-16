import pandas as pd 
import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from spectrum import pmtm
from spectrum.tools import nextpow2
import os
import csv
import errno
import scipy.signal as signal2
from datetime import datetime

class Processing(object):
    def __init__(self,id_Subject,cc_Subject,date,loc,save):
        self.__subject = id_Subject
        self.__cc = cc_Subject
        self.__date = date
        self.loc = loc
        self.path_save=save
    
    def run(self):
        self.__record = pd.DataFrame()
        name = str(self.__subject)+'_'+str(self.__cc)
        path_Record = self.loc +'/' +self.__date +'/Record_'+name+'.csv'
        path_Mark = self.loc +'/' +self.__date +'/Mark_'+name+'.csv'
        self.__fs = 250
        self.__time_stimuli = 4 # time to stimulation + time rest
        values = []
        frec = []
        now = datetime.now()
        d = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
        path_new = self.path_save+'/'+d[0]
        try:
            os.mkdir(path_new)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise     
        print ('Building ... ' + str(self.__subject)+'_'+str(self.__cc))
        Record=pd.read_csv(path_Record, sep=';', index_col=0)
        Mark=pd.read_csv(path_Mark, sep=';', index_col=0)
        index=list(range(0,len(Record['C1'])))
        Record['i'] = index
        listMark = Mark.values.tolist()
        Markdata = []
        for i in range(0,len(listMark)-1):
            start=list(Record.i[Record.H == Mark.iloc[i,0]])
            end=list(Record.i[Record.H == Mark.iloc[i+1,0]])
            MO=Record[start[0]:end[0]].drop(columns=['H','i'])
            Markdata.append(MO)
            
        # 0: FCZ #1: Oz -FCZ #2: O1-FCZ #3: PO7-FCZ #4: O2-FCZ #5: PO8-FCZ #6: PO3-FCZ #7: PO4-FCZ
        for i in range(0,len(Markdata)-1):
            data = Markdata[i].to_numpy()
            Sk_complex , weights , _ = pmtm(data[i], NW=2, k=4, show=False)
            Sk = abs(Sk_complex)**2;
            Sk = Sk.transpose();
            Sk = np.mean(Sk * weights, axis=1);
            frequencies = np.linspace(0,250,1024)
            position = np.where((frequencies >= 7) & (frequencies <= 8.5))
            maxValue = np.max(Sk[position[0]])
            values.append(maxValue)
            posicion= np.where(Sk==maxValue)
            maxValuex = frequencies[posicion[0]]
            frec.append(maxValuex[0])
            doc = pd.DataFrame(values,columns=['Max'])
            doc['Fre']=frec
            if not  os.path.isdir(self.loc):
                os.mkdir(self.loc)
                header=True
            else:
                if os.path.isfile(self.loc + name):
                    header=False
                else:
                    header=True
        doc.to_csv(path_new+'/'+'Parameters'+'_'+name+'.csv' ,mode='a',header=header,index=True, sep=';')           
#        return Record,Mark,index,listMark,start,end,Markdata,maxValue,values,frec
    
# In[To run individually]
if __name__ == '__main__':
    estimulo = Processing('p','p','06-15-2020')
    Record,Mark,index,listMark,start,end,Markdata,maxValue,maxi,frec=estimulo.run()
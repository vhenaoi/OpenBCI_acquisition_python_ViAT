import pandas as pd
import numpy as np
from spectrum import pmtm
import os
import errno
from datetime import datetime


class Processing(object):
    '''
    Spectral estimation with multitapering
    '''

    def __init__(self, id_Subject, cc_Subject, date, loc, save):
        '''
        Rec: ID of the subject registered in the database,
            ID of the subject registered in the database, date of registration,
            location of the registration and location to save.
        Func: Set the variables with the received elements.
        '''
        self.__subject = id_Subject
        self.__cc = cc_Subject
        self.__date = date
        self.loc = loc
        self.path_save = save

    def run(self):
        '''
        Create the directory to save the processing results, read the 
        registration and mark data, compare both files and separate the 
        signal by each mark, then take each group of marks and apply 
        Multitaper processing
        '''
        self.__record = pd.DataFrame()
        name = str(self.__subject)+'_'+str(self.__cc)
        path_Record = self.loc + '/'+name+'/' + self.__date + '/Record_'+name+'.csv'
        path_Mark = self.loc + '/'+name + '/' + self.__date + '/Mark_'+name+'.csv'
        self.__fs = 250
        self.__time_stimuli = 4  # time to stimulation + time rest
        values = []
        frec = []
        now = datetime.now()
        d = (now.strftime("%m-%d-%Y"), now.strftime("%H-%M-%S"))
        path = self.path_save+'/'+name
        path_new = path + '/' + d[0]
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
            if not os.path.isdir(path_new):
                os.mkdir(path_new)
            else:
                pass
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        print('Building ... ' + str(self.__subject)+'_'+str(self.__cc))
        Record = pd.read_csv(path_Record, sep=';', index_col=0)
        Mark = pd.read_csv(path_Mark, sep=';', index_col=0)
        index = list(range(0, len(Record['C1'])))
        Record['i'] = index
        listMark = Mark.values.tolist()
        Markdata = []
        for i in range(0, len(listMark)-1):
            start = list(Record.i[Record.H == Mark.iloc[i, 0]])
            end = list(Record.i[Record.H == Mark.iloc[i+1, 0]])
            MO = Record[start[0]:end[0]].drop(columns=['H', 'i'])
            Markdata.append(MO)

        # 0: FCZ #1: Oz -FCZ #2: O1-FCZ #3: PO7-FCZ #4: O2-FCZ #5: PO8-FCZ #6: PO3-FCZ #7: PO4-FCZ
        for i in range(0, len(Markdata)-1):
            data = Markdata[i].to_numpy()
            Sk_complex, weights, _ = pmtm(data[i], NW=2, k=4, show=False)
            Sk = abs(Sk_complex)**2
            Sk = Sk.transpose()
            Sk = np.mean(Sk * weights, axis=1)
            frequencies = np.linspace(0, 250, 1024)
            position = np.where((frequencies >= 7) & (frequencies <= 8.5))
            maxValue = np.max(Sk[position[0]])
            values.append(maxValue)
            posicion = np.where(Sk == maxValue)
            maxValuex = frequencies[posicion[0]]
            frec.append(maxValuex[0])
            doc = pd.DataFrame(values, columns=['Max'])
            doc['Fre'] = frec
            if not os.path.isdir(self.loc):
                os.mkdir(self.loc)
                header = True
            else:
                if os.path.isfile(self.loc + name):
                    header = False
                else:
                    header = True
        doc.to_csv(path_new+'/'+'Parameters'+'_'+name+'.csv',
                   mode='a', header=header, index=True, sep=';')
        # return Record,Mark,data,index,listMark,start,end,Markdata,maxValue,values,frec
        # return data


# In[To run individually]
if __name__ == '__main__':
    path_in = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
    path_out = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Processing'
    estimulo = Processing('H1', '1152207135', '06-28-2020', path_in, path_out)
    # Record,Mark,NoMark,index,listMark,start,end,Markdata,maxValue,values,frec = estimulo.run()
    estimulo.run()

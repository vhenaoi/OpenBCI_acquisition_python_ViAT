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
    def __init__(self,id_Subject,cc_Subject,date):
        self.__subject = id_Subject
        self.__cc = cc_Subject
        self.__date = date
    
    def run(self):
        self.__record = pd.DataFrame()
        self.__maxi = pd.DataFrame()
        self.__fre = pd.DataFrame()
        self.__total = pd.DataFrame()
        loc = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'
        path_Record = loc +'/' +self.__date +'/Record_'+str(self.__subject)+'_'+str(self.__cc)+'.csv'
        path_Mark = loc +'/' +self.__date +'/Mark_'+str(self.__subject)+'_'+str(self.__cc)+'.csv'
        path_save = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Processing'
        self.__fs = 250
        self.__time_stimuli = 4 # time to stimulation + time rest 
        now = datetime.now()
        d = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
        path_new = path_save+'/'+d[0]
        try:
            os.mkdir(path_new)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise     
        print ('Building ... ' + str(self.__subject)+'_'+str(self.__cc))
        Record=pd.read_csv(path_Record, sep=';', index_col=0)
        Mark=pd.read_csv(path_Mark, sep=';', index_col=0)
        c = Mark.merge(Record, how='inner')
        Record[Record.H == c.iloc[0,0]]
        Record[Record.H == c.iloc[1,0]]

    #            Record = pd.read_csv(path_Record, header=None) 
    #            Mark = pd.read_csv(path_Mark, header=None) 
    #            Record = Record.values
    #            Record = Record[0:8,:]*100000
    #            # 0: FCZ #1: Oz -FCZ #2: O1-FCZ #3: PO7-FCZ #4: O2-FCZ #5: PO8-FCZ #6: PO3-FCZ #7: PO4-FCZ
    #            f = lambda A, n=time_stimuli*fs: [A[i:i+n] for i in range(0, len(A), n)]
    #            signal = f(signal)
    #                
    #            values = []
    #            frec = []
    #                
    #    #        
    #    #            for i in range(0,7):
    #    ##                values.append(fourierTransform(signal[i],fs))
    #    #                datos = signal[i];
    #    #
    #    #            
    #    ##                Sk_complex , weights , _ = pmtm(datos , NW=2, k=3, show=False)
    #    #                Sk_complex , weights , _ = pmtm(datos , NW=2, k=4, show=False)
    #    ##                Sk_complex , weights , _ = pmtm(datos , NW=2.5, k=5, show=False)
    #    #                Sk = abs(Sk_complex)**2;
    #    #                Sk = Sk.transpose();
    #    #                Sk = np.mean(Sk * weights, axis=1);
    #    #                nblock = 250
    #    #                overlap = nblock/2;#10 
    #    #                win = signal2.hamming(int(nblock),True);
    #    #                f, Pxx = signal2.welch(datos, fs, window=win, noverlap=overlap, nfft=nblock, return_onesided=True);
    #    ##                plt.figure()
    #    ##                plt.plot(datos)
    #    #                plt.stem(f,Pxx)
    #    ##                plt.xlabel("Samples")
    #    ##                plt.ylabel("PSD")
    #    ##                plt.title('Welch periodogram ' + subject_name + register )
    #    ##                plt.xlim([0,40])
    #    #                imgWelch = ('Signal ' + subject_name + 'acuity_'+ y + str(i))
    #    ##                plt.savefig( path_save + '/' + subject_name + '/'  + imgWelch + 'acuity_'+ y + str(i) +'.jpg')
    #    #
    #    #                
    #    #                    
    #    #                #Skp = mtm_epochs(datos, 250);
    #    #                    
    #    #                #from pylab import semilogy
    #    ##                frequencies = np.linspace(0,250,1024)
    #    ##                position = np.where((frequencies >= 0) & (frequencies <= 40))
    #    ###                position = np.where((frequencies >= 7) & (frequencies <= 8.5))
    #    ##                maxValue = np.max(Sk[position[0]])
    #    ##                values.append(maxValue)
    #    ##                posicion= np.where(Sk==maxValue)
    #    ##                maxValuex = frequencies[posicion[0]]
    #    ##                frec.append(maxValuex[0])
    #    #            #plt.semilogy(frequencies,Skp);
    #    #            #plt.stem(frequencies,Sk);
    #    #            #
    #    #            #        plt.xlim([0, 6]);
    #    #            #        plt.show()
    #    #                    
    #    ##            x = np.array([0.30103,0.47712125,0.67778071,0.8750612,1.07918125,1.27300127,1.47712125])         
    #    ##            x = np.array([0.30103,0.47712125,0.574031268,0.67778071,0.77815125,
    #    ##                              0.8750612,0.971971276,1.07918125,1.176091259,1.27300127,
    #    ##                              1.380211242,1.47712125])
    #    ##            y_in = np.array(values)
    #    ##            y_plus = np.linspace(np.array(values[5]-1),-1,num=5)
    #    ##            y = np.concatenate((y_in, y_plus), axis=None) 
    #    ##            plt.figure()
    #    ##            plt.axhline(0, color="black")
    #    ##            #    plt.scatter(1.16,0,color="blue")
    #    ##            #    plt.xlim(1.15,1.17)
    #    ##            #    plt.ylim(-1,1)
    #    ##            plt.grid(True)
    #    ##            result = regression (x, y, new_path + subject_name)
    #    ##            df = pd.DataFrame(np.array(result), columns = [name]).T 
    #    ##            acuity = acuity.append(df)
    #    ##            m = pd.DataFrame(np.array(values), columns = [name]).T 
    #    ##            f = pd.DataFrame(np.array(frec), columns = [name]).T
    #    ##            maxi=maxi.append(m)
    #    ##            fre = fre.append(f)
    #    ###            plt.savefig( path_save + '/' + subject_name + '/'  + name + '.jpg') 
    #    ###    #    writer.writerows(acuity)
    #    ###        acuity.to_csv( path_save + '/' + subject_name + '/'  + 'Value.csv' , sep=';')
    #    ##        maxi.to_csv( path_save + '/' + subject_name + '/'  + 'Max.csv' , sep=';')
    #    ##        fre.to_csv( path_save + '/' + subject_name + '/'  + 'fre.csv' , sep=';')
    #    ##    acuity.to_csv( path_save + '/'  + 'Value'+tipe_name+'.csv' , sep=';')
    #    ##    acuity.to_csv( path_save + '/'  + 'Value'+suject_vector[j]+'.csv' , sep=';')
    #    #    
    #    #
    #    #
    #    #
    #    #   
# In[To run individually]
if __name__ == '__main__':
    estimulo = Processing('H1','1152207135','06-14-2020')
    estimulo.run()
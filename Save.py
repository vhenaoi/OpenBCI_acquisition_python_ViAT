from Mark import Mark
from stimulus import Stimulus
import time
tz=time.time()
#import numpy as np
#import csv
#
#SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
#SCALE_FACTOR_AUX = 0.002 / (2**4)
#mysample,sample_mark = Server.lsl_streamers()
#
#def Save(mysample,sample_mark):        
#    with open("data.csv","a") as csvfile:
#        writer = csv.writer(csvfile, delimiter=',')
#        writer.writerows([np.array(mysample)])
#    if sample_mark is not None:
#        M = sample_mark
#    else:
#        M = 0
#        data2write = np.array(mysample.channels_data)*SCALE_FACTOR_EEG
#        data2write = np.append(data2write,[M])
#        data2write = [data2write]

if __name__ == '__main__':
#    servidor = Server()
    estumilo = Stimulus()
    marca = Mark()
    
#    servidor.startServer();

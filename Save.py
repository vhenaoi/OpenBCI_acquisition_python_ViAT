from Marks import Marks
from Server import Server
import numpy as np
import csv
from datetime import datetime

sample_mark, timestamp = Marks.Marks()
mysample = Server.lslStreamers()

def Save(mysample,sample_mark,timestamp):        
    with open("data.csv","a") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
    if sample_mark is not None:
        data2write = np.append(sample_mark,datetime.fromtimestamp(timestamp))
        writer.writerows([np.array(data2write)])
    else:
        data2write = np.array(mysample.channels_data)*(4500000)/24/(2**23-1)
        data2write = np.append(data2write)
        writer.writerows([np.array(data2write)])

if __name__ == '__main__':
    Save = Save()



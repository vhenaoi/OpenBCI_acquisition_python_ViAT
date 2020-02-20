# In[Libraries]
import numpy as np
from pylsl import StreamInfo, StreamOutlet
#from Save import tz
import time
from pylsl import StreamInlet, resolve_stream


class Mark(object):
    print("looking for a marker stream...")
    streams = resolve_stream('type', 'Markers')
    inlet = StreamInlet(streams[0])
    inlet.pull_chunk()
    sample_mark, timestamp = inlet.pull_sample()
    if sample_mark is not None:
        print(sample_mark)
        print(timestamp)
#    def __init__(self):
#        #Marker
#        self.__info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'float32', 'myuidw43536')
#        # next make an outlet
#        self.__outlet = StreamOutlet(self.__info)
#        self.__start = False
#        time.sleep(1)
#        
#    def markers(self):
#        print("now sending markers...")
#        tm= time.time()
#        if tm-tz>=0:
#            self.__outlet.push_sample(np.array([1]))
#            self.__outlet.__del__
#        tm=tz
#    def Inlet(self):
#        print("looking for a marker stream...")
#        streams = resolve_stream('type', 'Markers')
#        inlet = StreamInlet(streams[0])
#        inlet.pull_chunk()
#        sample_mark, timestamp = inlet.pull_sample()
#        if sample_mark is not None:
#            print(sample_mark)
#            print(timestamp)
#            tm=time.time()
#            print(tm-tz)
#        return(sample_mark)


if __name__ == '__main__':
    In = Mark()
#    inlet = In.Inlet()
#    print(inlet)


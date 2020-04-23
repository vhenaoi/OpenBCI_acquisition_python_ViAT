import numpy as np
from pylsl import StreamInlet, resolve_stream

class Impedance(object):
    def __init__(self):
        # first resolve an EEG stream on the lab network
        streams = resolve_stream('type', 'EEG')
        # create a new inlet to read from the stream
        self.inlet = StreamInlet(streams[0])
    def sample(self):
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        sample, timestamp = self.inlet.pull_sample()
#        print(timestamp, sample)
        Z=[]    
        for i in range(0,8):
            Z_i=((sample[i])*np.sqrt(2))/(6*pow(10,-9))
            Z.append(Z_i/1000)
        return(sample,Z)

if __name__ == '__main__':
    while True:
        Z = Impedance()
        S = Z.sample()
        print('sample',S[0])
        print('impedance',S[1])






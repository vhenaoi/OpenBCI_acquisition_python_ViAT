"""Example program to demonstrate how to send a multi-channel time series to
LSL.

https://github.com/sccn/lsl_archived/tree/master/LSL/liblsl-Python/examples 
"""

import time
from random import random as rand

from pylsl import StreamInfo, StreamOutlet
import numpy as np


class RandData(object):

    # first create a new stream info (here we set the name to BioSemi,
    # the content-type to EEG, 8 channels, 100 Hz, and float-valued data) The
    # last value would be the serial number of the device or some other more or
    # less locally unique identifier for the stream as far as available (you
    # could also omit it but interrupted connections wouldn't auto-recover)
    def __init__(self):
        '''
        Define variables for StreamInfo and for StreamOutlet
        '''
        self.info = StreamInfo('BioSemi', 'EEG', 8, 250,
                               'float32', 'myuid34234')

        # next make an outlet
        self.outlet = StreamOutlet(self.info)
        print('Enviando datos')

    def sample(self):
        '''
        Creates an array of random data in a continuous cycle and generates 
        a push_sample, pushing one sample per channel to the output.
        '''
        while True:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            self.mysample = np.array([rand(), rand(), rand(), rand(), rand(),
                                      rand(), rand(), rand()])
            # now send it and wait for a bit
            self.outlet.push_sample(self.mysample)
#            print(self.mysample)
            time.sleep(0.003)


# In[To run individually]
if __name__ == '__main__':
    data = RandData()
    data.sample()

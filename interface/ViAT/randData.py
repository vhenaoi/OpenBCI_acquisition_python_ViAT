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
        self.info = StreamInfo('BioSemi', 'EEG', 8, 250,
                               'float32', 'myuid34234')

        # next make an outlet
        self.outlet = StreamOutlet(self.info)

    print("now sending data...")

    def sample(self):
        while True:
            # make a new random 8-channel sample; this is converted into a
            # pylsl.vectorf (the data type that is expected by push_sample)
            self.mysample = np.array([1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0])/10
            self.mysample = self.mysample.tolist()
#            [rand(), rand(), rand(), rand(),rand(), rand(), rand(), rand()]
            # now send it and wait for a bit
            self.outlet.push_sample(self.mysample)
            print(self.mysample)
            time.sleep(0.01)

# In[To run individually]
if __name__ == '__main__':
    data = RandData()
    data.sample()

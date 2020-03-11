'Autor: Verónica Henao Isaza'

'''Receive Mark
A data stream with Mark feature is created
A stream inlet; Inlets are used to receive streaming data 
(and meta-data) from the lab network.
Pull_chunk; Pull a chunk of samples from the inlet.
While pull samples and is not None.
Mark == 99.0
 '''


import numpy as np
from pylsl import StreamInfo, StreamOutlet
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

if __name__ == '__main__':
    In = Mark()



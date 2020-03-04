'Autor: Verónica Henao Isaza'

'''Send Mark
A data stream with Mark feature is created
A stream inlet; Inlets are used to receive streaming data 
(and meta-data) from the lab network.
Pull_chunk; Pull a chunk of samples from the inlet.
While pull samples and is not None.
Mark == 99.0
 '''
 
from pylsl import StreamInlet, resolve_stream
from datetime import datetime

    
if __name__ == '__main__':
    
    while True:
        print('Creating the flow')
        streams = resolve_stream('type', 'Markers')
        inlet = StreamInlet(streams[0])
        inlet.pull_chunk()
        while True:
            sample_mark, timestamp = inlet.pull_sample()
            if sample_mark is not None:
                print(sample_mark)
                print(type(sample_mark))
                print(datetime.fromtimestamp(timestamp))
                if sample_mark[0] == 99.0:
                    break

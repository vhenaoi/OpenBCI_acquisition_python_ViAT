from pylsl import StreamInlet, resolve_stream
from datetime import datetime

    
if __name__ == '__main__':
    
    while True:
        print('Creando el flujo')
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

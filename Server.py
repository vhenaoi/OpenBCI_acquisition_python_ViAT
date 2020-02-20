# In[Libraries]
from pyOpenBCI import OpenBCICyton
from pylsl import StreamInfo, StreamOutlet
import numpy as np
from serial.tools import list_ports
from datetime import datetime
serial_openBCI = 'DQ0081';
class Server(object):
    
    def __init__(self):
        # In[Information]
        print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")
        self.__info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCItestEEG')
        print("Creating LSL stream for AUX. \nName: OpenBCIAUX\nID: OpenBCItestEEG\n")
        self.__info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')
        # In[Outlet]
        self.__outlet_eeg = StreamOutlet(self.__info_eeg)
        self.__outlet_aux = StreamOutlet(self.__info_aux)
        #board = OpenBCICyton()
    # In[Functions]
    def lslStreamers(self,sample):
#        print(sample)
        try:
            SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
            SCALE_FACTOR_AUX = 0.002 / (2**4)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            self.__outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG,timestamp)
            self.__outlet_aux.push_sample(np.array(sample.aux_data)*SCALE_FACTOR_AUX,timestamp)
        except:
            print('Corrupted data')
#    def startServer(self):    
#        board = OpenBCICyton(port='COM6', daisy=False)
#        board.start_stream(self.lslStreamers)
#        print("Error")
        
    def port(self):
        Lista_puertos = list_ports.comports();
        print (Lista_puertos)
        for serial_device in Lista_puertos:
            code_serial = serial_device.serial_number 
            if code_serial != None:
                if code_serial.startswith(serial_openBCI):            
                    board = OpenBCICyton(port=serial_device.device, daisy=False)
                    Data = self.lslStreamers           
                    board.start_stream(Data)
                else:
                    print('No hay dispositivo OpenBCI, conectar y volver a iniciar el programa')
                    input('Presione enter para finalizar ...')
        
        
if __name__ == '__main__':
    servidor = Server()
    servidor.port();

'''
Created on 2020

@author: Verónica Henao Isaza


This module provides communication with the OpenBCI CYTON BOARD device.
The OpenBCI Cyton Board is an Arduino-compatible, 8-channel neural interface 
with a 32-bit processor. At its core, the OpenBCI Cyton Board implements the 
PIC32MX250F128B microcontroller, giving it lots of local memory and fast 
processing speeds.

The module identifies the OpenBCI device by checking the system ports 
'''

# In[Libraries]
from pyOpenBCI import OpenBCICyton
from pylsl import StreamInfo, StreamOutlet
import numpy as np
from serial.tools import list_ports
from datetime import datetime
serial_openBCI = 'DQ0081';

'''
OpenBCICyton: OpenBCICyton handles the connection to an OpenBCI Cyton board.

    The OpenBCICyton class interfaces with the Cyton Dongle and the Cyton +
    board to parse the data received and output it to Python as a 
    OpenBCISample object.

    Args:
        port: A string representing the COM port that the Cyton Dongle 
        is connected to. e.g for Windows users 'COM3', for MacOS or Linux users '/dev/ttyUSB1'. If no port is specified it will try to find the first port available.

        daisy: A boolean indicating if there is a Daisy connected to the 
        Cyton board.

        baud: An integer specifying the baudrate of the serial connection. 
        The maximum baudrate of the Cyton board is 115200.

        timeout: An float specifying the maximum milliseconds to wait for 
        serial data.

        max_packets_skipped: An integer specifying how many packets can 
        be dropped before attempting to reconnect.

for more information https://pypi.org/project/pyOpenBCI/

numpy: Operational

pylsl: Communication of data

StreamInfo: Whenever a program wants to provide a new stream on the 
    lab network it will typically first create a StreamInfo to 
    describe its properties and then construct a StreamOutlet 
    with it to create the stream on the network.

StreamOutlet: Outlets are used to make streaming data (and the meta-data) available on 
    the lab network.
'''


class Server(object):
    '''
    Create a StreamInfo for the 8 EEG channels and a StreamInfo for the 3 auxiliary channels (accelerometers)
    
    For each StreamInfo create a StreamOutlet
    '''
    
    def __init__(self):
        #[Information]
        print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")
        self.__info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCItestEEG')
        print("Creating LSL stream for AUX. \nName: OpenBCIAUX\nID: OpenBCItestEEG\n")
        self.__info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')
        #[Outlet]
        self.__outlet_eeg = StreamOutlet(self.__info_eeg)
        self.__outlet_aux = StreamOutlet(self.__info_aux)
        #board = OpenBCICyton()
    # In[Functions]
    def lslStreamers(self,sample):
        '''
        Perform a data conversion to allow viewing in microvolts
        
        :timestamp: It allows sending a time stamp associated with the data 
            through the pipeline
        
        :push_sample: Push a sample into the outlet. Each entry in the list 
            corresponds to one channel.
        
        '''
        try:
            SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
            SCALE_FACTOR_AUX = 0.002 / (2**4)
            now = datetime.now()
            timestamp = datetime.timestamp(now)  
            self.__outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG,timestamp)
            self.__outlet_aux.push_sample(np.array(sample.aux_data)*SCALE_FACTOR_AUX,timestamp)
#            R = (((sample.channels_data)*SCALE_FACTOR_EEG)*np.sqrt(2))/(6*pow(10,-9))
#            print(R)
        except:
            print('Corrupted data')
        
    def port(self):
        '''
        :list_ports: This module will provide a function called comports that 
            returns an iterable (generator or list) that will enumerate 
            available com ports. Note that on some systems non-existent ports 
            may be listed.
            
        :start_stream: Start handling streaming data from the board. 
            Call a provided callback for every single sample that is processed.
        '''
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
        
# In[To run individually]        
if __name__ == '__main__':
    servidor = Server()
    servidor.port();
    

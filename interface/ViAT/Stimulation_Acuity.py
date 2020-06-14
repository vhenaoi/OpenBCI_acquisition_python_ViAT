'''
Created on 2020

@author: Verónica Henao Isaza


This module provides a stimulation method for steady-state visual 
evoked potentials (SSVEP).
Sensitivity Vernier were conducted in the same SSVEP recording session 
for the two mode; binocular and monocular 
'''

import pygame
import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from datetime import datetime
import csv
import os
import pandas as pd
 

'''
pygame: Pygame adds functionality on top of the excellent SDL library.
This allows you to create fully featured games and multimedia programs 
in the python language.
for more information https://www.pygame.org/docs/

time:  Run the stimulation and control the rate

numpy: Operational

pylsl: Communication of data

datatime: Date control

csv: Save data

'''

class Stimulus(object):
    '''
    The frecuencia of stimulation is 7.5Hz and represents different level 
    vernier acuity at 6 point.    
    '''
    def __init__(self):
#                 id_Subject,cc_Subject):
        """
        See :func:`start_stimulus` for details
        
        StreamInfo: The StreamInfo object stores the declaration of a data
        stream, to describe its properties and then construct a 
        StreamOutlet with it to create the stream on the network.
        
        StreamOutlet:  Outlets are used to make streaming data 
        (and the meta-data) available on the lab network.
        """
        # Pygame stimulation main window
        pygame.init()
        Icon = pygame.image.load('icono.png')
        pygame.display.set_icon(Icon)
        pygame.display.set_caption('Agudeza de Vernier')
        self.__width = 300  # 1680
        self.__height = 300  # 1050
        self.__size = 300, 300  # 1680, 1050
#        self.__screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.__screen = pygame.display.set_mode(self.__size)
        pygame.display.flip()
#        self.info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'float32', 'myuidw43536')
#        self.__outlet = StreamOutlet(self.info,1,3)
#        self.id = id_Subject
#        self.cc = cc_Subject
    
        

    def display(self, imagen):
        '''
            Adjust the space on the screen
            image: Image designed with the thickness or characteristic for each
            level of visual acuity
            ::0 corresponds to the intermediate image between each visual 
            stimulation and change in level visual acuity
            ::0.1 Rest, corresponds to the intermediate image between each 
            change of state (binocular or monocular)
            :param img: image of the stimulus to present 
        '''
        try:
            img = pygame.image.load(imagen)
            img_width = int(img.get_width())
            img_height = int(img.get_height())
            img = pygame.transform.scale(img, (img_width, img_height))
            position_x = self.__width / 2 - img.get_width() // 2
            position_y = self.__height / 2 - img.get_height() // 2
            self.__screen.blit(img, (position_x, position_y))
            pygame.display.flip()
        except:
            pygame.quit()
            
    def save(self,Mark):
        """
        Allows you to save the timestamp when changing images.
        For this particular stimulus, it allows separating the acuities 
        into 6 levels
        
        """
        now = datetime.now()
        d = (now.strftime("%m-%d-%Y"),now.strftime("%H-%M-%S"))
        date = {'H':[str(d[1])]}
        loc = r'C:\Users\veroh\OneDrive - Universidad de Antioquia\Proyecto Banco de la republica\Trabajo de grado\Herramienta\HVA\GITLAB\interface\ViAT\Records'+ '/'+d[0]
        file = loc + '/'  + 'Mark_'+str(self.id)+'_'+str(self.cc)+'.csv'
        if not  os.path.isfile(file):
            header=True
        else:
            header=False
        M = pd.DataFrame(date,columns=['H'])
        M['M']=Mark
        M.to_csv(file ,mode='a',header=header,index=False, sep=';')

        
    def start_stimulus(self):
        """Start Vernier stimulation 
       
        The stimulus is repeated 3 times, the first time to stimulate the right
        eye, the second time to stimulate the left eye, and the third time to 
        stimulate both eyes: range(0,3)
        
        num: traverse levels of visual acuity range(1,7) for 6 levels of visual
        acuity
        
        timestamp: Return POSIX timestamp as float
        push_sample: Push a sample into the outlet.
        Each entry in the list corresponds to one channel.
        Keyword arguments:
        x -- A list of values to push (one per channel).
        timestamp -- Optionally the capture time of the sample, in agreement 
                     with local_clock(); if omitted, the current 
                     time is used. (default 0.0)
                     
        event.get(): Pygame will register all events from the user into an 
        event queue
        """
        try:
            cont = 0 # counter that controls the frequency (7.5 Hz) in
            #conjunction with time.sleep
            RUNNING, PAUSE = 0, 1
            state = RUNNING
            pause_text = pygame.font.SysFont('Consolas', 32).render(
                'Pausa', True, pygame.color.Color('White'))
            for i in range(0, 1):  # time of stimulation
                for num in range(0, 7):  # acuity levels
#                    self.save(num+1)        
                    while (cont <= 6):  # 19.75--8 
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                break
                            if e.type == pygame.KEYDOWN:
                                if e.key == pygame.K_p: # key p: pause
                                    state = PAUSE
                                if e.key == pygame.K_s: # key s: start
                                    state = RUNNING
                                if e.key == pygame.K_ESCAPE: # key escape: exit
                                    pygame.quit()
                        if state == RUNNING:
                            time.sleep(1/15)  # 1/15
                            self.display(str(num) + '.jpg')
                            time.sleep(1/15)  # 1/15
                            cont += 1
                            self.display('0.jpg')
                        elif state == PAUSE:
                            self.__screen.blit(pause_text, (100, 100))
                    cont = 0
                self.display('0.1.jpg')
                time.sleep(4) #Rest
#            self.__outlet.close_stream()
            pygame.quit()
        except:
            pygame.quit()

# In[To run individually]
if __name__ == '__main__':
    estimulo = Stimulus()
    estimulo.start_stimulus()

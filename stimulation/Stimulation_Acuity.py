import pygame
import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from datetime import datetime


class Stimulus(object):
    def __init__(self):
        self.__width = 1680
        self.__height = 1050
        white = (250, 250, 250)
        self.__screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        # Pygame stimulation main window
        pygame.init()
        self.__tz = time.time()
        pygame.draw.rect(self.__screen, white, [0, 0, 10, 10])
        pygame.display.flip()
        info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'float32', 'myuidw43536')
        self.__outlet = StreamOutlet(info)
        
    def display(self,imagen):
        img = pygame.image.load(imagen)
        img_width = int(img.get_width())
        img_height = int(img.get_height())
        img = pygame.transform.scale(img, (img_width, img_height))
        position_x = self.__width / 2 - img.get_width() // 2
        position_y = self.__height / 2 - img.get_height() // 2
        self.__screen.blit(img, (position_x, position_y))
        pygame.display.flip()
        pygame.display.update()
    def event(self):
        wait = False
        while not wait :
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    wait = True
    def starStimulus(self):
        active = True
        cont = 0
        for i in range(0,1):#times the stimulus is shown
            for num in range(1,7):#acuity levels
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                self.__outlet.push_sample(np.array([num]),timestamp=timestamp)
                print(num)
                print(datetime.fromtimestamp(timestamp))
                while (cont <= 8):#19.75
                    if active:
                        time.sleep(1/15)#1/15
                        self.display(str(num) + '.jpg')
                        time.sleep(1/15)#1/15
                        cont+=1
                        self.display('0.jpg')
                cont = 0
            self.display('0.1.jpg')
            time.sleep(4)

        self.__outlet.push_sample(np.array([99]))
        pygame.quit()                



if __name__ == '__main__':
    estimulo = Stimulus()
    estimulo.event()
    estimulo.starStimulus()
    
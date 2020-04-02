import sys, time

import pygame
import time
import numpy as np
#from pylsl import StreamInfo, StreamOutlet
from datetime import datetime
import csv

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

# https://www.pygame.org/docs/tut/PygameIntro.html
class Game(object):
    def __init__(self):
        pygame.init()
        self.game_init()
        
    # pygame initialization
    def display(self,imagen):
        self.__img = pygame.image.load(imagen)
        self.__img_width = int(self.__img.get_width())
        self.__img_height = int(self.__img.get_height())
        self.__img = pygame.transform.scale(self.__img, (self.__img_width, self.__img_height))
        self.__position_x = self.__width / 2 - self.__img.get_width() // 2
        self.__position_y = self.__height / 2 - self.__img.get_height() // 2
        
        
    def game_init(self):
        self.size = self.__width, self.__height = 300, 200
        self.black = 0, 0, 0
        self.__screen = pygame.display.set_mode(self.size)
        active = True
        cont = 0
        for i in range(0,1):#times the stimulus is shown
            for num in range(1,7):#acuity levels
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                print(num)
                print(datetime.fromtimestamp(timestamp))
                sample_mark = datetime.now()
                with open("Mark.csv","a") as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    data =(sample_mark.strftime("%m/%d/%Y"),sample_mark.strftime("%H:%M:%S"))
                    writer.writerows([np.array(data)])
                while (cont <= 6):#19.75--8
                    if active:
                        time.sleep(1/15)#1/15
                        self.display(str(num) + '.jpg')
                        time.sleep(1/15)#1/15
                        cont+=1
                        self.display('0.jpg')
                cont = 0
            self.display('0.1.jpg')
            time.sleep(4)

    # pygame main loop
    def loop(self, window):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

#        self.ballrect = self.ballrect.move(self.speed)
#        if self.ballrect.left < 0 or self.ballrect.right > self.width:
#            self.speed[0] = -self.speed[0]
#        if self.ballrect.top < 0 or self.ballrect.bottom > self.height:
#            self.speed[1] = -self.speed[1]

        

# https://pythonspot.com/en/pyqt5-buttons
class Window(QWidget):
    def __init__(self, game):
        super().__init__()
        pygame.init()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 300
        self.height = 200
        self.init_ui()
        self.init_pygame(game)
 
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.button = QPushButton('Do not click', self)
        self.button.setToolTip('Don\'t you dare!')
        self.button.move(100, 70)
        self.button.clicked.connect(self.on_click)

        self.show()

    def init_pygame(self, game):
        # https://stackoverflow.com/questions/46656634/pyqt5-qtimer-count-until-specific-seconds
        self.game = game
        self.timer = QTimer()
        self.timer.timeout.connect(self.pygame_loop)
        self.timer.start(0)

    def pygame_loop(self):
        if self.game.loop(self):
            self.close()

    def on_click(self):
        print('You clicked :\'(')

def main():
#    game = Game()
    app = QApplication(sys.argv)
    ex = Window(Game())
    result = app.exec_()
    print("Qt finished: " + str(result))
    pygame.quit()
    sys.exit(result)
    

if __name__ == "__main__":
    main()
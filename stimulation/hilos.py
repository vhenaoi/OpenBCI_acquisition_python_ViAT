from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys

import pygame
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from datetime import datetime
import csv

class Stimulus(object):
    def __init__(self):
        self.__width = 1680
        self.__height = 1050
        self.__size = 1680, 1050
        white = (250, 250, 250)
#        self.__screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.__screen = pygame.display.set_mode(self.__size)
        
        # Pygame stimulation main window
        pygame.init()
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
#        wait = False
#        while not wait :
#            for event in pygame.event.get():
#                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
#                    wait = True
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

        self.__outlet.push_sample(np.array([99]))
        pygame.quit() 
        
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()    

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress        

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
        


class MainWindow(QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
    
        self.counter = 0
    
        layout = QVBoxLayout()
        
        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)
    
        layout.addWidget(self.l)
        layout.addWidget(b)
    
        w = QWidget()
        w.setLayout(layout)
    
        self.setCentralWidget(w)
    
        self.show()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
    
    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        estimulo = Stimulus()
        estimulo.event()
        estimulo.starStimulus()
#        for n in range(0, 5):
#            time.sleep(1)
#            progress_callback.emit(n*100/4)
#            
#        return "Done."
 
    def print_output(self,s):
        print(s)
    
        
    def thread_complete(self):
        print("THREAD COMPLETE!")
 
    def oh_no(self):
        pygame.quit()
        # Pass the function to execute
        worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)#s
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)#n
        
        # Execute
        self.threadpool.start(worker) 


        
    def recurring_timer(self):
        self.counter +=1
        self.l.setText("Counter: %d" % self.counter)
    
    
app = QApplication([])
window = MainWindow()
app.exec_()
#sys.exit(app.exec_())
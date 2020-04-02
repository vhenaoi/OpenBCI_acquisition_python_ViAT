from otra import Stimulus
import sys
from PyQt5.QtWidgets import QApplication,QScrollArea
#%%
class Principal(object):
    def __init__(self):  
#        scroll_area = QScrollArea()
        self.__app=QApplication(sys.argv)
        self.__view=Stimulus()
    def main(self):
        self.__view.show()
        sys.exit(self.__app.exec_())
#%%
p=Principal()
p.main()
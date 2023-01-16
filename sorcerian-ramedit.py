# sorcerian-ramedit.py


import sys, os, math
from PyQt6.QtWidgets import \
    QApplication, \
    QWidget, \
    QLabel, \
    QMainWindow, \
    QGridLayout, \
    QFileDialog, \
    QPushButton, \
    QListWidget, \
    QMessageBox, \
    QAbstractItemView, \
    QMenuBar, \
    QMenu
from PyQt6.QtGui import QFont, QAction
    

class SorcerianRAM():
    def __init__(self, _data):
        self.bytes = _data
    ####
####

def fuzzy_search(data, pattern, step=0x110, start=0x2b0):
    i = 0 + start
    pi = 0
    while (i < len(data)):  # find the single byte. 
        while (data[i] != pattern[pi]):
            i += step #1 
            if (i > (len(data))): # catch for 'step'
                return -1
        pi += 1             # then check if its a match to the whole pattern
        while(data[i + pi] == pattern[pi]):
            pi += 1 
            if(pi == len(pattern)):
                return (i)  # if so, return the location  
        i += step
        pi = 0  # if its not, keep going. 
    return -1
####
def get_size(fi):
    op = fi.tell()
    fi.seek(0, os.SEEK_END)      # seek to end 
    sz = fi.tell()               # get size 
    fi.seek(0, op) #os.SEEK_SET)
    return sz
####
def error_new_exception(exception):
    m = QMessageBox()
    m.setText(exception.__str__())
    m.setWindowTitle("Exception!")
    m.exec()
####
def msg_load_ok(s):
    m = QMessageBox()
    m.setText(str(s) + "RAM file loaded OK.")
    m.setWindowTitle("OK")
    m.exec()
####
def warning_size(n):
    m = QMessageBox()
    m.setText("WARNING: File size does not match expected (" + str(n) + ").\nIs this a good dump?")
    m.setWindowTitle("Warning!")
    m.exec()
####

class MainWindow(QMainWindow):
#""" Main App """
    def __init__(self):
        super().__init__()
        self.populateMenuBar()

        self.ram = []
        self.txtram = []
        self.subram = []
        
        self.setWindowTitle("Sorcerian PC-88 RAM Dump Editor")
        self.setFixedSize(600, 400)
        
        self.grid = QGridLayout()
        container = QWidget()
        container.setLayout(self.grid)
        
        self.setCentralWidget(container)
    ####
    def populateMenuBar(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        
        act_open = QAction("Open Main RAM dump...", self)
        act_open.triggered.connect(self.openFile)
        act_opentr = QAction("Open TXT/HIRAM dump...", self)
        act_opentr.triggered.connect(self.openTRFile)
        act_opensr = QAction("Open SUBRAM dump...", self)
        act_opensr.triggered.connect(self.openSRFile)
        
        act_qsre = QAction("Close App", self)
        act_qsre.triggered.connect(self.quit_sorcram)
        
        fileMenu.addAction(act_open)
        fileMenu.addAction(act_opentr)
        fileMenu.addAction(act_opensr)
        fileMenu.addSeparator()
        fileMenu.addAction(act_qsre)
    ####
    def openFile(self, s, e_size=0x10000, tgt="Main"):
        fname = QFileDialog.getOpenFileName(self, 'Open file', filter='RAM dump (*.*)')
        try:
            f = open(fname[0], "rb")
            b = f.read()
            f.close()
            if(len(b) != e_size):
                warning_size(e_size)
            if(tgt == "Main"):
                self.ram = b
            elif(tgt == "TXT"):
                self.txt = b
            elif(tgt == "SUB"):
                self.sub = b
            msg_load_ok(tgt) 
        except Exception as e:
            error_new_exception(e)
    ####
    def openTRFile(self, s):
        self.openFile(s, e_size=4096, tgt="TXT")
    ####
    def openSRFile(self, s):
        self.openFile(s, e_size=0x8000, tgt="SUB")
    ####
    def quit_sorcram(self, s):
        print(s)
        sys.exit()
    ####
####

app = QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec()


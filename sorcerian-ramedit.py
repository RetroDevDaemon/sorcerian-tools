# sorcerian-ramedit.py


import sys, os, math
from PyQt6.QtWidgets import \
    QApplication, QWidget, QLabel, \
    QMainWindow, QGridLayout, QFileDialog, \
    QPushButton, QListWidget, QMessageBox, \
    QAbstractItemView, QMenuBar, QMenu, \
    QToolBar, QTextEdit, QComboBox
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import QSize
    

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

#pageLengths = [ 0x1000, 0x3800, 0x400, 0x400, 
#    0x400, 0x400, 0x800, 0x800, 
#    0xe00, 0xa00, 0x2000, 0x2000, 
#    0x2000, 0x800, 0x800, 0x800 ]
#txtPageLengths = [ 
#    0x400, 0x400, 0x100, 0x100, 0x600
#]
#subPageLengths = [ 
#    0x2000, 0x2000, 0x1000, 0xc00, 0x400, 0x1000, 0x1000
#]
pageBoundaries = [ 
    0, 0x1000, 0x4800, 0x4c00, 
    0x5000, 0x5400, 0x5800, 0x6000, 
    0x6800, 0x7600, 0x8000, 0xa000, 
    0xc000, 0xe000, 0xe800, 0xf000, 
    0xf400, 0xf800, 0xf900, 0xfa00
]

class MainWindow(QMainWindow):
#""" Main App """
    def __init__(self):
        super().__init__()
        self.populateMenuBar()

        self.ram = []
        self.txtram = []
        self.subram = []

        self.currentPage = 0 
        
        self.setWindowTitle("Sorcerian PC-88 RAM Dump Editor")
        self.setFixedSize(800, 400)
        
        grid = QGridLayout()
        
        self.pageSelect = QComboBox()
        self.pageSelect.addItem("[$0000] BIOS (Main)")
        self.pageSelect.addItem("[$1000] Main Prog PRNO2")
        self.pageSelect.addItem("[$4800] Magic/Monster Work RAM")
        self.pageSelect.addItem("[$4C00] Monster Code")
        self.pageSelect.addItem("[$5000] Player Parameters")
        self.pageSelect.addItem("[$5400] Position, patterns, etc")
        self.pageSelect.addItem("[$5800] Map")
        self.pageSelect.addItem("[$6000] SFX")
        self.pageSelect.addItem("[$6800] BGM")
        self.pageSelect.addItem("[$7600] Scenario")
        self.pageSelect.addItem("[$8000] Map GFX + Char Font")
        self.pageSelect.addItem("[$A000] Overlay Buffer")
        self.pageSelect.addItem("[$C000] Player GFX")
        self.pageSelect.addItem("[$E000] Magic GFX")
        self.pageSelect.addItem("[$E800] Monster GFX")

        self.pageSelect.addItem("[TXT $F000] Player Params (backup)")
        self.pageSelect.addItem("[TXT $F400] Temp VRAM (txt)")
        self.pageSelect.addItem("[TXT $F800] Scenario Item Data")
        self.pageSelect.addItem("[TXT $F900] Scenario Work RAM")
        self.pageSelect.addItem("[TXT $FA00] Text Mask/Empty")

        self.pageSelect.addItem("[SUB $0000] Disk System ROM")
        self.pageSelect.addItem("[SUB $2000] *Not Initialized*")
        self.pageSelect.addItem("[SUB $4000] Disk Buffer and Cache")
        self.pageSelect.addItem("[SUB $5000] Castle NPC Parameters")
        self.pageSelect.addItem("[SUB $5C00] Monster Desc. Text")
        self.pageSelect.addItem("[SUB $6000] Directory Buffer")
        self.pageSelect.addItem("[SUB $7000] BIOS (Sub)")
        self.pageSelect.currentIndexChanged.connect(self.pageChanged)

        self.hexDisplay = QTextEdit()
        self.hexDisplay.setFont(QFont("Courier", 12))
        
        grid.addWidget(self.pageSelect, 0, 0)
        grid.addWidget(self.hexDisplay, 1, 1)

        container = QWidget()
        container.setLayout(grid)
        self.setCentralWidget(container)
    ####
    def resetHexDisplay(self, page):
        i = 0 
        st = pageBoundaries[page]
        o = '[$' + '{:04X}'.format(st) + '] '
        l = 0 
        while ((i+st) < pageBoundaries[page+1]):
            o = o + '{:02X}'.format(self.ram[st+i]) + " "
            l += 1 
            i += 1 
            if(l == 16):
                o += "\n[$" + '{:04X}'.format(st+i) + "] "
                l = 0
        self.hexDisplay.setText(o)
    ####
    def pageChanged(self, page):
        self.page = page 
        self.resetHexDisplay(self.page)
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

        toolbar = QToolBar("toolbar")
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        tool_open = QAction("Main RAM...", self)
        tool_open.triggered.connect(self.openFile)
        toolbar.addAction(tool_open)
        tool_opentxt = QAction("TXT/HI RAM...", self)
        tool_opentxt.triggered.connect(self.openTRFile)
        toolbar.addAction(tool_opentxt)
        tool_opensub = QAction("Sub RAM...", self)
        tool_opensub.triggered.connect(self.openSRFile)
        toolbar.addAction(tool_opensub)
        
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
        self.resetHexDisplay(self.currentPage)
        
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


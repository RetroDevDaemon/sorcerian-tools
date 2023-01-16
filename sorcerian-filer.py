# sorcerian-filer.py 

import sys, os, math
from PyQt6.QtWidgets import \
    QApplication, \
    QWidget, \
    QLabel, \
    QMainWindow, \
    QGridLayout, \
    QFileDialog, \
    QLineEdit, \
    QPushButton, \
    QListWidget, \
    QMessageBox, \
    QAbstractItemView 
from PyQt6.QtGui import QFont
    

class SorcerianFile():
#""" File data and directory entry info """
    def __init__(self):
        self.name = '     '
        self.bytes=[]
        self.flags = 0
        self.ow = 0xff
        self.sz = 0
        self.tra_start = 0
        self.sec_start = 0
        self.tra_end = 0
        self.sec_end = 0
        self.offset = 0x0 
    ####
    def getName(self):
        s = ""
        i = 0
        while i < 5:
            if( (ord(self.name[i]) > 0x1f) and (ord(self.name[i]) < 0x80) ):
                s = s + self.name[i]
            i += 1 
        return s 
    ####
    def getOffset(self, _data):
        o = track_sector_to_chr_offset(self.tra_start, self.sec_start)
        p = [ o[0], o[1], o[2], 1, 16 ]
        self.offset = fuzzy_search(_data, p)    # slow and lazy, fix later
    ####
    def getBytesSlow(self, _data):
        b = []
        ofs = self.offset + 16  # skip header 
        last = ofs 
        
        o = track_sector_to_chr_offset(self.tra_end, self.sec_end)
        p = [ o[0], o[1], o[2], 1, 16 ]
        end = fuzzy_search(_data, p)            # slow and lazy, fix later
        end += 256 + 16        # skip header and data 
        print(hex(end))
        while (last < end):
            while (ofs < last + 256):   # todo - take this from d88 header 
                b.append(_data[ofs])
                ofs += 1 
            ofs += 16       # skip header 
            last = ofs 
        self.bytes = b 
    ####
####


class DiskData():
#""" Disk loaded in to app """
    def __init__(self, _data):
        self.bytes = _data
        self.files = []
        self.getFileList()  # populate itself when created 
    ####
    def getFileList(self):
        # 0x13c0 - hard code this for now 
        bc = 0x13c0 
        n = SorcerianFile() # scope 
        fc = 0 
        while self.bytes[bc+4] != 0xff:   # continue until 0xFF is found instead of a filename
            n = SorcerianFile()     # clean it 
            i = 0 
            s = []
            while i < 5:
                s.append(chr(self.bytes[bc+i]))
                i += 1
            n.name  = s             # assign values from disk data 
            n.flags = self.bytes[bc + 9]
            n.ow    = self.bytes[bc + 10]
            n.sz    = self.bytes[bc + 11]
            n.tra_start = self.bytes[bc + 12]
            n.sec_start = self.bytes[bc + 13]
            n.tra_end   = self.bytes[bc + 14]
            n.sec_end   = self.bytes[bc + 15]
            n.getOffset(self.bytes)
            self.files.append(n)
            bc += 0x10
            fc += 1 
            if(fc == 16):
                bc += 0x10
                fc = 0
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
def track_sector_to_chr_offset(t, s):
    c = math.floor(t / 2)
    h = t % 2 
    r = s 
    return (c, h, r)
####
def get_size(fi):
    op = fi.tell()
    fi.seek(0, os.SEEK_END)      # seek to end 
    sz = fi.tell()               # get size 
    fi.seek(0, op) #os.SEEK_SET)
    return sz
####
def error_invalid_file():
    m = QMessageBox()
    m.setText("Error: Invalid file. Are you sure this is a D88 disk image?")
    m.setWindowTitle("Bad file!")
    m.exec()
####
def error_invalid_dir():
    m = QMessageBox()
    m.setText("Error: Invalid directory!")
    m.setWindowTitle("Bad directory!")
    m.exec()
####
def error_fail_to_open(exception):
    m = QMessageBox()
    m.setText(exception.__str__())
    m.setWindowTitle("Exception!")
    m.exec()
####
def error_fail_to_write(exception, n):
    m = QMessageBox()
    m.setText(exception.__str__() + "\nFile #" + str(n) + " failed to write.")
    m.setWindowTitle("Exception!")
    m.exec()
####
def msg_files_ok(n):
    m = QMessageBox()
    m.setText(str(n) + " file(s) extracted OK.")
    m.setWindowTitle("OK!")
    m.exec()
####

class MainWindow(QMainWindow):
#""" Main App """
    def __init__(self):
        super().__init__()
        
        self.disk = None 
        
        self.setWindowTitle("Sorcerian PC-88 File Extractor")
        self.setFixedSize(500, 300)
        
        _lblfile = QLabel()         # Window GUI setup : 
        _lblfile.setText("Socerian disk to extract:")
        self.path = QLineEdit()
        
        self.filebtn = QPushButton()
        self.filebtn.setText("Open...")
        self.filebtn.clicked.connect(self.selectFile)
        
        self.extrbtn = QPushButton()
        self.extrbtn.setText("Extract file(s)...")
        self.extrbtn.clicked.connect(self.extractFile)
        
        self.flist = QListWidget()  # to select multiple at once : 
        self.flist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        self.grid = QGridLayout()
        self.grid.addWidget(_lblfile, 0, 0)
        self.grid.addWidget(self.path, 1, 0)
        self.grid.addWidget(self.filebtn, 1, 1)
        self.grid.addWidget(QWidget(), 2, 0)
        self.grid.addWidget(QWidget(), 3, 0)
        self.grid.addWidget(self.flist, 4, 0)
        self.grid.addWidget(self.extrbtn, 4, 1)

        container = QWidget()
        container.setLayout(self.grid)
        
        self.setCentralWidget(container)
    ####
    def listFiles(self):
        self.flist.clear()
        i = 0 
        while i < len(self.disk.files):
            self.flist.setFont(QFont("Courier", 14))
            self.flist.insertItem(i, self.disk.files[i].getName() + "\t[" \
                + hex(self.disk.files[i].offset) + "]")
            i += 1 
    ####
    def extractFile(self):
        lis = self.flist.selectedItems()
        if(len(lis) == 0):
            return              # if nothing selected, do nothing
        i = 0 
        dirname = QFileDialog.getExistingDirectory(self, "Select target directory")
        if(not os.path.isdir(dirname)): 
            error_invalid_dir()
            return              # if dir does not exist 
        fail = 0 
        while i < len(lis):
            fi = self.flist.indexFromItem(lis[i]).row()
            fn = self.disk.files[fi].getName()
            self.disk.files[fi].getBytesSlow(self.disk.bytes) # populate new array
            try: 
                f = open(dirname + "/" + fn, "wb")
                bc = 0 
                while bc < len(self.disk.files[fi].bytes):
                    f.write(bytes( [self.disk.files[fi].bytes[bc]] )) # bytes([v]) == char[1]={v}
                    bc += 1
                f.close()
            except Exception as e:
                error_fail_to_write(e, i)
                fail += 1 
            i += 1 
        msg_files_ok(i - fail)
        
    ####
    def selectFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', \
            filter='D88 files (*.d88 *.dsk *.bin *.img)')
        self.path.setText(fname[0])     
        try:
            f = open(fname[0], "rb")    # open file 
            if((get_size(f) > 500000) or (get_size(f) < 90000)):   # simple filesize check
                raise Exception("Invalid file! Are you sure this is a good .d88 image?")
            inby = f.read()             # else read it into ram 
            f.close()
            self.disk = DiskData(inby)  # make a new disk and file collection
            if(len(self.disk.files) < 1):
                raise Exception("No files found! Is this a Sorcerian disk?")
            self.listFiles()            # add file list to GUI window 
        except Exception as e:
            error_fail_to_open(e)
    ####
    
####

app = QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec()


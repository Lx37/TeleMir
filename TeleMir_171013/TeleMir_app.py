# -*- coding: utf-8 -*-
"""
TeleMir application - with fake devices
"""

#~ from pyacq import StreamHandler, EmotivMultiSignals
#~ from pyacq.gui import Oscilloscope, TimeFreq
#~ from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics

#~ import msgpack
#~ import gevent
#~ import zmq.green as zmq

#~ from PyQt4 import QtCore,QtGui
#~ from PyQt4.QtCore import QTimer

#~ import zmq
#~ import msgpack
#~ import time
#~ from TeleMir.analyses import TransmitFeatures

from PyQt4 import QtCore,QtGui
from TeleMir import TeleMir_Calibration, TeleMir_Vol#, Fake_TeleMir_Atterrissage
import numpy as np

from PyQt4.phonon import Phonon


class TeleMirMainWindow(QtGui.QWidget):  
  
    def __init__(self):
        super(TeleMirMainWindow, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.setGeometry(300, 300, 250, 250)
        self.setWindowTitle('TeleMir')
        #~ self.setWindowIcon(QtGui.QIcon('web.png'))        
        
        self.btn_1 = QtGui.QPushButton('Calibration', self)
        self.btn_1.clicked.connect(self.calibration)
        self.btn_1.resize(self.btn_1.sizeHint())
        self.btn_1.move(90, 50)
        self.btn_1.setEnabled(True)        
        
        self.btn_2 = QtGui.QPushButton('Vol', self)
        self.btn_2.clicked.connect(self.vol)
        self.btn_2.resize(self.btn_2.sizeHint())
        self.btn_2.move(90, 100) 
        self.btn_2.setEnabled(False)
        
        self.btn_3 = QtGui.QPushButton('Atterrissage', self)
        self.btn_3.clicked.connect(self.atterrissage)
        self.btn_3.resize(self.btn_3.sizeHint())
        self.btn_3.move(90, 150)
        self.btn_3.setEnabled(False)
    
        self.show()
        
    def calibration(self):
        
        print 'TéléMir :: Calibration'
        
        self.TC = TeleMir_Calibration()
        
        ## Read Mire on tv
        media1 = Phonon.MediaSource('/home/mini/Projets/Pyacq_TeleMir_git/TeleMir/mire/Mire12.avi')
        self.vp1 = Phonon.VideoPlayer()
        self.vp1.load(media1)
        self.vp1.play()
        self.vp1.resize(800,600)
        self.vp1.move(1000,200)
        self.vp1.show()
        
        self.vp2 = Phonon.VideoPlayer()
        self.vp2.load(media1)
        self.vp2.play()
        self.vp2.show()
        
        
        self.btn_1.setEnabled(False)
        self.btn_2.setEnabled(True)
        
        
     
     
    def vol(self):
        
        print 'TéléMir :: Vol'
        
        ## Boutons
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(True)
        
        ## Close Calibration phase
        self.TC.close()
        self.vp1.close()
        self.vp2.close()
        
        self.TV = TeleMir_Vol()
        
        self.TV.w_oscilo.resize(300,300)
        
        
        
        
    def atterrissage(self):
        
        print 'TéléMir :: Atterrissage'
        
        ## Boutons
        self.btn_1.setEnabled(True)
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(False)
        
        ## Close Vol phase
        self.TV.close()
        
        
        
    #def setScreen(self, Qwidget, screenNumber):
    



if __name__ == '__main__':
    
    app = QtGui.QApplication([])
    
    w = TeleMirMainWindow()
    
    app.exec_()
    
    
    





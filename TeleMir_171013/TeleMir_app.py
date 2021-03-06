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

from PyQt4 import QtCore,QtGui
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
        
        self.screensize = np.array((1920))
    
        self.show()
        
    def calibration(self):
        
        print 'TéléMir :: Calibration'
        
        self.TC = TeleMir_Calibration()
        
        ## Read Mire on tv
        numscreen = 1
        media1 = Phonon.MediaSource('/home/ran/Projets/mire/Mire1.avi')
        self.vp1 = Phonon.VideoPlayer()
        self.vp1.load(media1)
        self.vp1.play()
        self.vp1.resize(800,600)
        self.vp1.move(self.screensize + (numscreen-1) * 800 ,200)
        self.vp1.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp1.show()
        
        numscreen = 2
        media2 = Phonon.MediaSource('/home/ran/Projets/mire/Mire3.avi')
        self.vp2 = Phonon.VideoPlayer()
        self.vp2.load(media2)
        self.vp2.play()
        self.vp2.resize(800,600)
        self.vp2.move(self.screensize + (numscreen-1) * 800 ,200)
        self.vp2.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp2.show()
        #~ self.vp2.setWindowOpacity(0.2)
        
        numscreen = 3
        media3 = Phonon.MediaSource('/home/ran/Projets/mire/Mire4.avi')
        self.vp3 = Phonon.VideoPlayer()
        self.vp3.load(media3)
        self.vp3.play()
        self.vp3.resize(800,600)
        self.vp3.move(self.screensize +  (numscreen-1)  * 800 ,200)
        self.vp3.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp3.show()
        
        numscreen = 4
        media4 = Phonon.MediaSource('/home/ran/Projets/mire/Mire25.avi')
        self.vp4 = Phonon.VideoPlayer()
        self.vp4.load(media4)
        self.vp4.play()
        self.vp4.resize(800,600)
        self.vp4.move(self.screensize +  (numscreen-1)  * 800 ,200)
        self.vp4.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp4.show()
        
        numscreen = 5
        mire = '/home/ran/Projets/mire/Mire7.avi'
        media5 = Phonon.MediaSource(mire)
        self.vp5 = Phonon.VideoPlayer()
        self.vp5.load(media5)
        self.vp5.play()
        self.vp5.resize(800,600)
        self.vp5.move(self.screensize +  (numscreen-1)  * 800 ,200)
        #~ QtCore.QObject.connect(media5, QtCore.QObject.SIGNAL(aboutFinished()), self, SLOT(self.addNext(self.vp5,'/home/ran/Projets/mire/Mire7.avi')));
        self.vp5.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp5.show()
        
        numscreen = 6
        media6 = Phonon.MediaSource('/home/ran/Projets/mire/Mire8.avi')
        self.vp6 = Phonon.VideoPlayer()
        self.vp6.load(media6)
        self.vp6.play()
        self.vp6.resize(800,600)
        self.vp6.move(self.screensize +  (numscreen-1)  * 800 ,200)
        self.vp6.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp6.show()
        
        numscreen = 7
        media7 = Phonon.MediaSource('/home/ran/Projets/mire/Mire12.avi')
        self.vp7 = Phonon.VideoPlayer()
        self.vp7.load(media7)
        self.vp7.play()
        self.vp7.resize(800,600)
        self.vp7.move(self.screensize +  (numscreen-1)  * 800 ,200)
        self.vp7.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.vp7.show()
        
        print self.screensize
        
        self.btn_1.setEnabled(False)
        self.btn_2.setEnabled(True)
        
        
     
     
    def vol(self):
        
        print 'TéléMir :: Vol'
        
        ## Boutons
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(True)
        
        self.TV = TeleMir_Vol()
        
        ## Close Calibration phase
        self.TC.close()
        self.vp1.close()
        self.vp2.close()
        self.vp3.close()
        self.vp4.close()
        self.vp5.close()
        self.vp6.close()
        self.vp7.close()
        
        
        
    def atterrissage(self):
        
        print 'TéléMir :: Atterrissage'
        
        ## Boutons
        self.btn_1.setEnabled(True)
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(False)
        
        ## Close Vol phase
        self.TV.close()
        
    
    def addNext(media, media_file):
        media.enqueue(Phonon.MediaSource(media_file))
        
    #def setScreen(self, Qwidget, screenNumber):
    



if __name__ == '__main__':
    
    app = QtGui.QApplication([])
    
    w = TeleMirMainWindow()
    
    app.exec_()
    
    
    





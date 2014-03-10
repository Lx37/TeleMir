# -*- coding: utf-8 -*-
"""
TeleMir phase 1 : calibration des impedances
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, Topoplot_imp, KurtosisGraphics, freqBandsGraphics

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QTimer

import zmq
import msgpack
import time
from TeleMir.analyses import TransmitFeatures
import numpy as np

class TeleMir_Calibration:
    
    def __init__(self):
    
        self.streamhandler = StreamHandler()
        ## Configure and start
        self.dev = EmotivMultiSignals(streamhandler = self.streamhandler)
        self.dev.configure(buffer_length = 1800, # doit être un multiple du packet size
                                device_path = '',)
        self.dev.initialize()
        self.dev.start()
            
        # Impedances
        self.w_imp=Topoplot_imp(stream = self.dev.streams[1], type_Topo = 'imp')
        self.w_imp.show()
        
        
    def close(self):
        
        #close window
        self.w_imp.close()
    
        # Stope and release the device
        self.dev.stop()
        self.dev.close()



if __name__ == '__main__':
    
    
    app = QtGui.QApplication([])
    
    t = TeleMir_Calibration()
    
    app.exec_()
    
    t.close()
    






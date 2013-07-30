# -*- coding: utf-8 -*-
"""
Topoplot example
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time

def teleMir_CB():
    streamhandler = StreamHandler()
    
    # Configure and start
    dev = EmotivMultiSignals(streamhandler = streamhandler)
    dev.configure(buffer_length = 1800)   # doit être un multiple du packet size
    dev.initialize()
    dev.start()
    
    app = QtGui.QApplication([])
    #w0=Topoplot(stream = dev.streams[0], type = 'topo')
    #w0.show()
    #w1.showFullScreen()
    
    # Impedances
    w_imp=Topoplot(stream = dev.streams[1], type = 'imp')
    w_imp.show()
    
    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    
    # temps frequence
    w_Tf=TimeFreq(stream = dev.streams[0])
    w_Tf.show()  
    
    app.exec_()
    
    # Stope and release the device
    dev.stop()
    dev.close()



if __name__ == '__main__':
    teleMir_CB()

# -*- coding: utf-8 -*-
"""


"""

from TeleMir.gui import ScanningOscilloscope,KurtosisGraphics,SpectrumGraphics

from pyacq import StreamHandler, FakeMultiSignals, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq


import msgpack

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time

def main():
    streamhandler = StreamHandler()
    

    #dev = EmotivMultiSignals(streamhandler = streamhandler)
    #dev.configure(buffer_length = 1800)
    
    
    # Configure and start
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( #name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    
    dev.initialize()
    dev.start()
    
    app = QtGui.QApplication([])

    w1=SpectrumGraphics(dev.streams[0],3.,channels=[11,12])
  #  w2=KurtosisGraphics(dev.streams[0],3.,channels=range(2,8))

    w1.run()
  #  w2.run()

    w1.showFullScreen()
    
    app.exec_()
    
    w1.connect(w1,QtCore.SIGNAL("fermeturefenetre()"),dev.stop)
    dev.close()
    



if __name__ == '__main__':
    main()

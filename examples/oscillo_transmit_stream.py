# -*- coding: utf-8 -*-
"""
Transmit Stream oscillo Example
"""

from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope
from TeleMir import TransmitStream

import msgpack

from PyQt4 import QtCore,QtGui

def run_test():
    streamhandler = StreamHandler()
    
    # Configure and start acquisition stream
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 10,
                                )
    dev.initialize()
    dev.start()
    
    # Configure and start output stream (for extracted feature)
    fout = TransmitStream(streamhandler = streamhandler)
    fout.configure( name = 'Test fout',
                                nb_channel =14, # np.array([1:5])
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 10,
                                )
    fout.initialize(stream_in = dev.streams[0])  # Could take multistreams ?)
    fout.start()
    
    
    app = QtGui.QApplication([])
    
    w_in=Oscilloscope(stream = dev.streams[0])
    w_in.show()
    
    w_out=Oscilloscope(stream = fout.streams[0])
    w_out.show()
    

    app.exec_()

    
    print 'release device fout'
    # Stope and release the device
    fout.stop()
    fout.close()   
    print 'release device dev'
    dev.stop()
    dev.close()
    

if __name__ == '__main__':
    run_test()

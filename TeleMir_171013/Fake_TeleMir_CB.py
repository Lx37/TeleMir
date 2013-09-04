# -*- coding: utf-8 -*-
"""
TeleMir developpement version with fake acquisition device
"""

from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics
from TeleMir.analyses import TransmitFeatures

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
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    dev.initialize()
    dev.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 13,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0]) 
    fout.start()
    
    app = QtGui.QApplication([])
    
    # Impedances
    w_imp=Topoplot(stream = dev.streams[0], type = 'imp')
    w_imp.show()
    
    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    
    # temps frequence
    w_Tf=TimeFreq(stream = dev.streams[0])
    w_Tf.show()  
    
    # kurtosis 
    w_ku=KurtosisGraphics(stream = dev.streams[0], interval_length = 1.)
    w_ku.run()  
    
    # freqbands 
    w_sp=freqBandsGraphics(stream = dev.streams[0], interval_length = 1., channels = [11,12])
    w_sp.run()  
    
    w_feat=Oscilloscope(stream = fout.streams[0])
    w_feat.show()
       
    
    app.exec_()
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    dev.stop()
    dev.close()



if __name__ == '__main__':
    teleMir_CB()

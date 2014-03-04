# -*- coding: utf-8 -*-
"""
Topoplot example
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QTimer

import zmq
import msgpack
import time
from TeleMir.analyses import TransmitFeatures

def teleMir_CB():
    streamhandler = StreamHandler()
    
    # Configure and start
    dev = EmotivMultiSignals(streamhandler = streamhandler)
    dev.configure(buffer_length = 1800, # doit être un multiple du packet size
                                device_path = '',)
    dev.initialize()
    dev.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure(# name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 6,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0], stream_xy = dev.streams[2]) 
    fout.start()
    
    
    app = QtGui.QApplication([])
    #w0=Topoplot(stream = dev.streams[0], type_Topo = 'topo')
    #w0.show()
    
    # Impedances
    w_imp=Topoplot(stream = dev.streams[1], type_Topo = 'imp')
    w_imp.show()
    w_imp2=Oscilloscope(stream = dev.streams[1])
    w_imp2.show()
    
    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    w_oscilo.auto_gain_and_offset(mode = 1)
    w_oscilo.set_params(xsize = 10, mode = 'scroll')
    
    # giro
    w_xy=Oscilloscope(stream = dev.streams[2])
    w_xy.show()
    w_xy.auto_gain_and_offset(mode = 1)
    w_xy.set_params(xsize = 10, mode = 'scroll')
    
        
    w_feat1=Oscilloscope(stream = fout.streams[0])
    w_feat1.show()
    w_feat1.auto_gain_and_offset(mode = 1)
    w_feat1.set_params(xsize = 10, mode = 'scroll')
    
    
    # temps frequence
    #w_Tf=TimeFreq(stream = dev.streams[0])
    #w_Tf.show()  
    
    # kurtosis 
    #w_ku=KurtosisGraphics(stream = dev.streams[0], interval_length = 1.)
    #w_ku.run()  
    
    # freqbands 
    #w_sp=freqBandsGraphics(stream = dev.streams[0], interval_length = 1., channels = [11,12])
    #w_sp.run()  
        
    #w_feat1=Oscilloscope(stream = fout.streams[0])
    #w_feat1.show()
    #w_feat2=Oscilloscope(stream = fout.streams[0])
    #w_feat2.show()
    #w_feat3=Oscilloscope(stream = fout.streams[0])
    #w_feat3.show()
    
    app.exec_()
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    dev.stop()
    dev.close()



if __name__ == '__main__':
    
    teleMir_CB()
    
    print "suivant"






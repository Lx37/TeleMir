# -*- coding: utf-8 -*-
"""
TeleMir phase 2 : vol
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq import StreamHandler, FakeMultiSignals
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
import numpy as np

class Fake_TeleMir_Vol:
    
    def __init__(self, precomputed, precomputedXY):
    
        self.streamhandler = StreamHandler()
        # Configure and start
        self.dev = FakeMultiSignals(streamhandler = self.streamhandler)
        self.dev.configure( #name = 'Test dev',
                                    nb_channel = 14,
                                    sampling_rate =128.,
                                    buffer_length = 30.,
                                    packet_size = 1,
                                    precomputed = precomputed,
                                    )
        self.dev.initialize()
        self.dev.start()
        
         # Configure and start
        self.devXY = FakeMultiSignals(streamhandler = self.streamhandler)
        self.devXY.configure( #name = 'Test dev',
                                    nb_channel = 2,
                                    sampling_rate =128.,
                                    buffer_length = 30.,
                                    packet_size = 1,
                                    precomputed = precomputedXY,
                                    )
        self.devXY.initialize()
        self.devXY.start()
        
             ## Configure and start output stream (for extracted feature)
        self.fout = TransmitFeatures(streamhandler = self.streamhandler)
        self.fout.configure( #name = 'Test fout',
                                    nb_channel = 14, # np.array([1:5])
                                    nb_feature = 6,
                                    nb_pts = 128,
                                    sampling_rate =10.,
                                    buffer_length = 10.,
                                    packet_size = 1,
                                    )
        self.fout.initialize(stream_in = self.dev.streams[0], stream_xy = self.devXY.streams[0]) 
        self.fout.start()
            
        # Impedances
        #~ self.w_imp=Topoplot(stream = self.dev.streams[0], type_Topo = 'imp')
        #~ self.w_imp.show()
        
        # signal
        self.w_oscilo=Oscilloscope(stream = self.dev.streams[0])
        self.w_oscilo.show()
        self.w_oscilo.auto_gain_and_offset(mode = 1)
        self.w_oscilo.set_params(xsize = 10, mode = 'scroll')
        
        # giro
        self.w_xy=Oscilloscope(stream = self.devXY.streams[0])
        self.w_xy.show()
        self.w_xy.auto_gain_and_offset(mode = 1)
        self.w_xy.set_params(xsize = 10, mode = 'scroll')
        
        # temps frequence
        self.w_Tf=TimeFreq(stream = self.dev.streams[0])
        self.w_Tf.show()  
        self.w_Tf.set_params(xsize = 10)
        self.w_Tf.change_param_tfr(f_stop = 45, f0 = 1)
        #w_Tf.change_param_channel(clim = 20)
        
        #~ # freqbands 
        #~ w_sp_bd=freqBandsGraphics(stream = dev.streams[0], interval_length = 3., channels = [11,12])
        #~ w_sp_bd.run()  

        
        self.w_feat1=Oscilloscope(stream = self.fout.streams[0])
        self.w_feat1.show()
            
        
        
        
        
    def close(self):
        
        #close windows
        self.w_oscilo.close()
        self.w_xy.close()
        self.w_Tf.close()
        self.w_feat1.close()
    
        # Stope and release the device
        self.fout.stop()
        self.fout.close()
        self.dev.stop()
        self.dev.close()
        self.devXY.stop()
        self.devXY.close()



if __name__ == '__main__':
    
    
    app = QtGui.QApplication([])
    
    filename = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008860.raw'
    filenameImp = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008861.raw'
    filenameXY = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008862.raw'
    
    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedImp = np.fromfile(filenameImp , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedXY = np.fromfile(filenameXY , dtype = np.float32).reshape(-1, 2).transpose()
    
    t = Fake_TeleMir_Vol(precomputed, precomputedXY )
    
    app.exec_()
    
    t.close()
    






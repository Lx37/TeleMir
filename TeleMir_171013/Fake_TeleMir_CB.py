# -*- coding: utf-8 -*-
"""
TeleMir developpement version with fake acquisition device

lancer dans un terminal :
python examples/test_osc_receive.py
"""

from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics, glSpaceShip
from TeleMir.gui import ScanningOscilloscope,SpectrumGraphics
from TeleMir.analyses import TransmitFeatures
#from TeleMir.example import test_osc_receive

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui
#from multiprocessing import Process

import zmq
import msgpack
import time
import numpy as np

import os

def teleMir_CB():
       
    streamhandler = StreamHandler()
    
    # Configure and start
    #~ dev = FakeMultiSignals(streamhandler = streamhandler)
    #~ dev.configure( #name = 'Test dev',
                                #~ nb_channel = 14,
                                #~ sampling_rate =128.,
                                #~ buffer_length = 10.,
                                #~ packet_size = 1,
                                #~ )
    #~ dev.initialize()
    #~ dev.start()
    
    filename = '/home/mini/pyacq_emotiv_recording/rec 2013-09-19 16:20:36.580141_Alex/Emotiv Systems Pty Ltd #SN201105160008860.raw'
    #filename = '/home/mini/pyacq_emotiv_recording/rec 2013-09-13 15:06:22.747174/Emotiv Systems Pty Ltd  #SN201105160008860.raw'
    
    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    
    # Configure and start
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( #name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 30.,
                                packet_size = 1,
                                precomputed = precomputed,
                                )
    dev.initialize()
    dev.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( #name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 4,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0]) 
    fout.start()
    
    #Osc server
    #p = Process(target=., args=('bob',))
    
    
    app = QtGui.QApplication([])
    
    # Impedances
    #~ w_imp=Topoplot(stream = dev.streams[0], type_Topo= 'imp')
    #~ w_imp.show()
    
    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    w_oscilo.auto_gain_and_offset(mode = 1)
    w_oscilo.set_params(xsize = 10, mode = 'scroll')
    
    # temps frequence
    w_Tf=TimeFreq(stream = dev.streams[0])
    w_Tf.show()  
    w_Tf.set_params(xsize = 10)
    w_Tf.change_param_tfr(f_stop = 45, f0 = 1)
    #w_Tf.change_param_channel(clim = 20)
    
    # kurtosis 
    #w_ku=KurtosisGraphics(stream = dev.streams[0], interval_length = 1.)
    #w_ku.run()  
    
    # freqbands 
    w_sp_bd=freqBandsGraphics(stream = dev.streams[0], interval_length = 3., channels = [11,12])
    w_sp_bd.run()  
    
    ## Bien moins fluide
    # Spectre
    #~ w_sp=SpectrumGraphics(dev.streams[0],3.,channels=[11,12])
    #~ w_sp.run()
    
    w_feat1=Oscilloscope(stream = fout.streams[0])
    w_feat1.show()
    
    #w1 = glSpaceShip(dev.streams[0])
    #w1.run()
    #w1.showFullScreen()
    
       
    
    app.exec_()
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    dev.stop()
    dev.close()



if __name__ == '__main__':
    teleMir_CB()

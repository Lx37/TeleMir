# -*- coding: utf-8 -*-
"""
TeleMir developpement version with fake acquisition device

lancer dans un terminal :
python examples/test_osc_receive.py
"""

from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics#, glSpaceShip
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
    
    #~ filename = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/caro/Emotiv Systems Pty Ltd  #SN201105160008860.raw'
    #~ filenameXY = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/caro/Emotiv Systems Pty Ltd  #SN201105160008862.raw'
    #~ filename = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008860.raw'
    #~ filenameXY = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008862.raw'
    #~ filename = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/new_alex/Emotiv Systems Pty Ltd #SN200709276578910.raw'
    #~ filenameXY = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/new_alex/Emotiv Systems Pty Ltd #SN200709276578912.raw'
    filename = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/anneLise/Emotiv Systems Pty Ltd #SN200709276578910.raw'
    filenameXY = '/home/mi/Projets/pyacq_TeleMir/pyacq_emotiv_recording/anneLise/Emotiv Systems Pty Ltd #SN200709276578912.raw'
    
    
    
    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedXY = np.fromfile(filenameXY , dtype = np.float32).reshape(-1, 2).transpose()
    
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
    
    # Configure and start
    devXY = FakeMultiSignals(streamhandler = streamhandler)
    devXY.configure( #name = 'Test dev',
                                nb_channel = 2,
                                sampling_rate =128.,
                                buffer_length = 30.,
                                packet_size = 1,
                                precomputed = precomputedXY,
                                )
    devXY.initialize()
    devXY.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( #name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 6,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0], stream_xy = devXY.streams[0]) 
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
    
    # giro
    w_xy=Oscilloscope(stream = devXY.streams[0])
    w_xy.show()
    w_xy.auto_gain_and_offset(mode = 1)
    w_xy.set_params(xsize = 10, mode = 'scroll')
    
    # temps frequence
    w_Tf=TimeFreq(stream = dev.streams[0])
    w_Tf.show()  
    w_Tf.set_params(xsize = 10)
    w_Tf.change_param_tfr(f_stop = 45, f0 = 1)
    #w_Tf.change_param_channel(clim = 20)
    
    # kurtosis 
    #w_ku=KurtosisGraphics(stream = dev.streams[0], interval_length = 1.)
    #w_ku.run()  
    
    #~ # freqbands 
    #~ w_sp_bd=freqBandsGraphics(stream = dev.streams[0], interval_length = 3., channels = [11,12])
    #~ w_sp_bd.run()  
    
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

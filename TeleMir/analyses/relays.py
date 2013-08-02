# -*- coding: utf-8 -*-

import numpy as np
import msgpack
import multiprocessing as mp
from pyacq.gui.tools import RecvPosThread


def transmitterMainLoop(stop_flag,stream,data):
    pass


class Transmitter:
    
    def __init__(self,in_stream,stream_handler):
        
        self.in_stream=in_stream
        
        #definition of the memory zone to read
        self.zone_mem=stream['shared_array'].to_numpy_array()
        self.half_size=self.zone_mem.shape[1]/2

        #definition of the sent interval
        self.pos=self.half_size
        self.data=self.zone_mem[self.pos-self.in_stream['packet_size']:self.pos]
        
        #connexion to in_stream
        self.in_port=in_stream['port']
        self.context=zmq.Context()
        self.in_socket=self.context.socket(zmq.SUB)
        self.in_socket.connect("tcp://localhost:%d"%self.port)
        self.in_socket.setsockopt(zmq.SUBSCRIBE,'')

        #initialisation de la pile de réception des positions
        self.threadPos=RecvPosThread(socket=self.in_socket,port=self.in_port)
        self.threadPos.start()

        #initialization of out_stream
        self.stream_handler=stream_handler
        self.initialize_out_stream()

    def initialize_out_stream(self):
        sampling_rate=self.stream['sampling_rate']
        channel_indexes=self.stream['channel_indexes']
        channel_names=self.stream['channel_names']
        name=self.in_stream['name']+'_data'
        self.out_stream = self.stream_handler=new_data_stream(name=name,
                                                              sampling_rate=sampling_rate,
                                                              channel_indexes=channel_indexes,
                                                              channel_names=channel_names,
                                                              )
        

    def start(self):
        pass
    
    def stop(self):
        pass
        
        


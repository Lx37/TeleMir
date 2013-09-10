# -*- coding: utf-8 -*-
"""

Extracteur de parametres

Prends un tableau de donnees et extrait des parametres

first version by Lx37

"""

import numpy as np
import scipy as sc
import time
import pyeeg
from pyentropy import DiscreteSystem

class GetFeatures():
    def __init__(self,stream_in, name = 'test'):
        
        self.name = name
        self.nb_features = 9
        self.features = np.zeros((self.nb_features,1),dtype=np.float)
        self.channel_names = [ 'F3', 'F4', 'P7', 'FC6', 'F7', 'F8','T7','P8','FC5','AF4','T8','O2','O1','AF3'] 
        self.nb_chan = 14
        self.channels = np.arange(self.nb_chan)
        #self.feature_names =['DeltaMean','ThetaMean','AlphaMean','BetaMean','GammaMean','MuMean', 'pDeltaP7P8', 'pThetaAF34', 'pAlphaO12', 'pBetaF34', 'pGammaFC56', 'pMuT78', 'meanKurto','meanKurto']
        
        self.interval_length_sec = 1
        self.interval_length = 256
        
        # Get shared mem: to adapt analysis window size to feature caracteristics  
        self.stream_in = stream_in
        self.np_arr_in = self.stream_in['shared_array'].to_numpy_array()
        self.half_size_in = self.np_arr_in.shape[1]/2
        self.sr_in = self.stream_in['sampling_rate']
        self.packet_size_in = self.stream_in['packet_size']
        self.nb_pts = 128
        
        #for fft
        self.bands=np.array([[1,4],[4,8],[8,13],[13,30],[30,45],[12,16]])
        self.bands_name = ('delta', 'theta', 'alpha','beta','gamma', 'mu')
        self.nb_bands = 6
        #frequence max en entier
        self.freqMax=np.amax(self.bands)
        self.nFreqMax=int(self.freqMax*self.interval_length_sec)
        self.pows = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)
        
        # différentes tailles de fenetre en fonction des bandes  
        ## TODO : automatiser ce calcul ?  pourquoi en diminuant la taille de la fenetre en dessous de 1s on augmente la puissance dans les bandes de hts freq ??
        self.band_time_size = [5,1.5,1,1,1,1]#0.5,0.25,0.75]  ## Calculé par rapport aux frequences moy de chaque bande pour avoir 10 cycles et que ça tombe juste / Fe
        self.pows2 = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)
        
        print 'self.nFreqMax', self.nFreqMax 
        #respectons Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = round(self.interval_length/2)-1
            print 'self.nFreqMax', self.nFreqMax
        
        #Kurto
        self.kurtos = np.zeros((self.nb_chan), dtype = np.float)
        
        #Entrpy
        self.entropy = np.zeros((self.nb_chan,self.nb_chan), dtype = np.float)
        
        #Moyennes glissantes et cumulées
        self.alpha_cumul = []
        self.Xsmooth = 10
        self.Xsmooth2 = 50
        
    def extract_TCL(self, data):
        
        #fft
        self.getFeat(data)
        bandsAv = np.average(self.pows, axis = 0)
        bandsAv2 = np.average(self.pows2, axis = 0)
        total_power = np.average(bandsAv2, axis=0)
        
        #pDeltaP7P8 = (self.pows[3,0] + self.pows[8,0])/2
        pThetaAF34F34 = (self.pows2[9,1] + self.pows2[13,1] + self.pows2[0,1] + self.pows2[1,1])/2
        pAlphaO12 = (self.pows2[11,2] + self.pows2[12,2])/2
        pBetaF34 = (self.pows2[0,3] + self.pows2[1,3])/2
        #pGammaFC56 = (self.pows[4,4] + self.pows[9,4])/2
        #pMuT78 = (self.pows[7,5] + self.pows[11,5])/2
        
        self.alpha_cumul.append(bandsAv2[2])
        alpha_cumul = np.sum(self.alpha_cumul)
        
        if len(self.alpha_cumul) > self.Xsmooth:
            alpha_smooth = np.average(self.alpha_cumul[-self.Xsmooth:])
        else:
            alpha_smooth = np.average(self.alpha_cumul)
        
        if len(self.alpha_cumul) > self.Xsmooth2:
            alpha_smooth2 = np.average(self.alpha_cumul[-self.Xsmooth2:])
        else:
            alpha_smooth2 = np.average(self.alpha_cumul)
        
        # Ratios
        R1 = (bandsAv2[0]*bandsAv2[2]) / (bandsAv2[3]*bandsAv2[4])  #delta.alpha / beta.gamma
        R2 = (bandsAv2[1]*bandsAv2[1]) / (bandsAv2[3]*bandsAv2[4]) # theta ² / beta.gamma
        R3 = (bandsAv2[1] + bandsAv2[2] + bandsAv2[3]) / total_power # (theta + alpha + beta)/ total power
        R5 = bandsAv2[2] * bandsAv2[1] # alpha.theta
        R6 = bandsAv2[1] / bandsAv2[0] #theta / delta
        R7 = (bandsAv2[1] + bandsAv2[2]) / bandsAv2[0] #(theta + alpha) / delta
        R8 = (bandsAv2[0] + bandsAv2[2]) / (bandsAv2[0]*bandsAv2[0]) #(delta + alpha) / delta²
        R9 = (bandsAv2[0] + bandsAv2[2] + bandsAv2[3]) / (bandsAv2[0]*bandsAv2[0]*bandsAv2[0]) #(delta + alpha) / delta³
        
        meanKurto = np.average(self.kurtos, axis = 0)
        
        #features = np.array([bandsAv[0], bandsAv[1], bandsAv[2], bandsAv[3] , bandsAv[4], bandsAv[5], bandsAv2[0], bandsAv2[1], bandsAv2[2], bandsAv2[3],bandsAv2[4], bandsAv2[5]])
        features = np.array([bandsAv2[0], bandsAv2[1], bandsAv2[2], bandsAv2[3],bandsAv2[4], bandsAv2[5], pAlphaO12, alpha_cumul, alpha_smooth,alpha_smooth2, pThetaAF34F34, pBetaF34, R1, R2, R3, R5, R6, R7, R8, R9,  meanKurto])

        return features
    
    def getFeat(self,head):
        
        data = self.np_arr_in[:, head+self.half_size_in-self.nb_pts : head+self.half_size_in]
        
        # Taille de fenere adaptée pour 10 cycles d'ondes autours da la frequence médiane de bande
        #data_Delta = self.np_arr_in[:, head+self.half_size_in- self.nb_pts*5: head+self.half_size_in]  # 5s for 2Hz
        #data_Theta = self.np_arr_in[:, head+self.half_size_in-self.nb_pts*1.5 : head+self.half_size_in]  # 1,5s for 6Hz
        #data_Alpha = self.np_arr_in[:, head+self.half_size_in-self.nb_pts : head+self.half_size_in] # 1 s for  10 Hz
        #data_Beta = self.np_arr_in[:, head+self.half_size_in-self.nb_pts*0.5 : head+self.half_size_in] # 0.5 for 20 Hz
        #data_Gamma = self.np_arr_in[:, head+self.half_size_in-self.nb_pts*0.25 : head+self.half_size_in] # for 40 Hz
        
        
        for i in self.channels:  # For each channel
            j=0
            for bd in self.band_time_size:
                data_band = self.np_arr_in[i, head+self.half_size_in- (self.nb_pts*bd): head+self.half_size_in]
                #fft
                spectrum_band = np.array(abs(sc.fft(data_band))[1:self.nFreqMax+1])
                spectrum_band = np.average(spectrum_band[self.bands[j][0]:self.bands[j][1]], axis = 0)  # ! Borne Sup non comprise !
                
            #p_delta = np.average(np.array(abs(sc.fft(data_Delta[i]))[self.bands[0][0]:self.bands[0][1]+1]), axis = 0)
            #p_Theta  = np.average(np.array(abs(sc.fft(data_Theta[i]))[self.bands[1][0]:self.bands[1][1]+1]), axis = 0)
            #p_Alpha = np.array(abs(sc.fft(data_Alpha[i]))[1:self.nFreqMax+1])
            #p_Beta = np.average(np.array(abs(sc.fft(data_Beta[i]))[self.bands[3][0]:self.bands[3][1]+1]), axis = 0)
            #p_Gamma = np.array(abs(sc.fft(data_Gamma[i]))[self.bands[4]])
            
            #p_Alpha =  np.sum(p_Alpha[self.bands[2][0]:self.bands[2][1]])/(self.bands[2][1]-self.bands[2][0])
            #p_Alpha =  np.average(p_Alpha[self.bands[2][0]:self.bands[2][1]], axis = 0)
            #p_Alpha = np.average(np.array(abs(sc.fft(data_Alpha[i]))[self.bands[2][0]:self.bands[2][1]]), axis = 0)  # ! different !
            
            #self.pows2[i] = [p_delta, p_Theta, p_Alpha, p_Beta]
            #print self.pows2.shape
            
                self.pows2[i][j] = spectrum_band
                j=j+1
                
                
                
            #calcul des fft
            spectrum=np.array(abs(sc.fft(data[i]))[1:self.nFreqMax+1]) 
            #calcul des puissances par bandes
            self.pows[i]=self.bands_power(spectrum)
            # Kurtosis
            self.kurtos[i]=sc.stats.kurtosis(data[i])
            
            #Entropy
            #if i!=self.channels.length
             #   for k=i+1:self.channels.length:

            #~ for k in self.channels:
                #~ max_i = max(data[i,:].astype(int)) +1
                #~ max_k = max(data[k,:].astype(int)) +1
                #~ print data[i,:].astype(int)
                #~ print max_i
                #~ print data[k,:].astype(int)
                #~ print max_k
                #~ s = DiscreteSystem(data[i,:].astype(int), (1,max_i), data[k,:].astype(int), (1,max_k))
                #~ s.calculate_entropies(method='pt', calc=['HX', 'HXY'])
                #~ self.entropy[i,k] = s.I()
            #self.ApEntropy = pyeeg.ap_entropy(data[i],1,1)
        
    #Calcul des puissance des bandes
    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            #Conversion des Hz vers les entiers (sortie de la fft)
            nf0=f0*self.interval_length_sec
            nf1=f1*self.interval_length_sec
                
            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)-1])   ## Devrait etre pow.append ?
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                #som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1]) + (nf1-int(nf1))*spectrum[int(nf1)-1]   ## pourquoi int(nf1)-1 ?
                som = np.sum(spectrum[int(nf0):int(nf1)])  ## Utilisé pour tester sur alpha, on a bien la même chose :)
                mean=som/(f1-f0)
                pows.append(mean)
        return pows
        
        
        
        
        
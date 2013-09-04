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

class GetFeatures():
    def __init__(self, name = 'test'):
        
        self.name = name
        self.nb_features = 9
        self.features = np.zeros((self.nb_features,1),dtype=np.float)
        self.channel_names = [ 'F3', 'F4', 'P7', 'FC6', 'F7', 'F8','T7','P8','FC5','AF4','T8','O2','O1','AF3'] 
        self.nb_chan = 14
        self.channels = np.arange(self.nb_chan)
        #self.feature_names =['DeltaMean','ThetaMean','AlphaMean','BetaMean','GammaMean','MuMean', 'pDeltaP7P8', 'pThetaAF34', 'pAlphaO12', 'pBetaF34', 'pGammaFC56', 'pMuT78', 'meanKurto','meanKurto']
        
        self.interval_length_sec = 1
        self.interval_length = 256
        
        #for fft
        self.bands=np.array([[1,4],[4,8],[8,13],[13,30],[30,45],[12,16]])
        self.bands_name = ('delta', 'theta', 'alpha','beta','gamma', 'mu')
        self.nb_bands = 6
        #frequence max en entier
        self.freqMax=np.amax(self.bands)
        self.nFreqMax=int(self.freqMax*self.interval_length_sec)
        self.pows = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)
        
        print 'self.nFreqMax', self.nFreqMax 
        #respectons Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = round(self.interval_length/2)-1
        print 'self.nFreqMax', self.nFreqMax
        
        #Kurto
        self.kurtos = np.zeros((self.nb_chan), dtype = np.float)
        
    def extract_TCL(self, data):
        
        #fft
        self.getFeat(data)
        
        pDeltaP7P8 = (self.pows[3,0] + self.pows[8,0])/2
        pThetaAF34 = (self.pows[9,1] + self.pows[13,1])/2
        pAlphaO12 = (self.pows[11,2] + self.pows[12,2])/2
        pBetaF34 = (self.pows[0,3] + self.pows[1,3])/2
        pGammaFC56 = (self.pows[4,4] + self.pows[9,4])/2
        pMuT78 = (self.pows[7,5] + self.pows[11,5])/2
        
        bandsAv = np.average(self.pows, axis = 0)
        
        
        
        meanKurto = np.average(self.kurtos, axis = 0)
        
        #features = ['DeltaMean','ThetaMean','AlphaMean','BetaMean','GammaMean','MuMean', 'pDeltaP7P8', 'pThetaAF34', 'pAlphaO12', 'pBetaF34', 'pGammaFC56', 'pMuT78', 'meanKurto','meanKurto']
        #print features
        features = np.array([bandsAv[0], bandsAv[1], bandsAv[2], bandsAv[3] , bandsAv[4], bandsAv[5], pDeltaP7P8, pThetaAF34, pAlphaO12, pBetaF34, pGammaFC56, pMuT78, meanKurto])
    
        return features
    
    def getFeat(self,data):
        
        for i in self.channels:  # For each channel
            #calcul des fft
            spectrum=np.array(abs(sc.fft(data[i]))[1:self.nFreqMax+1])
            #calcul des puissances par bandes
            self.pows[i]=self.bands_power(spectrum)
            
            # Kurtosis
            self.kurtos[i]=sc.stats.kurtosis(data[i])
            
            # Entropy
            #self.ApEntropy = pyeeg.ap_entropy(data[i],1,1)
        
    #Calcul des puissance des bandes
    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            #Conversion des Hz vers les entiers (sortie de la fft)
            nf0=f0*self.interval_length_sec
            nf1=f1*self.interval_length_sec
                 
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)])
                
            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)-1])
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1]) + (nf1-int(nf1))*spectrum[int(nf1)-1] 
                mean=som/(f1-f0)
                pows.append(mean)
        return pows
        
        
        
        
        
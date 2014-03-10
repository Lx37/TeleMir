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
#from pyentropy import DiscreteSystem
#from sklearn.decomposition import FastICA
import pylab as pl
import matplotlib.mlab as mlab

class GetFeatures():
    def __init__(self,stream_in, name = 'test'):
        
        self.name = name
        self.nb_features = 6
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
        self.bands=np.array([[1,4],[4,8],[8,13],[13,35],[30,45],[12,16]])
        self.bands_name = ('delta', 'theta', 'alpha','beta','gamma', 'mu')
        self.nb_bands = 6
        #frequence max en entier
        self.freqMax=np.amax(self.bands)
        self.nFreqMax=int(self.freqMax*self.interval_length_sec)
        self.pows = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)
        
        # différentes tailles de fenetre en fonction des bandes  
        ## TODO : automatiser ce calcul 
        self.band_time_size = [5,1.5,1,1,1,1]#0.5,0.25,0.75]  ## Calculé par rapport aux frequences moy de chaque bande pour avoir 10 cycles et que ça tombe juste / Fe
        self.pows2 = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)
        
        print 'self.nFreqMax', self.nFreqMax 
        #respectons Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = round(self.interval_length/2)-1
            print 'self.nFreqMax', self.nFreqMax
        
        #Kurto
        #self.kurtos = np.zeros((self.nb_chan), dtype = np.float)
        
        #Moyennes glissantes et cumulées
        self.contrib_alpha_cumul_O1O2= []
        self.contrib_alpha_cumul = []
        self.alpha_cumul = []
        self.contrib_beta_cumul = []
        self.contrib_teta_cumul = []
        self.contrib_mu_cumul = []
        self.id_new_cumul = 0
        self.Xsmooth =30

        self.alpha_cumul_th = 200000#1000000
        self.contrib_alpha_cumul_th = 20
        #print 'self.contrib_alpha_cumul_th:', self.contrib_alpha_cumul_th
        print 'time :',time.time()
        
        mean = 0
        variance = 50
        sigma = np.sqrt(variance)
        x = np.linspace(-25,25,50)
        self.template_blink = mlab.normpdf(x,mean,sigma)*2500
        
        self.id_alpha_cumul = 0

        #blink_proj = np.load('./../TeleMir/analyses/ICA_proj.npy')
        blink_proj = np.load('./ICA_proj.npy')
        self.blink_invProj = np.linalg.inv(blink_proj)
        self.n_blink_comp = 2
        self.last_blink = 0    
        self.blink_threshold = 0.05#5
        
    def extract_TCL(self, data):
        
        #print data
        self.getFeat(data)
        blink_feat = self.is_blink(data)
        crisp_feat = 0 #self.get_crispation(data)
        
        bandsAv = np.average(self.pows, axis = 0)
        #~ bandsAv2 = np.average(self.pows2, axis = 0)
        total_power = np.sum(bandsAv, axis=0)
        
        #pDeltaP7P8 = (self.pows[3,0] + self.pows[8,0])/2
        #~ pThetaAF34F34 = (self.pows2[9,1] + self.pows2[13,1] + self.pows2[0,1] + self.pows2[1,1])/2
        pAlphaO12 = (self.pows[11,2] + self.pows[12,2])/2
        total_power_O1O2 =  np.sum(self.pows[11,:], axis=0) + np.sum(self.pows[12,:], axis=0)

        #pBetaF34 = (self.pows2[0,3] + self.pows2[1,3])/2
        #pGammaFC56 = (self.pows[4,4] + self.pows[9,4])/2
        #pMuT78 = (self.pows[7,5] + self.pows[11,5])/2
        
        #contribution alpha O1O2
        contrib_alpha_O1O2 = pAlphaO12/total_power_O1O2
        self.contrib_alpha_cumul_O1O2.append(contrib_alpha_O1O2)
        contrib_alpha_cumul_O1O2 = np.sum(self.contrib_alpha_cumul_O1O2)
        
        #contribution beta teta mu
        contrib_beta = bandsAv[3]/total_power
        self.contrib_beta_cumul.append(contrib_beta)
        contrib_beta_cumul = np.sum(self.contrib_beta_cumul[self.id_new_cumul:])
        contrib_teta = bandsAv[1]/total_power
        self.contrib_teta_cumul.append(contrib_teta)
        contrib_teta_cumul = np.sum(self.contrib_teta_cumul[self.id_new_cumul:])
        contrib_mu = bandsAv[5]/total_power
        self.contrib_mu_cumul.append(contrib_mu)
        contrib_mu_cumul = np.sum(self.contrib_mu_cumul[self.id_new_cumul:])
        
        
        #contribution alpha
        contrib_alpha = bandsAv[2]/total_power
        self.contrib_alpha_cumul.append(contrib_alpha)
        contrib_alpha_cumul = np.sum(self.contrib_alpha_cumul[self.id_new_cumul:])
        
        #alpha 
        self.alpha_cumul.append( bandsAv[2])
        alpha_cumul = np.sum(self.alpha_cumul[self.id_new_cumul:])
        
        #~ # alpha cumul
        #~ if (alpha_cumul > self.alpha_cumul_th):
            #~ print 'alpha_cumul : ', alpha_cumul
            #~ self.id_new_cumul = len(self.alpha_cumul)
            #~ print 'self.id_new_cumul : ', self.id_new_cumul 
            #~ alpha_cumul = 0
            #~ print 'self.id_alpha_cumul : ', self.id_alpha_cumul
            #~ self.id_alpha_cumul = self.id_alpha_cumul +1
            
        #~ if self.id_alpha_cumul > 8:
            #~ self.id_alpha_cumul = 0

        #print 'contrib_alpha_cumul :', contrib_alpha_cumul
            
        # contrib alpha cumul
        if (contrib_alpha_cumul > self.contrib_alpha_cumul_th):
            #print 'contrib alpha_cumul : ', contrib_alpha_cumul
            self.id_new_cumul = len(self.alpha_cumul)
            #print 'self.id_new_cumul : ', self.id_new_cumul 
            contrib_alpha_cumul = 0
            self.id_alpha_cumul = self.id_alpha_cumul +1
            print 'self.id_alpha_cumul : ', self.id_alpha_cumul

            print 'time :',time.time()

            
        if self.id_alpha_cumul > 8:
            self.id_alpha_cumul = 0
        
        
        if len(self.alpha_cumul) > self.Xsmooth:
            #~ contrib_alpha_O1O2_smooth = np.average(self.contrib_alpha_cumul_O1O2[-self.Xsmooth:])
            contrib_alpha_smooth = np.average(self.contrib_alpha_cumul[-self.Xsmooth:])
            contrib_beta_smooth = np.average(self.contrib_beta_cumul[-self.Xsmooth:])
            contrib_teta_smooth = np.average(self.contrib_teta_cumul[-self.Xsmooth:])
            contrib_mu_smooth = np.average(self.contrib_mu_cumul[-self.Xsmooth:])
            #alpha_smooth = np.average(self.alpha_cumul[-self.Xsmooth:])
        else:
            #~ contrib_alpha_O1O2_smooth = np.average(self.contrib_alpha_cumul_O1O2)
            contrib_alpha_smooth = np.average(self.contrib_alpha_cumul)
            contrib_alpha_smooth = np.average(self.contrib_alpha_cumul)
            contrib_beta_smooth = np.average(self.contrib_beta_cumul)
            contrib_teta_smooth = np.average(self.contrib_teta_cumul)
            contrib_mu_smooth = np.average(self.contrib_mu_cumul)
            #alpha_smooth = np.average(self.alpha_cumul)
        
        #~ # Norme alpha_smooth
        #~ if (alpha_smooth > 100 and alpha_smooth < 1000):
            #~ alpha_smooth_norm = (alpha_smooth - 100) / 9.9 
        #~ else:
            #~ if (alpha_smooth < 100):
                #~ alpha_smooth_norm = 0
            #~ else:
                #~ alpha_smooth_norm = 100
                
        # Norme contrib_alpha_smooth

        if (contrib_alpha_smooth > 0.1 and contrib_alpha_smooth < 0.4):
            contrib_alpha_smooth_norm = (contrib_alpha_smooth - 0.1) * 600  # etrange * 50, *33
        else:
            if (contrib_alpha_smooth < 0.1):
                contrib_alpha_smooth_norm = 0
            else:
                print 'contrib_alpha_smooth :',contrib_alpha_smooth
                contrib_alpha_smooth_norm = 100
 
        if (contrib_beta_smooth > 0.06 and contrib_beta_smooth < 0.3):
            contrib_beta_smooth_norm = (contrib_beta_smooth - 0.06) * 500
        else:
            if (contrib_beta_smooth < 0.06):
                contrib_beta_smooth_norm = 0
            else:
                print 'contrib_beta_smooth :',contrib_beta_smooth
                contrib_beta_smooth_norm = 100
                
        if (contrib_teta_smooth > 0.1 and contrib_teta_smooth < 0.4):
            contrib_teta_smooth_norm = (contrib_teta_smooth - 0.06) * 500
        else:
            if (contrib_teta_smooth < 0.1):
                contrib_teta_smooth_norm = 0
            else:
                print 'contrib_teta_smooth :',contrib_teta_smooth
                contrib_teta_smooth_norm = 100

        if (contrib_mu_smooth > 0.1 and contrib_mu_smooth < 0.4):
            contrib_mu_smooth_norm = (contrib_mu_smooth - 0.1) * 600
        else:
            if (contrib_mu_smooth < 0.1):
                contrib_mu_smooth_norm = 0
            else:
                print 'contrib_mu_smooth :',contrib_mu_smooth
                contrib_mu_smooth_norm = 100
        
        # Norme contrib_alpha_smooth O1O2
        #~ if (contrib_alpha_O1O2_smooth > 100 and contrib_alpha_O1O2_smooth < 1000):
            #~ contrib_alpha_O1O2_smooth_norm = (contrib_alpha_smooth_O1O2 - 100) / 9.9 
        #~ else:
            #~ if (contrib_alpha_O1O2_smooth < 100):
                #~ contrib_alpha_O1O2_smooth_norm = 0
            #~ else:
                #~ contrib_alpha_O1O2_smooth_norm = 100
        
        #crispation + 1000 ?
        if total_power < 2000:
            crisp_feat = 0
        else:
            if total_power < 3000:
                crisp_feat = 1
            else:
                if total_power < 4000:
                    crisp_feat = 2
                else:
                    if total_power < 5000:
                        crisp_feat = 3
                    else:
                        crisp_feat = 4
                        

        if contrib_alpha_smooth_norm>6:
            blink_feat =0
        
        # Giro
        
        
        # Ratios
        #~ R1 = (bandsAv2[0]*bandsAv2[2]) / (bandsAv2[3]*bandsAv2[4])  #delta.alpha / beta.gamma
        #~ R2 = (bandsAv2[1]*bandsAv2[1]) / (bandsAv2[3]*bandsAv2[4]) # theta ² / beta.gamma
        #~ R3 = (bandsAv2[1] + bandsAv2[2] + bandsAv2[3]) / total_power # (theta + alpha + beta)/ total power
        #~ R5 = bandsAv2[2] * bandsAv2[1] # alpha.theta
        #~ R6 = bandsAv2[1] / bandsAv2[0] #theta / delta
        #~ R7 = (bandsAv2[1] + bandsAv2[2]) / bandsAv2[0] #(theta + alpha) / delta
        #~ R8 = (bandsAv2[0] + bandsAv2[2]) / (bandsAv2[0]*bandsAv2[0]) #(delta + alpha) / delta²
        #~ R9 = (bandsAv2[0] + bandsAv2[2] + bandsAv2[3]) / (bandsAv2[0]*bandsAv2[0]*bandsAv2[0]) #(delta + alpha) / delta³
        
        #~ meanKurto = np.average(self.kurtos, axis = 0)
        
        #features = np.array([bandsAv[0], bandsAv[1], bandsAv[2], bandsAv[3] , bandsAv[4], bandsAv[5], bandsAv2[0], bandsAv2[1], bandsAv2[2], bandsAv2[3],bandsAv2[4], bandsAv2[5]])
        #features = np.array([bandsAv2[0], bandsAv2[1], bandsAv2[2], bandsAv2[3],bandsAv2[4], bandsAv2[5], pAlphaO12, alpha_cumul, alpha_smooth,alpha_smooth2, pThetaAF34F34, pBetaF34, R1, R2, R3, R5, R6, R7, R8, R9,  meanKurto])
        #features = np.array([contrib_alpha_smooth,self.id_alpha_cumul, blink_feat, crisp_feat])
        #features = np.array([contrib_alpha_smooth_norm,self.id_alpha_cumul, blink_feat, crisp_feat]) #Claude B
        features = np.array([contrib_alpha_smooth_norm,blink_feat, crisp_feat, contrib_beta_smooth_norm, contrib_teta_smooth_norm, contrib_mu_smooth_norm])

        
        return features
    
    def is_blink(self, head):

        # sur combien de points  ? ici 64 ??
        #data = self.np_arr_in[:, head+self.half_size_in - 2*self.nb_pts : head+self.half_size_in]
        data = self.np_arr_in[:, head+self.half_size_in - self.nb_pts : head+self.half_size_in]
        
        
        data = np.transpose(data) 
        data_rect = data - np.mean(data, axis = 0)
        data_rect = np.transpose(data_rect)
        
        #~ temp_comp = np.dot( self.blink_invProj, data)
        #~ isBlink = np.mean(temp_comp[self.n_blink_comp,:])

        
        blink_comp = np.dot( self.blink_invProj[self.n_blink_comp], data_rect[:,data_rect.shape[1]-15:data_rect.shape[1]]) 
        #data_rect[:,data_rect.shape[1]-10:data_rect.shape[1]]
        
        
        if np.mean(blink_comp) > self.blink_threshold and self.lastBlink < self.blink_threshold:
            isBlink = 1
        else:
            isBlink = 0
        
        self.lastBlink = np.mean(blink_comp)
        # recentre
        #~ mean_chan = np.median(data,axis=0)
        #~ data_centred = data - mean_chan[np.newaxis,:]
        #~ data_centerd_sum = data_centred[:,[0,1,3,4,5,8,9,13]].mean(axis = 1)
        #~ cv =  np.convolve(data_centerd_sum,self.template_blink, 'valid')[0]
        #~ print cv
            
        #~ if cv > 45000:
            #~ isBlink =1
        #~ else:
            #~ isBlink = 0
            
        return isBlink
    
    
    def getFeat(self,head):
        
        data = self.np_arr_in[:, head+self.half_size_in-self.nb_pts : head+self.half_size_in]

        for i in self.channels: 
            j=0
            #~ for bd in self.band_time_size:
                #~ data_band = self.np_arr_in[i, head+self.half_size_in- (self.nb_pts*bd): head+self.half_size_in]
                #~ #fft
                #~ spectrum_band = np.array(abs(sc.fft(data_band)))
                #~ spectrum_band = np.average(spectrum_band[self.bands[j][0]:self.bands[j][1]], axis = 0)  # ! Borne Sup non comprise !
                
                #~ self.pows2[i][j] = spectrum_band                
                #~ j=j+1
                
                
                
            #calcul des fft
            spectrum=np.array(abs(sc.fft(data[i]))[1:self.nFreqMax+1]) 
            
            #calcul des puissances par bandes
            self.pows[i]=self.bands_power(spectrum)
            # Kurtosis
           # self.kurtos[i]=sc.stats.kurtosis(data[i])
            
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
            
        #ICA
        #ica = FastICA()
        #S_ = ica.fit(data).transform(data)
        #print S_.shape
            
        #Correlation to blink template
        #print self.np_arr_in[:,head+self.half_size_in]
        #print np.correlate(self.np_arr_in[:,head+self.half_size_in], self.template_blink )/50000
            
            
        
    #Calcul des puissance des bandes
    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            #Conversion des Hz vers les entiers (sortie de la fft)
            nf0=f0*self.interval_length_sec
            nf1=f1*self.interval_length_sec
                
            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)-1])   ## Devrait etre pows.append ?
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1]) + (nf1-int(nf1))*spectrum[int(nf1)-1]   
                #som = np.sum(spectrum[int(nf0):int(nf1)])  ## Utilisé pour tester sur alpha, on a bien la même chose :)
                mean=som/(f1-f0)
                pows.append(mean)
        return pows
        
        
        
        
        
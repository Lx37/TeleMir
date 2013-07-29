# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraphWorker as pw    
from scipy import fft
import BarGraphItem as bg

class freqBandsGraphics(pw.PyQtGraphicsWorker):
    def __init__(self,stream,interval_length,colorMode=True,channels=None,title=None,**kwargs):
        super(freqBandsGraphics,self).__init__(stream,interval_length,channels,title,**kwargs)

        self.time_length=interval_length

        self.bands=np.array([[1,4],[4,8],[8,13],[13,30],[30,50],[12,16]])
            			
            #frequence max en entier
        self.freqMax=np.amax(self.bands)
        self.nFreqMax=int(self.freqMax*interval_length)
            
            #Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = self.interval_length/2
                    
            #Pile contenant les dernières fft
        self.stackLen=100
        self.lastResults={}
        self.posLastResult=0

            #Modes d'affichage
        self.colorMode=colorMode

    def initPlots(self):
               #transformation de l'axe des abscisses

        x0=self.bands[:,0]
        x1=self.bands[:,1]

        self.barGraphs={}            
        for i in self.channels:
                #calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax+1])
            
                #affichages par octaves
            pows=self.bands_power(spectrum)

                #Création de la pile des fft passees
            self.lastResults[i]=np.zeros(self.stackLen*(len(pows))).reshape(self.stackLen,len(pows))
            self.lastResults[i][0]=pows
            self.posLastResult=1
                


            if self.colorMode:
 #Couleurs en fonction des valeurs de puissances
                #initialisation du gradient
                self.colMap=pg.ColorMap(pos=np.array([1,0.7]),
                                        color=np.array([[255,0,0,128],[0,0,255,128]]),
                                        #mode=pg.ColorMap.HSV_POS,
                                        )
                brushes=self.scaledBrushes(pows,i)
            else:
                brushes=None
                
            print brushes

                #affichage
            p=self.addPlot(None)
               # p.getAxis('bottom').setLogMode(True)
            self.barGraphs[i]=bg.BarGraphItem(x0=x0,
                                              x1=x1,
                                              # width=width,
                                              height=pows,
                                              brushes=brushes 
                                              )
            
            p.addItem(self.barGraphs[i])
            self.nextRow()
             
    def scaledBrushes(self,spectrum,chan):
            #étalonnage sur du gradient sur les valeurs du spectre
        self.sMax=np.amax(self.lastResults[chan])                
        self.colMap.pos[0]=self.sMax
        
                #choix des couleurs en fonction des puissances
        return self.colMap.map(spectrum)

    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            nf0=f0*self.time_length
            nf1=f1*self.time_length
                 
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)-1])
            else :
                som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1])+(nf1-int(nf1))*spectrum[int(nf1)-1] 
                mean=som/(f1-f0)
                pows.append(mean)


        return pows

    def updatePlots(self):

        for i in self.channels:
                #calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax+1])
                
            pows=self.bands_power(spectrum)

                #enregistrement dans la pile de sauvegardes
            self.lastResults[i][self.posLastResult]=pows
            self.posLastResult=(self.posLastResult+1)%self.stackLen
                
            if self.colorMode:
                #étalonnage du gradient de couleurs sur les valeurs du spectre
                brushes=self.scaledBrushes(pows,i)
            else:
                brushes=None

                #mise à jour des graphes           
            self.barGraphs[i].updateHeights(pows,brushes)
        
    def adaptRange(self):
        for i in self.channels:
            maxS=np.max(self.lastResults[i])
            self.barGraphs[i].parentWidget().setRange(yRange=(0,maxS*1.1))
            
    def keyPressEvent(self,e):
        if e.key()==pg.QtCore.Qt.Key_Escape:
            self.showNormal()
        elif e.key()==pg.QtCore.Qt.Key_Space:
            self.adaptRange()


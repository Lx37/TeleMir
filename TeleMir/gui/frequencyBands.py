# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraphWorker as pw    
from scipy import fft
import BarGraphItem as bg
import random

class freqBandsGraphics(pw.PyQtGraphicsWorker):
    def __init__(self,stream,interval_length,colorMode=True,channels=None,title=None,**kwargs):
        super(freqBandsGraphics,self).__init__(stream,interval_length,channels,title,**kwargs)
        random.seed(5)
        self.time_length=interval_length

        self.bands=np.array([[1,4],[4,8],[8,13],[13,30],[30,45],[12,16]])
        self.titles=[QtCore.QString(QtCore.QChar(948)),QtCore.QString(QtCore.QChar(952)),QtCore.QString(QtCore.QChar(945)),QtCore.QString(QtCore.QChar(946)),QtCore.QString(QtCore.QChar(947)),QtCore.QString(QtCore.QChar(956))]    			

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

    #Ajout des étiquettes correspondant aux noms des bandes de fréquence
        #Ajout d'une view box de taille limitée
        v=self.addViewBox()
        v.setMaximumHeight(80)
        #création du widget qui soutient le texte
        p=pg.PlotItem(None)
        #Effacer les axes
        p.showAxis('bottom',False)
        p.showAxis('left',False)
        #mettre l'axe des abscisses à la bonne échelle
        p.getAxis('bottom').setRange(0,self.freqMax)
        #définition des étiquettes
        for i in range(len(self.bands)):
            label=pg.TextItem(html='<div style="text-align: center"><span style="color: #DDD; font-size: 19pt;">'+self.titles[i]+'</span></div>')
            p.addItem(label)
            label.setPos(sum(self.bands[i])/2./50.,0.5)
            
        v.addItem(p)

        self.nextRow()

            
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

                #affichage
            p=self.addPlot(None)
            self.barGraphs[i]=bg.BarGraphItem(x0=x0,
                                              x1=x1,
                                              # width=width,
                                              height=pows,
                                              brushes=brushes 
                                              )
            
            p.addItem(self.barGraphs[i])

            #effacer l'axe des ordonnées
            p.showAxis('left',False)
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
                
            if self.colorMode:
                #étalonnage du gradient de couleurs sur les valeurs du spectre
                brushes=self.scaledBrushes(pows,i)
            else:
                brushes=None

                #mise à jour des graphes           
            self.barGraphs[i].updateHeights(pows,brushes)

        self.posLastResult=(self.posLastResult+1)%self.stackLen


    def adaptRange(self):
        for i in self.channels:
            maxS=np.max(self.lastResults[i])
            self.barGraphs[i].parentWidget().setRange(yRange=(0,maxS*1.1))
            
    def keyPressEvent(self,e):
        if e.key()==pg.QtCore.Qt.Key_Escape:
            self.showNormal()
        elif e.key()==pg.QtCore.Qt.Key_Space:
            self.adaptRange()


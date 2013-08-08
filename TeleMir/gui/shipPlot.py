# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, QtOpenGL,Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy
from objloader import *
from .pyqtgraphWorker import GraphicsWorker


class glSpaceShip(QtOpenGL.QGLWidget,GraphicsWorker):
    '''
    Cette classe affiche un vaisseau spatiale dont les mouvements
    sont liées à des vitesses amenée par un flux (deux canaux).
    Il y a aussi des carrés qui se déplacent vers l'écran.
    C'est pas vraiment fini.
    '''    

    def __init__(self,stream,parent=None):
        QtOpenGL.QGLWidget.__init__(self,parent)
        GraphicsWorker.__init__(self,stream,1.)# on ne se soucis pas de la taille de la fenêtre, puisqu'on utilisera toujours la dernière valeur.
        
        #Coordonnées du vaisseau
        self.x=0
        self.y=0
        self.vitx=0
        self.vity=0
        
        #distance des cubes (passer tout ça en objet, c'est trop laid comme ça)
        self.dists=[50,0,-50]
        self.xcubes=[-20,20,30]
        self.zcubes=[10,-30,20]


    def initPlots(self):
        self.setFixedSize(1600,1600)
        self.show()
        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)  

        self.obj = OBJ('spaceFighter.obj', swapyz=True)

        glMatrixMode( GL_PROJECTION )
        glLoadIdentity( )
        gluPerspective(70,640./480,1,200)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

    def updatePlots(self):

        self.vitx=(self.data[1,-1]+2.)*5
        self.vity=(self.data[0,-1]+3.)*5

        #filtre des valeurs les plus basses, pour éviter un peu la dérive
        if abs(self.vitx) == 5 : self.vitx=0
        if abs(self.vity) == 5 : self.vity=0

        #Euler
        self.x+=self.vitx*self.period/1000.
        self.y+=self.vity*self.period/1000.

        #Les cubes avancent
        self.dists=[(dist-58)%200 - 200 + 50 for dist in self.dists]
        self.updateGL()


    def paintGL(self):
                
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        #position de la caméra
        gluLookAt(0,-150,0,0,0,0,0,0,1)

        self.dessiner_navette()

        for i in range(len(self.xcubes)):
            self.dessiner_cube(i)

        glFlush()

    def dessiner_navette(self):

        glPushMatrix()
        
        #rotation en fonction des valeurs enregistrées
        glRotated(-self.x,1,0,0)
        glRotated(self.y,0,0,1)
     
        glCallList(self.obj.gl_list)

        glPopMatrix()
        


    def dessiner_cube(self,i):

        glPushMatrix()
        glTranslated(self.xcubes[i],self.dists[i],self.zcubes[i])
        #print self.dist
        glBegin(GL_QUADS)
        
        taille_cube=5
        #face rouge
        glColor3ub(200,200,200)
        glVertex3d(taille_cube,taille_cube,taille_cube)
        glVertex3d(taille_cube,-taille_cube,taille_cube)
        glVertex3d(taille_cube,-taille_cube,-taille_cube)
        glVertex3d(taille_cube,taille_cube,-taille_cube)

        #face
        glColor3ub(60,60,60)
        glVertex3d(-taille_cube,taille_cube,taille_cube)
        glVertex3d(-taille_cube,taille_cube,-taille_cube)
        glVertex3d(-taille_cube,-taille_cube,-taille_cube)
        glVertex3d(-taille_cube,-taille_cube,taille_cube)

        #face verte
        glColor3ub(100,100,100)
        glVertex3d(taille_cube,taille_cube,taille_cube)
        glVertex3d(taille_cube,taille_cube,-taille_cube)
        glVertex3d(-taille_cube,taille_cube,-taille_cube)
        glVertex3d(-taille_cube,taille_cube,taille_cube)

        #face bleue
        glColor3ub(140,140,140)
        glVertex3d(taille_cube,-taille_cube,taille_cube)
        glVertex3d(-taille_cube,-taille_cube,taille_cube)
        glVertex3d(-taille_cube,-taille_cube,-taille_cube)
        glVertex3d(taille_cube,-taille_cube,-taille_cube)

        #face blanche
        glColor3ub(170,170,170)
        glVertex3d(taille_cube,taille_cube,taille_cube)
        glVertex3d(-taille_cube,taille_cube,taille_cube)
        glVertex3d(-taille_cube,-taille_cube,taille_cube)
        glVertex3d(taille_cube,-taille_cube,taille_cube)

        #face
        glColor3ub(200,200,200)
        glVertex3d(taille_cube,taille_cube,-taille_cube)
        glVertex3d(taille_cube,-taille_cube,-taille_cube)
        glVertex3d(-taille_cube,-taille_cube,-taille_cube)
        glVertex3d(-taille_cube,taille_cube,-taille_cube)

        
        glEnd()

        glPopMatrix()
        glFlush()
        

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Left:
            self.x+=5
        if event.key()==QtCore.Qt.Key_Right:
            self.x-=5

        if event.key()==QtCore.Qt.Key_Q:
            self.y+=5
        if event.key()==QtCore.Qt.Key_D:
            self.y-=5
        
        self.updateGL()

    def mousePressEvent(self, event): #simpleclic
        pass
        #print event.pos()

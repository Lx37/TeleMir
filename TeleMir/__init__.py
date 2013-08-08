# -*- coding: utf-8 -*-
"""
TeleMir depend on pyacq that offer some device and in particular Emotiv.

You can find here main core object of teleMir that can be re-usable projet by projets.

Divide in 2 parts:
    * TeleMir.analyses   for Rt analysis with no graphic interface
    * TeleMir.gui   for displaying signals and everything related based on PyQt4 and pyqtgraph


"""

from .analyses import *

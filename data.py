# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:31:38 2017

@author: chenf
"""

import numpy  as np
import pandas as pd
import platform
import os



def getDropboxLoc():
    """
    get the drop box location on each computer.
    """
    compNode =  platform.node()
    if compNode == "DESKTOP-5R528PV":
        path = "C:\\Users\\chenf\\Dropbox\\Stat Arb Data"
    elif compNode == "Golden":
        path = "C:\\Users\\zil20\\Dropbox\\Stat Arb Data"
        
    return path

dropboxPath = getDropboxLoc()

def getFiveFactorData(path = dropboxPath, dataPath = "Validation Data\\F-F_Research_Data_5_Factors_2x3.CSV"):
    return pd.read_csv(os.path.join(path, dataPath))
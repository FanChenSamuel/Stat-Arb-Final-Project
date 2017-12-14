# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:31:38 2017

@author: chenf, linz
"""

import numpy  as np
import pandas as pd
import platform
import os

def convertMonthToContinuous(monthIndex):
    return (monthIndex // 100) + (monthIndex % 100 / 12)    

def getDropboxLoc():
    """
    get the drop box location on each computer.
    """
    compNode =  platform.node()
    if compNode == "DESKTOP-5R528PV":
        path = "C:\\Users\\chenf\\Dropbox\\Stat Arb Data"
    elif compNode == "Golden":
        path = "C:\\Users\\zil20\\Dropbox\\Stat Arb Data"
    elif compNode == "LAPTOP-DRMK58F0":
        path = "C:\\Users\\Alex Huang\\Dropbox\\Stat Arb Data"
    elif compNode == "apple-PC.wv.cc.cmu.edu":
        path = "/Users/Fei/Dropbox/Stat Arb Data"
    return path

dropboxPath = getDropboxLoc()

def cleanFrenchData(df):
    # -99.99 is the missing value of the French data
    df[df < -99] = np.nan
    return df

def cleanCRSP(df):
    # all the codes that will clean crsp go here
    # clear all the data without NAICS codes
    df = df[pd.notnull(df['NAICS'])]
    # change all date format from yyyymmdd to yyyymm
    df["date"] = df.date // 100
    # change all the column names to lower case
    df.columns = [x.lower() for x in list(df)]
    # change negative bid, ask, price numbers
    changeneg = lambda x:np.nan if x <= 0 else x
    df['bidlo'] = df['bidlo'].apply(changeneg)
    df['askhi'] = df['askhi'].apply(changeneg)
    df['prc'] = df['prc'].apply(changeneg)
    return df

def cleanCompustat(df):
    # all the codes that will clean compustat go here
    df = df[pd.notnull(df['naics'])]
    df = df[pd.notnull(df['cusip'])]
    # change data format from yyyymmdd to yyyymm
    df["datadate"] = df.datadate // 100
    # change the datadate column name to date
    df = df.rename(columns = {'datadate':'date'})
    # delete the last digit of cusip so that it can be merged with crsp data
    killdigit = lambda x:x[:-1]
    df["cusip"] = df["cusip"].apply(killdigit)
    return df

def cleanMergeData(df):
    # Remove useless columns
    df = df.drop(labels = ['permno', 'exchcd', 'ncusip', 'permco', 'spread', 'altprc', 'spread', 'gvkey', 'fyearq', 'fqtr', 'indfmt', 'consol', 'popsrc', 'datafmt', 'tic', 'curcdq', 'datacqtr', 'datafqtr', 'exchg', 'costat', 'mkvaltq', 'naics_y'], axis=1)
    # change the naics_x column name to naics
    df= df.rename(columns = {'naics_x': 'naics'})
    # use cumulative factor to adjust price to adjust price
    df['prc'] = df['prc']/df['cfacpr']
    df['shrout'] = df['shrout']/df['cfacshr']
    df = df.drop(labels = ['cfacpr', 'cfacshr'], axis = 1)
    # forward fill data
    df[['atq', 'cshprq','epspxq']] = df[['atq', 'cshprq', 'epspxq']].ffill()
    # calculate Book to Market ratio
    # df['b2m'] = df['prc']*df['shrout']/(1000*df['atq'])
    return df

def getFiveFactorData(path = dropboxPath, dataPath = os.path.join("Validation Data", "F-F_Research_Data_5_Factors_2x3.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanFrenchData(df)

def get5IndustryPort(path = dropboxPath, dataPath = os.path.join("Validation Data", "5_Industry_Portfolios.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanFrenchData(df)

def get10IndustryPort(path = dropboxPath, dataPath = os.path.join("Validation Data", "10_Industry_Portfolios.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanFrenchData(df)

def get49IndustryPort(path = dropboxPath, dataPath = os.path.join("Validation Data", "49_Industry_Portfolios.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanFrenchData(df)

def getSP500Data(path = dropboxPath, dataPath = os.path.join("Validation Data", "SP500.csv")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return df

def getCRSP(path = dropboxPath, dataPath = os.path.join("Project Data","crsp.CSV")): 
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanCRSP(df)

def getCompustat(path = dropboxPath, dataPath = os.path.join("Project Data","compustat.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return cleanCompustat(df)

def getMergeData():
    return cleanMergeData(pd.merge(getCRSP(), getCompustat(), on=['cusip', 'date'], how = "left"))

def getCleanData(path = dropboxPath, dataPath = os.path.join("Project Data", "cache_clean_data.CSV")):
    df = pd.read_csv(os.path.join(path, dataPath))
    return df

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:31:38 2017

@author: chenf, linz
"""

import numpy  as np
import pandas as pd
import platform
import os
from datetime import timedelta

# MOM_LAG = 4

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
    df['b2m'] = df['prc']*df['shrout']/(1000*df['atq'])
    # calculate the momentum measure as the return from the previous month minus MOM_LAG numbers of months
    # df['mom'] = 
    # map all the naics codes to fama french industry
    df = mapSector(df)
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
    df["Month"] = df.Date.apply(pd.Timestamp) - timedelta(days = 1)
    df.Month = df.Month.astype(str).apply(lambda x: int(x[0:4] + x[5:7]))
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

# Input a vector of NAICS codes
# The function will map the codes to Fama French
def mapSector(df):
    for i in range(len(df["naics"])):
        if i % 1000 == 0:
            print(i)
        f4 = int(str(df["naics"][i])[:4])
        ind = ""
        if 100 <= f4 <= 999:
            ind = "NoDur"
        elif 2000 <= f4 <= 2399:
            ind = "NoDur"
        elif 2700 <= f4 <= 2749:
            ind = "NoDur"
        elif 2770 <= f4 <= 2799:
            ind = "NoDur"
        elif 3100 <= f4 <= 3199:
            ind = "NoDur"
        elif 3940 <= f4 <= 3989: 
            ind = "NoDur"
        elif 2500 <= f4 <= 2519:
            ind = "Durbl"
        elif 2590 <= f4 <= 2599:
            ind = "Durbl"
        elif 3630 <= f4 <= 3659:
            ind = "Durbl"
        elif 3710 <= f4 <= 3711: 
            ind = "Durbl"
        elif 3714 <= f4 <= 3714:
            ind = "Durbl"
        elif 3716 <= f4 <= 3716:
            ind = "Durbl"
        elif 3750 <= f4 <= 3751: 
            ind = "Durbl"
        elif 3792 <= f4 <= 3792: 
            ind = "Durbl"
        elif 3900 <= f4 <= 3939:
            ind = "Durbl"
        elif 3990 <= f4 <= 3999: 
            ind = "Durbl"
        elif 2520 <= f4 <= 2589:
            ind = "Manuf"
        elif 2600 <= f4 <= 2699:
            ind = "Manuf"
        elif 2750 <= f4 <= 2769:
            ind = "Manuf"
        elif 2800 <= f4 <= 2829: 
            ind = "Manuf"
        elif 2840 <= f4 <= 2899: 
            ind = "Manuf"
        elif 3000 <= f4 <= 3099:
            ind = "Manuf"
        elif 3200 <= f4 <= 3569:
            ind = "Manuf"
        elif 3580 <= f4 <= 3621: 
            ind = "Manuf"
        elif 3623 <= f4 <= 3629: 
            ind = "Manuf"
        elif 3700 <= f4 <= 3709: 
            ind = "Manuf"
        elif 3712 <= f4 <= 3713: 
            ind = "Manuf"
        elif 3715 <= f4 <= 3715:
            ind = "Manuf"
        elif 3717 <= f4 <= 3749: 
            ind = "Manuf"
        elif 3752 <= f4 <= 3791:
            ind = "Manuf"
        elif 3793 <= f4 <= 3799:
            ind = "Manuf"
        elif 3860 <= f4 <= 3899:
            ind = "Manuf"
        elif 1200 <= f4 <= 1399: 
            ind = "Enrgy"
        elif 2900 <= f4 <= 2999:
            ind = "Enrgy"
        elif 3570 <= f4 <= 3579:
            ind = "HiTec"
        elif 3622 <= f4 <= 3622: 
            ind = "HiTec"
        elif 3660 <= f4 <= 3692: 
            ind = "HiTec"
        elif 3694 <= f4 <= 3699:
            ind = "HiTec"
        elif 3810 <= f4 <= 3839: 
            ind = "HiTec"
        elif 7370 <= f4 <= 7379: 
            ind = "HiTec"
        elif 7391 <= f4 <= 7391:
            ind = "HiTec"
        elif 8730 <= f4 <= 8734:
            ind = "HiTec"
        elif 4800 <= f4 <= 4899:
            ind = "Telcm"
        elif 5000 <= f4 <= 5999:
            ind = "Shops"
        elif 7200 <= f4 <= 7299:
            ind = "Shops"
        elif 7600 <= f4 <= 7699:
            ind = "Shops"
        elif 2830 <= f4 <= 2839:
            ind = "Hlth"
        elif 3693 <= f4 <= 3693:
            ind = "Hlth"
        elif 3840 <= f4 <= 3859: 
            ind = "Hlth"
        elif 8000 <= f4 <= 8099:
            ind = "Hlth"
        elif 4900 <= f4 <= 4949: 
            ind = "Hlth"
        else:
            ind = "Other"
        df["naics"][i]=ind 
    df= df.rename(columns = {'naics': 'ffind'})
    return df
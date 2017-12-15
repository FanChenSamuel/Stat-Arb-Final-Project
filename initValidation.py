# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin
"""

from data import (getFiveFactorData, 
                 get5IndustryPort, 
                 get10IndustryPort, 
                 get49IndustryPort, 
                 convertMonthToContinuous,
                 getSP500Data)
                 
from Filter import long_short_filter, ranking_filter, long_ranking_filter
import statsmodels.api as sm
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import OrderedDict

#function that extracts the p value for skew test 
def Skewtest(array):
    return stats.skewtest(array)[1]

#function that extracts the p value for kurtosis test
def Kurtotest(array):
    return stats.kurtosistest(array)[1]

## Missing Descriptive statistics
def descStatistics(indDf: pd.DataFrame, rfDf: pd.DataFrame): 
    indName=indDf.columns[1:]
    '''merge industry data with risk free data by month'''
    mergeDf=pd.merge(indDf, rfDf, on = ["Month"])
    '''excess return data'''
    excessRet=mergeDf[indName].subtract(mergeDf['RF'], axis = 0)
    '''compute descriptive stats'''
    meanret=excessRet.apply(np.mean,axis=0)
    std=excessRet.apply(np.std,axis=0)
    skew=excessRet.apply(stats.skew,axis=0)
    skewpvalue=excessRet.apply(Skewtest,axis=0)
    kurto=excessRet.apply(stats.kurtosis,axis=0)
    kurtopvalue=excessRet.apply(Kurtotest,axis=0)
    return pd.DataFrame(OrderedDict((("Mean Return",meanret),("Standard Deviation",std),
                         ("Skew",skew),("Skew-pvalue",skewpvalue),
                         ("Kurtosis",kurto),("Kurtosis-pvalue",kurtopvalue))))
    

def regressFactorModel(factorDf: pd.DataFrame, indDf: pd.DataFrame, rfDf: pd.DataFrame, period = 36, min_period = 12):
    """
    Get the 
    Input: 
        - factorDf: DataFrame with first column - Month, the other columns are 
        the return of the factors
        
        - industryDf: DataFrame with first column Month, the other columns are 
        the return of each industries.
        
        - period: (Default: 36) should be an int. The length of lookback period
        in the regression
        
        - min_period: (Default: 12) Should be an int. The minimum observations 
        required in the regression
    
    Output: dict of DataFrame, that represents the intercept and beta to each of
    the factors
    
    """
    
    assert factorDf.columns[0] == "Month"
    assert indDf.columns[0] == "Month"
    assert type(period) == int
    assert type(min_period) == int
    
    nFactor = len(factorDf.columns) - 1
    nind    = len(indDf.columns) - 1
    
    factorName = factorDf.columns[1:]
    indName    = indDf.columns[1:]
    
    # Merge Data
    mergeDf = pd.merge(factorDf, indDf, on = ["Month"])
    mergeDf = pd.merge(mergeDf, rfDf, on = ["Month"])
    
    # Get Excess return of each of the industry
    mergeDf[indName] = mergeDf[indName].subtract(mergeDf['RF'], axis = 0)
    mergeDf.index = mergeDf.Month
    n = len(mergeDf)
    regOutput = dict(zip( factorDf.columns[1:] , [pd.DataFrame(columns = indName, index = mergeDf["Month"] )] * nFactor) )
    regOutput['Alpha'] = pd.DataFrame(columns = indName, index = mergeDf["Month"] )
    
    def regress(y, X): 
        try: 
            X = sm.add_constant(X)
            model = sm.OLS( y, X, missing = "drop")
            results = model.fit()
            coefs   = results.params
            if results.nobs < min_period:    
                coefs = coefs * np.nan         
        except:
            coefs = pd.Series(data = np.nan, index = ["const"] + list(factorName))
        return coefs
    
    for i in range(period, n):
        Month = mergeDf.Month[(i - period): i]
        curMonth = Month.values[-1]
        for ind in indName:
            y = mergeDf[ind][Month]
            X = mergeDf[factorName].loc[Month]
            temp_coef = regress(y, X)
            regOutput["Alpha"][ind].loc[curMonth] = temp_coef.const
            for factor in factorName:
                regOutput[factor][ind].loc[curMonth] = temp_coef[factor]
                            
    return regOutput

def validateInitStrategy(signal, portReturn, long_short = True, selection = ranking_filter):
    """
    Use the alpha signal to generate the portfolio return 
    """
    portReturn.index = convertMonthToContinuous(portReturn.Month)
    portReturn = portReturn.drop(["Month"], axis = 1)
    nPort = len(signal.columns)
    
    firstMonthIdx = np.min(np.where(np.sum(pd.isnull(signal), axis = 1) < nPort - 0.01))
    firstMonth    = signal.index[firstMonthIdx]
    
    signal = signal[signal.index >= firstMonth]
    signal = signal.astype(np.float64)
    portReturn = portReturn[portReturn.index >= firstMonth]
    
    portValue = [1]
    curValue  = 1
    
    for i in range(len(signal) - 1):
        temp_pos = selection(signal.iloc[i])
#        print(np.sum(temp_pos))
        temp_ret = np.dot(temp_pos , portReturn.iloc[i + 1])
        curValue *= 1 + (temp_ret / 100)
        portValue.append(curValue)
    
    return pd.DataFrame({"Portfolio Value":portValue}, index = signal.index)

if __name__ == "__main__":
    fiveFactor = getFiveFactorData()
    ind_5      = get5IndustryPort()
    ind_10     = get10IndustryPort()
    ind_49     = get49IndustryPort()
    
    print("Data Successfully loaded!")
    ind_5_factor = regressFactorModel(fiveFactor.iloc[:, 0:6], ind_5, fiveFactor[['Month', 'RF']])
    print("5 Industry Completed!")
    ind_10_factor = regressFactorModel(fiveFactor.iloc[:, 0:6], ind_10, fiveFactor[['Month', 'RF']]) 
    print("10 Industry Completed!")
    ind_49_factor = regressFactorModel(fiveFactor.iloc[:, 0:6], ind_49, fiveFactor[['Month', 'RF']])
    print("49 Industry Completed!")
    
    ind_10_alpha = ind_10_factor['Alpha']
    ind_10_alpha.index = convertMonthToContinuous(ind_10_alpha.index)
    
    ind_10_alpha.plot(figsize = (12, 4))
    plt.title("Industry Fama-French Five-Factor Model Alpha")
    plt.savefig("alpha.png")
    
    ind_10_rank = ind_10_alpha.rank(axis = 1, method = "max")
    plt.figure(figsize = (12, 4))
    for ind in ind_10_rank.columns:
        plt.scatter(ind_10_rank.index, ind_10_rank[ind], marker = "s", label = ind)
    plt.legend()
    plt.title("Industry Ranking")
    plt.savefig("IndustryRanking.png")
    # Ranking plot
    
    plt.figure(figsize = (8,6))
#    ax1 = ind_10_alpha.iloc[:, 0:5].plot()
    ax1 = ind_10_alpha.plot()
    lines, legends = ax1.get_legend_handles_labels()
    
    des_5 =descStatistics(ind_5,fiveFactor[['Month', 'RF']])
    des_10=descStatistics(ind_10,fiveFactor[['Month', 'RF']])
    des_49=descStatistics(ind_49,fiveFactor[['Month', 'RF']])
    
    res = validateInitStrategy(ind_10_alpha, ind_10, selection = long_ranking_filter)
    benchmarkData = getSP500Data()
    benchmarkData.index = convertMonthToContinuous(benchmarkData.Month)
    
    res = pd.merge(res, benchmarkData, how = "left", left_index=True, right_index = True)
    res["Benchmark"] = res.Close / res.Close.values[0]
    
    res[["Portfolio Value", "Benchmark"]].plot()    
    
    
    
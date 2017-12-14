# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin
"""

from data import getFiveFactorData, get5IndustryPort, get10IndustryPort, get49IndustryPort
import statsmodels.api as sm
import pandas as pd
import numpy  as np

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
    
    
    
    
    
    
    
    
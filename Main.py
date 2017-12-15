# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special thank to Junyi Zhou, my asset management teammate, to co-author the 
strategy-framework in this case
"""


#import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
#from functools import partial

from Strategy import SectorRotationStrategy
from Cost import LinearCost
from Filter import long_short_filter, ranking_filter, equal_weight, long_ranking_filter
from data import getMergeData, get10IndustryPort, getFiveFactorData, convertMonthToContinuous
from initValidation import regressFactorModel

if __name__ == "__main__":
    mergeDf = getMergeData()
    mergeDf = mergeDf.rename(columns = {"date": "Month"})
    price   = mergeDf.pivot_table(index = "Month", columns = "ticker", values = "prc", aggfunc = "first")
    bid = mergeDf.pivot_table(index = "Month", columns = "ticker", values = "bidlo", aggfunc = "first")
    ask = mergeDf.pivot_table(index = "Month", columns = "ticker", values = "askhi", aggfunc = "first")
    
    ind_10     = get10IndustryPort()
    ind_list   = ind_10.columns[1:]
    fiveFactor = getFiveFactorData()
    ind_10_factor = regressFactorModel(fiveFactor.iloc[:, 0:6], ind_10, fiveFactor[['Month', 'RF']]) 
    
    ind_10_alpha = ind_10_factor['Alpha']
    ind_10_alpha.index = convertMonthToContinuous(ind_10_alpha.index)    
    
    alphaDf = ind_10_alpha.unstack().reset_index().rename(columns = {"level_0":"Industry", 0: "Alpha"})
    alphaDf.Month = alphaDf.Month.apply(lambda x:  int( (x%1) * 12 + (x // 1) * 100 ))
    mergeDf = pd.merge(mergeDf, alphaDf, how = "left", on = ["Industry", "Month"])
    
    alpha = mergeDf.pivot_table(index = "Month", columns = "ticker", values = "Alpha", aggfunc = "first")
    industry = mergeDf.pivot_table(index = "Month", columns = "ticker", values = "Industry", aggfunc = "first")
    
    valid_list = alpha.columns.intersection(price.columns)
    valid_list = valid_list.intersection(bid.columns)
    valid_list = valid_list.intersection(ask.columns)
    industry = industry[valid_list]
    
    alpha = alpha[valid_list]
    bid   = bid[valid_list]
    ask   = ask[valid_list]    
    price = price[valid_list]
    
    alpha.to_pickle("alpha.pkl")    
    bid.to_pickle("bid.pkl")    
    ask.to_pickle("ask.pkl")    
    price.to_pickle("price.pkl")    
    industry.to_pickle("industry.pkl")    
    
    alpha = pd.read_pickle("alpha.pkl").reset_index(drop = True)
    bid = pd.read_pickle("bid.pkl").reset_index(drop = True)
    ask = pd.read_pickle("ask.pkl").reset_index(drop = True)
    price = pd.read_pickle("price.pkl").reset_index(drop = True)
    industry = pd.read_pickle("industry.pkl").reset_index(drop = True)
    
    lin_cost = LinearCost(0.001)
    strat = SectorRotationStrategy(price, bid, ask, alpha, industry, 6, 1, long_ranking_filter, equal_weight, lin_cost, ind_list)
    strat.run()
    
    print("Mission Complete!")
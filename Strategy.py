# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special Thanks to Junyi Zhou, Fan's Asset Management Teammate, to provide the 
start-up code for the project
"""

import numpy as np
import pandas as pd

class SectorRotationStrategy:
    def __init__(self, price, bid, ask, score, industry, forming, holding, ind_fltr, stock_fltr, cost_model, ind_list, capital=1000, second_score = None):
        """
        :param price: df of prices
        :param b2m: df of book to market
        :param bid: df of bid
        :param ask: df of ask
        :param forming: forming period
        :param holding: holding period
        :param lag: lag period
        :param filtr: a function that takes vector of score and returns vector of position weight
        :param cost_model: cost model
        :param capital: capital for long-short (eg. capital=1000 means if you sum all portfolios, long 1000 and short 1000)
        """
        self.price = price
        self.bid = bid
        self.ask = ask
        self.forming = forming
        self.holding = holding
        self.score   = score
        self.industry = industry
        self.capital = capital
        self.ind_fltr = ind_fltr
        self.stock_fltr = stock_fltr
        self.cost_model = cost_model
        self.ind_list   = ind_list
        self.momentum = self.price.pct_change(forming)       # lagged rolling return
        self.second_score = second_score if second_score else self.momentum 
        
    def filtr(self, score, second_score, ind):
        res = score * np.nan
        indDf = pd.DataFrame({'Ind': ind, "score": score}).drop_duplicates(subset = "Ind")
        indDf["Weight"] = self.ind_fltr(indDf.score)
        print("Industry Weight", np.nansum(indDf.Weight))
        for indsty in self.ind_list:
            if len(indDf.Weight[indDf.Ind == indsty].values) > 0:
                res[ind == indsty]  = self.stock_fltr(second_score[ind == indsty]) * indDf.Weight[indDf.Ind == indsty].values[0]
            else: 
                res[ind == indsty]  = self.stock_fltr(second_score[ind == indsty]) * 0
            print("Industry", indsty,"Stock Weight Sum", np.nansum(res[ind == indsty]))
        return res
    
    def run(self):
        self.cash = pd.Series(data=0., index=list(self.price.index))    # assume all strategy have zero value to set up
        self.shares = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.weights = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.value = pd.Series(data=0., index=list(self.price.index))            # value of all current portfolios
        bid = np.zeros(self.price.shape[1])
        ask = np.zeros(self.price.shape[1])
        price = np.zeros(self.price.shape[1])
        nPeriod = self.price.shape[0]
        
        for i in range(self.forming, nPeriod):
#            bid_price = self.bid.iloc[i]
#            ask_price = self.ask.iloc[i]
#            cur_price = self.price.iloc[i]            
#            
#            cur_score = self.score.iloc[i]
#            cur_sec_score = self.second_score.iloc[i]
#            cur_ind   = self.industry.iloc[i]
#            
#            pos = self.filtr(cur_score, cur_sec_score, cur_ind)
#            
#            if i <= (nPeriod - self.holding):
#                values_to_open = pos * self.capital / self.holding
#                shares_to_open = ((values_to_open*(values_to_open>0)/ask_price).replace(np.nan,0)
#                                + (values_to_open*(values_to_open<0)/bid_price).replace(np.nan,0))
#            else:
#                shares_to_open = 0
#                
#            if i >= (self.forming + self.holding - 1):
#                shares_to_close = self.shares.iloc[i - self.holding]
#            else:
#                shares_to_close= 0
#                
#            reposition_shares = (shares_to_open - shares_to_close).replace(np.nan, 0)
#            reposition = ((reposition_shares[reposition_shares>0] * ask_price).replace(np.nan,0)
#                 + (reposition_shares[reposition_shares<0] * bid_price).replace(np.nan,0))
#            
#            t_cost = self.cost_model.calculate_cost(np.abs(reposition))
#            self.cash.iloc[i] = self.cash.iloc[i - 1] - sum(reposition + t_cost)
#            self.shares.iloc[i] = shares_to_open
#            total_shares = self.shares.iloc[max((i-self.holding+1),0):(i+1)].sum()
#            self.value.iloc[i] = self.cash.iloc[i] + sum((total_shares*cur_price).replace(np.nan, 0))
            
            # print(self.momentum.index[i])
            bid = bid * (np.isnan(self.bid.iloc[i])) + self.bid.iloc[i] * (~np.isnan(self.bid.iloc[i]))
            ask = ask * (np.isnan(self.ask.iloc[i])) + self.ask.iloc[i] * (~np.isnan(self.ask.iloc[i]))
            price = price * (np.isnan(self.price.iloc[i])) + self.price.iloc[i] * (~np.isnan(self.price.iloc[i]))
            print(i)
            # close old position
            if i >= self.forming + self.holding - 1:
                shares_to_close = np.nan_to_num(self.shares.iloc[i - self.holding])
            else:
                shares_to_close = 0
            # open new position, stop building new position when holding period < time left
            if i <= self.price.shape[0] - self.holding and (~np.isnan(self.momentum.iloc[i])).any():
                weights = self.filtr(self.score.iloc[i], self.second_score.iloc[i], self.industry.iloc[i])
                print(np.nansum(weights))
                values_to_open = np.nan_to_num( weights * self.capital / self.holding)
                shares_to_open = np.nan_to_num(values_to_open * (values_to_open>0) / ask
                                               + values_to_open * (values_to_open<0) / bid)
            else:
                shares_to_open = 0
                values_to_open = 0
            
            # reposition is actual value of portfolio that need to be traded
            reposition_shares = shares_to_open - shares_to_close
            reposition = np.nan_to_num(reposition_shares * (reposition_shares>0) * ask
                                       + reposition_shares * (reposition_shares<0) * bid)
            transaction_cost = self.cost_model.calculate_cost(np.abs(reposition))
            # current cash = previous cash + proceed from closing - cost to open - transaction
            self.cash[i] = self.cash[i-1] - np.nansum(reposition + transaction_cost)
            self.shares.iloc[i] = shares_to_open
            self.weights.iloc[i] = values_to_open
            total_shares = self.shares.iloc[i-self.holding+1:i+1].sum(axis=0)
            # this is the value of portfolio if we close out everything now
            self.value.iloc[i] = np.sum(total_shares*(total_shares>0)*bid
                                        + total_shares*(total_shares<0)*ask) + self.cash[i]

#    def run_without_bid_ask(self):
#        self.cash = pd.Series(data=0., index=list(self.price.index))  # assume all strategy have zero value to set up
#        self.shares = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
#        self.weights = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
#        self.value = pd.Series(data=0., index=list(self.price.index))  # value of all current portfolios
#        trading_price = np.zeros(
#            self.price.shape[1])  # if price is na, will use last trading price, otherwise current price
#        for i in range(self.forming + self.lag, self.price.shape[0]):
#            # print(self.momentum.index[i])
#            trading_price = trading_price * (np.isnan(self.price.iloc[i])) \
#                            + self.price.iloc[i] * (~np.isnan(self.price.iloc[i]))
#
#            # close old position
#            if i >= self.forming + self.holding - 1:
#                shares_to_close = np.nan_to_num(self.shares.iloc[i - 6])
#            else:
#                shares_to_close = 0
#            # open new position, stop building new position when holding period < time left
#            if i <= self.price.shape[0] - self.holding \
#                    and np.isnan(self.momentum.iloc[i]).any():
#                shares_to_open = np.nan_to_num(
#                    self.filtr(self.score.iloc[i], self.second_score.iloc[i]) * self.capital / self.holding / trading_price)
#            else:
#                shares_to_open = 0
#
#            # reposition is actual value of portfolio that need to be traded
#            reposition = np.nan_to_num(np.abs(shares_to_open - shares_to_close) * trading_price)
#            transaction_cost = self.cost_model.calculate_cost(reposition)
#            # current cash = previous cash + proceed from closing - cost to open - transaction
#            self.cash[i] = self.cash[i - 1] + np.nansum(
#                shares_to_close * trading_price - shares_to_open * trading_price - transaction_cost)
#            self.shares.iloc[i] = shares_to_open
#            self.weights.iloc[i] = shares_to_open * trading_price / self.capital * self.holding
#            self.value.iloc[i] = np.sum(self.shares.iloc[i - self.holding+1:i + 1].sum(axis=0) * trading_price) + self.cash[i]
#
#    def calculate_metrics(self):
#        annual_return = self.value[-1] / self.capital / (self.price.shape[0] - self.forming) * 12
#        volatility = np.nanstd(self.value.diff() / self.capital) * np.sqrt(12/(self.price.shape[0] - self.forming))
#        return annual_return, volatility, annual_return / volatility
#    
#class SectorRotationStrategy(Strategy):
#    def __init__(self, price : pd.DataFrame, forming, holding, filtr, cost_model, capital=1000, smooth=0):
#        super().__init__(price, forming, holding, filtr, cost_model, capital, smooth)
#        self.score = self.price.pct_change(forming)     # rolling return
#        if smooth:
#            for i in range(holding+forming, price.shape[0]):
#                self.score.iloc[i] = (1-smooth)*self.score.iloc[i] + smooth*self.score.iloc[i-holding]

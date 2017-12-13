# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special Thanks to Junyi Zhou, Fan's Asset Management Teammate, to provide the 
start-up code for the project
"""

import numpy as np
import pandas as pd

class Strategy:
    def __init__(self, price : pd.DataFrame, forming, holding, filtr, cost_model, capital=1000, smooth=0):
        """
        :param price: df of prices
        :param forming: forming period
        :param holding: holding period
        :param filtr: a function that takes vector of score and returns vector of position weight
        :param cost_model: cost model
        :param capital: capital for long-short (eg. capital=100 means if you sum all portfolios, long 100 and short 100)
        :param smooth: parameter used to smooth scores
        """
        self.price = price
        self.forming = forming
        self.holding = holding
        self.capital = capital
        self.filter = filtr
        self.cost_model = cost_model
        self.score = None   # TO BE initialized in child class

    def run(self):
        self.cash = pd.Series(data=0., index=list(self.price.index))    # assume all strategy have zero value to set up
        self.shares = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.weights = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.value = pd.Series(data=0., index=list(self.price.index))            # value of all current portfolios
        bid = np.zeros(self.price.shape[1])
        ask = np.zeros(self.price.shape[1])
        price = np.zeros(self.price.shape[1])
        for i in range(self.forming+self.lag, self.price.shape[0]):
            # print(self.momentum.index[i])
            bid = bid * (np.isnan(self.bid.iloc[i])) + self.bid.iloc[i] * (~np.isnan(self.bid.iloc[i]))
            ask = ask * (np.isnan(self.ask.iloc[i])) + self.ask.iloc[i] * (~np.isnan(self.ask.iloc[i]))
            price = price * (np.isnan(self.price.iloc[i])) + self.price.iloc[i] * (~np.isnan(self.price.iloc[i]))

            # close old position
            if i >= self.forming + self.holding - 1:
                shares_to_close = np.nan_to_num(self.shares.iloc[i - self.holding])
            else:
                shares_to_close = 0
            # open new position, stop building new position when holding period < time left
            if i <= self.price.shape[0] - self.holding and (~np.isnan(self.momentum.iloc[i])).any():
                values_to_open = np.nan_to_num(self.filter(self.momentum.iloc[i],self.b2m.iloc[i]) * self.capital / self.holding)
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

    def run_without_bid_ask(self):
        self.cash = pd.Series(data=0., index=list(self.price.index))  # assume all strategy have zero value to set up
        self.shares = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.weights = pd.DataFrame(data=0., columns=list(self.price), index=list(self.price.index))
        self.value = pd.Series(data=0., index=list(self.price.index))  # value of all current portfolios
        trading_price = np.zeros(
            self.price.shape[1])  # if price is na, will use last trading price, otherwise current price
        for i in range(self.forming + self.lag, self.price.shape[0]):
            # print(self.momentum.index[i])
            trading_price = trading_price * (np.isnan(self.price.iloc[i])) \
                            + self.price.iloc[i] * (~np.isnan(self.price.iloc[i]))

            # close old position
            if i >= self.forming + self.holding - 1:
                shares_to_close = np.nan_to_num(self.shares.iloc[i - 6])
            else:
                shares_to_close = 0
            # open new position, stop building new position when holding period < time left
            if i <= self.price.shape[0] - self.holding \
                    and np.isnan(self.momentum.iloc[i]).any():
                shares_to_open = np.nan_to_num(
                    self.filter(self.momentum.iloc[i], self.b2m.iloc[i]) * self.capital / self.holding / trading_price)
            else:
                shares_to_open = 0

            # reposition is actual value of portfolio that need to be traded
            reposition = np.nan_to_num(np.abs(shares_to_open - shares_to_close) * trading_price)
            transaction_cost = self.cost_model.calculate_cost(reposition)
            # current cash = previous cash + proceed from closing - cost to open - transaction
            self.cash[i] = self.cash[i - 1] + np.nansum(
                shares_to_close * trading_price - shares_to_open * trading_price - transaction_cost)
            self.shares.iloc[i] = shares_to_open
            self.weights.iloc[i] = shares_to_open * trading_price / self.capital * self.holding
            self.value.iloc[i] = np.sum(self.shares.iloc[i - self.holding+1:i + 1].sum(axis=0) * trading_price) + self.cash[i]

class MomentumStrategy(Strategy):
    def __init__(self, price : pd.DataFrame, forming, holding, filtr, cost_model, capital=1000, smooth=0):
        super().__init__(price, forming, holding, filtr, cost_model, capital, smooth)
        self.score = self.price.pct_change(forming)     # rolling return
        if smooth:
            for i in range(holding+forming, price.shape[0]):
                self.score.iloc[i] = (1-smooth)*self.score.iloc[i] + smooth*self.score.iloc[i-holding]


class BetaStrategy(Strategy):
    def __init__(self, price : pd.DataFrame, beta : pd.DataFrame, holding, filtr, cost_model, capital=1000, smooth=0):
        super().__init__(price, 1, holding, filtr, cost_model, capital, smooth)
        valid_tickers = price.columns & beta.columns
        self.score = -beta[valid_tickers]       # negative since betting against beta
        self.price = price[valid_tickers]
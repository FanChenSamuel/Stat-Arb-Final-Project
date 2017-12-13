# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 14:27:38 2017

@author: chenf
"""

import numpy as np
import pandas as pd

class Strategy:
    def __init__(self, price : pd.DataFrame, forming, holding, filtr, cost_model, capital=1000):
        """
        :param price: df of prices
        :param forming: forming period
        :param holding: holding period
        :param filtr: a function that takes vector of score and returns vector of position weight
        :param cost_model: cost model
        :param capital: capital for long-short (eg. capital=1000 means if you sum all portfolios, long 1000 and short 1000)
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
        self.shares = pd.DataFrame(columns=list(self.price), index=list(self.price.index))
        self.value = pd.Series(index=list(self.price.index))            # value of all current portfolios
        trading_price = np.zeros(self.price.shape[1])  # if price is na, will use last trading price, otherwise current price
        for i in range(self.forming - 1, self.price.shape[0]):
            # Deal with delisting
            trading_price = trading_price * (np.isnan(self.price.iloc[i])) \
                            + self.price.iloc[i] * (~np.isnan(self.price.iloc[i]))

            # close old position
            if i >= self.forming + self.holding - 1:
                shares_to_close = np.nan_to_num(self.shares.iloc[i - 6])
            else:
                shares_to_close = 0
                
            # open new position
            if i <= self.price.shape[0] - self.holding:  # stop building new position when holding period < time left
                shares_to_open = np.nan_to_num(
                    self.filter(self.score.iloc[i]) * self.capital / self.holding / trading_price)
            else:
                shares_to_open = 0

            # reposition is actual value of portfolio that need to be traded
            reposition = np.nan_to_num(np.abs(shares_to_open - shares_to_close) * trading_price)
            transaction_cost = self.cost_model.calculate_cost(reposition)
            # current cash = previous cash + proceed from closing - cost to open - transaction
            self.cash[i] = self.cash[i-1] + np.nansum(shares_to_close*trading_price - shares_to_open*trading_price - transaction_cost)
            self.shares.iloc[i] = shares_to_open
            self.value.iloc[i] = np.sum(self.shares.iloc[i - 5:i + 1].sum(axis=0) * trading_price) + self.cash[i]


class MomentumStrategy(Strategy):
    def __init__(self, price : pd.DataFrame, forming, holding, filtr, cost_model, capital=1000):
        super().__init__(price, forming, holding, filtr, cost_model, capital)
        self.score = self.price.pct_change(forming - 1)     # rolling return


class BetaStrategy(Strategy):
    def __init__(self, price : pd.DataFrame, beta : pd.DataFrame, holding, filtr, cost_model, capital=1000):
        super().__init__(price, 1, holding, filtr, cost_model, capital)
        valid_tickers = price.columns & beta.columns
        self.score = -beta[valid_tickers]       # negative since betting against beta
        self.price = price[valid_tickers]

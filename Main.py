# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special thank to Junyi Zhou, my asset management teammate, to co-author the 
strategy-framework in this case
"""


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from functools import partial

from Strategy import Strategy, BetaStrategy
from Cost import LinearCost, QuadraticCost
from Filter import long_short_filter, ranking_filter, equal_weight

if __name__ == '__main__':
    # price = pd.DataFrame.from_csv("cleaned_price.csv")
    # price = price.loc[price.index > pd.Timestamp(1997,1,1)]
    # price = pd.DataFrame.from_csv("large_price.csv")
    price = pd.DataFrame.from_csv("mid_price.csv")
    # price = pd.DataFrame.from_csv("small_price.csv")
    # price = price.loc[price.index < pd.Timestamp(2007,1,1)]
    beta = pd.read_csv("clean_beta.csv")

    cost = LinearCost(0.005)
    # strat = MomentumStrategy(price, 6, 6, ranking_filter, cost)
    another_long_short_filter = partial(long_short_filter, long=80, short=20)
    strat = BetaStrategy(price, beta, 12, ranking_filter, cost)
    strat.run()
    plt.plot(strat.value)
    plt.show()

    # data = pd.read_csv("LargeCap.csv")
    # data = pd.read_csv("Beta.csv")
    # tickers = sorted(list(set(data['TICKER']) - {np.nan}))
    # dates = sorted(list(set(data['DATE'])))
    # cleaned = pd.DataFrame(columns=tickers, index=dates)
    # for row in data.itertuples():
    #     cleaned.loc[row.DATE,row.TICKER] = row.b_mkt
    # cleaned = np.abs(cleaned)
    # cleaned.to_csv("clean_beta.csv")

    print('ok')
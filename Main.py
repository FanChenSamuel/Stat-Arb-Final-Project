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

from Strategy import BetaStrategy, MomentumStrategy
from Cost import LinearCost, QuadraticCost, ADVCost
from Filter import long_short_filter, ranking_filter, equal_weight

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

if __name__ == '__main__':
    
    dropboxLoc = getDropboxLoc()
    # cap = "small"
    # cap = "mid"
    os.chdir(os.path.join(dropboxLoc, "Data Framework"))
    cap = "large"
    price = pd.DataFrame.from_csv("{}_price.csv".format(cap))
    volume = pd.DataFrame.from_csv("{}_vol.csv".format(cap))
    val = volume * price
    beta = pd.read_csv("clean_beta.csv")
    stats = {}
    margin = 5

    # ------ profit vs cost ------
    lin_costs = [0., .001, .002, .005, .01]
    quad_costs = [[c/2,c/200] for c in lin_costs]
    adv_costs = [[c, c*1.2] for c in lin_costs]
    capital = 1e5
    for i in range(len(lin_costs)):
        lin_cost = LinearCost(lin_costs[i])
        quad_cost = QuadraticCost(quad_costs[i][0],quad_costs[i][1])
        adv_cost = ADVCost(val, adv_costs[i][0], adv_costs[i][1])
        lin_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, lin_cost, capital=capital)
        lin_beta_strat = BetaStrategy(price, beta, 6, ranking_filter, lin_cost, capital=capital)
        quad_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, quad_cost, capital=capital)
        quad_beta_strat = BetaStrategy(price, beta, 6, ranking_filter, quad_cost, capital=capital)
        adv_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, adv_cost, capital=capital)
        adv_beta_strat = BetaStrategy(price, beta, 6, ranking_filter, lin_cost, capital=capital)
        lin_mom_strat.run()
        lin_beta_strat.run()
        quad_mom_strat.run()
        quad_beta_strat.run()
        adv_mom_strat.run()
        adv_beta_strat.run()
        stats['lin_mom_{}'.format(lin_costs[i])] = lin_mom_strat.calculate_metrics()
        stats['lin_beta_{}'.format(lin_costs[i])] = lin_beta_strat.calculate_metrics()
        stats['quad_mom_{}'.format(quad_costs[i])] = quad_mom_strat.calculate_metrics()
        stats['quad_beta_{}'.format(quad_costs[i])] = lin_beta_strat.calculate_metrics()
        stats['adv_mom_{}'.format(adv_costs[i])] = adv_mom_strat.calculate_metrics()
        stats['adv_beta_{}'.format(adv_costs[i])] = adv_beta_strat.calculate_metrics()
        if i == 0:
            lin_mom_values = pd.DataFrame(lin_mom_strat.value/capital*100, columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
            lin_beta_values = pd.DataFrame(lin_beta_strat.value/capital*100, columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
            quad_mom_values = pd.DataFrame(quad_mom_strat.value/capital*100, columns=['{}'.format(quad_costs[i][1] * 1e4)])
            quad_beta_values = pd.DataFrame(quad_beta_strat.value/capital*100, columns=['{}'.format(quad_costs[i][1] * 1e4)])
            adv_mom_values = pd.DataFrame(adv_mom_strat.value / capital * 100, columns=['{:.2f}'.format(adv_costs[i][1] * 1e4)])
            adv_beta_values = pd.DataFrame(adv_beta_strat.value / capital * 100, columns=['{:.2f}'.format(adv_costs[i][1] * 1e4)])
        else:
            lin_mom_values['{:.0f}'.format(lin_costs[i] * 1e4)] = lin_mom_strat.value/capital*100
            lin_beta_values['{:.0f}'.format(lin_costs[i] * 1e4)] = lin_beta_strat.value/capital*100
            quad_mom_values['{}'.format(quad_costs[i][1] * 1e4)] = quad_mom_strat.value/capital*100
            quad_beta_values['{}'.format(quad_costs[i][1] * 1e4)] = quad_beta_strat.value/capital*100
            adv_mom_values['{:.2f}'.format(adv_costs[i][1] * 1e4)] = adv_mom_strat.value / capital * 100
            adv_beta_values['{:.2f}'.format(adv_costs[i][1] * 1e4)] = adv_beta_strat.value / capital * 100
    lin_mom_values.plot(title='Momentum vs. Linear Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_mom_lin.png".format(cap), dpi=600)
    lin_beta_values.plot(title='BAB vs. Linear Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_beta_lin.png".format(cap), dpi=600)
    quad_mom_values.plot(title='Momentum vs. Quadratic Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_mom_quad.png".format(cap), dpi=600)
    quad_beta_values.plot(title='BAB vs. Quadratic Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_beta_quad.png".format(cap), dpi=600)
    adv_mom_values.plot(title='Momentum vs. ADV Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_mom_adv.png".format(cap), dpi=600)
    adv_beta_values.plot(title='BAB vs. ADV Cost (bps)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_beta_adv.png".format(cap), dpi=600)


    # ------ profit vs capital ------
    capitals = [10000 * np.power(10,x) for x in range(3)]
    for i, capital in enumerate(capitals):
        quad_cost = QuadraticCost(.0005, .0005/200)
        quad_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, quad_cost, capital=capital)
        quad_beta_strat = BetaStrategy(price, beta, 6, ranking_filter, quad_cost, capital=capital)
        quad_mom_strat.run()
        quad_beta_strat.run()
        if i == 0:
            quad_mom_values = pd.DataFrame(quad_mom_strat.value/capital*100, columns=['{}'.format(capital)])
            quad_beta_values = pd.DataFrame(quad_beta_strat.value/capital*100, columns=['{}'.format(capital)])
        else:
            quad_mom_values['{}'.format(capital)] = quad_mom_strat.value/capital*100
            quad_beta_values['{}'.format(capital)] = quad_beta_strat.value/capital*100
    quad_mom_values.plot(title='Momentum Profit vs. Portfolio Size (Quadratic Cost)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("mom_vs_capital_{}.png".format(cap), dpi=600)
    quad_beta_values.plot(title='BAB Profit vs. Portfolio Size (Quadratic Cost)')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("beta_vs_capital_{}.png".format(cap), dpi=600)


    # ------ profit vs market cap ------
    lin_costs = [0., .001, .002, .005, .01]
    adv_costs = [[c, c * 1.2] for c in lin_costs]
    capital = 1e8
    for i in range(len(lin_costs)):
        lin_cost = LinearCost(lin_costs[i])
        adv_cost = ADVCost(val, adv_costs[i][0], adv_costs[i][1])
        lin_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, lin_cost, capital=capital)
        adv_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, adv_cost, capital=capital)
        lin_mom_strat.run()
        adv_mom_strat.run()
        if i == 0:
            diff = pd.DataFrame((lin_mom_strat.value - adv_mom_strat.value) / capital * 100, columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
        else:
            diff['{:.0f}'.format(lin_costs[i] * 1e4)] = (lin_mom_strat.value - adv_mom_strat.value) / capital * 100 - diff['0']
    diff['0'] = 0
    diff.plot(title='{} Cap Difference in Transaction Cost'.format(cap.title()), ylim=(-.2,13))
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("lin_vs_adv_{}.png".format(cap), dpi=600)


    # ------ smoothed momentum ------
    lin_costs = [0., .001, .002, .005, .01]
    capital = 1e5
    smooth = .69
    for i in range(len(lin_costs)):
        lin_cost = LinearCost(lin_costs[i])
        lin_mom_strat = MomentumStrategy(price, 6, 6, ranking_filter, lin_cost, capital=capital, smooth=smooth)
        lin_mom_nosmooth = MomentumStrategy(price, 6, 6, ranking_filter, lin_cost, capital=capital)
        lin_mom_strat.run()
        lin_mom_nosmooth.run()
        stats['lin_smoothed_mom_{}'.format(lin_costs[i])] = lin_mom_strat.calculate_metrics()
        stats['lin_nonsmoothed_mom_{}'.format(lin_costs[i])] = lin_mom_nosmooth.calculate_metrics()
        if i == 0:
            lin_mom_values = pd.DataFrame(lin_mom_strat.value/capital*100, columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
            ns_lin_mom_values = pd.DataFrame(lin_mom_nosmooth.value / capital * 100,
                                          columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
            diffs = pd.DataFrame((lin_mom_strat.value - lin_mom_nosmooth.value)/capital*100, columns=['{:.0f}'.format(lin_costs[i] * 1e4)])
        else:
            ns_lin_mom_values['{:.0f}'.format(lin_costs[i] * 1e4)] = lin_mom_nosmooth.value/capital*100
            lin_mom_values['{:.0f}'.format(lin_costs[i] * 1e4)] = lin_mom_strat.value / capital * 100
            diffs['{:.0f}'.format(lin_costs[i] * 1e4)] = (lin_mom_strat.value - lin_mom_nosmooth.value)/capital*100 - diffs['0']
    y_high = max(lin_mom_values.max().max(), ns_lin_mom_values.max().max()) + margin
    y_low = min(lin_mom_values.min().min(), ns_lin_mom_values.min().min()) - margin
    lin_mom_values.plot(title='Smoothed Strategy Portfolio Value', ylim=(y_low,y_high))
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_smooth_mom_lin_.png".format(cap), dpi=600)
    ns_lin_mom_values.plot(title='Non-smoothed Strategy Portfolio Value', ylim=(y_low,y_high))
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_nonsmooth_mom_lin_.png".format(cap), dpi=600)
    diffs['0'] = 0
    diffs.plot(title='Transaction Cost Saved')
    plt.ylabel("Portfolio Value (%)")
    plt.legend(loc='best')
    plt.axhline(y=0., color='k', linestyle='-', linewidth=.5)
    plt.savefig("{}_cost_save.png".format(cap), dpi=600)

    stats_df = pd.DataFrame.from_dict(stats, orient='index')
    stats_df.columns = ['ER','Vol','Sharpe']
    stats_df.to_csv("stats_{}.csv".format(cap))

    # plt.show()

    # raw = pd.read_csv("{}Cap.csv".format(cap))
    # new = raw.pivot_table(index='date', columns='TICKER', values='VOL')
    # new.to_csv("{}_vol.csv".format(cap))
    print("ok")
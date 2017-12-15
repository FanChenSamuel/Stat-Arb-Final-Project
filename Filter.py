# -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special Thanks to Junyi Zhou, Fan's Asset Management Teammate, to provide the 
start-up code for the project
"""
import numpy as np
import scipy.stats.mstats as mstats

def long_short_filter(score, long=90, short=10):
    """
    :param score: vector of score
    :param long: percent to long, 90 if long top 10%
    :param short: percent to short, 10 if short bottom 10%
    :return: vector of position ratio
    """
    long_q = np.nanpercentile(score, long)
    short_q = np.nanpercentile(score, short)
    long_list = score > long_q
    short_list = score < short_q
    return long_list / np.sum(long_list) - short_list / np.sum(short_list)


def ranking_filter(score):
    """lecture 4 slide 35"""
    n = np.sum(~np.isnan(score))
    ranks = mstats.rankdata(np.ma.masked_invalid(score))
    ranks[ranks == 0] = np.nan
    pos = np.nan_to_num(ranks - np.nansum(ranks) / n)
    pos /= np.nansum(np.abs(pos)) / 2
    return pos

def long_ranking_filter(score):
    ranks = mstats.rankdata(np.ma.masked_invalid(score))
    ranks[ranks == 0] = np.nan
    pos = np.nan_to_num( ranks/ np.nansum(ranks))
    return pos   
    

def equal_weight(score):
    return (~np.isnan(score)) / np.sum(~np.isnan(score))


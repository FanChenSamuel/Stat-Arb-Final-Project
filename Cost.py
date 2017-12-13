 # -*- coding: utf-8 -*-
"""
Statistical Arbitrage Team Project

@author: Fan Chen, Zhijiang Huang, Fei Li, Zhixian Lin

Special Thanks to Junyi Zhou, Fan's Asset Management Teammate, to provide the 
start-up code for the project
"""
import numpy as np


class LinearCost:
    def __init__(self, cost):
        """
        :param cost: cost in abs (1% is 0.01)
        """
        self.cost = cost

    def calculate_cost(self, reposition):
        """
        :param reposition: vector of change in position value
        :param mkt_cap: vector of market cap
        :return: vector of transaction cost
        """
        return reposition * self.cost


class QuadraticCost:
    def __init__(self, linear, quadratic):
        self.linear = linear
        self.quadratic = quadratic

    def calculate_cost(self, reposition):
        return reposition * self.linear + np.power(reposition, 2) * self.quadratic


class ADVCost:
    def __init__(self, total_value : pd.DataFrame, min_cost, max_cost):
        self.min_cost = min_cost
        self.max_cost = max_cost
        self.total_value = total_value

    def calculate_cost(self, reposition, i):
        return reposition * (self.min_cost + (self.max_cost-self.min_cost) * np.sqrt(reposition / self.total_value.iloc[i]))


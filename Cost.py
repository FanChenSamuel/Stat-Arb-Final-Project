g # -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 14:29:59 2017

@author: chenf
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
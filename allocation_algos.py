"""
Different allocation Algorithms Template

Modern portfolio theory (MPT), or mean-variance analysis:
    https://en.wikipedia.org/wiki/Modern_portfolio_theory

Markowitz portfolio optimization in Python:
    https://blog.quantopian.com/markowitz-portfolio-optimization-2/
"""

import math
import scipy
import numpy as np
import pandas as pd

# Zipline takes a while to install, so unit tests run without installing it
try:
    import zipline.api as zipline
    from zipline.api import sid
except ImportError:
    zipline = None
    sid = None

def initialize(context):
    """
    Called once at the start of the algorithm.
   
    """   
    # STANDARD SETTINGS
    # set_benchmark(sid(8554)) #SPY
    # set_slippage(slippage.FixedSlippage(spread=0.00))
    # set_commission(commission.PerShare(cost=0.0, min_trade_cost=0))
    
     # DAILY, WEEKLY, MONTHLY
    context.rebalance_frequency = RebalanceFrequency.DAILY
   
    # Must be a positive integer, refer to parameters of each function
    # rebalance_number = 5 if RebalanceFrequency.DAILY and you want to rebalance every 5 days
    # rebalance_number = 3 if RebalanceFrequency.MONTHLY and you want to rebalance every 3 months
    context.rebalance_number = 1
    
    context.lookback = 42
    
    # Default universe
    
    context.securities = [
        (sid(19662)), #XLY
        (sid(21652)), #IYR
        (sid(21647)), #IYG
        (sid(19656)), #XLF
        (sid(19658)), #XLK
        (sid(19655)), #XLE
        (sid(19661)), #XLV
        (sid(19657)), #XLI
        (sid(19659)), #XLP
        (sid(19654)), #XLB
        (sid(19660)) #XlU

    ]

  
    # Run at the start of each month, when the market opens and rebalance
    
    zipline.schedule_function(
        rebalance,
        context.rebalance_frequency,
        time_rule=zipline.time_rules.market_open())


class RebalanceFrequency:
    MONTHLY = zipline.date_rules.month_start(days_offset=0)
    WEEKLY = zipline.date_rules.week_start(days_offset=0)
    DAILY = zipline.date_rules.every_day()
    
 
""" 
Minimum Variance Weights 
"""
def get_min_var_weights(context, data):
    context.weights = []
    context.tradeable_securities = [s for s in context.securities if data.can_trade(s)]
    if len(context.tradeable_securities) == 1:
        context.weights.append([context.tradeable_securities[0], 1.0])
        context.previous_tradeable_securities = context.tradeable_securities
    else:
        h = data.history(context.tradeable_securities, 'price', context.lookback,'1d')
        
        pct_change = h.pct_change().dropna()
       
        #calculate correlation matrix
        corr = pct_change.corr()
        #print(corr)
        if corr.dropna().empty:
            context.tradeable_securities = context.previous_tradeable_securities
            h = data.history(context.tradeable_securities, 'price', context.lookback,'1d')
            pct_change = h.pct_change().dropna()
            corr = pct_change.corr()
        context.previous_tradeable_securities = context.tradeable_securities
        
        
        cov_inv = np.linalg.inv(pct_change.cov())
        ones = np.ones(len(cov_inv))
        v = cov_inv.dot(ones)
        weights = v / ones.T.dot(v)
        
        #weights = tangent_portfolio(pct_change, 0.2)
        print(weights)
        #weights = map(abs, weights)
        #weights /= sum(weights)
        #print pd.Series(weights, index=pct_change.columns)
        #print(weights)
        total_weight = 0
        abs_weights = map(abs, weights)
        while sum(abs_weights) > 2.7:
            weights /= 1.01
            abs_weights = map(abs, weights)
            
        for i in range(len(context.tradeable_securities)):
            security = context.tradeable_securities[i]
            #print("hi" + str(security))
            #print("weights" + str(weights[i]))
            #if weights[i] > 0:
                #total_weight += weights[i]
            context.weights.append([security, weights[i]])
        #shy_weight = 1 - total_weight
        #order_target_percent(sid(23911), shy_weight)
            
            #log.info(" symbol: " + str(security.symbol) + " w: " + str(context.weights[security]))

"""
Calculation of the Efficient Frontier 
"""              
def efficient_frontier(R, target_return):
    """
    Efficient Frontier Portfolio weights.
    An EF portfolio can be thought of as the
    portfolio with the minimum risk for a given target return.
    parameters
    ----------
    R : pandas.DataFrame
        asset returns
    target_return : float
        the target return for the portfolio
    returns
    -------
    pandas.Series
        efficient frontier portfolio weights
    """
    c_inv = np.linalg.inv(R.cov())
    ones = np.ones(len(c_inv))
    mu_t = np.array([target_return, 1.0])
    M = np.array([R.mean(), ones]).T
    B = np.dot(M.T, c_inv.dot(M))
    B_inv = np.linalg.inv(B)
    v = np.dot(c_inv, M)
    u = np.dot(B_inv, mu_t)
    w = np.dot(v, u)
    return pd.Series(w, index=R.columns)

"""
Calculation of the Tangent Portfolio

"""
def tangent_portfolio(R, rfr):
    """
    Modern portfolio theory tangency portfolio
    given a risk free rate
    parameters
    ----------
    R : pandas.DataFrame
        asset returns
    rfr : float
        the risk free rate
    returns
    -------
    pandas.Series
        tangent portfolio weights
    """
    c_inv = np.linalg.inv(R.cov())
    mu = R.mean()
    ones = np.ones(len(mu), dtype=float)
    rf = rfr * ones
    t = c_inv.dot(mu - rf) / ones.T.dot(c_inv.dot(mu - rf))
    return pd.Series(t, index=R.columns)

def is_time_to_trade_day(current_day, rebalance_number):
    """
    Parameters:
        current_day: integer from 1 to 30
        rebalance_number: indicates how often to rebalance the portfolio
    """
    return (current_day - 1) % rebalance_number == 0

def is_time_to_trade_week(current_week, rebalance_number):
    """
    Parameters:
        current_week: integer from 1 to 4
        rebalance_number: indicates how often to rebalance the portfolio
    """
    return (current_week - 1) % rebalance_number == 0
    
def is_time_to_trade_month(current_month, rebalance_number, current_day):
    """
    Parameters:
        current_month: integer from 1 to 12
        rebalance_number: indicates how often to rebalance the portfolio
    """
    if current_day == 1:
        return (current_month - 1) % rebalance_number == 0
    return False
    
def rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    today = get_datetime('US/Eastern')
    if ((today.day > 7 or today.day < 15) and today.month == 11 and today.year == 2016):
        trade(context, data)
    if is_time_to_trade_month(today.month, 3, today.day):
        trade(context, data)
                

def trade(context, data):
    context.tradeable_securities = [s for s in context.securities if data.can_trade(s)]
    get_min_var_weights(context, data)
    today = get_datetime('US/Eastern')
    context.weights.append([sid(28232), 0.05]) #bte
    
    if (today.year != 2017 or (today.year == 2017 and today.month < 6)):
        context.weights.pop()
        context.weights.append([sid(28232), 0])
    
    context.weights.append([sid(26994), -0.05]) #drys
    

    if (today.day > 7 or today.day < 15) and  today.month == 11 and today.year == 2016:
        context.weights.pop()
        context.weights.append([sid(26994), 0.005])
    
    for security, weight in context.weights:
        if data.can_trade(security):
            order_target_percent(security, weight)
            
            #log securities and their weights
            #today = get_datetime('US/Eastern')
            #if today.day == 1: #start of each rebalancing month
            log.info(str(security) + " weight:" + str(weight))
    

def has_open_orders(context, data):               
    # Only rebalance when we have zero pending orders.
    has_orders = False
    for security in context.securities:
        orders = get_open_orders(security)
        if orders: #there are stocks with open orders
            has_orders = True
    return has_orders 

def handle_data(context, data):
    record(leverage = context.account.leverage)

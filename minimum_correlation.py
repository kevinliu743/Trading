"""
Minimum Correlation Algorithm as described:
https://www.r-bloggers.com/minimum-correlation-algorithm-paper/

https://cssanalytics.wordpress.com/2012/07/16/diversification-and-risk-reduction/
Similar to Minimum Variance Algorithm
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
    
    # DAILY, WEEKLY, MONTHLY
    context.rebalance_frequency = RebalanceFrequency.WEEKLY
   
    # Must be a positive integer, refer to parameters of each function
    # rebalance_number = 5 if RebalanceFrequency.DAILY and you want to rebalance every 5 days
    # rebalance_number = 3 if RebalanceFrequency.MONTHLY and you want to rebalance every 3 months
    context.rebalance_number = 1
    
    context.lookback = 42 # lookback days to calculate corelation matrix
    
    context.algo = 1 # 1 if Min Correlation 1, 2 if Min Correlation 2
    
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
    
    
     
    # Data Set 1- 8 assets
    """
    context.securities = [
        (sid(8554)), #SPY
        (sid(19920)), #QQQ
        (sid(24705)), #EEM
        (sid(21519)), #IWM
        (sid(22972)), #EFA
        (sid(23921)), #TLT
        (sid(21652)), #IYR
        (sid(26807)), #GLD
    ]
    """
    
    #min cor pdf
    """
    context.securities = [
        (sid(25485)), #AGG
        (sid(24705)), #EEM
        (sid(14520)), #EWJ
        (sid(26807)), #GLD
        (sid(32406)), #GSG
        (sid(22446)), #ICF
        (sid(21769)), #IEV
        (sid(22739)) #VTI
    ]
    """
    
    
  
    # Run at the start of each month, when the market opens and rebalance
    zipline.schedule_function(
        rebalance,
        context.rebalance_frequency,
        time_rule=zipline.time_rules.market_open())

class RebalanceFrequency:
    MONTHLY = zipline.date_rules.month_start(days_offset=0)
    WEEKLY = zipline.date_rules.week_start(days_offset=0)
    DAILY = zipline.date_rules.every_day()

    
def get_min_corr_weights(context, data, algo):
    context.weights = []
    context.tradeable_securities = [s for s in context.securities if data.can_trade(s)]
    if len(context.tradeable_securities) == 1:
        context.weights.append([context.tradeable_securities[0], 1.0])
        context.previous_tradeable_securities = context.tradeable_securities
    else:
        h = data.history(context.tradeable_securities, 'price', context.lookback,'1d')
        
        pct_change = h.pct_change().dropna()
       
        # calculate correlation matrix
        corr = pct_change.corr()

        # Make sure history of securities exist
        # if not, make tradeable_securities =  the previous tradeable securities
        if corr.dropna().empty: 
            context.tradeable_securities = context.previous_tradeable_securities
            h = data.history(context.tradeable_securities, 'price', context.lookback,'1d')
            pct_change = h.pct_change().dropna()
            corr = pct_change.corr()
        # update previous_tradeable_securities to the current one
        context.previous_tradeable_securities = context.tradeable_securities
        
        #calculate adjusted correlation matrix
        adj_corr = get_adjusted_corr_matrix(corr)
        
        if algo == 2:
            # average value for each row is initial portfolio weight estimate
            initial_weights = corr.T.mean() 

        if algo == 1:
            # average value for each row of adjusted correlation matrix is initial portfolio                 weight estimate
            initial_weights = adj_corr.mean()
        
        # rank portfolio weight estimates
        ranks = initial_weights.rank()
        ranks /= ranks.sum()
        
        # combine with adjusted correlation matrix, normalize after ranking
        weights = adj_corr.dot(ranks).dropna()
        weights /= weights.sum()
        
        # scale by standard deviation, and normalize
        weights = weights / pct_change.std() 
        weights /= weights.sum()
        
        for i in range(len(context.tradeable_securities)):
            security = context.tradeable_securities[i]
            #print("hi" + str(security))
            #print("weights" + str(weights[i]))
            context.weights.append([security, weights[i]])
            
            #log.info(" symbol: " + str(security.symbol) + " w: " + str(context.weights[security]))


def get_adjusted_corr_matrix(cor):
    """
    Helper function for get_reduced_correlation_weights
    parameters
    ----------
    cor : pandas.DataFrame
        Asset returns correlation matrix
    returns
    -------
    pandas.DataFrame
        adjusted correlation matrix
    """
    data = cor.values.flatten()
    mu = np.mean(data)
    sd = np.std(data)
    distribution = scipy.stats.norm(mu, sd)
    return 1 - cor.apply(lambda x: distribution.cdf(x))

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
    
def is_time_to_trade_month(current_month, rebalance_number):
    """
    Parameters:
        current_month: integer from 1 to 12
        rebalance_number: indicates how often to rebalance the portfolio
    """
    return (current_month - 1) % rebalance_number == 0
    
def rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    today = get_datetime('US/Eastern')
    
    if context.rebalance_frequency == RebalanceFrequency.DAILY:
        if is_time_to_trade_day(today.day, context.rebalance_number):
            trade(context, data)
    elif context.rebalance_frequency == RebalanceFrequency.WEEKLY:
        if is_time_to_trade_week((today.day/7) + 1, context.rebalance_number):
            trade(context, data)
    else:
        if is_time_to_trade_month(today.month, context.rebalance_number):
            trade(context, data)              

def trade(context, data):
    context.tradeable_securities = [s for s in context.securities if data.can_trade(s)]
    get_min_corr_weights(context, data, context.algo)
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

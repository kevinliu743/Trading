""" 
Implementation of - JP Morgan SCTO strategy 
https://www.globalxfunds.com/funds/scto/

JPMorgan U.S. Sector Rotator Index ETF (SCTO) strategy - a XL-sector/RWR rotation strategy
with the typical associated risks and returns with a momentum equity strategy.

Every month, compute the return (~3 month lookback period) and rank. 
Take the top 5 ranks, and weight them in a normalized fashion to the inverse 
of their 22-day volatility. Zero out any that have negative returns. Lastly, 
check the predicted annualized vol of the portfolio, and if it’s greater than 20%,
bring it back down to 20%. The cash asset–SHY–receives any remaining allocation 
due to setting securities to zero.

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
    set_commission(commission.PerShare(cost=0))
    set_slippage(slippage.FixedSlippage(spread=0.00))
    
    # 9 sector spiders and RWR from Link, SHY is cash_asset, and it gets remaining
    context.etfs = [
        (sid(19654)), #XLB
        (sid(19655)), #XLE
        (sid(19656)), #XLF
        (sid(19657)), #XLI
        (sid(19658)), #XLK
        (sid(19659)), #XLP
        (sid(19660)), #XLU
        (sid(19661)), #XLV
        (sid(19662)), #XLY
        (sid(22635)), #RWR
        (sid(23911)) #SHY

    ]
    
    # US Sector ETFs and real estate
    # Best OOS Performance
    # High performing and volatile Sector ETFs - best for Minimum Variance Allocation
    """
    context.etfs = symbols(#'IYR',  # Real Estate ETF in place of XLFS
                           'XLY',  # XLY Consumer Discrectionary SPDR Fund  
                           'IYG',  # Financial Services etf in place of 
                           'XLF',  # XLF Financial SPDR Fund or change for TLT 
                           'XLK',  # XLK Technology SPDR Fund  
                           'XLE',  # XLE Energy SPDR Fund  
                           'XLV',  # XLV Health Care SPRD Fund  
                           'XLI',  # XLI Industrial SPDR Fund  
                           'XLP',  # XLP Consumer Staples SPDR Fund   
                           'XLB',  # XLB Materials SPDR Fund  
                           'XLU')  # XLU Utilities SPRD Fund
    """
    
                          
   # DAILY, WEEKLY, MONTHLY
    context.rebalance_frequency = RebalanceFrequency.MONTHLY
   
    # Must be a positive integer, refer to parameters of each function
    # rebalance_number = 5 if RebalanceFrequency.DAILY and you want to rebalance every 5 days
    # rebalance_number = 3 if RebalanceFrequency.MONTHLY and you want to rebalance every 3 months
    context.rebalance_number = 1
    context.cash_asset = sid(23911) #SHY
    context.lookback = 65 # days lookback for returns
    context.volatility_lookback = 22 # days lookback for volatility
    context.invest_num = 5  # number of assets you wish to invest in
    context.max_volatility = 0.2 # max allowable volatility
    
    zipline.schedule_function(rebalance, 
                              context.rebalance_frequency, 
                              time_rules.market_open())
    

class RebalanceFrequency:
    MONTHLY = zipline.date_rules.month_start(days_offset=0)
    WEEKLY = zipline.date_rules.week_start(days_offset=1)
    DAILY = zipline.date_rules.every_day()
    
### is_time_to_trade_x functions allow for more precise rebalancing periods
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
    
     
def get_weights(context, data, max_volatility):
    context.toplist = []
    daily_returns = data.history(context.tradeable_securities, 'price', context.lookback,'1d')    
    #print pct_change
    net_return = daily_returns.iloc[[0, -1]].pct_change().dropna().squeeze()
    context.ranks = net_return.rank().sort_values(ascending = False)


    # Compute daily volatility  
    historical_vol_daily = np.std(daily_returns)  
    
    # Convert daily volatility to annual volatility
    historical_vol = 1 / historical_vol_daily * math.sqrt(context.volatility_lookback)  
    
    # rank portfolio weight estimates
    context.ranks = context.ranks[:context.invest_num]
    
    vol = [s for s in historical_vol.index]

    for i in range(len(context.ranks)):
        s = context.ranks.index[i]
        if s in vol:
            j = vol.index(s)
            context.ranks[i] = historical_vol[j]
    
    for i in range(context.invest_num):
        s = context.ranks.index[i]
        if net_return[i] < 0:
            context.ranks[i] = 0
        else:
            context.toplist.append(s)
    context.ranks /= sum(context.ranks.values)

            
    if len(context.toplist) > 1:
        # updated
        new_daily_returns = data.history(context.ranks.index, 'price', context.lookback,'1d')
        # daily percent change
        pct_change = new_daily_returns.pct_change().dropna()

        cov = pct_change.cov()
        # check the predicted annualized vol of the portfolio, and if it’s greater than 20%, bring it back down to 20%
        #compute forecasted vol of portfolio
        predicted_volatility = context.ranks.T.dot(cov).dot(context.ranks)
        predicted_annualized_volatility = predicted_volatility * math.sqrt(252)
        #print "here"
        #print predicted_annualized_volatility
        #print context.ranks
        #if forecasted vol greater than vol limit, cut it down
        if predicted_annualized_volatility > max_volatility:
            context.ranks *= (max_volatility / predicted_annualized_volatility)
        #print context.ranks
        
        for i in range(len(context.ranks)):
            if context.ranks.index[i] != sid(23911):
                context.weights[context.ranks.index[i]] = context.ranks[i]
       
    
            
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
    elif context.rebalance_frequency == RebalanceFrequency.MONTHLY:
        if is_time_to_trade_month(today.month, context.rebalance_number):
            trade(context, data)          
    
def trade(context, data):
    context.tradeable_securities = [s for s in context.etfs if data.can_trade(s)]

    context.weights = {}
    for s in context.tradeable_securities:
        if s != sid(23911):
            context.weights[s] = 0.0
    get_weights(context, data, context.max_volatility)
    # keeps track of leverage
    invest_weight = 0.0
    if has_open_orders(context, data):
        return

    for security in context.weights.keys():
        if data.can_trade(security):
            weight = context.weights[security]
            order_target_percent(security, weight)
            invest_weight += weight
            log.info(str(security) + " weight:" + str(weight))
            
    
    # weight for risk-free-asset
    w = 1.0 - invest_weight
    order_target_percent(sid(23911), w)
    log.info("weight of SHY: " + str(w))
        

    
def has_open_orders(context, data):               
    # Only rebalance when we have zero pending orders.
    has_orders = False
    for security in context.weights.keys():
        orders = get_open_orders(security)
        if orders: #there are stocks with open orders
            has_orders = True
    return has_orders 

def handle_data(context, data):
    record(leverage = context.account.leverage)



""" Implementation of - Minimum Variance Algorithm
as described here - https://cssanalytics.wordpress.com/2013/04/01/minimum-variance-algorithm-mva/

https://www.quantopian.com/posts/adaptive-asset-allocation-algorithms

ETFs that are more volatile are more suitable for this algorithm. If an ETF such as SHY or TLT is incorporated within the portfolio, the minimum variance algorithm will almost always strictly selected that ETF since that security has a very low variance. Thus, if you wish to incorporate a low variance security, you should turn on the Time Series Momentum Rule (TMOM) since it filters out securities that have low returns.
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
    
    # DEFAULT: US Sector ETFs and real estate
    # Best OOS Performance
    # High performing and volatile Sector ETFs - best for Minimum Variance Allocation
    
    context.etfs = symbols(#'IYR',  # Real Estate ETF in place of XLFS
                           'XLY',  # XLY Consumer Discrectionary SPDR Fund  
                           'IYG',  # Financial Services etf in place of 
                           'XLF',  # XLF Financial SPDR Fund  
                           'XLK',  # XLK Technology SPDR Fund  
                           'XLE',  # XLE Energy SPDR Fund  
                           'XLV',  # XLV Health Care SPRD Fund  
                           'XLI',  # XLI Industrial SPDR Fund  
                           'XLP',  # XLP Consumer Staples SPDR Fund   
                           'XLB',  # XLB Materials SPDR Fund  
                           'XLU')  # XLU Utilities SPRD Fund
    
    
    
    
    #Asset #1 - test 7 asset scenario from paper - the small global multi asset universe
    # from Keller/Butler - Elastic Asset Allocation (EAA)
    #removed HYG from sample set to allow for longer backtest
    
    """
    context.etfs = symbols('SPY', #proxy for S&P
                           'EFA', #proxy for EAFE
                           'EEM', #proxy for EEM
                           'QQQ', #proxy for US Tech
                           'EWJ', #proxy for Japan Topix
                           'IEF') #proxy for US Govt 10 yr
    """
    

                          
   # DAILY, WEEKLY, MONTHLY
    context.rebalance_frequency = RebalanceFrequency.MONTHLY
   
    # Must be a positive integer, refer to parameters of each function
    # rebalance_number = 5 if RebalanceFrequency.DAILY and you want to rebalance every 5 days
    # rebalance_number = 3 if RebalanceFrequency.MONTHLY and you want to rebalance every 3 months
    context.rebalance_number = 3
    
    
    #POSSIBLE MINIMUM VARIANCE COMBINATIONS:
    #COMBO 1: risk_free: false, momentum_state: false - purely minimum variance
    #COMBO 2: risk_free: false, momentum_state: true - minimum variance with momentum
        # need to change length of invest_num to quantify how many assets are underperforming and will not be purchased
        # context.invest_num must be less than or equal to len(context.etfs)
    #COMBO 3: risk_free: true, momentum_state: true - minimum variance with momentum to include risk_free asset
   
    context.risk_free_state = False # with risk free asset if true, without if false
    context.risk_free_asset = symbol('SHY') # risk-free asset (variance = 0 by definition)
    context.momentum_state = False # with TMOM (Time Series Momentum Rule) if true, without if false - switch to turn the time series momentum rule on and off
    context.invest_num = len(context.etfs)  # number of assets you wish to invest in
    context.initial_invest_num = context.invest_num # records invest_num for later reference 
    context.lookback = 240 # days lookback for tmom
    context.atr_bars_back = 42 # days lookback to calculate variance of various assets
    
    zipline.schedule_function(rebalance, 
                              context.rebalance_frequency, 
                              time_rules.market_close(minutes=60))
    

class RebalanceFrequency:
    # Brendon: Temporarily changing to rebalance at month start instead of month end
    MONTHLY = zipline.date_rules.month_start(days_offset=0)
    WEEKLY = zipline.date_rules.week_start(days_offset=0)
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
    
     
def get_minvar_weights(context, toplist, data):
    """
    Parameters:
        toplist: A list of securities to be considered for minimum variance weight calculations
    Return Values:
        context.weights: A dictionary of securities mapped to their corresponding minimum variance weights
    """
    context.weights = {}
    if len(toplist) > 0:
        # if length of list is 1 then weight should be 100% there is no min variance
        if len(toplist) == 1:
            context.weights[toplist[0]]=1.0
        else:
            # retrieve price history of securities with lookback period specified                         # this price history will be used for variance calculations
            h = data.history(toplist, 'price', context.atr_bars_back,'1d')[toplist]
            
            # pandas.DataFrame- Timeseries of asset returns
            pct_change = h.pct_change()
            
            # calculate covariance matrix
            cov = pct_change.cov()
 
            # mean pairwise covariance value matrix
            avg_cov = cov.mean()
            
            # keeps track of column the asset is in the matrix
            i=0 
            
            # gaussian conversion dictionary 
            # maps from security to its complementary cumulative distribution function (ccdf)             # ccdf = 1 - cdf = tail distribution: P(X > x)
            gauss_conv = {}
            inv_var = {}
            
            for s in toplist:
                # gaussian conversion: change to standard normal distribution
                # shifts to standard normal distribution to create positive weight values
                # conventional MVA algorithm skips this step and generates negative weights
                gauss_conv[s] = 1-scipy.stats.norm.cdf((avg_cov[s]-avg_cov.mean())/avg_cov.std())

                
                # inverse variance
                # inverse-variance weighting aggregates random variables to minimize the                         variance of the weighted average
                inv_var[s] = 1.0/cov.ix[i,i]
                i += 1
    
            gc = pd.Series(gauss_conv,name='Symbol')
            iv = pd.Series(inv_var, name='Symbol')
            # inverse variance weight
            inv_var_weight = iv/iv.sum()
            
            # proportional average covar weight
            avg_covar_weight = gc/gc.sum()
            
            # product of proportional average covar weight and inverse variance weight
            prod_avg_covar_inv_var = avg_covar_weight * inv_var_weight
            
            # final weights
            for s in toplist:
                context.weights[s] = prod_avg_covar_inv_var[s] / prod_avg_covar_inv_var.sum()
                log.info(" symbol: " + str(s.symbol) + " w: " + str(context.weights[s]) )
    
# rank symbols by TMOM
def mom_rank(context,data):    
    # get TMOM
    h = data.history(context.tradeable_securities, 'price', context.lookback,'1d')
    h = h.resample('M').last()
    # drop first row because it is nan
    pct_change =h.iloc[[0,-2]].pct_change()[1:]
    # drop any other nan values
    pct_change = pct_change.dropna(axis=1)
    # convert dataframe to series for sorting. Then sort in descending order
    context.pct_change_series =  pct_change.squeeze().sort_values(ascending=False)
    
    # get top TMOM list
    context.toplist = []
    for i in range(context.invest_num) :
        s = context.pct_change_series.index[i]
        if data.can_trade(s):
            context.toplist.append(s)
            
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
    context.toplist = []
    context.tradeable_securities = [s for s in context.etfs if data.can_trade(s)]
    # can return to initial invest_num in case security becomes available to trade later
    context.invest_num = context.initial_invest_num
    if context.invest_num > len(context.tradeable_securities):
            context.invest_num = len(context.tradeable_securities)
    # rank by TMOM rule, and filter out underperforming securities
    if context.momentum_state:
        mom_rank(context,data)
    # put all securities into toplist
    else:
        for i in range(context.invest_num):
            context.toplist.append(context.tradeable_securities[i])
        if context.risk_free_state:
            context.toplist.append(context.risk_free_asset)
    
    # calculate minimum variance weights
    get_minvar_weights(context,context.toplist, data)
    
    # keeps track of leverage
    invest_weight = 0.0
    
    for s in context.tradeable_securities:
        if context.momentum_state:
            # only securities with positive returns are selected
            if s in context.toplist and context.pct_change_series[s] > 0.0:
                order_target_percent(s,context.weights[s])
                invest_weight += context.weights[s]
            else:
                order_target_percent(s,0.0)
        else: 
            if s in context.toplist:
                order_target_percent(s,context.weights[s])
                invest_weight += context.weights[s]
            else:
                order_target_percent(s,0.0)
    
    # weight for risk-free-asset
    w = 1.0 - invest_weight
    log.info("weight of SHY: " + str(w))
    order_target_percent(context.risk_free_asset,w)


def handle_data(context, data):
    record(leverage = context.account.leverage)



"""
Simple Lazy Portfolio Algorithm

Description:
    Relatively safe investment strategy that rebalances securities periodically.
    Has the functionality of being able to rebalance as frequently as necessary.

Pseudocode:
    Each rebalance period, make sure each security make up the weight value assigned to it.
"""
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
    
    
    # Default universe
    
    context.security_weights = [
        (sid(22739), 0.25), # Vanguard Total Stock Market Index Fund (VTI)
        (sid(33652), 0.25), # Vanguard Total Bond Market Index Fund (BND)
        (sid(36486), 0.25), # Vanguard Total International Stock Index Fund (VXUS)
        (sid(26994), 0.25) # DRYS, a plummeting company
    ]
    
    
    # 60-40
    """
    context.security_weights = [
        (sid(22739), 0.30), # Vanguard Total Stock Market Index Fund (VTI)
        (sid(33652), 0.40), # Vanguard Total Bond Market Index Fund (BND)
        (sid(36486), 0.24), # Vanguard Total International Stock Index Fund (VXUS)
        (sid(26669), 0.06) #Vanguard REIT Index Fund (VNQ)
    ]
    """
    
    # Betterment- 60% stock allocation
    """
    context.security_weights = [
        #Stocks
        (sid(22739), 0.12), # (VTI)
        (sid(25909), 0.10), # (VTV)
        (sid(32521), 0.03), # (VOE)
        (sid(25901), 0.03), # (VBR)
        (sid(34385), 0.27), # (VEA)
        (sid(27102), 0.05), # (VWO)
        
        #Bonds
        (sid(33154), 0.14), # (SHV)
        (sid(43529), 0.06), # (VTIP)
        (sid(34648), 0.14), # (MUB)
        (sid(23881), 0.02), # (LQD)
        (sid(44849), 0.02), # (BNDX)
        (sid(35323), 0.02) # (EMB)      
    ]
    """
    
    
    # MVA 8-asset ETFs
    """
    context.security_weights = [
        (sid(8554), 0.125), # SPY
        (sid(19920), 0.125), # QQQ
        (sid(24705), 0.125), # EEM
        (sid(21519), 0.125), # IWM
        (sid(22972), 0.125), # EFA
        (sid(23921), 0.125), # TLT
        (sid(21652), 0.125), # IYR
        (sid(26807), 0.125) # GLD
        ]
    """
    
    # Merriman all-value moderate
    """
    context.security_weights = [
        #Stocks
        (sid(40144), 0.15), # (VONV)
        (sid(28143), 0.15), # (RZV)
        (sid(27536), 0.12), # (EFV)
        (sid(34155), 0.12), # (DLS)
        (sid(36254), 0.06), # (EWX)
        (sid(38986), 0.12), # (VGSH)
        (sid(33947), 0.20), # (ITE)
        (sid(43529), 0.08) # (VTIP) 
         
    ]
    """
    
    # Merriman all-value conservative
    """
    context.security_weights = [
        #Stocks
        (sid(40144), 0.10), # (VONV)
        (sid(28143), 0.10), # (RZV)
        (sid(27536), 0.08), # (EFV)
        (sid(34155), 0.08), # (DLS)
        (sid(36254), 0.04), # (EWX)
        (sid(38986), 0.18), # (VGSH)
        (sid(33947), 0.30), # (ITE)
        (sid(43529), 0.12) # (VTIP) 
         
    ]
    """
    
    # Merriman all-value aggressive
    """
    context.security_weights = [
        #Stocks
        (sid(40144), 0.25), # (VONV)
        (sid(28143), 0.25), # (RZV)
        (sid(27536), 0.20), # (EFV)
        (sid(34155), 0.20), # (DLS)
        (sid(36254), 0.10) # (EWX)
         
    ]
    """
    
 
    # Merriman buy&hold conservative
    """
    context.security_weights = [
        # Stocks/REITs
        (sid(40107), 0.045), # VOO
        (sid(40144), 0.045), # VONV
        (sid(40103), 0.045), # VIOO
        (sid(28143), 0.045), # RZV
        (sid(26669), 0.02), # VNQ
        (sid(34385), 0.036), # VEA
        (sid(27536), 0.036), # EFV
        (sid(38272), 0.036), # VSS
        (sid(34155), 0.036), # DLS
        (sid(27102), 0.018), # VWO
        (sid(36254), 0.018), # EWX
        (sid(40337), 0.02), # VNQI
        
        # Bonds
        (sid(38986), 0.18), # VGSH
        (sid(33947), 0.30), # ITE
        (sid(43529), 0.12) # VTIP 
         
    ]
    """
    
    
    # Merriman buy&hold moderate
    """
    context.security_weights = [
        # Stocks/REITs
        (sid(40107), 0.067), # VOO
        (sid(40144), 0.068), # VONV
        (sid(40103), 0.067), # VIOO
        (sid(28143), 0.068), # RZV
        (sid(26669), 0.03), # VNQ
        (sid(34385), 0.054), # VEA
        (sid(27536), 0.054), # EFV
        (sid(38272), 0.054), # VSS
        (sid(34155), 0.054), # DLS
        (sid(27102), 0.027), # VWO
        (sid(36254), 0.027), # EWX
        (sid(40337), 0.03), # VNQI
        
        # Bonds
        (sid(38986), 0.12), # VGSH
        (sid(33947), 0.20), # ITE
        (sid(43529), 0.08) # VTIP
         
    ]
    """
    
    
    #Merriman buy&hold aggressive
    """
    context.security_weights = [
        # Stocks/REITs
        
        (sid(40107), 0.112), # VOO
        (sid(40144), 0.113), # VONV
        (sid(40103), 0.112), # VIOO
        (sid(28143), 0.113), # RZV
        (sid(26669), 0.05), # VNQ
        (sid(34385), 0.09), # VEA
        (sid(27536), 0.09), # EFV
        (sid(38272), 0.09), # VSS
        (sid(34155), 0.09), # DLS
        (sid(27102), 0.045), # VWO
        (sid(36254), 0.045), # EWX
        (sid(40337), 0.05) # VNQI
         
    ]
    """
    
    # Morningstar Conservative Retirement Saver – 50% equity
    """
    context.security_weights = [
        (sid(22739), 0.33), # VTI
        (sid(25901), 0.05), # VBR
        (sid(34385), 0.1), # VEA
        (sid(27102), 0.04), # VWO
        (sid(25485), 0.3), # IUSB 2014, replaced with AGG 
        (sid(43529), 0.07), # VTIP 
        (sid(33651), 0.07), # BSV
        (sid(35631), 0.04) # GCC
    ]
    """
    
    # Morningstar Moderate Retirement Saver – 80% equity
    """
    context.security_weights = [
        (sid(22739), 0.47), # VTI
        (sid(25901), 0.8), # VBR
        (sid(34385), 0.2), # VEA
        (sid(27102), 0.05), # VWO
        (sid(35631), 0.05), # GCC
        (sid(25485), 0.15), # IUSB 2014, replaced with AGG 
    ]
    """
    
    # Morningstar Aggressive Retirement Saver – 95% equity
    """
    context.security_weights = [
        (sid(22739), 0.5), # VTI
        (sid(25901), 0.1), # VBR
        (sid(34385), 0.3), # VEA
        (sid(27102), 0.05), # VWO
        (sid(35631), 0.05), # GCC  
    ]
    """
    
    
    # Morningstar conservative retirement – 30% equity
    """
    context.security_weights = [
        # Bucket 1: Years 1–2
        # 12% cash for capital preservation
        
        # Bucket 2: Years 3–12
        (sid(33651), 0.13), # BSV
        (sid(43529), 0.10), # VTIP
        (sid(47107), 0.20), # IUSB
        (sid(44408), 0.06), # SRLN
        (sid(28364), 0.21), # VIG (5% bucket 2, 16% bucket 3)
        
        # Bucket 3: Years 13+
        (sid(33486), 0.07), # VEU
        (sid(28054), 0.05), # DBC
        (sid(25952), 0.03), # HYG as ETF alternate to VWEHX
        (sid(35323), 0.03) # EMB 
    ]
    """
    
    # Morningstar moderate retirement – 40% equity
    """
    context.security_weights = [
        # Bucket 1: Years 1–2
        # 10% cash for capital preservation
        
        # Bucket 2: Years 3–12
        (sid(33651), 0.075), # BSV
        (sid(43529), 0.075), # VTIP
        (sid(44408), 0.075), # SRLN
        (sid(47107), 0.15), # IUSB
        (sid(28364), 0.225), # VIG (12.5% bucket 2, 10% bucket 3)
        
        # Bucket 3: Years 13+
        (sid(22739), 0.10), # VTI
        (sid(33486), 0.10), # VEU
        (sid(28054), 0.05), # DBC
        (sid(25952), 0.025), # HYG as ETF alternate to VWEHX
        (sid(35323), 0.025) # EMB  
    ]
    """
    
    # Morningstar aggressive post-retirement – 55% equity
    """
    context.security_weights = [
        # Bucket 1: Years 1–2
        # 8% cash for capital preservation
        
        # Bucket 2: Years 3–12
        (sid(33651), 0.07), # BSV
        (sid(43529), 0.07), # VTIP
        (sid(47107), 0.13), # IUSB
        (sid(28364), 0.28), # VIG (5% bucket 2, 23% bucket 3)
        
        # Bucket 3: Years 13+
        (sid(22739), 0.13), # VTI
        (sid(33486), 0.13), # VEU
        (sid(25952), 0.03), # HYG as ETF alternate to VWEHX
        (sid(35323), 0.03), # EMB
        (sid(28054), 0.05), # DBC
    ]
    """
    
    # Swensen
    """
    context.security_weights = [
        #Stocks
        (sid(22739), 0.30), # (VTI)
        (sid(22972), 0.15), # (EFA)
        (sid(27102), 0.10), # (VWO)
        (sid(25801), 0.15), # (TIP)
        (sid(23870), 0.15), # IEF
        (sid(26669), 0.15) # (VNQ)
    ]
    """
    
    # Dalio
    """
    context.security_weights = [
        (sid(33649), 0.40), # BLV
        (sid(33650), 0.15), # BIV
        (sid(40107), 0.30), # VOO
        (sid(26807), 0.075), # GLD
        (sid(28054), 0.075), # DBC
    ]
    """
    
    # Scott Burns' Couch Potato
    """
    context.security_weights = [
        #Stocks
        (sid(22739), 0.34), # (VTI)
        (sid(40785), 0.33), # (VXUS)
        (sid(25801), 0.33) # (TIP)

    ]
    """
    
    # Tai
    """
    context.security_weights = [
        #Stocks
        (sid(22739), 0.26), # (VTI)
        (sid(22972), 0.26), # (EFA)
        (sid(27102), 0.10), # (VWO) 
        (sid(21519), 0.03), # (IWM)
        (sid(23881), 0.10), # (LQD) 
        (sid(25952), 0.08), # (HYG)
        (sid(25801), 0.08), # (TIP)
        (sid(44849), 0.04), # (BNDX) 
        (sid(26669), 0.05) # (VNQ) 

    ]
    """
    
    # Rick Ferri's Lazy Three Fund
    """
    context.security_weights = [
        #Stocks
        (sid(22739), 0.40), # (VTI)
        (sid(33652), 0.40), # (BND)
        (sid(40785), 0.20) # (VXUS)
    ]
    """
    
    # GMP - equal weighting
    """
    context.security_weights = [
        (sid(22739), 0.076), # (VTI)
        (sid(34385), 0.077), # (VEA)
        (sid(33652), 0.077), # (BND) 
        (sid(44849), 0.077), # (BWX)
        (sid(34793), 0.077), # (VWO) 
        (sid(39701), 0.077), # (PICB)
        (sid(39941), 0.077), # (EMLC)
        (sid(25952), 0.077), # (HYG)
        (sid(26669), 0.077), # (VNQ)
        (sid(40337), 0.077), # (VNQI)
        # (sid(24700), 0.002),  (DJP) commondity removed
        (sid(25801), 0.077), # (TIP)
        (sid(42753), 0.077), # (HYXU)
        (sid(35927), 0.077) # (WIP)

    ]
    """
    
    
    # GMP - market cap weighting
    """
    context.security_weights = [
        (sid(22739), 0.358), # (VTI)
        (sid(34385), 0.232), # (VEA)
        (sid(33652), 0.19), # (BND) 
        (sid(44849), 0.138), # (BWX)
        (sid(34793), 0.033), # (VWO) 
        (sid(39701), 0.019), # (PICB)
        (sid(39941), 0.009), # (EMLC)
        (sid(33655), 0.009), # (HYG)
        (sid(26669), 0.005), # (VNQ)
        (sid(40337), 0.003), # (VNQI)
        # (sid(24700), 0.002),  (DJP) commondity removed
        (sid(25801), 0.001), # (TIP)
        (sid(42753), 0.002), # (HYXU)
        (sid(35927), 0.001) # (WIP)

    ]
    """
    
    # GestaltU strategic (w/ Morningstar return projections)
    """
    context.security_weights = [
        (sid(22739), 0.35), # VTI, total US market
        (sid(36486), 0.20), # VT, non-US stocks; Vanguard recommends 2:1
        (sid(36201), 0.05), # VNQ US real estate
        (sid(25485), 0.025), # AGG, domestic highly rated corporate bonds
        (sid(23881), 0.025), # LQD, domestic investment grade bonds
        (sid(33655), 0.10), # HYG, domestic high yield bonds
        (sid(44849), 0.15), # BNDX, international government/corporate bonds, correlated with other i-bonds
        (sid(23921), 0.10) # TLT (EDV reduces returns)
        #(sid(23870), 0.07), # IEF 7–10 year treasure bonds
        #(sid(33151), 0.03) # IEI 3–7 year treasury bonds
        
        # Extra Securities
        # (sid(35927), 0.015), # WIP
        # (sid(23881), 0.10), # LQD
        # (sid(38013), 0.14), # IGOV
        # (sid(36201), 0.07), # RWO global real estate
        # (sid(35970), 0.38) # global stocks
    ]
    """
    
    # GestaltU portfolio - rebalance quarterly!!!!
    """
    context.security_weights = [
        (sid(25801), 0.015), # (TIP)
        (sid(35323), 0.03), # (EMB)
        (sid(35927), 0.015), # (ITIP) # ITIP to WIP
        (sid(44849), 0.09), # (BNDX)
        (sid(23881), 0.10), # (LQD) 
        (sid(38013), 0.14), # (IGOV)
        (sid(23870), 0.075), # (IEF)
        (sid(33151), 0.075), # (IEI) 
        (sid(36201), 0.07), # (RWO) 
        (sid(35970), 0.38) # (ACWI)

    ]
    """
    
    # GestaltU equal weight 
    """
    context.security_weights = [
        (sid(25801), 0.1), # (TIP)
        (sid(35323), 0.1), # (EMB)
        (sid(35927), 0.1), # (ITIP) # ITIP to WIP
        (sid(44849), 0.1), # (BNDX)
        (sid(23881), 0.1), # (LQD) 
        (sid(38013), 0.1), # (IGOV)
        (sid(23870), 0.1), # (IEF)
        (sid(33151), 0.1), # (IEI) 
        (sid(36201), 0.1), # (RWO) 
        (sid(35970), 0.1) # (ACWI)

    ]
    """
    
    # GestaltU Strategic Equal Weight
    """
    context.security_weights = [
        (sid(22739), 0.125), # VTI, total US market
        (sid(36486), 0.125), # VT, non-US stocks; Vanguard recommends 2:1
        (sid(36201), 0.125), # VNQ US real estate
        (sid(25485), 0.125), # AGG, domestic highly rated corporate bonds
        (sid(23881), 0.125), # LQD, domestic investment grade bonds
        (sid(33655), 0.125), # HYG, domestic high yield bonds
        (sid(44849), 0.125), # BNDX, international government/corporate bonds, correlated with other i-bonds
        (sid(23921), 0.125) # TLT (EDV reduces returns)
    ]
    """
    """
    # GestaltU w factor tilts
    
    context.security_weights = [
        (sid(25801), 0.045), # (TIP)
        (sid(35323), 0.03), # (EMB)
        (sid(35927), 0.015), # (ITIP) # ITIP to WIP
        (sid(44849), 0.09), # (BNDX)
        (sid(23881), 0.10), # (LQD) 
        (sid(38013), 0.14), # (IGOV)
        (sid(23870), 0.08), # (IEF)
        (sid(33151), 0.08), # (IEI) 
        (sid(36201), 0.07), # (RWO) 
        (sid(43392), 0.02), # (FM)
        
        #no XOVR, AIMOX
        (sid(42369), 0.02), # (EELV)
        (sid(42370), 0.04), # (IDLV)
        (sid(41382), 0.04), # (SPLV) 
        (sid(35357), 0.01), # (PIE)
        (sid(33441), 0.03), # (PDP) 
        (sid(34746), 0.01), # (PXH)
        (sid(34745), 0.005), # (PDN)
        (sid(34076), 0.02), # (PXF) 
        (sid(32595), 0.005), # (PRFZ) 
        (sid(27089), 0.02), # (PWV)
        (sid(46529), 0.03), # (GVAL)
        (sid(35970), 0.10) # (ACWI)

    ]
    """
    """
    # GestaltU w factor tilts equal 
    
    context.security_weights = [
        (sid(25801), 0.045), # (TIP)
        (sid(35323), 0.045), # (EMB)
        (sid(35927), 0.045), # (ITIP) # ITIP to WIP
        (sid(44849), 0.045), # (BNDX)
        (sid(23881), 0.045), # (LQD) 
        (sid(38013), 0.045), # (IGOV)
        (sid(23870), 0.045), # (IEF)
        (sid(33151), 0.045), # (IEI) 
        (sid(36201), 0.045), # (RWO) 
        (sid(43392), 0.045), # (FM)
       
        #no XOVR, AIMOX
        (sid(42369), 0.045), # (EELV)
        (sid(42370), 0.045), # (IDLV)
        (sid(41382), 0.045), # (SPLV) 
        (sid(35357), 0.045), # (PIE)
        (sid(33441), 0.045), # (PDP) 
        (sid(34746), 0.045), # (PXH)
        (sid(34745), 0.045), # (PDN)
        (sid(34076), 0.045), # (PXF) 
        (sid(32595), 0.045), # (PRFZ) 
        (sid(27089), 0.045), # (PWV)
        (sid(46529), 0.045), # (GVAL)
        (sid(35970), 0.055) # (ACWI)
    ]
    """

    # Run at the start of each month, when the market opens and rebalance
    zipline.schedule_function(
        my_rebalance,
        context.rebalance_frequency,
        time_rule=zipline.time_rules.market_open())
    
    #records security values
    zipline.schedule_function(
        record_vars, 
        date_rules.every_day(), 
        zipline.time_rules.market_close()
    )

class RebalanceFrequency:
    MONTHLY = zipline.date_rules.month_start(days_offset=0)
    WEEKLY = zipline.date_rules.week_start(days_offset=0)
    DAILY = zipline.date_rules.every_day()

def record_vars(context, data):
    # track security value in portfolio
    # track cash amount
    for stock, weight in context.security_weights:
      shares = context.portfolio.positions[stock].amount
      cost = context.portfolio.positions[stock].cost_basis

    longs = shorts = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            longs += 1
        elif position.amount < 0:
            shorts += 1
    

    # Record our variables.
    record(leverage=context.account.leverage, long_count=longs, short_count=shorts)
    
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
    
def my_rebalance(context,data):
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
    tradeable_security_weights = [sw for sw in context.security_weights if data.can_trade(sw[0])]

    _, weights = zip(*tradeable_security_weights)
    total_weight = sum(weights)

    for security, weight in context.security_weights:
        if data.can_trade(security):
            order_target_percent(security, weight / total_weight)
            
            #log securities and their weights
            today = get_datetime('US/Eastern')
            if today.day == 1: #start of each rebalancing month
                log.info(str(security) + " weight:" + str(weight / total_weight))

def has_open_orders(context, data):               
    # Only rebalance when we have zero pending orders.
    has_orders = False
    for security, portfolio_weight in context.security_weights:
        orders = get_open_orders(security)
        if orders: #there are stocks with open orders
            has_orders = True
    return has_orders 

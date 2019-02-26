import pandas as pd
import PairsTrading as pt
import time
import fxcmpy

myUrl_base = 'https://api-demo.fxcm.com:443'
TOKEN = ''
bearer_access_token=pt.get_bearer(myUrl_base,TOKEN)
con = fxcmpy.fxcmpy(access_token=TOKEN, log_level='error')
def get_Positionsize(Account,risk_rate):
    Balance=Account.loc[Account.index[2],0]
    account_risk=Balance*risk_rate
    size=round(account_risk/(30*10))
    return(size)
def check_Margin(pair1,pair2,symbols,Account,offers,size,safety_rate):
    usableMargin=Account.loc[Account.index[11],0]
    pair1_id=symbols[pair1]
    pair2_id=symbols[pair2]
    Margin=offers['mmr'].at[pair1_id+1]+offers['mmr'].at[pair2_id+1]
    if size*1000*Margin < usableMargin*safety_rate:
               return True
    else:
               return False
            
               
df=pd.DataFrame()
symbols={}
openedPosition=False
while True:
    Account=con.get_accounts().T
    offers=con.get_offers(kind='dataframe')
    pt.prepare_data(df,symbols,bearer_access_token,myUrl_base)
    if not openedPosition :
       pair1,pair2=pt.coint_test(df,symbols)
    #spread=pt.Spread_RollingRegression(df,pair1,pair2)
    spread=pt.Spread_KalmanFilterRegression(df,pair1,pair2)
    zscore=pt.zscore(spread)['{}_{}'.format(pair1,pair2)].iat[-1]
    if not openedPosition:
      size=get_Positionsize(Account,0.02)
      if zscore >= 2 :
        if check_Margin(pair1,pair2,symbols,Account,offers,size,0.5) :
            buy_order = con.open_trade(symbol=pair2, is_buy=True,
                             rate=0,amount=str(size),
                             time_in_force='FOK',order_type='AtMarket')  
            short_order=buy_order = con.open_trade(symbol=pair1, is_buy=False,
                                            rate=0,amount=str(size),
                                            time_in_force='FOK',order_type='AtMarket')
            if con.open_pos :
               openedPosition=True
               orders_ids=con.get_open_trade_ids()
               long=pair2
               short=pair1
               print(orders_ids)
             
      if zscore <= -2 :
        if check_Margin(pair1,pair2,symbols,offers,size,0.5) :
            buy_order = con.open_trade(symbol=pair1, is_buy=True,
                                       rate=0,amount=str(size),
                                       time_in_force='FOK',order_type='AtMarket')   
            short_order=con.open_trade(symbol=pair2, is_buy=False,
                                       rate=0,amount=str(size),
                                       time_in_force='FOK',order_type='AtMarket')
            orders_ids=con.get_open_trade_ids()
            if con.open_pos:
               openedPosition=True
               orders_ids=con.get_open_trade_ids()
               long=pair1
               short=pair2
               print(orders_ids)
  
        
    else:
      long_price=df[long].iat[-1]
      short_price=df[short].iat[-1]
      if zscore < 0.1 and zscore > -0.1:
         close_buy=con.close_trade(trade_id=orders_ids[0], amount=size)
         close_sell=con.close_trade(trade_id=orders_ids[1], amount=size)
         if not con.open_pos:
              openedPosition=False
              size=0
              long=''
              short=''
              print(con.old_orders)
    time.sleep(86400)          

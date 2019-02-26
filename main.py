import pandas as pd
import time
from ClassTrade import Trade
import PairsTrading as pt





myUrl_base = 'https://api-demo.fxcm.com:443'
df=pd.DataFrame()
symbols={}
bearer_access_token=pt.get_bearer(myUrl_base)
trade=Trade()
trade_pairs=''
while True:
  pt.prepare_data(df,symbols,bearer_access_token,myUrl_base)
  if trade.openedPosition:
     pair1,pair2=pt.coint_test(df,symbols)

  #spread=pt.Spread_RollingRegression(df,pair1,pair2)
  spread=pt.Spread_KalmanFilterRegression(df,pair1,pair2)
  zscore=pt.zscore(spread)['{}_{}'.format(pair1,pair2)].iat[-1]
  if not trade.openedPosition:
      zscore=2
      if zscore >= 2 :
        if trade.check_Margin(pair1,pair2,symbols):
            tradetype='short'
            trade.open_position(pair1,pair2,tradetype,df)
            print(trade.openedPosition)
               
               
             
      if zscore <= -2 :
        if trade.check_Margin(pair1,pair2):
            tradetype='long'
            trade.open_position(pair1,pair2,tradetype,df)
            if trade.openedPosition :
               trade_pairs=pair2+'&'+pair1
  
        
  else:
       long_price=df[trade.long].iat[-1]
       short_price=df[trade.short].iat[-1]
       trade.get_loses()
       if zscore < 0.1 and zscore > -0.1:
          trade.close_position()
          trade.openedPosition
                 
       elif trade.loss >= 60 :
          trade.close_position()
          trade.openedPosition      
  #time.sleep(86400)

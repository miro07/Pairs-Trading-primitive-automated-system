import pandas as pd
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
  if trade_pairs=='':
     pair1,pair2=pt.coint_test(df,symbols)

  #spread=pt.Spread_RollingRegression(df,pair1,pair2)
  spread=pt.Spread_KalmanFilterRegression(df,pair1,pair2)
  zscore=pt.zscore(spread)['{}_{}'.format(pair1,pair2)].iat[-1]
  if not trade.openedPosition:
      trade.get_Positionsize()
      if zscore >= 2 :
        if trade.check_Margin(pair1,pair2,symbols):
            tradetype='short'
            trade.open_position(pair1,pair2,tradetype,df)
            if trade.openedPosition :
               trade_pairs='pair2' '&' 'pair1'
               
             
      if zscore <= -2 :
        if trade.check_Margin(pair1,pair2):
            tradetype='long'
            trade.open_position(pair1,pair2,tradetype,df)
            if trade.openedPosition :
               trade.pairs='pair2' '&' 'pair1'
  
        
  else:
       long_price=df['trade.long'].at[-1]
       short_price=df['trade.short'].at[-1]
       trade.get_loss
       trade.get_Positionsize()
       if zscore < 0.1 and zscore > -0.1:
          trade.close_position()
          if not trade.openedPosition:
                 trade_pairs=''
       elif trade.loss >= 60 :
          trade.close_position()
          if not trade.openedPosition:
                 trade_pairs=''

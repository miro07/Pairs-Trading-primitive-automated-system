#import necessary libraries
import requests
import json
import pandas as pd
import numpy as np
import datetime as dt
from statsmodels.tsa.stattools import coint
from pyfinance.ols import PandasRollingOLS
from socketIO_client import SocketIO
from pykalman import KalmanFilter
# define functions to connect with the API and to prepare the Data. 
def connect():
    print('websocket connected:' + socketIO._engineIO_session.id)
def close():
    print('websocket colsed')
def get_bearer(myUrl_base):  
 mytoken='c2340cde1dbf571ab43d235cfa7b0f940ed6b429'
 websocket_port=443
 socketIO=SocketIO(myUrl_base,websocket_port,params={'access_token':'{}'.format(mytoken)})
 socketIO.on('connect',connect)
 socketIO.on('disconnect',close)
 bearer_access_token='Bearer '+ socketIO._engineIO_session.id + mytoken
 return(bearer_access_token)
def prepare_data(df,symbols,bearer_access_token,myUrl_base):
    #get the available pairs and creat a dict contain their id for ulterior using.
    Url='{}/trading/get_instruments/?'.format(myUrl_base)
    head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': bearer_access_token }
    symbols_reponse=requests.get(Url,headers=head)
    symbols_json=symbols_reponse.json()
    symbols_data=pd.DataFrame(symbols_json['data'])
    symbols.update({'EUR/USD':1,'USD/JPY':2,'GBP/USD':3,'USD/CHF':4,'EUR/CHF':5,'AUD/USD':6,'USD/CAD':7,'NZD/USD':8,'EUR/GBP':9,'EUR/JPY':10})
    #get prices,calculate their mid prices and assemble them on the same DataFrame indexed by Date.
    for symbol in symbols.keys():
        midprice=[]
        symbol_id=symbols[symbol]
        Url='{}/candles/{}/D'.format(myUrl_base,symbol_id)
        head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': bearer_access_token } 
        data_reponse=requests.get(Url,headers=head,params={'num':1000})
        if data_reponse.status_code ==200:
         data_json=data_reponse.json()
         candles_data=pd.DataFrame(data_json['candles'])
         candles_data.columns=["time","bidopen","bidclose","bidhigh","bidlow","askopen","askclose","askhigh","asklow","tickQ"]
         for count,tm in enumerate(candles_data['time']):
              candles_data.at[count,'time']=dt.datetime.fromtimestamp(tm)
              mid=(candles_data.at[count,"bidclose"]+candles_data.at[count,"askclose"])/2
              midprice.append(mid)
         candles_data['time']=pd.to_datetime(candles_data['time']).dt.floor('d')
         if 'Time' not in df:
            df['Time']=candles_data['time']
         df['{}'.format(symbol)]=midprice
        else:
             print(False,data_reponse.status_code)   
    df.set_index('Time',inplace=True)
    del df.index.name
#This function will test the co-integration between all the pairs and returns the best co_integrate pair.
def coint_test(df,symbols):
    pair1='None'
    pair2='None'
    min_coint_pvalue=1
    for p1 in list(df):
        for p2 in list(df):
            if p1!= p2:
                #search for the small p-value with an F-static less than critical value.
                coint_res=coint(df[p1],df[p2])
                print(coint_res)
                #F-value=coint_res[0]
                #critical_value=coint_res[2][1]
                if coint_res[1] < min_coint_pvalue and  coint_res[0] < coint_res[2][1] :
                   min_coint_pvalue=coint_res[1]
                   pair1=p1
                   pair2=p2
    return(pair1,pair2)
# Construct a Kalman filter rolling mean 
def KalmanFilterAverage(V):
  # Construct a Kalman filter
  kf = KalmanFilter(transition_matrices = [1],
     observation_matrices = [1],
     initial_state_mean = 0,
     initial_state_covariance = 1,
     observation_covariance=1,
     transition_covariance=.01)
  # Get the rolling mean
  state_means, _ = kf.filter(V.values)
  state_means = pd.Series(state_means.flatten(), index=V.index)
  return state_means
# Kalman filter regression
def Spread_KalmanFilterRegression(df,pair1,pair2):
  x=KalmanFilterAverage(df[pair1])
  y=KalmanFilterAverage(df[pair2])                    
  delta = 1e-3
  trans_cov = delta / (1 - delta) * np.eye(2) # How much random walk wiggles
  obs_mat = np.expand_dims(np.vstack([[x], [np.ones(len(x))]]).T, axis=1)
  kf = KalmanFilter(n_dim_obs=1, n_dim_state=2, # y is 1-dimensional, (alpha, beta) is 2-dimensional
     initial_state_mean=[0,0],
     initial_state_covariance=np.ones((2, 2)),
     transition_matrices=np.eye(2),
     observation_matrices=obs_mat,
     observation_covariance=2,
     transition_covariance=trans_cov)
  # Get running estimates and errors for the state parameters
  state_means, state_covs = kf.filter(y.values)
  #Build the spread
  spread=pd.DataFrame()
  spread['{}_{}'.format(pair1,pair2)]=df[pair1]-state_means[:,0]*df[pair2]
  spread.dropna(inplace=True)
  return(spread)
def Spread_RollingRegression(df,pair1,pair2):    
       spread=pd.DataFrame()
       #calculate hedge ratio using Rolling Regression Function.
       rolling_ols=PandasRollingOLS(df[pair1],df[pair2],window=20)
       spread['{}_{}'.format(pair1,pair2)]=df[pair1]-rolling_ols.beta['feature1']*df[pair2]
       spread.dropna(inplace=True)
       return(spread)
#Calculate z-score using Rolling mean and standard deviation.    
def zscore(spread):    
       std=spread.rolling(center=False,window=40).std()
       mean=spread.rolling(center=False,window=40).mean()
       x=spread.rolling(center=False,window=1).mean()
       zscore=(x-mean)/std
       zscore.dropna(inplace=True)
       return(zscore)


        
        

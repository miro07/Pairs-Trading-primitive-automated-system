import requests
import json 
from PairsTrading import get_bearer

class Trade(object):
    myUrl_base = 'https://api-demo.fxcm.com:443'
    bearer_access_token=get_bearer(myUrl_base)
    def __init__(self):
        self.openedPosition=False
        self.tradetype=''
        self.long=''
        self.short=''
        self.long_entry=0
        self.short_entry=0
        self.longsize=0
        self.shortsize=0
        self.Balance=0
        self.accountId=''
        self.usableMargin=0
        self.longorderid=0
        self.shortorderid=0
        self.loses=0
    def get_loses(self,long_price,short_price):
        self.loses=self.long_entry-long_price+short_price-self.short_entry 
        return self.loses
    def get_Margininfo(self):
        Url='{}/trading/get_model/?models=Account'.format(Trade.myUrl_base)
        head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
        account_reponse=requests.get(Url,headers=head)
        account_json=account_reponse.json()
        self.usableMargin=account_json['accounts'][0]['usableMargin']
        return(self.usableMargin)
    def get_Balance(self):         
        Url='{}/trading/get_model/?models=Account'.format(Trade.myUrl_base)
        head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
        account_reponse=requests.get(Url,headers=head)
        account_json=account_reponse.json()
        self.Balance=account_json['accounts'][0]['balance']
        return(self.Balance)
    def get_accountId(self):         
        Url='{}/trading/get_model/?models=Account'.format(Trade.myUrl_base)
        head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
        account_reponse=requests.get(Url,headers=head)
        account_json=account_reponse.json()
        self.accountId=account_json['accounts'][0]['accountId']
        return(self.accountId)
    def get_Positionsize(self):
        self.get_Balance()
        account_risk=self.Balance*0.02
        self.longsize=round(account_risk/(30*10))
        self.shortsize=round(account_risk/(30*10))
        return (self.longsize,self.shortsize)
    def check_Margin(self,pair1,pair2,symbols):
        self.get_Margininfo()
        Url='{}/trading/get_model/?models=Offer'.format(Trade.myUrl_base)
        head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
        offer_reponse=requests.get(Url,headers=head)
        offer_json=offer_reponse.json()
        pair1_id=symbols[pair1]
        pair2_id=symbols[pair2]
        Margin1=offer_json['offers'][pair1_id]['mmr']
        Margin2=offer_json['offers'][pair2_id]['mmr']
        Margintotal=Margin1+Margin2
        if (self.longsize+self.shortsize)*100*Margintotal < self.usableMargin*0.5:
            return True
        else:
            return False
    def open_position(self,pair1,pair2,tradetype,df):
        self.get_Positionsize()
        self.get_accountId()
        if tradetype=='short':
           Url='https://api-demo.fxcm.com:443/trading/open_trade'
           head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                   'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
           buy_reponse=requests.get(Url,headers=head,params={"account_id":self.accountId,
                                                             "symbol":pair1,"is_buy":True,
                                                             "rate":0,"amount":str(self.longsize),
                                                             "at_market":0,"order_type":"AtMarket","time_in_force":"FOK"})
           if buy_reponse.status_code==200:
              buy_json=buy_reponse.json()
              self.longorderid=buy_json[1]["orderId"]
              self.long='pair1'
              self.long_entry=df['pair1'].iat[-1]
              Url='https://api-demo.fxcm.com:443/trading/open_trade'
              head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                   'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
              sell_reponse=requests.get(Url,headers=head,params={"account_id":self.accountId,
                                                                 "symbol":pair2,"is_buy":False,
                                                                 "rate":0,"amount":str(self.shortsize),
                                                                 "at_market":0,"order_type":"AtMarket","time_in_force":"FOK"})
              sell_json=sell_reponse.json()
              if sell_reponse.status_code==200:
                 sell_json=sell_reponse.json()
                 self.shortorderid=sell_json[1]["orderId"]
                 self.short_entry=df['pair2'].iat[-1]
                 self.short='pair2'
                 file = open("tradehistory.txt","w")
                 file.write(str([buy_json,sell_json]))
                 file.close()
                 self.openedPosition=True
                 print ('The trade order was executed')
              else:
                  while self.long != '':
                        Url='https://api-demo.fxcm.com:443/trading/close_trade'
                        head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                                'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
                        Cbuy_reponse=requests.get(Url,headers=head,params={"trade_id": self.longorderid ,
                                                                           "rate": 0,"amount": str(self.longsize),
                                                                           "at_market": 0,"order_type": "AtMarket",
                                                                           "time_in_force": "FOK"})
                        sell_json=sell_reponse.json()
                        self.longorderid=0
                        self.long=''
                        self.long_entry=0
                        print ('The trade order was not executed',[buy_reponse,sell_reponse])
        elif tradetype=='long':
           Url='https://api-demo.fxcm.com:443/trading/open_trade'
           head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                   'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
           buy_reponse=requests.get(Url,headers=head,params={"account_id":self.accountId,"symbol":pair2,
                                                             "is_buy": True,"rate":0,"amount":str(self.longsize),
                                                             "at_market":0,"order_type":"AtMarket","time_in_force": "FOK"})
           if buy_reponse.status_code==200:
              buy_json=buy_reponse.json()
              self.longorderid=buy_json[1]["orderId"]
              self.long='pair2'
              self.long_entry=df['pair2'].iat[-1]
              Url='https://api-demo.fxcm.com:443/trading/open_trade'
              head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                   'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
              sell_reponse=requests.get(Url,headers=head,params={"account_id":self.accountId,
                                                                 "symbol": pair1,"is_buy": False,
                                                                 "rate": 0,"amount":str(self.shortsize),
                                                                 "at_market":0,"order_type":"AtMarket","time_in_force": "FOK"})
              if sell_reponse.status_code==200:
                 sell_json=sell_reponse.json()
                 self.shortorderid=sell_json[1]["orderId"]
                 self.short_entry=df['pair1'].iat[-1]
                 self.short='pair1'
                 file = open("tradehistory.txt","w")
                 file.write(str([buy_json,sell_json]))
                 file.close()
                 self.openedPosition=True
                 print ('The trade order was executed')
              else:
                  while self.long != '':
                      Url='https://api-demo.fxcm.com:443/trading/close_trade'
                      head = {'User-Agent': 'request', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'application/json', 'Connection': 'keep-alive',
                   'Authorization':Trade.bearer_access_token , 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '134'}
                      Cbuy_reponse=requests.get(Url,headers=head,params={"trade_id":self.longorderid ,
                                                                         "rate":0,"amount":str(self.longsize),
                                                                         "at_market":0,"order_type": "AtMarket",
                                                                         "time_in_force": "FOK"})
                      if Cbuy_reponse.status_code!=200 :
                         self.longorderid=0
                         self.long=''
                         self.long_entry=0
                         print ('The trade order was not executed',[buy_reponse,sell_reponse])
    def close_position(self):
          while self.long != '' :
                Url='https://api-demo.fxcm.com:443/trading/close_trade'
                head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
                Cbuy_reponse=requests.get(Url,headers=head,params={"trade_id":self.longorderid ,
                                                                   "rate":0,"amount":str(self.longsize),
                                                                   "at_market":0,"order_type": "AtMarket",
                                                                   "time_in_force": "FOK"})
                if Cbuy_reponse.status_code==200:
                   Cbuy_json=Cbuy_reponse.json()
                   self.longorderid=0
                   self.long_entry=0
                   self.long=''
          while self.short != '':
                Url='https://api-demo.fxcm.com:443/trading/close_trade'
                head = {'User-Agent': 'request','Accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded','Authorization': Trade.bearer_access_token }
                Csell_reponse=requests.get(Url,headers=head,params={"trade_id":self.shortorderid ,
                                                                    "rate":0,"amount":str(self.longsize),
                                                                    "at_market":0,"order_type": "AtMarket",
                                                                    "time_in_force": "FOK"})
                if Csell_reponse.status_code==200 :
                   Csell_json=Csell_reponse.json()
                   self.openedPosition=False
                   self.shortorderid=0
                   self.short_entry=0
                   self.short=''
                   file = open("tradehistory.txt","w")
                   file.write(str([Cbuy_json,Csell_json]))
                   file.close()
                   print ('The order was closed')
                else:
                   print ('The trade order was not closed',[Cbuy_reponse,Csell_reponse])
        
        
   

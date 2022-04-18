import os
import threading
import json
import requests
from datetime import date
from datetime import datetime
import time

import pandas as pd


headers = {
            'Content-type': 'application/json',
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"
}
class Trade:
    def __init__(self, logging, priceBuy, priceSell, schemaId, base_url):
        self.priceBuy = round(float(priceBuy))
        self.priceSell = round(float(priceSell))

        if self.priceSell < self.priceBuy  * 1.001: 
            self.priceSell = round(float(priceBuy) * 1.001)
            self.priceBuy = round(float(priceBuy) * 0.998)

        self.schemaId = int(schemaId)
        self.logging = logging
        self.url_order = '{base_url}/order/'.format(base_url=base_url)
        logging.info("INIT TRADE")
        

    
    def Method2(self):
        self.logging.info("Method 2 started")
        self.m2_order(self.priceBuy, self.priceSell)

    def m2_order(self, pb, ps):
        order = None
        order_id = 0
        isRunning = False
        n_try = 0
        try:
            order = self.executeTrade(True, pb)
            self.logging.info("::::::Order Buy Created:::::")
            self.logging.info(order)
            transactionTime = datetime.now()
            time.sleep(10)
            
            order_id = int(order['id'])
            isRunning = True
        except  Exception as e:
            self.logging.error(e)

        if(not isRunning):
            return
        
        while(isRunning):
            try:
                order = self.getOrder(order_id)
                sec_from_start = (datetime.now() - transactionTime).seconds
                self.logging.info("{n_try}::::::Checking Buy order:::::".format(n_try=n_try))
                if((order['status'] == 'NEW' or order['status'] == 'PENDING') and sec_from_start > 60*60):
                   
                    self.logging.info("{n_try}::::::Cancelling Buy order:::::".format(n_try=n_try))
                    self.cancelOrder(order_id)
                    self.logging.info("{n_try}::::::Cancelled Buy order:::::".format(n_try=n_try))

                if(order['status'] == 'FILLED'):
                    self.logging.info("::::::Creating Order Sell:::::")
                    self.executeTrade(False, ps)
                    self.logging.info("::::::Order Sell Created:::::")
                    isRunning = False

                if(order['status'] == 'CANCELLED'):
                    isRunning = False

            except  Exception as e:
                self.logging.error(e)
                isRunning = n_try <= 10
                n_try = n_try + 1
            time.sleep(5)
        
        return

    def getOrder(self, id):
        res = requests.get('{url_order}{id}'.format(url_order = self.url_order, id=id))
        return res.json()

    def cancelOrder(self, id):
        res = requests.delete('{url_order}{id}'.format(url_order = self.url_order, id=id))
        return res.json()

    def executeTrade(self,  isBuy, price):
        order = 0
        try:
            data = json.dumps({ 
                "isBuy": isBuy,
                "value": price,
                "schemaId": self.schemaId
            })
            self.logging.info(data)
            order = requests.post(self.url_order, data=data, headers=headers).json()
            self.logging.info(order)
        except Exception as e:
            self.logging.error(e)
        return order


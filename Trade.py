import os
import threading


from datetime import date
from datetime import datetime
import time
import math

import pandas as pd


class Trade:
    def __init__(self, symbol, priceBuy, priceSell, amount):
        self.symbol = symbol
        self.priceBuy = priceBuy
        self.priceSell = priceSell
        self.amount = amount 
        

    def Method1(self):
        threading.Thread(target=self.m1_order, args=(True, self.priceBuy, self.amount, )).start()
        threading.Thread(target=self.m1_order, args=(False, self.priceSell, self.amount, )).start()

    def m1_order(self, isBuy, price, amount):
        order = None
        order_id = 0
        isRunning = False
        try:
            order = self.executeTrade(self.symbol, isBuy, price, amount)
            transactionTime = datetime.now()
            order_id = str(order['orderId'])
            isRunning = True
        except  Exception as e:
            print('-'*40)
            print('-'*40)
            print(datetime.now())
            print(self.symbol, isBuy, price, amount )
            print(e)
            print('-'*40)


        if(not isRunning):
            return
        
        while(isRunning):
            try:
                order = client.get_order(symbol=self.symbol,orderId = order_id)
                sec_from_start = (datetime.now() - transactionTime).seconds

                if(order['status'] == 'NEW' and sec_from_start > 60*60):
                    client.cancel_order(symbol=self.symbol, orderId=order)

                if((order['status'] == 'FILLED' or order['status'] == 'CANCELED')):
                    isRunning = False
            except  Exception as e:
                print('-'*40)
                print('-'*40)
                print(self.symbol, isBuy, price, amount)
                print('Order ID: ' + str(order_id))
                print(e)
                print('-'*40)
                isRunning = False
            time.sleep(10)

    def Method2(self):
        threading.Thread(target=self.m2_order, args=(self.priceBuy, self.priceSell, self.amount, )).start()

    def m2_order(self, pb, ps, amount):
        order = None
        order_id = 0
        isRunning = False
        n_try = 0
        try:
            order = self.executeTrade(self.symbol, True, pb, amount)
            print("::::::Order Buy Created:::::")
            transactionTime = datetime.now()
            time.sleep(10)
            
            order_id = int(order['orderId'])
            isRunning = True
        except  Exception as e:
            print('-'*40)
            print('-'*40)
            print(datetime.now())
            print(order)
            print(e)
            print('-'*40)

        if(not isRunning):
            return
        
        while(isRunning):
            try:
                order = client.get_order(symbol=self.symbol, orderId = order_id)
                sec_from_start = (datetime.now() - transactionTime).seconds
                print(str(order_id), "::::::Checking Buy order:::::", n_try)
                if(order['status'] == 'NEW' and sec_from_start > 60*15):
                    print(str(order_id), "::::::Cancelling Buy order:::::", n_try)
                    client.cancel_order(symbol=order['symbol'], orderId=order['orderId'])
                    print(str(order_id), "::::::Cancelled Buy order:::::", n_try)

                if(order['status'] == 'FILLED'):
                    self.executeTrade(self.symbol, False, ps, amount)
                    print(str(order_id), "::::::Order Sell Created:::::")
                    print(order)
                    isRunning = False

                if(order['status'] == 'CANCELED'):
                    isRunning = False

            except  Exception as e:
                print('-'*40)
                print('-'*40)
                print(order)
                print('Order ID: ' + str(order_id))
                print(e)
                print('-'*40)
                isRunning = n_try <= 10
                n_try = n_try + 1
            time.sleep(5)


    def getCurrentTrades(self, symbols):
        depth = client.get_order_book(symbol=symbols)
        bids = pd.DataFrame(depth["bids"])
        bids.columns = ['bids_price','bids_qnt']
        bids.sort_values(by=['bids_price'], inplace=True, ignore_index=True)

        asks = pd.DataFrame(depth["asks"])
        asks.columns = ['asks_price','asks_qnt']
        asks.sort_values(by=['asks_price'], inplace=True, ignore_index=True)
        
        return pd.concat([asks, bids], axis=1)

    def executeTrade(self, symbols,isBuy, price, qnt):
        order = 0
        try:
            order = client.create_order(
                symbol=symbols,
                side = Client.SIDE_BUY if isBuy else Client.SIDE_SELL,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=client.TIME_IN_FORCE_GTC,
                price=price,
                quantity=qnt)
        except Exception as e:
            print("ERROR SELLING LIMIT ({s})".format(s=symbols))
            print(e)
        return order

    def executeLiquidate(self, symbols, qnt, isBuy):
        print("Selling market: " + str(qnt) + "({s})".format(s=symbols))
        order = 0
        try:
            order = client.create_order(
                symbol=symbols,
                side = Client.SIDE_BUY if isBuy else Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=qnt)
        except Exception as e:
            print("ERROR SELLING MARKET ({s})".format(s=symbols))
            print(e)
        return order

    def cancelAllOpenOrders(self, open_orders):
        for o in open_orders:
            print("Canceling order: " + str(o['orderId']) + "({s})".format(s=str(o['symbol']) ))
            client.cancel_order(symbol=o['symbol'], orderId=o['orderId'])

    def cancelAllOpenBuyOrders(self, open_orders, inverted):
        for o in open_orders:
            if(o['side'] == 'SELL' if inverted else 'BUY' ):
                print("Canceling order: " + str(o['orderId']) + "({s})".format(s=str(o['symbol']) ))
                client.cancel_order(symbol=o['symbol'], orderId=o['orderId'])

    



class Trades:
    def rebalanceOrders(self, symbol, amount_trans, digits):
        open_orders = pd.DataFrame(client.get_open_orders(symbol=symbol))
        print("Rebalancing orders...")
        if(open_orders.shape[0]==0):
            print("No orders to rebalance")
            return
        open_orders['pred_value'] = open_orders['price'].astype(float) * open_orders['origQty'].astype(float)

        #Get AVG ORDERS BUY
        qnt_buy = round(open_orders[open_orders['side'] == 'BUY']['origQty'].astype(float).sum(), 5)
        print("Qnt Open BUY: " + str(qnt_buy))

        #Get AVG ORDERS SELL
        qnt_sell = round(open_orders[open_orders['side'] == 'SELL']['origQty'].astype(float).sum(),5)
        print("Qnt Open SELL: " + str(qnt_sell))

        
        if(open_orders[open_orders['side'] == 'BUY'].shape[0] > 1):
            price_buy = open_orders[open_orders['side'] == 'BUY']['pred_value'].astype(float).sum()/qnt_buy
            price_buy = round(price_buy ,digits)
            #Cancel Orders
            for o in open_orders.iterrows():
                if(o[1]['side'] == 'BUY'):
                    print("Canceling order: " + str(o[1]['orderId']) + "({s})".format(s=str(o[1]['symbol']) ))
                    client.cancel_order(symbol=o[1]['symbol'], orderId=o[1]['orderId'])
            client.create_order(
                symbol=symbol,
                side = Client.SIDE_BUY,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=client.TIME_IN_FORCE_GTC,
                price=price_buy,
                quantity=qnt_buy)

        if(open_orders[open_orders['side'] == 'SELL'].shape[0] > 1):
            price_sell = open_orders[open_orders['side'] == 'SELL']['pred_value'].astype(float).sum()/qnt_sell
            price_sell = round(price_sell ,digits)
            #Cancel Orders
            for o in open_orders.iterrows():
                if(o[1]['side'] == 'SELL'):
                    print("Canceling order: " + str(o[1]['orderId']) + "({s})".format(s=str(o[1]['symbol']) ))
                    client.cancel_order(symbol=o[1]['symbol'], orderId=o[1]['orderId'])
            client.create_order(
                symbol=symbol,
                side = Client.SIDE_SELL,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=client.TIME_IN_FORCE_GTC,
                price=price_sell,
                quantity=qnt_sell)

    def cancelAllOrdersTime(self, open_orders, hrs):
        for o in open_orders:
            transactionTime = datetime.fromtimestamp(int(o['time']) / 1000)
            if((datetime.now() - transactionTime).seconds > 60*60*hrs ):
                print("Canceling order: " + str(o['orderId']) + "({s})".format(s=str(o['symbol']) ))
                client.cancel_order(symbol=o['symbol'], orderId=o['orderId'])

    def cancelAllOrdersDays(self, open_orders, days):
        for o in open_orders:
            transactionTime = datetime.fromtimestamp(int(o['time']) / 1000)
            if((datetime.now() - transactionTime).days > days ):
                print("Canceling order: " + str(o['orderId']) + "({s})".format(s=str(o['symbol']) ))
                client.cancel_order(symbol=o['symbol'], orderId=o['orderId'])

    def run(self, symbol, amount_trans, digits):
        print(str(datetime.now())  + ": STARTING : " + s_from + ">>" + s_to)
        last_update = datetime.now()

        pred_low_v = 0
        pred_high_v = 0

        count_predictions = 0
        open_orders = client.get_open_orders(symbol=symbol)
        print(str(datetime.now())  + ": Checking Open Orders: <<" + s_from + ">>")
        #self.cancelAllOrdersTime(open_orders, 1)
        #self.rebalanceOrders(symbol, amount_trans, digits)
        while(1==1):
            try:
                if(datetime.now().minute % 15 == 0 and last_update.minute != datetime.now().minute ):
                    time.sleep(30)
                    if(count_predictions >= 4):
                        predictions.updateModels()
                        count_predictions = 0
                        self.rebalanceOrders(symbol, amount_trans, digits)

                    count_predictions += 1

                    last_update = datetime.now()
                    open_orders = client.get_open_orders(symbol=symbol)
                    print(str(datetime.now())  + ": Checking Open Orders: <<" + s_from + ">>")
                    #self.cancelAllOrdersDays(open_orders, 2)
                    

                    predictions.updateValues()
                    pred_low_v = predictions.value_low
                    pred_high_v = predictions.value_high

                    candle_up =  bool(predictions.candle) 
                    
                    print(str(datetime.now())  + ": Updated: " + s_from + ">>" + s_to + " > Pred Low: " + str(pred_low_v))
                    print(str(datetime.now())  + ": Updated: " + s_from + ">>" + s_to + " > Pred High: " + str(pred_high_v))

                    price_to_buy = round(pred_low_v, digits) 
                    minimum_sell = price_to_buy * 1.002
                    price_to_sell = round(pred_high_v if pred_high_v >= minimum_sell else minimum_sell, digits)

                    t = Trade(s_from, s_to, price_to_buy, price_to_sell, amount_trans)
                    #t.Method1()
                    t.Method2()

                    time.sleep((14 - (datetime.now().minute % 15)) * 60) 
                time.sleep(5)
            except  Exception as e:
                print("=========ERROR======ERROR========ERROR=======")
                print(str(datetime.now())  + ": Updated: " + s_from + ">>" + s_to)
                print(e)



threading.Thread(target=Trades().run, args=('BTC', 'BUSD', 0.00021, 2, )).start()
#threading.Thread(target=Trades().run, args=('BNB', 'BUSD', 0.05, 4, )).start()
#threading.Thread(target=Trades().run, args=('ETH', 'BUSD', 0.007, 2, )).start()
#threading.Thread(target=Trades().run, args=('ETH', 'BTC', 0.007, 6, )).start()
#threading.Thread(target=Trades().run, args=('BNB', 'BTC', 0.05, 7, )).start()
#threading.Thread(target=Trades().run, args=('BNB', 'ETH', 0.05, 6, )).start()

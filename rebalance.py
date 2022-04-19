import os
import errno
import requests
import time
import logging
from optparse import OptionParser
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import json
import pandas as pd

from Trade import Trade

def mkdir_p(path):
    try:
        os.makedirs(path, exist_ok=True)  
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: 
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise


current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)

#base_url = 'https://api.evaluatz.com'
base_url = 'http://localhost:3000'
headers = {
            'Content-type': 'application/json',
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"
}

current_time = datetime.utcnow()
last_update = current_time - timedelta(minutes=current_time.minute % 15) - timedelta(seconds=current_time.second)

oparser = OptionParser()
oparser.add_option("-s", "--order-schema", dest="order_schema_id", help="ORDER SCHEMA", metavar="ORDER-SCHEMA")
(options, args) = oparser.parse_args()

foldername = '{current_dir}/logs/{dt_lst_update}/{lst_update}'.format(current_dir=current_dir, dt_lst_update=last_update.strftime("%Y%m%d") , lst_update=last_update.strftime("%Y%m%d_%H_%M_%S"))
mkdir_p(foldername)
filename = 'log_rebalance_{schema_id}'.format(foldername=foldername,schema_id=str(options.order_schema_id)) 
log_path = '{foldername}/{filename}.log'.format(foldername=foldername,filename=filename) 
print("log location", log_path)
logging.basicConfig(filename=log_path,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


logging.info("----------------------------STARTING---------------------------")
logging.info("LAST UPDATE " + last_update.strftime("%Y-%m-%d %H:%M:%S"))
url_order = '{base_url}/order/'.format(base_url=base_url)
schemaId = options.order_schema_id
url_order_schema_details = '{base}/order-schema/{order_schema_id}'.format(base=base_url, order_schema_id=schemaId)

logging.info('Request:' + url_order_schema_details)
order_schema_details_res = requests.get(url_order_schema_details)
order_schema_details = order_schema_details_res.json()

order_list = []
order_original_list = []


def checkForChildOrders(order_id):
    order_list_x = []
    url_order_x = '{url_order}{order_id}'.format(url_order=url_order, order_id=order_id)
    order_temp = requests.get(url_order_x, headers=headers).json()
    order_temp_orders = order_temp['orders']
    if len(order_temp_orders) > 0:
        for o in order_temp_orders:
            order_list_x.extend(checkForChildOrders(o['id']))
    else: 
        order_list_x.append(order_temp)
    return order_list_x


for order in order_schema_details['orders']:
    if order['status']['id'] == 0 and not order['isBuy']:
        order_list_x = checkForChildOrders(order['id'])
        order_original_list.append(order['id'])
        order_list.extend(order_list_x)

if len(order_list) > 1:
    dfNewOrders = pd.DataFrame(order_list)
    meanValue = round(dfNewOrders['value'].astype(float).mean())
    qntToSell = float(order_schema_details['quantity']) * dfNewOrders['id'].count()    
    data = json.dumps({ 
                "isBuy": False,
                "value": meanValue,
                "schemaId": schemaId,
                "orders": order_original_list
            })
    order = requests.post(url_order, data=data, headers=headers).json()

logging.info("----------------------------FINISHED---------------------------")

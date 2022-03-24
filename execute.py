import os
import errno
import requests
import time
import logging
from optparse import OptionParser
from datetime import datetime
from datetime import timedelta
from dateutil import parser

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

base_url = 'https://api.evaluatz.com'

current_time = datetime.utcnow()
last_update = current_time - timedelta(minutes=current_time.minute % 15) - timedelta(seconds=current_time.second)

oparser = OptionParser()
oparser.add_option("-s", "--order-schema", dest="order_schema_id", help="ORDER SCHEMA", metavar="ORDER-SCHEMA")
(options, args) = oparser.parse_args()

foldername = '{current_dir}\logs\{dt_lst_update}\{lst_update}'.format(current_dir=current_dir, dt_lst_update=last_update.strftime("%Y%m%d") , lst_update=last_update.strftime("%Y%m%d_%H_%M_%S"))
mkdir_p(foldername)
filename = 'log_execute_order_{schema_id}'.format(foldername=foldername,schema_id=str(options.order_schema_id)) 
log_path = '{foldername}\{filename}.log'.format(foldername=foldername,filename=filename) 
print("log location", log_path)
logging.basicConfig(filename=log_path,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


logging.info("----------------------------STARTING---------------------------")
logging.info("LAST UPDATE " + last_update.strftime("%Y-%m-%d %H:%M:%S"))

url_order_schema_details = '{base}/order-schema/{order_schema_id}'.format(base=base_url, order_schema_id=options.order_schema_id)

logging.info('Request:' + url_order_schema_details)
order_schema_details_res = requests.get(url_order_schema_details)
order_schema_details = order_schema_details_res.json()
logging.info('Response:' + str(order_schema_details))

url_prediction_strategy_low = '{base}/prediction-strategy/{prediction_strategy_low_id}'.format(base=base_url, prediction_strategy_low_id=order_schema_details['lowPredictor'])
url_prediction_strategy_high = '{base}/prediction-strategy/{prediction_strategy_high_id}'.format(base=base_url, prediction_strategy_high_id=order_schema_details['highPredictor'])


def getLastPredictions():
    logging.info('Request:' + url_prediction_strategy_low)
    prediction_strategy_low  = requests.get(url_prediction_strategy_low).json()
    logging.info('Request:' + url_prediction_strategy_high)
    prediction_strategy_high  = requests.get(url_prediction_strategy_high).json()
    last_prediction_low = parser.parse(prediction_strategy_low['lastPrediction']['openTime']) 
    last_prediction_high = parser.parse(prediction_strategy_high['lastPrediction']['openTime'])
    logging.info("last_prediction_low " + last_prediction_low.strftime("%Y-%m-%d %H:%M:%S")) 
    logging.info("last_prediction_high " + last_prediction_high.strftime("%Y-%m-%d %H:%M:%S")) 
    return prediction_strategy_low, prediction_strategy_high, last_prediction_low, last_prediction_high


prediction_strategy_low, prediction_strategy_high, last_prediction_low, last_prediction_high = getLastPredictions()

    
   

while last_prediction_low.strftime("%Y-%m-%d %H:%M:%S") != last_prediction_high.strftime("%Y-%m-%d %H:%M:%S") or last_prediction_low.strftime("%Y-%m-%d %H:%M:%S") != last_update.strftime("%Y-%m-%d %H:%M:%S"):
    time.sleep(5)
    prediction_strategy_low, prediction_strategy_high, last_prediction_low, last_prediction_high = getLastPredictions()
    

t = Trade(logging, prediction_strategy_low['lastPrediction']['value'], prediction_strategy_high['lastPrediction']['value'], options.order_schema_id, base_url)
t.Method2()
logging.info("----------------------------FINISHED---------------------------")

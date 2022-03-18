import requests
from optparse import OptionParser
import time
#from Trade import Trade

base_url = 'http://localhost:3000'

parser = OptionParser()
parser.add_option("-s", "--order-schema", dest="order_schema_id", help="ORDER SCHEMA", metavar="ORDER-SCHEMA")


(options, args) = parser.parse_args()
print(options)

url_order_schema_details = '{base}/order-schema/{order_schema_id}'.format(base=base_url, order_schema_id=options.order_schema_id)

order_schema_details = requests.get(url_order_schema_details).json()

url_prediction_strategy_low = '{base}/prediction-strategy/{prediction_strategy_low_id}'.format(base=base_url, prediction_strategy_low_id=order_schema_details['lowPredictor'])
url_prediction_strategy_high = '{base}/prediction-strategy/{prediction_strategy_high_id}'.format(base=base_url, prediction_strategy_high_id=order_schema_details['highPredictor'])






next_update = '2022-03-09T16:45:00.000Z'

prediction_strategy_low  = requests.get(url_prediction_strategy_low).json()
prediction_strategy_high  = requests.get(url_prediction_strategy_high).json()
last_prediction_low = prediction_strategy_low['lastPrediction']['openTime']
last_prediction_high = prediction_strategy_high['lastPrediction']['openTime']
    
   

while last_prediction_low != last_prediction_high or last_prediction_low != next_update:
    time.sleep(5)
    prediction_strategy_low  = requests.get(url_prediction_strategy_low).json()
    prediction_strategy_high  = requests.get(url_prediction_strategy_high).json()
    last_prediction_low = prediction_strategy_low['lastPrediction']['openTime']
    last_prediction_high = prediction_strategy_high['lastPrediction']['openTime']   


#t = Trade(s_from, s_to, price_to_buy, price_to_sell, amount_trans)
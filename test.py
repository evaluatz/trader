import setproctitle 
import time
setproctitle.setproctitle('TEST')

priceBuy = 42367.83
priceSell = 42385.39
spriceSell = priceSell
spriceBuy = priceBuy

if priceSell < priceBuy * 1.001: 
    spriceSell = round(priceBuy * 1.001,2)
    spriceBuy = round(priceBuy * 0.998,2)
print(spriceBuy, priceSell)

while 1==1: 
    print("RR")
    time.sleep(5)


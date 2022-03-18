from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--symbol", dest="symbol", help="Symbol", metavar="SYMBOL")
parser.add_option("-q", "--quantity", help="Quantity", metavar="QUANTITY")
parser.add_option("-k", "--key", help="Binance Key", metavar="KEY")
parser.add_option("-p", "--secret", help="Binance Secret", metavar="SECRET")

(options, args) = parser.parse_args()
print(options)
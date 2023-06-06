from classes.buff import Buff
from classes.BuffIdUpdater import BuffIdUpdater
import csv

prices_file = '../prices.csv'

buff = Buff()
buff_id = BuffIdUpdater()


itemNameLookup = input("Type the name of the item to lookup: ")
pair = input("Type the currency you want to convert to: ") #At the moment only usd
rate=buff.currencyConverter("cny",pair)
itemID = buff_id.search_id(itemNameLookup)
prices = buff.getBuffPriceById(itemID,rate)

data = [[itemNameLookup, str(price['price']), str(price['priceUSD']), price['Phase/Fade']] for price in prices]

with open(prices_file, 'w', newline='', encoding="utf8") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Item', 'Price(CNY)', 'Price(USD)', 'Attributes'])
    for item in data:
        writer.writerow(item)

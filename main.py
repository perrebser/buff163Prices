from classes.buff import Buff
from classes.BuffIdUpdater import BuffIdUpdater
import csv

prices_file = '../prices.csv'

buff = Buff()
buff_id = BuffIdUpdater()

itemNameLookup = input("Type the name of the item to lookup: ")
itemID = buff_id.search_id(itemNameLookup)
prices = buff.getBuffPriceById(itemID)

data = [[itemNameLookup, str(price['price']), price['Phase/Fade']] for price in prices]

with open(prices_file, 'w', newline='', encoding="utf8") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Item', 'Price', 'Attributes'])
    for item in data:
        writer.writerow(item)

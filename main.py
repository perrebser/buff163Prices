from classes.buff import Buff
from classes.BuffIdUpdater import BuffIdUpdater
import csv

prices_file = '../prices.csv'

buff = Buff()
buff_id = BuffIdUpdater()

item_list = []
while True:
    itemName = input("Type the name/s of the item to lookup (0 for exit): ")
    if itemName == "0":
        break
    item_list.append(itemName)

pair = input("Type the currency you want to convert to: ")  # At the moment only usd
rate = buff.currencyConverter("cny", pair)
item_id_list = buff_id.search_id(item_list)
prices = buff.getBuffPriceById(item_id_list, rate)

data = []
for i, item_prices in enumerate(prices):
    item_name = item_list[i]
    for price in item_prices:
        price_value = str(price['price'])
        price_value_usd = str(price['priceUSD'])
        phase_fade = price['Phase/Fade']
        data.append([item_name, price_value, price_value_usd, phase_fade])


with open(prices_file, 'w', newline='', encoding="utf8") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Item', 'Price(CNY)', 'Price(USD)', 'Attributes'])
    for item in data:
        writer.writerow(item)

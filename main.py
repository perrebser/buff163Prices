from classes.buff import Buff
from classes.BuffIdUpdater import BuffIdUpdater
from gui.main_window import MainWindow
import csv

prices_file = '../prices.csv'

buff = Buff()
buff_id = BuffIdUpdater()
# window=MainWindow()
# window.mainloop()

item_list = []
numOffersToCheck = int(input("How many offers would you like to check?Type the number of offers you want to check: (1,2,"
                          "3...): "))
check_with_file=input("Would you like to read item name from txt file or input manually? Y(file)/N(manual)")
if(check_with_file!='Y'):
    while True:
        itemName = input("Type the name/s of the item to lookup (0 for exit): ")
        if itemName == "0":
            break
    item_list.append(itemName)
else:
    file_dir=input("Type the name of the file with the items name(must be in this directory): ")
    with open(file_dir, 'r',encoding="utf8") as file:
        items=file.read().splitlines()
        for item in items:
            item_list.append(item)

pair = input("Type the currency you want to convert to: ")  # At the moment only usd
rate = buff.currencyConverter("cny", pair)
item_id_list = buff_id.search_id(item_list)
prices = buff.getBuffPriceById(item_id_list, rate, numOffersToCheck)

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

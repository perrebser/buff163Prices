from classes.buff import Buff
from classes.BuffIdUpdater import BuffIdUpdater
import csv


prices_file='../prices.csv'

buff=Buff()
buff_id=BuffIdUpdater()

itemNameBuscar=input("Type the name of the item to lookup: ")
itemID=buff_id.search_id(itemNameBuscar)
prices=buff.getBuffPriceById(itemID)

data = [[itemNameBuscar, str(price['price']), price['Phase/Fade']] for price in prices]


with open(prices_file,'w',newline='',encoding="utf8") as file:
     writer=csv.writer(file,delimiter=',')
     writer.writerow(['Item','Price','Attributes'])
     for item in data:
        writer.writerow(item)

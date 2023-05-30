from classes.buff import Buff
from classes.buffIds import BuffId
import csv


prices_file='../prices.csv'

buff=Buff()
buff_id=BuffId()
itemNameBuscar=input("Type the name of the item to lookup: ")
itemID=buff_id.search_id(itemNameBuscar)
precios=buff.getBuffPriceById(itemID)

data=[[itemNameBuscar,str(precio)]for precio in precios]


with open(prices_file,'w',newline='',encoding="utf8") as file:
     writer=csv.writer(file,delimiter=',')
     writer.writerow(['Item','Price'])
     for item in data:
        writer.writerow(item)

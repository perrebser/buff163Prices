from classes.buff import Buff
import csv
import os

prices_file='../prices.csv'

buff=Buff()
itemID="43091"
precio=buff.getBuffPrice(itemID)

with open(prices_file,'w',newline='') as file:
    writer=csv.writer(file)
    writer.writerow(['Precio'])

    for precio in precio:
        writer.writerow([precio])
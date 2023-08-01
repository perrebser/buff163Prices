import asyncio
import csv
import distutils
import urllib

import aiohttp
import requests

from classes.BuffIdUpdater import BuffIdUpdater


class BuffPricesManager:
    def __init__(self, header):
        self.BuffIdUpdater = BuffIdUpdater()
        self.header = {
            "Cookie": str(header)
        }

    def get_user_input(self):
        item_list = []
        num_offers_to_check = int(
            input("How many offers would you like to check? Type the number of offers you want to check: "))

        check_with_file = input("Would you like to read item names from a txt file? (Y/N): ")

        if check_with_file.upper() == 'Y':
            file_dir = input("Type the name of the file with the item names (must be in this directory): ")
            with open(file_dir, 'r', encoding="utf8") as file:
                item_list = file.read().splitlines()
        else:
            while True:
                item_name = input("Type the name/s of the item to lookup (0 to exit): ")
                if item_name == '0':
                    break
                item_list.append(item_name)

        pair = input("Type the currency you want to convert to: ")  # At the moment only USD

        check_buy_orders = distutils.util.strtobool(input("Also check buy orders prices? (Y/N): "))
        check_float = distutils.util.strtobool(
            input("Do you want to search within a specific range of floats? (Y/N): "))
        min_float = None
        max_float = None
        if not check_float:
            pass
        else:
            min_float = input("Enter minimum value for float: ")
            max_float = input("Enter maximum value for float: ")
        return item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float
        # return item_list, num_offers_to_check, pair, check_buy_orders

    def currencyConverter(self, toCurrency, fromCurrency):
        pair = fromCurrency.upper() + toCurrency.upper()
        URL = "https://www.freeforexapi.com/api/live?pairs=" + pair
        r = requests.get(URL).json()
        rate = 1 / float(r["rates"][pair]["rate"])
        return rate

    async def fetch_sell_prices(self, session, item_id, rate, num_offers_to_check, **kwargs):
        min_float = kwargs.get('min_float')
        max_float = kwargs.get('max_float')
        URL = f"https://buff.163.com/api/market/goods/sell_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": item_id
        }
        url = URL + '?' + urllib.parse.urlencode(params)
        async with session.get(url) as response:
            resp = await response.json()
            items = resp["data"]["items"][:num_offers_to_check]
            data = []
            for item in items:
                price = float(item["price"])
                price_usd = round(float(price * rate), 2)
                wear = (item["asset_info"]["paintwear"])
                metaphysic = item["asset_info"]["info"].get("metaphysic", {}).get("data", {}).get("name", {})
                item_data = {"price": price, "priceUSD": price_usd, "Phase/Fade": metaphysic, "Wear": wear}
                data.append(item_data)
            return data

    async def fetch_buy_orders(self, session, item_id, rate, num_offers_to_check):
        URL = f"https://buff.163.com/api/market/goods/buy_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": item_id
        }
        url = URL + '?' + urllib.parse.urlencode(params)
        async with session.get(url) as response:
            resp = await response.json()
            items = resp["data"]["items"][:num_offers_to_check]
            data = []
            for item in items:
                price = float(item["price"])
                price_usd = round(float(price * rate), 2)
                item_data = {"buy_order": price, "priceUSD": price_usd}
                data.append(item_data)
            return data

    def write_to_csv(self, sell_prices, buy_orders, item_list, prices_file):
        with open(prices_file, 'w', newline='', encoding="utf8") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(
                ['Item', 'Sell Price(CNY)', 'Sell Price(USD)', 'Buy Order(CNY)', 'Buy Order(USD)', 'Phase-Fade',
                 'Wear'])

            for sell_data, buy_data, item_name in zip(sell_prices, buy_orders, item_list):
                sell_price = sell_data[0]['price']
                sell_price_usd = sell_data[0]['priceUSD']
                buy_price = buy_data[0]['buy_order']
                buy_price_usd = buy_data[0]['priceUSD']
                attributes = sell_data[0]['Phase/Fade']
                wear = sell_data[0]['Wear']

                writer.writerow([item_name, sell_price, sell_price_usd, buy_price, buy_price_usd, attributes, wear])

    async def run(self):
        item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float = self.get_user_input()

        kwargs = {}
        if min_float is not None:
            kwargs['min_float'] = min_float
        if max_float is not None:
            kwargs['max_float'] = max_float
        rate = self.currencyConverter("cny", pair)
        item_id_list = self.BuffIdUpdater.search_id(item_list)

        sell_prices = []
        buy_orders = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item_id in item_id_list:
                tasks.append(self.fetch_sell_prices(session, item_id, rate, num_offers_to_check, **kwargs))
                if check_buy_orders:
                    tasks.append(self.fetch_buy_orders(session, item_id, rate, num_offers_to_check))

            results = await asyncio.gather(*tasks)
            sell_prices = results[::2]
            buy_orders = results[1::2]

        self.write_to_csv(sell_prices, buy_orders, item_list, '../prices.csv')

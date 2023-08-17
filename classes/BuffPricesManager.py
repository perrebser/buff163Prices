import asyncio
import csv
import distutils
import json
import urllib

import aiohttp
import requests

from classes.BuffIdUpdater import BuffIdUpdater


class BuffPricesManager:
    FILE_PATH = '../prices.csv'

    def __init__(self, header):
        self.BuffIdUpdater = BuffIdUpdater()
        self.header = {
            "Cookie": str(header)
        }

    def get_user_input(self):
        item_list = []
        try:
            num_offers_to_check = int(
                input("How many offers would you like to check? Type the number of offers you want to check: "))

            check_with_file = input("Would you like to read item names from a txt file? (Y/N): ").upper()

            if check_with_file == 'Y':
                file_dir = input("Type the name of the file with the item names (must be in this directory): ")
                try:
                    with open(file_dir, 'r', encoding="utf8") as file:
                        item_list = file.read().splitlines()
                except FileNotFoundError as ex:
                    print(f"Error opening file '{file_dir}': {ex.strerror}")
            else:
                while True:
                    item_name = input("Type the name/s of the item to lookup (0 to exit): ")
                    if item_name == '0':
                        break
                    item_list.append(item_name)

            pair = input("Type the currency you want to convert to: ").upper()

            check_buy_orders = distutils.util.strtobool(input("Also check buy orders prices? (Y/N): "))
            check_float = distutils.util.strtobool(
                input("Do you want to search within a specific range of floats? (Y/N): "))
            min_float = None
            max_float = None
            if check_float:
                min_float = input("Enter minimum value for float: ")
                max_float = input("Enter maximum value for float: ")

        except ValueError as e:
            print("Invalid input:", e)
            return None

        return item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float

    def currencyConverter(self, toCurrency, fromCurrency):
        pair = fromCurrency.upper() + toCurrency.upper()
        URL = "https://www.freeforexapi.com/api/live?pairs=" + pair
        response = requests.get(URL)
        if response.status_code == 200:
            try:
                response_json = response.json()
                if 'message' not in response_json:
                    rate = 1 / float(response_json["rates"][pair]["rate"])
                    return rate
                else:
                    print("Currency pair not found in response:", pair)
            except json.JSONDecodeError:
                print("Error decoding json response")
        else:
            print("Request currency converter failed with status code", response.status_code)
        return None

    async def fetch_sell_prices(self, session, item_id, rate, num_offers_to_check, check_buy_orders, **kwargs):
        min_float = kwargs.get('min_float')
        max_float = kwargs.get('max_float')
        base_url = f"https://buff.163.com/api/market/goods/"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": item_id
        }
        sell_url = base_url + 'sell_order' + '?' + urllib.parse.urlencode(params)
        buy_url = base_url + 'buy_order' + '?' + urllib.parse.urlencode(params)
        async with session.get(sell_url) as response:
            resp = await response.json()
            item_name = resp["data"]["goods_infos"][item_id]["market_hash_name"]
            items = resp["data"]["items"][:num_offers_to_check]
            data = []
            for item in items:
                price = float(item["price"])
                price_usd = round(float(price * rate), 2)
                wear = (item["asset_info"]["paintwear"])
                metaphysic = item["asset_info"]["info"].get("metaphysic", {}).get("data", {}).get("name", {})
                item_data = {"item_name": item_name, "price": price, "priceUSD": price_usd, "buy_order": '',
                             "priceUSDBuy": '', "Phase/Fade": metaphysic,
                             "Wear": wear}
                data.append(item_data)
                if check_buy_orders:
                    async with session.get(buy_url) as buy_response:
                        buy_resp = await buy_response.json()
                        items_buy = buy_resp["data"]["items"][:num_offers_to_check]
                        for i, item_buy in enumerate(items_buy):
                            if i < len(data):
                                buy_price = float(item_buy["price"])
                                buy_price_usd = round(float(buy_price * rate), 2)
                                data[i]["buy_order"] = buy_price
                                data[i]["priceUSDBuy"] = buy_price_usd
            return data

    def write_to_csv(self, items_prices, prices_file):
        data = []
        for item_price_offers in items_prices:
            for item_price in item_price_offers:
                sell_price = item_price['price']
                sell_price_usd = item_price['priceUSD']
                buy_price = item_price['buy_order']
                buy_price_usd = item_price['priceUSDBuy']
                attributes = item_price['Phase/Fade']
                wear = item_price['Wear']
                item_name = item_price['item_name']
                data.append([item_name, sell_price, sell_price_usd, buy_price, buy_price_usd, attributes, wear])
        try:
            with open(prices_file, 'w', newline='', encoding="utf8") as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(
                    ['Item', 'Sell Price(CNY)', 'Sell Price(USD)', 'Buy Order(CNY)', 'Buy Order(USD)', 'Phase-Fade',
                     'Wear'])
                for item in data:
                    writer.writerow(item)
        except PermissionError as e:
            print(f"You don't have permission to write to the file: {e}")
        except IOError as ex:
            print(f"Error writing file: {ex}")

    async def run(self):
        item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float = self.get_user_input()

        kwargs = {}
        if min_float is not None:
            kwargs['min_float'] = min_float
        if max_float is not None:
            kwargs['max_float'] = max_float
        rate = self.currencyConverter("cny", pair)
        item_id_list = self.BuffIdUpdater.search_id(item_list)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for item_id in item_id_list:
                tasks.append(
                    self.fetch_sell_prices(session, item_id, rate, num_offers_to_check, check_buy_orders, **kwargs))

            results = await asyncio.gather(*tasks)
        self.write_to_csv(results, self.FILE_PATH)

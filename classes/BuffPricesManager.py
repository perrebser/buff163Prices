import asyncio
import csv
import distutils
import json
import sys
import urllib
from datetime import datetime

import aiohttp
import requests

from classes.BuffIdUpdater import BuffIdUpdater


class BuffPricesManager:
    FILE_PATH = '../prices.csv'
    FILE_PATH_LAST_SALES = '../last_sales.csv'
    RED_COLOR_FOR_ERROR = '\033[91m'

    def __init__(self, header):
        self.BuffIdUpdater = BuffIdUpdater()
        self.header = {
            "Cookie": str(header)
        }

    def check_config_json(self):
        cookie = self.header.get('Cookie')
        if cookie == '':
            print("config.json empty!\n.You need to configure config.json file")
            sys.exit()
        values = cookie.split(";")
        dictionary = {}
        for value in values:
            key, value = value.split('=')
            dictionary[key.strip()] = value.strip()
        for val in ['Device-Id', 'session', 'csrf_token']:
            if dictionary.get(val) is None:
                print(f'{self.RED_COLOR_FOR_ERROR}Wrong config.json.\n Please check the config guide: '
                      'https://github.com/perrebser/buff163Prices#setup-buff163-cookies')
                sys.exit()

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
                min_float = float(input("Enter minimum value for float: "))
                max_float = float(input("Enter maximum value for float: "))
                if min_float > max_float:
                    raise ValueError("Minimum value cannot be greater than maximum value")
        except ValueError as e:
            print("Invalid input:", e)
            return None
        check_last_sales = distutils.util.strtobool(input("Do you want to generate a file with the latest sales of the "
                                                          "items? (Config.json file configuration required) Y/N: "))
        return item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float, check_last_sales

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
        data = []
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
        if min_float and max_float is not None:
            sell_url = sell_url + f'&min_paintwear={min_float}&max_paintwear={max_float}'  ##Only available when logged in using cookies
            buy_url = buy_url + f'&min_paintwear={min_float}&max_paintwear={max_float}'
        async with session.get(sell_url) as response:
            resp = await response.json()
            if len(resp["data"]["items"]) == 0:
                print(f"Not offers found for item with id: {item_id}")
                data = []
            else:
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

    def write_to_csv(self, items_prices, last_sales, prices_file, last_sales_file):
        data = []
        data_last_sales = []
        if items_prices[0] is not None:
            for item_price_offers in items_prices:
                sell_price = item_price_offers['price']
                sell_price_usd = item_price_offers['priceUSD']
                buy_price = item_price_offers['buy_order']
                buy_price_usd = item_price_offers['priceUSDBuy']
                attributes = item_price_offers['Phase/Fade']
                wear = item_price_offers['Wear']
                item_name = item_price_offers['item_name']
                data.append([item_name, sell_price, sell_price_usd, buy_price, buy_price_usd, attributes, wear])
        if last_sales[0] is not None:
            for last_sale_info in last_sales:
                item_id = last_sale_info["item_id"]
                item_wear = last_sale_info["float"]
                date = last_sale_info["sell_date"]
                price = last_sale_info["sell_price"]
                sell_type = "Sell" if last_sale_info["sell_type"] == 1 else "Buy_Order"
                data_last_sales.append([item_id, item_wear, date, price, sell_type])
        try:
            with open(prices_file, 'w', newline='', encoding="utf8") as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(
                    ['Item', 'Sell Price(CNY)', 'Sell Price(USD)', 'Buy Order(CNY)', 'Buy Order(USD)', 'Phase-Fade',
                     'Wear'])
                for item in data:
                    writer.writerow(item)
            with open(last_sales_file, 'w', newline='', encoding="utf8") as file2:
                writer = csv.writer(file2, delimiter=',')
                writer.writerow(
                    ['ItemID', 'Wear', 'Sell Date', 'Sell Price', 'Sell Type'])
                for item in data_last_sales:
                    writer.writerow((item)
                                    )
        except PermissionError as e:
            print(f"You don't have permission to write to the file: {e}")
        except IOError as ex:
            print(f"Error writing file: {ex}")

    async def fetch_last_sales(self, session, item_id):
        base_url = f"https://buff.163.com/api/market/goods/"
        data = []
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": item_id,
            "page_size": 10
        }
        last_sales_url = base_url + 'bill_order' + '?' + urllib.parse.urlencode(params)
        async with session.get(last_sales_url) as response:
            resp = await response.json()
            items = resp["data"]["items"][:10]
            for item in items:
                item_id = item["asset_info"]["goods_id"]
                sell_price = float(item["price"])
                sell_date = datetime.fromtimestamp(item["transact_time"])
                sell_type = item["type"]
                wear = item["asset_info"]["paintwear"]
                item_data = {"item_id": item_id, "sell_price": sell_price, "sell_date": sell_date,
                             "sell_type": sell_type, "float": wear}
                data.append(item_data)
        return data

    async def run(self):
        item_list, num_offers_to_check, pair, check_buy_orders, min_float, max_float, check_last_sales = self.get_user_input()
        kwargs = {}
        if (isinstance(min_float, float) and isinstance(max_float, float)) or check_last_sales:
            kwargs['min_float'] = min_float
            kwargs['max_float'] = max_float
            self.check_config_json()
        rate = self.currencyConverter("cny", pair)
        item_id_list = self.BuffIdUpdater.search_id(item_list)
        headers = self.header
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for item_id in item_id_list:
                tasks.append(
                    self.fetch_sell_prices(session, item_id, rate, num_offers_to_check, check_buy_orders, **kwargs))
                if check_last_sales:
                    tasks.append(self.fetch_last_sales(session, item_id))
            results_sells, result_last_sales = await asyncio.gather(*tasks)
        self.write_to_csv(results_sells, result_last_sales, self.FILE_PATH, self.FILE_PATH_LAST_SALES)

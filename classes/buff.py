import asyncio
import urllib

import aiohttp
import requests
import pandas as pd


class Buff:
    def currencyConverter(self, toCurrency, fromCurrency):
        pair = fromCurrency.upper() + toCurrency.upper()
        URL = "https://www.freeforexapi.com/api/live?pairs=" + pair
        r = requests.get(URL).json()
        rate = 1 / float(r["rates"][pair]["rate"])
        return rate

    def get_price_item(self, itemID, rate, numOffersToCheck):
        URL = "https://buff.163.com/api/market/goods/sell_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": itemID
        }
        r = requests.get(URL, params=params).json()
        items = r["data"]["items"][:numOffersToCheck]
        data = []
        for item in items:
            price = float(item["price"])
            price_usd = round(float(price * rate), 2)
            # if the item has attributes(phase on doppler or % on fades get them)
            metaphysic = item["asset_info"]["info"].get("metaphysic", {}).get("data", {}).get("name", {})
            item_data = {"price": price, "priceUSD": price_usd, "Phase/Fade": metaphysic}
            data.append(item_data)
        return data

    async def fetch_item_price(self, session, itemID, rate, numOffersToCheck):
        URL = "https://buff.163.com/api/market/goods/sell_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": itemID
        }
        url = URL + '?' + urllib.parse.urlencode(params)
        async with session.get(url) as response:
            resp = await response.json()
            items = resp["data"]["items"][:numOffersToCheck]
            data = []
            for item in items:
                price = float(item["price"])
                price_usd = round(float(price * rate), 2)
                metaphysic = item["asset_info"]["info"].get("metaphysic", {}).get("data", {}).get("name", {})
                item_data = {"price": price, "priceUSD": price_usd, "Phase/Fade": metaphysic}
                data.append(item_data)
            return data

    async def main(self, items, rate, numOffersToCheck):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for itemID in items:
                task = self.fetch_item_price(session, itemID, rate, numOffersToCheck)
                tasks.append(task)

            prices = await asyncio.gather(*tasks)

            items_prices = []
            for price in prices:
                items_prices.append(price)
            return items_prices

    def getBuffPriceById(self, item_id_list, rate, numOffersToCheck):
        buff = Buff()
        items_prices = asyncio.run(self.main(item_id_list, rate, numOffersToCheck))
        return items_prices

    def get_buyorder_item(self, itemId, rate):
        URL = "https://buff.163.com/api/market/goods/buy_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": itemId
        }
        r = requests.get(URL, params=params).json()
        items = r["data"]["items"][:3]
        data = []
        for item in items:
            price = float(item["price"])
            price_usd = round(float(price * rate), 2)
            item_data = {"price": price, "priceUSD": price_usd}
            df = pd.DataFrame(item_data)
            return df

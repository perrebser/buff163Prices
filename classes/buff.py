import requests


class Buff:
    def currencyConverter(self, toCurrency, fromCurrency):
        pair = fromCurrency.upper() + toCurrency.upper()
        URL = "https://www.freeforexapi.com/api/live?pairs=" + pair
        r = requests.get(URL).json()
        rate = 1 / float(r["rates"][pair]["rate"])
        return rate

    def get_price_item(self, itemID, rate):
        URL = "https://buff.163.com/api/market/goods/sell_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": itemID
        }
        r = requests.get(URL, params=params).json()
        items = r["data"]["items"][:3]
        data = []
        for item in items:
            price = float(item["price"])
            price_usd = round(float(price * rate), 2)
            # if the item has attributes(phase on doppler or % on fades get them)
            metaphysic = item["asset_info"]["info"].get("metaphysic", {}).get("data", {}).get("name", {})
            item_data = {"price": price, "priceUSD": price_usd, "Phase/Fade": metaphysic}
            data.append(item_data)
        return data

    def getBuffPriceById(self, item_id_list, rate):
        items_prices = []
        for item in item_id_list:
            items_prices.append(self.get_price_item(item, rate))
        return items_prices

    def get_buyorder_item(self, itemId, rate):
        URL = "https://buff.163.com/api/market/goods/buy_order"
        params = {
            "game": "csgo",
            "page_num": "1",
            "goods_id": itemId
        }
        r = requests.get(URL, params=params).json()

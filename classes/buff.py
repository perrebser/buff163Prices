import requests

class Buff:
    def getBuffPriceById(self,itemID):
        URL ="https://buff.163.com/api/market/goods/sell_order"
        params={
            "game" : "csgo",
            "page_num" : "1",
            "goods_id" : itemID
        }
        r=requests.get(URL,params=params).json()
        items=r["data"]["items"][:3]
        precios=[float(items["price"])for items in items]
        return precios
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
        data=[]
        for item in items:
            precio=float(item["price"])
            #if the item has attributes(phase on doppler or % on fades get them)
            metaphysic=item["asset_info"]["info"].get("metaphysic",{}).get("data",{}).get("name",{})
            item_data={"price":precio,"Phase/Fade": metaphysic }
            data.append(item_data)
        return data
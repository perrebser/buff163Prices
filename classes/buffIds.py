import os
import requests

class BuffId:
    URL="https://raw.githubusercontent.com/ModestSerhat/buff163-ids/main/buffids.txt"
    FILE_NAME="goodsIds.txt"

    def __init__(self):
        self.update_file_items_id()

    def update_file_items_id(self):
        response=requests.get(BuffId.URL)
        new_content=response.text
        if os.path.exists(BuffId.FILE_NAME):
            with open(BuffId.FILE_NAME, 'r',encoding="utf8") as file:
                existing_content = file.read()
            
            if existing_content != new_content:
                with open(BuffId.FILE_NAME, 'w',encoding="utf8") as file:
                    file.write(new_content)
        else:
            with open(BuffId.FILE_NAME, 'w',encoding="utf8") as file:
                file.write(new_content)
    
    def search_id(self,itemName):
        with open(BuffId.FILE_NAME,'r',encoding="utf8") as file:
            lines=file.readlines()
            for line in lines:
                id,name=line.strip().split(';')
                if(itemName==name):
                    return id
            return None


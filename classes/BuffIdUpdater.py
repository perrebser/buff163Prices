import os
import requests
import pandas as pd


class BuffIdUpdater:
    # This class is based on a project by ModestSerhat on GitHub. It is used to obtain the goods ID based on their name.
    URL = "https://raw.githubusercontent.com/ModestSerhat/buff163-ids/main/buffids.txt"
    FILE_NAME = "goodsIds.txt"

    def __init__(self):
        self.update_file_items_id()
        self.dataframe_items = self.store_in_dataframe()

    def update_file_items_id(self):
        response = requests.get(BuffIdUpdater.URL)
        new_content = response.text
        if os.path.exists(BuffIdUpdater.FILE_NAME):
            with open(BuffIdUpdater.FILE_NAME, 'r', encoding="utf8") as file:
                existing_content = file.read()

            if existing_content != new_content:
                with open(BuffIdUpdater.FILE_NAME, 'w', encoding="utf8") as file:
                    file.write(new_content)
        else:
            with open(BuffIdUpdater.FILE_NAME, 'w', encoding="utf8") as file:
                file.write(new_content)

    def store_in_dataframe(self):
        dataframe_items = pd.read_csv(BuffIdUpdater.FILE_NAME, sep=";", header=None, names=["id", "name"])
        dataframe_items.set_index("name",inplace=True)
        return dataframe_items

    def search_id(self, item_list):
        id_list = []
        for item in item_list:
            if item in item_list:
                if item in self.dataframe_items.index:
                    id_list.append(self.dataframe_items.loc[item,"id"])
                else:
                    id_list.append(None)
        return id_list

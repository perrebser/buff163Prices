import csv
import os
import requests


class BuffIdUpdater:
    # This class is based on a project by ModestSerhat on GitHub. It is used to obtain the goods ID based on their name.
    URL = "https://raw.githubusercontent.com/ModestSerhat/buff163-ids/main/buffids.txt"
    FILE_NAME = "goodsIds.txt"
    dicdt = {}

    def __init__(self):
        self.update_file_items_id()
        self.store_in_dict()

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

    def store_in_dict(self):
        with open(BuffIdUpdater.FILE_NAME, 'r', encoding="utf8") as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                item_id = row[0]
                item_name = row[1]
                self.dicdt[item_name] = item_id

    def search_id(self, item_list):
        id_list = []
        for item in item_list:
            id_list.append(self.dicdt.get(item))
        return id_list

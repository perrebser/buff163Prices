import os
import requests


class BuffIdUpdater:
    # This class is based on a project by ModestSerhat on GitHub. It is used to obtain the goods ID based on their name.
    URL = "https://raw.githubusercontent.com/ModestSerhat/buff163-ids/main/buffids.txt"
    FILE_NAME = "goodsIds.txt"

    def __init__(self):
        self.update_file_items_id()

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

    def search_id(self, item_list):
        id_list = []
        with open(BuffIdUpdater.FILE_NAME, 'r', encoding="utf8") as file:
            lines = file.readlines()
            for item in item_list:
                found = False
                for line in lines:
                    id, name = line.strip().split(';')
                    if item == name:
                        id_list.append(id)
                        found = True
                        break
                if not found:
                    id_list.append(None)

                file.seek(0)

        return id_list


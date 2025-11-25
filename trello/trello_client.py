import requests
import os

API_KEY = "REPLACE_WITH_TRELLO_API_KEY"
API_TOKEN = "REPLACE_WITH_TRELLO_API_TOKEN"
BOARD_ID = "REPLACE_WITH_TRELLO_BOARD_ID"


class TrelloClient:
    def __init__(self):
        self.base = "https://api.trello.com/1"

    def get_cards(self):
        url = f"{self.base}/boards/{BOARD_ID}/cards"
        params = {"key": API_KEY, "token": API_TOKEN}
        return requests.get(url, params=params).json()

    def get_lists(self):
        url = f"{self.base}/boards/{BOARD_ID}/lists"
        params = {"key": API_KEY, "token": API_TOKEN}
        return requests.get(url, params=params).json()

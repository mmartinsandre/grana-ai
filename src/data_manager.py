import json
from config import Config

class DataManager:
    def __init__(self):
        self.config = Config()
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.config.DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self):
        with open(self.config.DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_user_data(self, user_id):
        return self.data.get(str(user_id), {"transactions": [], "goals": []})

    def set_user_data(self, user_id, user_data):
        self.data[str(user_id)] = user_data
        self.save_data()

    def add_transaction(self, user_id, transaction):
        user_data = self.get_user_data(user_id)
        user_data["transactions"].append(transaction)
        self.set_user_data(user_id, user_data)

    def get_user_transactions(self, user_id):
        return self.get_user_data(user_id)["transactions"]

    def set_user_currency(self, user_id, currency):
        user_data = self.get_user_data(user_id)
        user_data["currency"] = currency
        self.set_user_data(user_id, user_data)

    def get_user_currency(self, user_id):
        return self.get_user_data(user_id).get("currency", "BRL")

    def reset_user_data(self, user_id):
        if str(user_id) in self.data:
            del self.data[str(user_id)]
            self.save_data()

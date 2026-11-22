import pickle

class Inventory:
    def __init__(self):
        self.items: list = []

    def has_item(self, item):
        return item in self.items

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def list_items(self):
        return self.items

    def save_inventory(self, filename="inventory.inventory"):
        with open(filename, "wb") as file:
            pickle.dump(self.items, file)

    def load_inventory(self, filename="inventory.inventory"):
        try:
            with open(filename, "rb") as file:
                self.items = pickle.load(file)
        except FileNotFoundError:
            self.items = []
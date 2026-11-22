import json

from .enemy import Enemy

class GameState:
    def __init__(self):
        self.is_running = True
        self.current_room = None
        self.inventory = []
        self.health = 100
        self.attack_power = 10

    def save_game(self, world, filename="savegame.json"):
        save_data = {
            "current_room": self.current_room.name,
            "inventory": self.inventory,
            "health": self.health,
            "attack_power": self.attack_power,
            "world": {  # Save the state of all rooms
                room_name: {
                    "items": room.items,
                    "locked": room.locked,
                    "enemy": {
                        "name": room.enemy.name,
                        "health": room.enemy.health,
                        "attack_power": room.enemy.attack_power
                    } if room.enemy else None
                }
                for room_name, room in world.items()
            }
        }
        with open(filename, "w") as file:
            json.dump(save_data, file)
        print("Game saved.")

    def load_game(self, world, filename="savegame.json"):
        try:
            with open(filename, "r") as file:
                save_data = json.load(file)

            self.current_room = world[save_data["current_room"]]
            self.inventory = list(save_data.get("inventory", []))
            self.health = save_data["health"]
            self.attack_power = save_data["attack_power"]

            # Restore room states
            for room_name, room_state in save_data["world"].items():
                room = world[room_name]
                room.items = room_state["items"]
                room.locked = room_state["locked"]
                if room_state["enemy"]:
                    enemy_state = room_state["enemy"]
                    room.enemy = Enemy(
                        name=enemy_state["name"],
                        health=enemy_state["health"],
                        attack_power=enemy_state["attack_power"]
                    )
                else:
                    room.enemy = None

            print("Game loaded.")
        except FileNotFoundError:
            print("No saved game found.")

    def save_replay(self, commands, filename="replay.json"):
        with open(filename, "w") as file:
            json.dump(commands, file)

        print("Replay saved.")
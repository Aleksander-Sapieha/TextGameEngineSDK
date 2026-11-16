import json
import select
import subprocess
import time
import sys
import pickle
import requests
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from . import GJ_Game

try:
    import msvcrt
except ImportError:
    msvcrt = None


pygame.mixer.init()

intro = pygame.mixer.Sound("audio/intro.wav")

def play_intro():
    subprocess.call('cls' if os.name == "nt" else "clear", shell=True)
    print("Game created by Source Guy")
    intro.play()
    time.sleep(3)
    intro.fadeout(20)

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



class Room:
    def __init__(self, name, description, connections=None, items=None, enemy=None, locked=False, key=None, end=False):
        self.name = name
        self.description = description
        self.connections = connections or {}
        self.items = items or []
        self.enemy = enemy  # Instance of Enemy class
        self.locked = locked  # Is the room locked?
        self.key = key  # Key required to unlock
        self.end = end or False

    def describe(self, inventory=None):
        desc = f"{self.name}\n{self.description}\n"
        visible_items = [item for item in self.items if item not in (inventory or [])]
        if visible_items:
            desc += f"You see: {', '.join(visible_items)}\n"
        if self.enemy:
            desc += f"A {self.enemy.name} is here! Prepare for battle.\n"
        return desc

class Enemy:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power

class Puzzle:
    def __init__(self, question, answer, reward=None):
        self.question = question
        self.answer = answer
        self.reward = reward

    def solve(self, user_answer):
        return user_answer.lower() == self.answer.lower()

def parse_input(user_input):
    commands = user_input.strip().lower().split()
    action = commands[0] if commands else None
    target = " ".join(commands[1:]) if len(commands) > 1 else None
    return action, target

class Crafting:
    def __init__(self):
        self.recipes = {
            "torch Set Series 1": ["stick", "cloth", "flint"],
            "wire cutters Set Series 1": ["metal", "plastic"]
        }

    def has_required_items(self, item_to_craft):
        if item_to_craft in self.recipes:
            required_items = self.recipes[item_to_craft]
            return all(item in self.inv.list_items() for item in required_items)
        return False

    def craft(self, inventory, item_to_craft):
        if item_to_craft in self.recipes:
            required_items = self.recipes[item_to_craft]
            if all(item in inventory for item in required_items):
                for item in required_items:
                    inventory.remove(item)
                inventory.append(item_to_craft)
                return True, f"You crafted {item_to_craft}!"
            else:
                return False, f"You don't have the required items to craft {item_to_craft}."
        else:
            return False, f"{item_to_craft} cannot be crafted."

def display(text):
    print(text)

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

class DropSystem:
    def __init__(self, drop_chance=0.60):  # Default drop chance is 60%
        self.drop_chance = drop_chance

    def attempt_drop(self, item=None, chance=None):
        import random
        if chance is None:
            chance = self.drop_chance
        if random.random() < chance:
            return True, f"You found a {item}!" if item else "You found something!"
        else:
            return False, "No items dropped."

class BugReporter:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_bug_report(self, description):
        data = {
            "content": f"**New Bug Report**\n\nPython version: {sys.version}\n\nOperating System: {sys.platform}\n\n{description}"
        }

        response = requests.post(self.webhook_url, json=data)

        if response.status_code == 204:
            print("Bug report sent!")
        else:
            print("Failed to send report:", response.status_code)
        print("Thank you for reporting the bug. We will look into it.")

class Api:
    def __init__(self, GAME_ID, GAME_SECRET):
        self.GAME_ID = GAME_ID
        self.GAME_SECRET = GAME_SECRET
        self.gj_game = GJ_Game.GJ_Game(GAME_ID=GAME_ID, GAME_SECRET=GAME_SECRET)

class Auth:
    def __init__(self, api):
        self.logged_in = False
        self.username = None
        self.token = None

    def login(self, username, token, api):
        self.username = username
        self.token = token
        gj_game = GJ_Game.GJ_Game(api.GAME_ID, api.GAME_SECRET)
        response = gj_game.log_in(username, token)
        if "success" in response.lower():
            self.logged_in = True
            print("Login successful!")
            with open("credentials.txt", "w") as f:
                f.write(f"{username}\n{token}")
            return True
        else:
            print("Login failed. Please check your credentials.")
            self.logged_in = False
            return False
        return False

class Trophies:
    def __init__(self, api):
        self.api = api

    def add_trophy(self, username, token, trophy_id):
        gj_game = GJ_Game.GJ_Game(self.api.GAME_ID, self.api.GAME_SECRET)
        response = gj_game.addTrophy(username, token, trophy_id)
        return response

    def remove_trophy(self, username, token, trophy_id):
        gj_game = GJ_Game.GJ_Game(self.api.GAME_ID, self.api.GAME_SECRET)
        response = gj_game.removeTrophy(username, token, trophy_id)
        return response

class TextGameEngine:
    def __init__(self, webhook_url, GAME_ID="1087229", GAME_SECRET="9c28a0641edb8972318db701368aa384"):
        self.game_state = GameState()
        self.world = {}

        self.inv = Inventory()

        self.crafting = Crafting()

        self.drop = DropSystem()

        self.bug_reporter = BugReporter(webhook_url=webhook_url)

        self.api = Api(GAME_ID=GAME_ID, GAME_SECRET=GAME_SECRET)
        self.auth = Auth(api=self.api)
        self.trophies = Trophies(api=self.api)

        from .renderer import Renderer
        self.renderer = Renderer()

        self.replay_commands = []
        self._command_buffer = ""
        self._last_room_text = None
        self._transient_message_until = 0.0
        self._last_realtime_move = 0.0

        from .videoExporter import VideoExporter

        self.exporter = VideoExporter()

    def poll_key_press(self):
        if msvcrt is not None:

            if not msvcrt.kbhit():
                return None

            key = msvcrt.getwch()
            if key == "\xe0":
                arrow_key = msvcrt.getwch()
                arrow_map = {
                    "H": "UP",
                    "P": "DOWN",
                    "K": "LEFT",
                    "M": "RIGHT"
                }
                return arrow_map.get(arrow_key, arrow_key)
            if key == "\x00":
                function_key = msvcrt.getwch()
                function_map = {
                    ";": "F1",
                    "<": "F2",
                    "=": "F3",
                    ">": "F4",
                    "?": "F5",
                    "@": "F6",
                    "A": "F7",
                    "B": "F8",
                    "C": "F9",
                    "D": "F10"
                }
                return function_map.get(function_key, function_key)
            return key
        else:
            if not select.select([sys.stdin], [], [], 0)[0]:
                return None

            key = sys.stdin.read(1)
            if key == "\x1b" and select.select([sys.stdin], [], [], 0.05)[0]:
                sequence_start = sys.stdin.read(1)
                if sequence_start in ("[", "O"):
                    sequence = ""
                    while select.select([sys.stdin], [], [], 0.05)[0]:
                        char = sys.stdin.read(1)
                        sequence += char
                        if "@" <= char <= "~":
                            break

                    sequence_map = {
                        "[A": "UP",
                        "[B": "DOWN",
                        "[D": "LEFT",
                        "[C": "RIGHT",
                        "OP": "F1",
                        "OQ": "F2",
                        "OR": "F3",
                        "OS": "F4",
                        "[11~": "F1",
                        "[12~": "F2",
                        "[13~": "F3",
                        "[14~": "F4",
                        "[15~": "F5",
                        "[17~": "F6",
                        "[18~": "F7",
                        "[19~": "F8",
                        "[20~": "F9",
                        "[21~": "F10",
                        "[23~": "F11",
                        "[24~": "F12"
                    }
                    return sequence_map.get(sequence_start + sequence)
            return key

    def handle_realtime_input(self, key):
        hotkey_map = {
            "w": "north",
            "W": "north",
            "UP": "north",
            "s": "south",
            "S": "south",
            "DOWN": "south",
            "a": "west",
            "A": "west",
            "LEFT": "west",
            "d": "east",
            "D": "east",
            "RIGHT": "east"
        }
        if key in hotkey_map:
            now = time.monotonic()
            if now - self._last_realtime_move < 0.2:
                return
            self._last_realtime_move = now
            self.handle_go(hotkey_map[key])
            self.exporter.add_frame(self.renderer.get_text())
            return

        if key in ("F6", "f6") or (key in ("x", "X") and not self._command_buffer):
            trophy_id = "307955"
            self.process_command("export", None)
            self.exporter.add_frame(self.renderer.get_text())
            self.trophies.add_trophy(self.auth.username, self.auth.token, trophy_id)

            return

        if key in ("F4", "f4"):
            self.process_command("save", None)
            self.exporter.add_frame(self.renderer.get_text())
            return

        if key in ("F5", "f5"):
            self.process_command("load", None)
            self.exporter.add_frame(self.renderer.get_text())
            return

        if key in ("e", "E"):
            self.handle_take_all()
            self.exporter.add_frame(self.renderer.get_text())
            return

        if key in ("\r", "\n"):
            if self._command_buffer.strip():
                command_text = self._command_buffer.strip()
                self.replay_commands.append(command_text)
                action, target = parse_input(command_text)
                self.process_command(action, target)
                self.exporter.add_frame(self.renderer.get_text())
            self._command_buffer = ""
            return

        if key in ("\b", "\x08"):
            self._command_buffer = self._command_buffer[:-1]
            return

        if key == "\x03":
            self._command_buffer = ""
            return

        if key.isprintable():
            self._command_buffer += key

        self.renderer.print(f"\r> {self._command_buffer}")

    def set_transient_message(self, message, duration=1.0):
        self._transient_message_until = time.monotonic() + duration
        self.renderer.print(message)

    def sync_inventory(self, source="state"):
        if source == "state":
            self.inv.items = list(self.game_state.inventory)
        elif source == "inv":
            self.game_state.inventory = list(self.inv.items)

    def load_world(self, world_data):
        for room_name, room_info in world_data.items():
            enemy = None
            if room_info.get("enemy"):
                enemy_info = room_info["enemy"]
                enemy = Enemy(enemy_info["name"], enemy_info["health"], enemy_info["attack_power"])
            
            self.world[room_name] = Room(
                room_name,
                room_info['description'],
                room_info.get('connections'),
                room_info.get('items'),
                enemy,
                room_info.get('locked', False),
                room_info.get('key'),
                room_info.get('end')
            )
        self.game_state.current_room = self.world.get("start")

    def main_loop(self):
        if msvcrt is not None or not sys.stdin.isatty():
            self._run_game_loop()
            return

        import termios
        import tty

        stdin_fd = sys.stdin.fileno()
        original_terminal_settings = termios.tcgetattr(stdin_fd)
        try:
            tty.setcbreak(stdin_fd)
            self._run_game_loop()
        finally:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, original_terminal_settings)

    def _run_game_loop(self):
        while self.game_state.is_running:
            current_room = self.game_state.current_room
            room_text = "\n" + current_room.describe(self.game_state.inventory)
            if room_text != self._last_room_text:
                self.renderer.print(room_text)
                self._last_room_text = room_text

            if self._transient_message_until and time.monotonic() >= self._transient_message_until:
                self.renderer.clear()
                self.renderer.print(room_text)
                self._transient_message_until = 0.0

            if current_room.enemy:
                self.fight_enemy(current_room.enemy)
                time.sleep(1)

            if current_room.end:
                self.renderer.print("You win!")
                self.trophies.add_trophy(self.auth.username, self.auth.token, "307970")
                time.sleep(3)
                sys.exit(1)

            pressed_key = self.poll_key_press()
            if pressed_key is not None:
                self.handle_realtime_input(pressed_key)

            time.sleep(0.05)
            self.exporter.add_frame(
                self.renderer.get_text()
            )

    def process_command(self, action, target):
        if action == "quit":
            self.game_state.is_running = False
            self.renderer.print("Thanks for playing!")
        elif action == "go":
            self.handle_go(target)
        elif action == "take":
            self.handle_take(target)
        elif action == "drop":
            self.handle_drop(target)
        elif action == "inventory":
            self.handle_inventory()
        elif action == "save":
            self.game_state.save_game(self.world)
        elif action == "load":
            self.game_state.load_game(self.world)
            self.sync_inventory(source="state")
        elif action == "replay":
            self.game_state.save_replay(self.replay_commands)
        elif action == "export":
            self.exporter.export()
        else:
            self.renderer.print("Unknown command.")

    def handle_go(self, direction):
        current_room = self.game_state.current_room
        if direction in current_room.connections:
            next_room = self.world[current_room.connections[direction]]
            unlocked = False
            if next_room.locked:
                if next_room.key in self.game_state.inventory:
                    next_room.locked = False
                    unlocked = True
                else:
                    self.clearGameScreen()
                    self.set_transient_message("The door is locked. You need a key.", duration=1.0)
                    return

            self.game_state.current_room = next_room
            room_text = "\n" + next_room.describe(self.game_state.inventory)
            self.clearGameScreen()
            if unlocked:
                self.renderer.print("You unlock the door.")
            self.renderer.print(f"You move {direction}.")
            self.renderer.print(room_text)
            self._last_room_text = room_text

            drop_roll, _ = self.drop.attempt_drop(chance=self.drop.drop_chance)
            if drop_roll:
                import random
                possible_items = ["metal", "plastic", "stick", "cloth", "flint", "wire cutters", "torch recipe Set Series 1", "wire cutters recipe Set Series 1"]
                item = random.choice(possible_items)
                if item not in self.game_state.inventory:
                    self.game_state.inventory.append(item)
                    self.renderer.print(f"You found {item}!")
                    self.trophies.add_trophy(self.auth.username, self.auth.token, "307966")

            self.sync_inventory(source="state")
            self.inv.save_inventory()  # Save inventory after moving to a new room
        else:
            self.clearGameScreen()
            self.set_transient_message("You can't go that way.", duration=1.0)

    def fight_enemy(self, enemy):
        while enemy.health > 0 and self.game_state.health > 0:
            self.renderer.print(f"The {enemy.name} attacks you!")
            self.game_state.health -= enemy.attack_power
            self.renderer.print(f"You have {self.game_state.health} health left.")
            if self.game_state.health <= 0:
                self.renderer.print("You died. Game over.")
                self.game_state.is_running = False
                return
            
            self.renderer.print(f"You attack the {enemy.name}.")
            enemy.health -= self.game_state.attack_power
            self.renderer.print(f"The {enemy.name} has {enemy.health} health left.")
            if enemy.health <= 0:
                self.renderer.print(f"You defeated the {enemy.name}!")
                self.game_state.current_room.enemy = None

    def handle_take(self, item):
        if item in self.game_state.current_room.items and item not in self.inv.list_items():
            self.game_state.inventory.append(item)
            self.game_state.current_room.items.remove(item)
            self.renderer.print(f"You take the {item}.")
            self.inv.add_item(item)
            self.sync_inventory(source="state")
            self.inv.save_inventory()  # Save inventory after taking an item
        else:
            self.renderer.print(f"There is no {item} here.")

    def handle_take_all(self):
        room = self.game_state.current_room
        if not room.items:
            self.renderer.print("There are no items here.")
            return

        collected_items = list(room.items)
        room.items.clear()
        for item in collected_items:
            if item not in self.game_state.inventory:
                self.game_state.inventory.append(item)

        self.sync_inventory(source="state")
        self.inv.save_inventory()
        self.renderer.print(f"You collect: {', '.join(collected_items)}.")

    def handle_drop(self, item):
        if item in self.game_state.inventory:
            self.inv.remove_item(item)
            self.game_state.inventory.remove(item)
            self.game_state.current_room.items.append(item)
            self.renderer.print(f"You drop the {item}.")
            self.sync_inventory(source="state")
            self.inv.save_inventory()  # Save inventory after dropping an item
        else:
            self.renderer.print(f"You don't have {item}.")

    def handle_inventory(self):
        if self.inv.list_items():
            self.renderer.print(f"You are carrying: {', '.join(self.inv.list_items())}")
        else:
            self.renderer.print("Your inventory is empty.")

    def clearGameScreen(self):
        subprocess.call('cls' if os.name == "nt" else "clear", shell=True)
        self.renderer.clear()

import select
import subprocess
import time
import sys
import requests
import os

import TextGameEngineSDK.sourceaudio as sourceaudio
from .inventory import Inventory
from . import GJ_Game
from .game_state import GameState
from .enemy import Enemy
from .room import Room
from .trophies import Trophies
from .item_drop import DropSystem
from.authentication import Auth
from .gj_api import Api
from .puzzle import *
from .bug_reporter import BugReporter

try:
    import msvcrt
except ImportError:
    msvcrt = None


audio = sourceaudio.Audio()



def play_intro():
    subprocess.call('cls' if os.name == "nt" else "clear", shell=True)
    print("Game created by [Your Name]")
    if audio.load_music("audio/intro.wav"):
        audio.play_music(loop=True)
    else:
        print("Could not load music!")
    time.sleep(3)
    audio.stop_music()

class TextGameEngine:
    def __init__(self, webhook_url, GAME_ID="1087229", GAME_SECRET="9c28a0641edb8972318db701368aa384"):
        self.game_state = GameState()
        self.world = {}

        self.inv = Inventory()

        self.drop = DropSystem()

        self.bug_reporter = BugReporter(webhook_url=webhook_url)

        self.api = Api(GAME_ID=GAME_ID, GAME_SECRET=GAME_SECRET)
        self.auth = Auth(api=self.api)
        self.trophies = Trophies(api=self.api)

        from ..renderer import Renderer
        self.renderer = Renderer()

        self.replay_commands = []
        self._command_buffer = ""
        self._last_room_text = None
        self._transient_message_until = 0.0
        self._last_realtime_move = 0.0

        from ..videoExporter import VideoExporter

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

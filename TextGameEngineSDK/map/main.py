import os
import subprocess
import time

from ..engine import *

# print("Commands: ")
# print("1. quit (Quits the game)")
# print("2. go <direction> (Goes to the desired direction)")
# print("3. take <item> (Picks up an item)")
# print("4. drop <item> (Drops an item)")
# print("5. inventory (Displays inventory)")
# print("6. save (Saves the game)")
# print("7. load (Loads the game)")
# print("8. export (Exports the current session as a .mp4 replay)")

def inventory(engine):
    print("Inventory: ")
    for item in engine.inv.list_items():
        print(f"- {item}")


def inspectItem(item, engine):
    if item in engine.inv.list_items():
        if item == "torch":
            print(f"You inspect the {item}. It can light up dark places.")
        elif item == "screwdriver":
            print(f"You inspect the {item}. It can be used in crafting.")
    else:
        print(f"You don't have a {item} in your inventory.")

world_data = {
    "start": {
        "description": "You are in a dark room. At north you see stairs going up",
        "connections": {"north": "main"},
        "items": ["torch"]
    },
    "main": {
        "description": "You entered a long corridor. You see two doors on both west and east. \nThere are also stairs going down at south. You can also go north.",
        "connections": {"south": "start", "north": "circus", "east": "workshop", "west": "storage"},
        "locked": False
    },
    "circus": {
        "description": "You entered a room full of balloons, with a creepy clown drawing on a wall... You feel uneasy. \nThe only exits are south and north",
        "connections": {"south": "main", "north": "master room"},
        "locked": False
    },
    "workshop": {
        "description": "You enter the workshop. Half-finished animatronic clown heads stare at you from shelves. You see exits on west and south.",
        "connections": {"west": "main", "south": "office"},
        "items": ["screwdriver", "wire cutters recipe Set Series 1"],
        "locked": False
    },
    "office": {
        "description": "You entered the manager's office. You can go north and east.",
        "connections": {"north": "workshop", "east": "safe room"},
        "locked": False
    },
    "storage": {
        "description": "You enter the storage room. You see a lot of boxes. Exits are east and south.",
        "connections": {"east": "main", "south": "boiler room"},
        "items": ["safe_room_key"],
        "locked": False
    },
    "boiler room": {
        "description": "You entered the boiler room. It's hot in here. You can only go north.",
        "connections": {"north": "storage"},
        "items": ["master_key"],
        "locked": True,
        "key": "boiler_key"
    },
    "safe room": {
        "description": "You see a lot of dolls inside the safe room. You can only go west",
        "connections": {"west": "storage"},
        "items": ["boiler_key"],
        "locked": True,
        "key": "safe_room_key"
    },
    "master room": {
        "description": "You enter the master room, where you see an animatronic clown! You can exit by going east",
        "connections": {"east": "exit"},
        "enemy": {"name": "Jack the clown", "health": 46, "attack_power": 12},
        "locked": True,
        "key": "master_key",
        "end": True
    },


}


def main():
    play_intro()
    Engine = TextGameEngine(webhook_url="https://discord.com/api/webhooks/1534934575976022169/awjCN65slNIILo1EXwOFo7yDvabSL-3HO4Nr8bDPmg3kVhLDBR9w1y8_Bmgxe30aSoa5", GAME_ID="1087229", GAME_SECRET="9c28a0641edb8972318db701368aa384")
    Engine.inv.load_inventory()  # Load inventory before displaying
    Engine.sync_inventory(source="inv")
    if os.path.exists("credentials.txt"):
        with open("credentials.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                username = lines[0].strip()
                token = lines[1].strip()
                if Engine.auth.login(username, token=token, api=Engine.api):
                    print("Login successful!")
                else:
                    print("Login failed. Please check your credentials.")
    while True:
        Engine.clearGameScreen()
        pygame.mixer.music.load("audio/menu.wav")
        pygame.mixer.music.play(-1)
        print("MAP v1.14")
        print("1. Start Game")
        print("2. Inventory")
        print("3. Crafting")
        print("4. Exit")
        print("5. Report a bug")
        print("6. Replays")
        if Engine.auth.logged_in:
            print("7. Log Out")
        else:
            print("7. Log In")
        input_choice = input("> ")
        if input_choice == "1":
            Engine.clearGameScreen()
            input("Use WASD to move. Press any key to continue...")
            Engine.load_world(world_data)
            Engine.main_loop()
        elif input_choice == "2":
            Engine.inv.load_inventory()  # Load inventory before displaying
            Engine.sync_inventory(source="inv")
            Engine.clearGameScreen()
            inventory(Engine)
            print("1. Inspect Item")
            print("2. Back")
            input_choice = input("> ")
            if input_choice == "1":
                item = input("Enter the item name to inspect: ")
                inspectItem(item, Engine)
                time.sleep(2)
            elif input_choice == "2":
                continue
        elif input_choice == "3":
            Engine.clearGameScreen()
            print("Choose a set you want to craft:")
            print("1. Torch")
            print("2. Wire Cutters")
            input_choice = input("> ")
            if input_choice == "1":
                Engine.inv.load_inventory()  # Load inventory before displaying
                Engine.sync_inventory(source="inv")
                if Engine.inv.has_item("torch recipe Set Series 1"):
                    print("Required parts:")
                    print("- Stick")
                    print("- Cloth")
                    print("- Flint")
                    if Engine.crafting.has_required_items("torch recipe Set Series 1"):
                        Engine.crafting.craft(Engine.inv.items, "torch")
                        Engine.trophies.add_trophy(Engine.auth.username, Engine.auth.token, "307967")
                else:
                    print("You don't own the recipe for a torch.")
                    time.sleep(1)
            elif input_choice == "2":
                Engine.inv.load_inventory()  # Load inventory before displaying
                Engine.sync_inventory(source="inv")
                if Engine.inv.has_item("wire cutters recipe Set Series 1"):
                    print("Required parts:")
                    print("- Metal")
                    print("- Plastic")
                    if Engine.crafting.has_required_items("wire cutters recipe Set Series 1"):
                        Engine.crafting.craft(Engine.inv.items, "wire cutters")
                        Engine.trophies.add_trophy(Engine.auth.username, Engine.auth.token, "307968")
                else:
                    print("You don't own the recipe for wire cutters.")
            else:
                print("Invalid choice. Please try again.")
            time.sleep(2)
        elif input_choice == "4":
            print("Thanks for playing!")
            sys.exit(0)
        elif input_choice == "5":
            choice = input("Tell us what you did before the bug, and what happened after: ")

            Engine.bug_reporter.send_bug_report(choice)
            time.sleep(2)

        elif input_choice == "6":
            if not os.name == "nt":
                subprocess.Popen(['xdg-open', "replays"])
            else:
                print("Replays are saved in the \"replays\" directory.")

        elif input_choice == "7":
            if Engine.auth.logged_in:
                Engine.auth.logged_in = False
                Engine.auth.username = None
                Engine.auth.token = None
                print("Logged out successfully.")
                time.sleep(2)
                continue
            username = input("Enter your gamejolt username: ")
            token = input("Enter your gamejolt game token: ")

            if Engine.auth.login(username, token=token, api=Engine.api):
                continue
            else:
                print("Login failed. Please check your credentials.")
            time.sleep(2)
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

if __name__ == "__main__":
    main()
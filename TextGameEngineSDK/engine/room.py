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
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
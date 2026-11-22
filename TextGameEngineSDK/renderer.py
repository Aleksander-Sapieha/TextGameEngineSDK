
class Renderer:
    def __init__(self, max_lines=20):
        self.history = []
        self.max_lines = max_lines

    def print(self, text=""):
        if text:
            for line in text.splitlines():
                self.history.append(line)

            self.history = self.history[-self.max_lines:]

        self.refresh()

    def get_text(self):
        return "\n".join(self.history)

    def clear(self):
        self.history = []
        self.refresh()

    def refresh(self):
        # Desktop terminal backend for now
        print("\033[2J\033[H", end="")
        print(self.get_text())

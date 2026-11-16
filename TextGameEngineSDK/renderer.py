class Renderer:
    def __init__(self, max_lines=20):
        self.history = []
        self.max_lines = max_lines

    def print(self, text=""):
        print(text)
        if not text:
            return

        for line in text.splitlines():
            self.history.append(line)

        if len(self.history) > self.max_lines:
            self.history = self.history[-self.max_lines:]

    def get_text(self):
        return "\n".join(self.history)

    def clear(self):
        self.history = []
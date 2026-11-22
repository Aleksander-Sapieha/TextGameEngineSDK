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

def display(text):
    print(text)
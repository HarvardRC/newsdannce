from collections.abc import Callable
class Migration:
    up: Callable
    down: Callable
    name: str
    def __init__(self, name, up, down):
        self.name = name
        self.up = up
        self.down = down

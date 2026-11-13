import os
import random
import select
import shutil
import sys
import time
from collections import deque
from contextlib import contextmanager

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty

RESET = "\033[0m"
DIM = "\033[90m"
WHITE = "\033[97m"
BOLD = "\033[1m"
HEAD = f"{BOLD}{WHITE}% {RESET}"
BODY = f"{WHITE}# {RESET}"
FOOD = f"{BOLD}{WHITE}* {RESET}"
BG = (f"{DIM}▪ {RESET}", f"{DIM}▫ {RESET}")
DIRECTIONS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0),
              "up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def dimensions():
    while True:
        try:
            width = int(input("x (width): "))
            height = int(input("y (height): "))
        except ValueError:
            print("Enter whole numbers.")
            continue
        if width < 2 or height < 2:
            print("Both dimensions must be at least 2.")
        else:
            return width, height


def zen_cycle(width, height):

    if width % 2:
        if height % 2 == 0:
            return [(y, x) for x, y in zen_cycle(height, width)]
        width -= 1

    path = [(0, y) for y in range(height)]
    for x in range(1, width):
        ys = range(height - 1, 0, -1) if x % 2 else range(1, height)
        path.extend((x, y) for y in ys)
    path.extend((x, 0) for x in range(width - 1, 0, -1))
    return path


def spawn_food(width, height, snake, allowed=None):
    occupied = set(snake)
    candidates = allowed if allowed is not None else (
        (x, y) for y in range(height) for x in range(width)
    )
    free = [point for point in candidates if point not in occupied]
    return random.choice(free) if free else None


def display(width, height, snake, food, score, zen):
    head = snake[0]
    body = set(list(snake)[1:])
    output = ["\033[H", f"{'ZEN' if zen else 'PLAY'}  |  score: {score}  |  Q: quit\n"]
    for y in range(height):
        row = []
        for x in range(width):
            point = (x, y)
            if point == head:
                row.append(HEAD)
            elif point in body:
                row.append(BODY)
            elif point == food:
                row.append(FOOD)
            else:
                row.append(BG[(x + y) % 2])
        output.append("".join(row) + "\n")
    output.append("\033[J")
    sys.stdout.write("".join(output))
    sys.stdout.flush()


@contextmanager
def raw_keyboard():
    if os.name != "nt" and sys.stdin.isatty():
        fd = sys.stdin.fileno()
        previous = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, previous)
    else:
        yield


def get_key():
    if os.name == "nt":
        key = None
        while msvcrt.kbhit():
            char = msvcrt.getwch()
            if char in ("\x00", "\xe0"):
                code = msvcrt.getwch()
                key = {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code, key)
            else:
                key = char.lower()
        return key
    if not sys.stdin.isatty():
        return None
    fd = sys.stdin.fileno()
    if select.select([fd], [], [], 0)[0]:
        data = os.read(fd, 64).decode(errors="ignore")
        arrows = {"\x1b[A": "up", "\x1b[B": "down", "\x1b[D": "left", "\x1b[C": "right"}
        for seq, name in arrows.items():
            if seq in data:
                return name
        for ch in reversed(data):
            if ch.lower() in "wasdq":
                return ch.lower()
    return None


def run(width, height, zen):
    if zen:
        path = zen_cycle(width, height)
        snake = deque([path[0]])
        next_index = 1
        food = spawn_food(width, height, snake, path)
    else:
        snake = deque([(width // 2, height // 2)])
        direction = (1, 0)
        food = spawn_food(width, height, snake)

    score = 0
    won = False
    sys.stdout.write("\033[2J\033[?25l")
    sys.stdout.flush()
    try:
        with raw_keyboard():
            while True:
                display(width, height, snake, food, score, zen)
                time.sleep(0.085 if zen else 0.13)
                key = get_key()
                if key == "q":
                    break

                if zen:
                    target = path[next_index]
                    next_index = (next_index + 1) % len(path)
                else:
                    proposed = DIRECTIONS.get(key)
                    if proposed is not None and proposed != (-direction[0], -direction[1]):
                        direction = proposed
                    target = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                    if not (0 <= target[0] < width and 0 <= target[1] < height):
                        break

                growing = target == food
                blocked = list(snake) if growing else list(snake)[:-1]
                if target in blocked:
                    break

                snake.appendleft(target)
                if growing:
                    score += 1
                    allowed = path if zen else None
                    food = spawn_food(width, height, snake, allowed)
                    if food is None and not zen:
                        won = True
                        display(width, height, snake, food, score, zen)
                        break
                else:
                    snake.pop()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()

    if not zen:
        print("YOU WIN!" if won else f"Game over! Score: {score}")


def main():
    if os.name == "nt":
        os.system("")  
    print("SNAKE\n1) Play\n2) Zen mode\n")
    while True:
        choice = input("Choose [1/2]: ").strip().lower()
        if choice in ("1", "play", "p"):
            zen = False
            break
        if choice in ("2", "zen", "z", "zen mode"):
            zen = True
            break
        print("Type 1 or 2.")

    width, height = dimensions()
    columns, lines = shutil.get_terminal_size((80, 24))
    if width * 2 > columns or height + 2 > lines:
        print(f"Tip: enlarge your terminal to at least {width * 2} columns × {height + 2} lines.")
        input("Press Enter to start...")
    run(width, height, zen)


if __name__ == "__main__":
    main()

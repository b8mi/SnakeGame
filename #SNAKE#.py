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

DIRECTIONS = {
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}

MODES = {
    "1": "PLAY",
    "2": "ZEN",
    "3": "BORDERLESS"
}


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
            continue

        return width, height


def choose_mode():
    print("SNAKE")
    print("1) Play")
    print("2) Zen mode")
    print("3) Borderless mode")
    print()

    aliases = {
        "play": "1",
        "p": "1",
        "zen": "2",
        "z": "2",
        "zen mode": "2",
        "borderless": "3",
        "b": "3",
        "borderless mode": "3",
        "wrap": "3"
    }

    while True:
        choice = input("Choose [1/2/3]: ").strip().lower()
        choice = aliases.get(choice, choice)

        if choice in MODES:
            return MODES[choice]

        print("Type 1, 2 or 3.")


def zen_cycle(width, height):
    if width % 2:
        if height % 2 == 0:
            return [(y, x) for x, y in zen_cycle(height, width)]

        width -= 1

    path = [(0, y) for y in range(height)]

    for x in range(1, width):
        if x % 2:
            ys = range(height - 1, 0, -1)
        else:
            ys = range(1, height)

        path.extend((x, y) for y in ys)

    path.extend((x, 0) for x in range(width - 1, 0, -1))

    return path


def spawn_food(width, height, snake, allowed=None):
    occupied = set(snake)

    if allowed is None:
        candidates = ((x, y) for y in range(height) for x in range(width))
    else:
        candidates = allowed

    free = [point for point in candidates if point not in occupied]

    return random.choice(free) if free else None


def inside_board(point, width, height):
    x, y = point
    return 0 <= x < width and 0 <= y < height


def wrap_position(point, width, height):
    x, y = point
    return x % width, y % height


def next_position(head, direction, width, height, borderless):
    target = (head[0] + direction[0], head[1] + direction[1])

    if borderless:
        return wrap_position(target, width, height)

    if not inside_board(target, width, height):
        return None

    return target


def body_collision(snake, target, growing):
    occupied = set(snake)

    if not growing:
        occupied.discard(snake[-1])

    return target in occupied


def change_direction(direction, key, snake):
    proposed = DIRECTIONS.get(key)

    if proposed is None:
        return direction

    reverse = (-direction[0], -direction[1])

    if len(snake) > 1 and proposed == reverse:
        return direction

    return proposed


def display(width, height, snake, food, score, mode):
    head = snake[0]
    body = set(snake)
    body.discard(head)

    output = ["\033[H", f"{mode} | score: {score} | Q: quit\n"]

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

                arrows = {
                    "H": "up",
                    "P": "down",
                    "K": "left",
                    "M": "right"
                }

                key = arrows.get(code, key)

            else:
                char = char.lower()

                if char == "q":
                    return char

                if char in DIRECTIONS:
                    key = char

        return key

    if not sys.stdin.isatty():
        return None

    fd = sys.stdin.fileno()

    if select.select([fd], [], [], 0)[0]:
        data = os.read(fd, 64).decode(errors="ignore")

        arrows = {
            "\x1b[A": "up",
            "\x1b[B": "down",
            "\x1b[D": "left",
            "\x1b[C": "right"
        }

        if "q" in data.lower():
            return "q"

        key = None
        index = 0

        while index < len(data):
            sequence = data[index:index + 3]

            if sequence in arrows:
                key = arrows[sequence]
                index += 3
                continue

            char = data[index].lower()

            if char in DIRECTIONS:
                key = char

            index += 1

        return key

    return None


def run(width, height, mode):
    zen = mode == "ZEN"
    borderless = mode == "BORDERLESS"

    path = None
    next_index = 0
    direction = (1, 0)

    if zen:
        path = zen_cycle(width, height)
        snake = deque([path[0]])
        next_index = 1

    else:
        snake = deque([(width // 2, height // 2)])

    food = spawn_food(width, height, snake, path)

    score = 0
    won = False
    quit_game = False
    reason = ""

    sys.stdout.write("\033[2J\033[?25l")
    sys.stdout.flush()

    try:
        with raw_keyboard():
            while True:
                display(width, height, snake, food, score, mode)

                time.sleep(0.085 if zen else 0.13)

                key = get_key()

                if key == "q":
                    quit_game = True
                    break

                if zen:
                    target = path[next_index]
                    next_index = (next_index + 1) % len(path)

                else:
                    direction = change_direction(direction, key, snake)
                    target = next_position(snake[0], direction, width, height, borderless)

                    if target is None:
                        reason = "You hit a wall."
                        break

                growing = target == food

                if body_collision(snake, target, growing):
                    reason = "You hit your own body."
                    break

                snake.appendleft(target)

                if growing:
                    score += 1
                    food = spawn_food(width, height, snake, path)

                    if food is None and not zen:
                        won = True
                        display(width, height, snake, food, score, mode)
                        break

                else:
                    snake.pop()

    except KeyboardInterrupt:
        quit_game = True

    finally:
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()

    if won:
        print(f"YOU WIN! Score: {score}")

    elif quit_game:
        print(f"Game ended. Score: {score}")

    elif not zen:
        print(f"Game over! Score: {score}")

        if reason:
            print(reason)


def check_terminal(width, height):
    columns, lines = shutil.get_terminal_size((80, 24))
    required_columns = max(width * 2, 40)
    required_lines = height + 2

    if columns < required_columns or lines < required_lines:
        print(f"Tip: enlarge your terminal to at least {required_columns} columns × {required_lines} lines.")
        input("Press Enter to start...")


def main():
    if os.name == "nt":
        os.system("")

    mode = choose_mode()
    width, height = dimensions()

    check_terminal(width, height)

    if mode == "BORDERLESS":
        print("Walls are disabled.")
        print("Cross any edge to appear on the opposite side.")
        print("Body collisions still count.")
        input("Press Enter to start...")

    run(width, height, mode)


if __name__ == "__main__":
    main()

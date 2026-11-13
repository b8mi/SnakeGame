# ASCII Snake 🐍

A tiny terminal Snake game built with **Python**, no libraries to install.

* `%` = snake head
* `#` = snake body
* `\\\*` = food
* `▪` `▫` = dark checkerboard background
* Two terminal columns per tile for a square-looking grid.

## Play

```bash
python snake.py
```

Choose **Play** or **Zen mode**, then enter the board dimensions:

```text
SNAKE
1) Play
2) Zen mode

Choose \\\[1/2]: 1
x (width): 20
y (height): 12
```

**Play:** use **W A S D** or the **arrow keys** to move. Eat `\\\*`, grow, and avoid walls and your body. Press **Q** to quit.

**Zen mode:** watch the snake play itself. It follows a safe looping route and **never crashes**. On boards where both dimensions are odd, one column is reserved to guarantee a safe loop. The snake keeps moving even after filling its route.

## Requirements

* Python 3.8+
* Windows Terminal, PowerShell, macOS Terminal, or a Linux terminal
* No external packages

> Tip: use a monospace terminal, and make your window at least `2 × width` columns wide and `height + 2` lines tall.

## How Zen mode works

Zen mode uses a **Hamiltonian cycle** on an even-sized rectangular region: a closed path that visits every tile in that region once. The head always follows the cycle, and the body follows behind, so self-collisions cannot happen. This is a simple guaranteed-safe autopilot rather than a learning AI.

## GitHub topics

`python` · `snake-game` · `terminal-game` · `ascii-art` · `cli` · `autoplay` · `hamiltonian-cycle` · `zero-dependencies`




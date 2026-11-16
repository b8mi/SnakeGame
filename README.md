
# ASCII Snake 🐍

A terminal Snake game written in Python. No external libraries needed.

* `%` = head of snake
* `#` = snake body
* `*` = food
* `▪` `▫` = dark checkerboard background
* Two terminal columns per tile make the grid look square.

## Play

```bash
python snake.py
```

Select **Play** or **Zen mode**. Specify the size of the board:

```text
SNAKE
1) Play
2) Zen mode

Choose [1/2]: 1
x (width): 20
y (height): 12
```

**Play:** use **W A S D** or the **arrow keys** to move. Eat `*`, grow, and avoid walls and the snake's body. Hit **Q** to quit.

**Zen mode:** let the snake handle itself. The snake follows a safe looping pattern and makes sure it stays alive. On boards where both dimensions are odd, one column is kept for safety to guarantee a safe looping zone. The snake keeps moving even after filling its route.

## Requirements

* Python 3.8+
* Windows Terminal, PowerShell, macOS Terminal, or a Linux terminal
* No external packages

> **Tip:** Use a monospace terminal. Make your window at least `2 × width` columns wide and `height + 2` lines tall.

## Operating Zen mode

In Zen mode, a path exists around a rectangular area. It covers every location exactly once before returning to the start, called a **Hamiltonian cycle**. The snake's head, body, and tail follow that cycle, so the snake never collides with itself. Guaranteed-safe autopilot, not an AI. Very simple.

## GitHub topics

`python` · `snake-game` · `terminal-game` · `ascii-art` · `cli` · `autoplay` · `hamiltonian-cycle` · `zero-dependencies`

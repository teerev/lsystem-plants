# lsystem-plants

A Python command-line tool for generating plant-like images using
[L-systems](https://en.wikipedia.org/wiki/L-system) (Lindenmayer systems).
Define a grammar with an axiom and rewrite rules, pick an angle and step size,
and the tool expands the grammar, interprets it with turtle graphics, and
renders the result to a PNG file.

## Quick start

```bash
# Clone the repo
git clone <repo-url> && cd lsystem-plants

# (Optional) install Pillow for faster rendering – not required
pip install Pillow

# Generate a simple branching plant
python -m lsysviz \
  --axiom "F" \
  --rule "F=FF+[+F-F-F]-[-F+F+F]" \
  --iterations 4 \
  --angle 25.7 \
  --step 5 \
  --output plant.png
```

Open `plant.png` and you should see a branching plant structure.

## Requirements

- Python 3.10+
- **Optional:** [Pillow](https://pypi.org/project/Pillow/) (`pip install Pillow`).
  If Pillow is not installed a pure-Python PNG writer is used as a fallback, so
  there are zero required external dependencies.

## Usage

```
python -m lsysviz [OPTIONS]
```

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--axiom` | string | yes | — | Starting axiom string |
| `--rule` | string | yes | — | Rewrite rule `SYMBOL=REPLACEMENT` (repeatable) |
| `--iterations` | int | yes | — | Number of expansion iterations |
| `--angle` | float | yes | — | Turn angle in degrees |
| `--step` | float | yes | — | Forward step length in pixels |
| `--output` | path | yes | — | Output PNG file path |
| `--width` | int | no | 800 | Image width in pixels |
| `--height` | int | no | 600 | Image height in pixels |
| `--version` | flag | no | — | Print version and exit |

Rules are specified with `--rule SYMBOL=REPLACEMENT` and can be repeated to
define multiple rules:

```bash
python -m lsysviz \
  --axiom "X" \
  --rule "X=F+[[X]-X]-F[-FX]+X" \
  --rule "F=FF" \
  --iterations 5 \
  --angle 25 \
  --step 4 \
  --output fractal_plant.png
```

## Turtle commands

The expanded L-system string is interpreted using these turtle graphics
commands:

| Symbol | Action |
|--------|--------|
| `F` | Move forward by `step` and draw a line |
| `+` | Turn left (counter-clockwise) by `angle` degrees |
| `-` | Turn right (clockwise) by `angle` degrees |
| `[` | Push current position and heading onto a stack |
| `]` | Pop position and heading from the stack |
| *anything else* | Ignored (useful as placeholders in rules) |

## Example plants

Below are some classic L-system plant grammars you can try. All of them
produce interesting organic-looking structures.

### 1 — Fractal plant (Lindenmayer)

```bash
python -m lsysviz \
  --axiom "X" \
  --rule "X=F+[[X]-X]-F[-FX]+X" \
  --rule "F=FF" \
  --iterations 6 \
  --angle 25 \
  --step 2 \
  --output fractal_plant.png \
  --width 1200 --height 900
```

### 2 — Bushy weed

```bash
python -m lsysviz \
  --axiom "F" \
  --rule "F=FF+[+F-F-F]-[-F+F+F]" \
  --iterations 4 \
  --angle 25.7 \
  --step 5 \
  --output bushy_weed.png
```

### 3 — Stochastic-looking tree

```bash
python -m lsysviz \
  --axiom "X" \
  --rule "X=F[+X]F[-X]+X" \
  --rule "F=FF" \
  --iterations 6 \
  --angle 20 \
  --step 2 \
  --output tree.png \
  --width 1000 --height 800
```

### 4 — Sierpinski triangle

```bash
python -m lsysviz \
  --axiom "F-G-G" \
  --rule "F=F-G+F+G-F" \
  --rule "G=GG" \
  --iterations 6 \
  --angle 120 \
  --step 3 \
  --output sierpinski.png
```

### 5 — Dragon curve

```bash
python -m lsysviz \
  --axiom "FX" \
  --rule "X=X+YF+" \
  --rule "Y=-FX-Y" \
  --iterations 12 \
  --angle 90 \
  --step 4 \
  --output dragon.png \
  --width 1000 --height 1000
```

### 6 — Koch snowflake

```bash
python -m lsysviz \
  --axiom "F--F--F" \
  --rule "F=F+F--F+F" \
  --iterations 4 \
  --angle 60 \
  --step 3 \
  --output koch.png
```

## Python API

You can also use the package as a library:

```python
from lsysviz.types import Grammar
from lsysviz.expand import expand
from lsysviz.turtle import interpret
from lsysviz.render import render_to_png

# 1. Define a grammar
grammar = Grammar(axiom="F", rules={"F": "FF+[+F-F-F]-[-F+F+F]"})

# 2. Expand for N iterations
lstring = expand(grammar, iterations=4)

# 3. Interpret with turtle graphics
segments = interpret(lstring, angle_deg=25.7, step_length=5.0)

# 4. Render to PNG
render_to_png(segments, width=800, height=600, output_path="plant.png")
```

### Key types

- **`Grammar(axiom, rules)`** — a named tuple holding the start string and a
  `dict[str, str]` mapping each symbol to its replacement.
- **`Segment(x0, y0, x1, y1)`** — a named tuple representing a single line
  segment produced by the turtle.

## Running the tests

```bash
# With pytest
python -m pytest -q

# Or use the included verify script
./scripts/verify.sh
```

## How it works

1. **Expand** — The axiom string is rewritten by simultaneously replacing every
   symbol that has a matching rule. This is repeated for the specified number of
   iterations, producing a (potentially very long) string.

2. **Interpret** — A turtle starts at the origin heading upward. It walks the
   expanded string character by character: `F` draws a line forward, `+`/`-`
   turn, and `[`/`]` save/restore the turtle state (enabling branching).

3. **Render** — All line segments are collected, auto-scaled to fit the canvas
   (with a 10 % margin), and rasterised into a PNG image (black lines on a
   white background).

## Tips

- **Increase iterations gradually.** The string length grows exponentially.
  Start with 3--4 iterations and go up from there.
- **Use `X` as a placeholder.** Symbols that aren't `F`, `+`, `-`, `[`, or `]`
  are ignored by the turtle but still participate in rewriting. This lets you
  create more complex grammars.
- **Tune the angle.** Small angle changes (e.g. 20 vs 25 degrees) can
  dramatically alter the look of a plant.

## License

See repository for license details.

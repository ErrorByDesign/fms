# scripts/lib/palette.py
# --- --- --- --- --- --- --- --- --- --- --- --
# -<< P A L E T T E >>- --- --- --- --- --- --- --
# --- --- --- --- --

# -< IMPORTS
import colorsys
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# -< IMPORTS: LOCAL
import scripts.config.colors as c

# -< IMPORTS: RICH
from rich.console import Console
from rich.style import Style
from rich.text import Text
console = Console()



# -<< COMP COLOR
# --- --- --- --- ---
def comp_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + 0.5) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    return f"#{round(r*255):02X}{round(g*255):02X}{round(b*255):02X}"

# -<< TEXT COLOR
# --- --- --- --- ---
def text_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#FFFFFF" if brightness < 128 else "#000000"

# -<< TINT COLOR
# --- --- --- --- ---
def tint_color(hex_color, factor):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = max(0, min(255, round(r * factor)))
    g = max(0, min(255, round(g * factor)))
    b = max(0, min(255, round(b * factor)))

    return f"#{r:02X}{g:02X}{b:02X}"



# =<< GET TERMUX BACKGROUND
# === === === === === === === ===
def get_termux_bg():
    path = Path.home() / ".termux" / "colors.properties"
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("background="):
            return line.split("=", 1)[1].strip()
    raise ValueError("background not found")

# =<< GET BASE COLOR
# === === === === === === === ===
def get_base_color():
    if len(sys.argv) > 1 and sys.argv[1] == "--base":
        if len(sys.argv) < 3:
            raise ValueError("Usage: python pallette.py --base #123456")
        return sys.argv[2]
    return get_termux_bg()



# -<< GLOBALS: COLORS
# --- --- --- --- ---
base            = get_base_color()
trmx            = base
trmx_dark1      = tint_color(trmx, 0.85)
trmx_dark2      = tint_color(trmx, 0.70)
trmx_lite1      = tint_color(trmx, 1.15)
trmx_lite2      = tint_color(trmx, 1.30)
trmx_comp       = comp_color(trmx)
trmx_comp_dark1 = tint_color(trmx_comp, 0.85)
trmx_comp_dark2 = tint_color(trmx_comp, 0.70)
trmx_comp_lite1 = tint_color(trmx_comp, 1.15)
trmx_comp_lite2 = tint_color(trmx_comp, 1.30)
trmx_text       = text_color(trmx)
trmx_txtd1      = text_color(trmx_dark1)
trmx_txtd2      = text_color(trmx_dark2)
trmx_txtl1      = text_color(trmx_lite1)
trmx_txtl2      = text_color(trmx_lite2)
trmx_comp_text  = text_color(trmx_comp)
trmx_comp_txtd1 = text_color(trmx_comp_dark1)
trmx_comp_txtd2 = text_color(trmx_comp_dark2)
trmx_comp_txtl1 = text_color(trmx_comp_lite1)
trmx_comp_txtl2 = text_color(trmx_comp_lite2)
n = "base" if len(sys.argv) > 1 and sys.argv[1] == "--base" else "trmx"



# =<< SHOW COLORS
# === === === === === === === ===
def show_colors():
    colors = {
        f"{n}": trmx,
        f"{n}_dark1": trmx_dark1,
        f"{n}_dark2": trmx_dark2,
        f"{n}_lite1": trmx_lite1,
        f"{n}_lite2": trmx_lite2,
        f"{n}_comp": trmx_comp,
        f"{n}_comp_dark1": trmx_comp_dark1,
        f"{n}_comp_dark2": trmx_comp_dark2,
        f"{n}_comp_lite1": trmx_comp_lite1,
        f"{n}_comp_lite2": trmx_comp_lite2,
        f"{n}_text": trmx_text,
        f"{n}_txtd1": trmx_txtd1,
        f"{n}_txtd2": trmx_txtd2,
        f"{n}_txtl1": trmx_txtl1,
        f"{n}_txtl2": trmx_txtl2,
        f"{n}_comp_text": trmx_comp_text,
        f"{n}_comp_txtd1": trmx_comp_txtd1,
        f"{n}_comp_txtd2": trmx_comp_txtd2,
        f"{n}_comp_txtl1": trmx_comp_txtl1,
        f"{n}_comp_txtl2": trmx_comp_txtl2,
    }
    for name, value in colors.items():
        print(f"{n} = {value}")

# =<< SHOW RICH COLORS
# === === === === === === === ===
def show_rich_colors():
    palette = [
        (f"{n}", trmx),
        (f"{n}_dark1", trmx_dark1),
        (f"{n}_dark2", trmx_dark2),
        (f"{n}_lite1", trmx_lite1),
        (f"{n}_lite2", trmx_lite2),
        (f"{n}_comp", trmx_comp),
        (f"{n}_comp_dark1", trmx_comp_dark1),
        (f"{n}_comp_dark2", trmx_comp_dark2),
        (f"{n}_comp_lite1", trmx_comp_lite1),
        (f"{n}_comp_lite2", trmx_comp_lite2),
        (f"{n}_text", trmx_text),
        (f"{n}_txtd1", trmx_txtd1),
        (f"{n}_txtd2", trmx_txtd2),
        (f"{n}_txtl1", trmx_txtl1),
        (f"{n}_txtl2", trmx_txtl2),
        (f"{n}_comp_text", trmx_comp_text),
        (f"{n}_comp_txtd1", trmx_comp_txtd1),
        (f"{n}_comp_txtd2", trmx_comp_txtd2),
        (f"{n}_comp_txtl1", trmx_comp_txtl1),
        f(f"{n}_comp_txtl2", trmx_comp_txtl2),
    ]
    for name, color in palette:
        console.print(Text(f"{name:<18} {color}", style=f"bold {color}"))

# =<< SHOW BLOCKS WITH ALIGNED TEXT
# === === === === === === === ===
def show_blocks_with_aligned_text():
    palette = [
        (f"{n}", trmx),
        (f"{n}_dark1", trmx_dark1),
        (f"{n}_dark2", trmx_dark2),
        (f"{n}_lite1", trmx_lite1),
        (f"{n}_lite2", trmx_lite2),
        (f"{n}_comp", trmx_comp),
        (f"{n}_comp_dark1", trmx_comp_dark1),
        (f"{n}_comp_dark2", trmx_comp_dark2),
        (f"{n}_comp_lite1", trmx_comp_lite1),
        (f"{n}_comp_lite2", trmx_comp_lite2),
        (f"{n}_text", trmx_text),
        (f"{n}_txtd1", trmx_txtd1),
        (f"{n}_txtd2", trmx_txtd2),
        (f"{n}_txtl1", trmx_txtl1),
        (f"{n}_txtl2", trmx_txtl2),
        (f"{n}_comp_text", trmx_comp_text),
        (f"{n}_comp_txtd1", trmx_comp_txtd1),
        (f"{n}_comp_txtd2", trmx_comp_txtd2),
        (f"{n}_comp_txtl1", trmx_comp_txtl1),
        (f"{n}_comp_txtl2", trmx_comp_txtl2),
    ]
    for name, color in palette:
        fg = text_color(color)
        line = f"{name:<15}{' ' * 22}{color}"
        console.print(line, style=Style(bgcolor=color, color=fg))



# === === === === === === === ===
# == =<< MAIN >>- --- --- --- ---
if __name__ == "__main__":
    # show_colors()
    # print()
    # show_rich_colors()
    show_blocks_with_aligned_text()
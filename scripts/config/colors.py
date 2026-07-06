# scripts/config/colors.py

from scripts.config.utils import comp_color, text_color, tint_color

# Termux
trmx            = "#161821"
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

# Semantics
back = "indian_red"
base = "grey70"
crmb = "light_slate_grey"
exit = "orange_red1"
info = "light_cyan1"
inst = "misty_rose1"
link = "cornflower_blue"
mute = "#808080"

# Semantics bold
ACTV = "bold light_sky_blue1"
BASE = "bold grey70"
DONE = "bold green"
DOS  = "bold #E3E6EC"
ERR  = "bold bright_red"
FAIL = "bold red"
PASS = "bold bright_green"
VAL  = "bold thistle1"
WARN = "bold bright_yellow"

# Banner families
BNNR1 = "bold plum3"
bnnr1 = "thistle1"
bnrd1 = "cadet_blue"
bnnr1x = "light_salmon1"

BNNR2 = "bold bright_cyan"
bnnr2 = "light_sky_blue1"
bnrd2 = "steel_blue"
bnnr2x = "plum3"

BNNR3 = "bold light_goldenrod2"
bnnr3 = "light_goldenrod1"
bnrd3 = "light_goldenrod3"
bnnr3x = "bright_cyan"

BNNR4 = "bold bright_green"
bnnr4 = "pale_green1"
bnrd4 = "dark_sea_green3"
bnnr4x = "plum3"

# Option ladder
opt1 = "bright_blue"
opt2 = "bright_cyan"
opt3 = "bright_green"
opt4 = "bright_yellow"
opt5 = "bright_magenta"
opt6 = "bright_red"

# Row Ladders: blue
b1 = "#EBF6FF"
b2 = "#D8EDFF"
b3 = "#C5E4FF"
b4 = "#B2DBFF"
b5 = "#9FD2FF"
b6 = "#8CC9FF"

# Row Ladders: cyan
c1 = "#EBFFFF"
c2 = "#D8FFFF"
c3 = "#C5FFFF"
c4 = "#B2FFFF"
c5 = "#9FFFFF"
c6 = "#8cffff"

# Row Ladders: green
g1 = "#E1FFFF"
g2 = "#D2FFFF"
g3 = "#C3FFFF"
g4 = "#B4FFF5"
g5 = "#A7FFE8"
g6 = "#84FFC5"

# Row Ladders: yellow
y1 = "#FFE4FF"
y2 = "#FFD2FF"
y3 = "#FFA1FF"
y4 = "#FDFFD0"
y5 = "#FBFFA1"
y6 = "#FBFF72"

# Row Ladders: orange
o1 = "#FFFFE7"
o2 = "#FFEAD0"
o3 = "#FFD4B8"
o4 = "#FFBFA1"
o5 = "#FFA98A"
o6 = "#FF9473"

# Row ladders: pink
p1 = "#FFEDFF"
p2 = "#FFE4FF"
p3 = "#FFDBFF"
p4 = "#FFD2FF"
p5 = "#FFC9FF"
p6 = "#FFA1FF"

# Row ladders: red
r1 = "#FFE5E2"
r2 = "#FFCBC6"
r3 = "#FFB1A9"
r4 = "#FF978D"
r5 = "#FF7D70"
r6 = "#FF6353"

# Extras
frg1 = "plum3"
frg2 = "cadet_blue"
frg3 = "aquamarine1"
frg4 = "steel_blue"
frg5 = "violet"
frg6 = "tan"
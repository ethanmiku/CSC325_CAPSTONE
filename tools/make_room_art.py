#!/usr/bin/env python3
"""Draw the door, window and furniture sprites the room generator looks up by name.

Run from the repository root:

    python3 tools/make_room_art.py

Writes PNGs under game/shared_assets/. Everything is hard-edged pixel art in the pack's
palette (no anti-aliasing, no partial alpha). Where the pack already has a close sprite,
the new one is derived from it (cropped, recoloured, mirrored or repainted) so palette,
outline weight and lighting stay consistent:

- Door frames: three states per door (_closed, _half, _open). The frame (jambs, lintel,
  threshold) is identical across a door's states and fully opaque, so it covers whatever
  doorway tile is underneath in any room. Only the leaf and the opening change.
- North doors keep the existing door_n_closed/door_n_open leaf art inside a frame that
  is now shared and opaque.
- French doors are repainted from game/maps/*/furniture/french_doors_*.png.
- Chairs, armchair, loveseats and the bookshelf are taken from existing sprites or from
  the artist's room previews.
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
SHARED = os.path.join(GAME, "shared_assets")
DOORS = os.path.join(SHARED, "architecture", "doors")
WINDOWS = os.path.join(SHARED, "architecture", "windows")
SEATING = os.path.join(SHARED, "furniture", "seating")
STORAGE = os.path.join(SHARED, "furniture", "storage")
MAPS = os.path.join(GAME, "maps")

# ---------------------------------------------------------------- palette (from the pack)
OUTLINE = "#1b1622"   # furniture outline
EDGE = "#2e1d1b"      # door-frame dark edge
DARK = "#36201c"      # door outline
WOOD_L = "#9e6c46"    # light wood (lit edge)
WOOD_M = "#784c30"    # mid wood
WOOD_D = "#4e3022"    # dark wood
WOOD_DD = "#422820"   # deeper wood
WOOD_H = "#603c2a"    # panel shade
AMBER = "#a06e2a"     # gold-brown trim
GOLD = "#e0b040"
PALE = "#fade80"
VOID = "#160e18"      # dark opening
VOID_DOT = "#3c2622"  # texture in the dark opening
FLOOR_A = "#6c4634"   # threshold boards (neutral wood, not a room's floor)
FLOOR_B = "#583628"
FLOOR_C = "#422820"
# night and snow
NIGHT = "#263460"
NIGHT_D = "#182042"
NIGHT_DD = "#0e1228"
SNOW = "#d6e4f6"
SNOW_W = "#f4f8ff"
SNOW_B = "#aac0e2"
SNOW_S = "#b0c4e4"
# warm lit glass
LIT = "#ffd678"
LIT_D = "#f0aa46"
# burgundy upholstery
BURG_D = "#581c2e"
BURG_M = "#702638"
BURG_L = "#96384c"
BURG_DD = "#3c1424"


def rgba(c):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (255,)
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)


class Canvas:
    def __init__(self, w, h, fill=None):
        self.im = Image.new("RGBA", (w, h), rgba(fill) if fill else (0, 0, 0, 0))
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), rgba(c) if c is not None else (0, 0, 0, 0))

    def rect(self, x0, y0, x1, y1, c):
        """Filled rectangle, inclusive corners."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def paste(self, im, x=0, y=0):
        self.im.alpha_composite(im.convert("RGBA"), (x, y))

    def grid(self, rows, key, x0=0, y0=0):
        """Paint a character grid; '.' (or a char missing from key) is left alone."""
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in key:
                    self.px(x0 + x, y0 + y, key[ch])

    def copy(self):
        c = Canvas(self.w, self.h)
        c.im = self.im.copy()
        return c


def load(path):
    return Image.open(path).convert("RGBA")


def recolour(im, mapping):
    """Swap exact colours. mapping: {old: new}."""
    m = {rgba(k)[:3]: rgba(v) for k, v in mapping.items()}
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] and p[:3] in m:
                px[x, y] = m[p[:3]]
    return out


def mirror(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def alpha_values(im):
    return set(im.getchannel("A").histogram()[i] and i for i in range(256)) - {0} | (
        {0} if im.getchannel("A").histogram()[0] else set())


def check_opaque(im, name):
    alphas = alpha_values(im)
    assert alphas == {255}, f"{name} must be fully opaque, has alpha {sorted(alphas)}"


def check_hard_alpha(im, name):
    alphas = alpha_values(im)
    assert alphas <= {0, 255}, f"{name} has semi-transparent pixels {sorted(alphas)}"


WRITTEN = []


def save(im, folder, name, opaque=False):
    if isinstance(im, Canvas):
        im = im.im
    check_hard_alpha(im, name)
    if opaque:
        check_opaque(im, name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    im.save(path)
    WRITTEN.append((os.path.relpath(path, ROOT), im.size))


# ================================================================ west / east doors (16x32)
# Side walls are a strip seen from above. The doorway frame: a gold-topped lintel ledge at
# the top (as the room tilesets draw it), a dark outer jamb on the wall's outside edge, a
# casing on the room side and a sill at the bottom. The leaf hangs from the top (north)
# jamb: closed it fills the opening; opening it swings into the room and foreshortens
# up against the lintel, uncovering the dark doorway. Light comes from the left, as in
# the pack; the east door is the mirror image (the tilesets mirror their east doorways too).

SIDE_OPEN = (3, 5, 12, 28)  # x0, y0, x1, y1 of the opening, inclusive


def side_frame():
    c = Canvas(16, 32)
    # lintel ledge (same bands as the tilesets' door_w_top)
    c.hline(0, 15, 0, GOLD)
    c.hline(0, 15, 1, WOOD_M)
    c.hline(0, 15, 2, WOOD_M)
    c.hline(0, 15, 3, WOOD_D)
    c.hline(0, 15, 4, EDGE)            # shadow under the ledge
    # outer jamb (wall's outside edge)
    c.vline(0, 5, 31, EDGE)
    c.vline(1, 5, 31, WOOD_M)
    c.vline(2, 5, 31, AMBER)
    # room-side casing
    c.vline(13, 5, 31, EDGE)
    c.vline(14, 5, 31, WOOD_M)
    c.vline(15, 5, 31, WOOD_D)
    c.px(14, 5, WOOD_L)
    # sill
    c.hline(3, 12, 29, AMBER)
    c.hline(3, 12, 30, WOOD_DD)
    c.hline(1, 14, 31, EDGE)
    return c


def side_void(c, x0, y0, x1, y1):
    c.rect(x0, y0, x1, y1, VOID)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x * 3 + y * 5) % 11 == 0 and x not in (x0, x1):
                c.px(x, y, VOID_DOT)


def plank_leaf(c, y0, y1, knob=True, battens=True):
    """Board door, boards running the length of the doorway, between rows y0..y1."""
    x0, _, x1, _ = SIDE_OPEN
    c.rect(x0, y0, x1, y1, WOOD_M)
    c.vline(x0, y0, y1, WOOD_L)          # lit edge (hinge side faces the light)
    for x in (6, 9):                     # board joints
        c.vline(x, y0, y1, WOOD_D)
    c.vline(x1, y0, y1, WOOD_D)          # shaded edge
    c.hline(x0, x1, y0, WOOD_L)          # top edge catches the light
    c.hline(x0, x1, y1, DARK)            # bottom edge
    h = y1 - y0
    if battens and h >= 10:
        for by in (y0 + 3, y1 - 4):
            c.hline(x0 + 1, x1 - 1, by, WOOD_L)
            c.hline(x0 + 1, x1 - 1, by + 1, WOOD_D)
    elif battens and h >= 4:
        c.hline(x0 + 1, x1 - 1, y0 + 2, WOOD_D)
    if knob:
        ky = y0 + max(2, h * 11 // 24)
        c.px(x1 - 1, ky, GOLD)
        c.px(x1, ky, PALE)
        c.px(x1 - 1, ky + 1, AMBER)
        if h >= 10:
            c.px(x1 - 1, ky + 3, VOID)       # keyhole


def door_w(state):
    c = side_frame()
    x0, y0, x1, y1 = SIDE_OPEN
    if state == "closed":
        plank_leaf(c, y0, y1)
    else:
        leaf_h = {"half": 11, "open": 5}[state]
        side_void(c, x0, y0, x1, y1)
        plank_leaf(c, y0, y0 + leaf_h - 1, battens=True)
        # the leaf's swung edge shades the opening just below it
        c.hline(x0, x1, y0 + leaf_h, EDGE)
    return c


# ================================================================ south doors (32x16)
# The south wall is a thin dark strip seen from above and behind. In the doorway the wall
# is cut back to two jamb posts with a sill on the room side. Like every other door, wood
# means shut and a dark opening means open: closed, a board door (the side doors' leaf,
# seen foreshortened) fills the gap; open, it stands edge-on against the left post.

S_X0, S_X1 = 4, 27      # opening columns
S_LEAF_Y0, S_LEAF_Y1 = 2, 13


def south_frame():
    c = Canvas(32, 16)
    for (a, b, cc, d) in ((0, 1, 2, 3), (31, 30, 29, 28)):
        light = a == 0
        c.vline(a, 0, 15, EDGE)
        c.vline(b, 0, 15, WOOD_L if light else WOOD_M)
        c.vline(cc, 0, 15, WOOD_M if light else WOOD_D)
        c.vline(d, 0, 15, WOOD_D if light else EDGE)
        # post tops
        for x in (b, cc):
            c.px(x, 0, GOLD)
        c.px(b, 1, AMBER)
        c.px(cc, 1, AMBER)
    # sill on the room side, and the dark doorway behind it
    side_void(c, S_X0, 2, S_X1, 14)
    c.hline(S_X0, S_X1, 0, AMBER)
    c.hline(S_X0, S_X1, 1, WOOD_DD)
    c.hline(0, 31, 15, EDGE)
    return c


def south_leaf_closed(c):
    y0, y1 = S_LEAF_Y0, S_LEAF_Y1
    c.rect(S_X0, y0, S_X1, y1, WOOD_M)
    c.hline(S_X0, S_X1, y0, WOOD_L)               # top edge catches the light
    c.hline(S_X0, S_X1, y1, DARK)
    for x in range(S_X0 + 5, S_X1, 6):            # board joints
        c.vline(x, y0 + 1, y1 - 1, WOOD_D)
    c.vline(S_X0, y0, y1, WOOD_L)
    c.vline(S_X1, y0, y1, WOOD_D)
    c.px(S_X1 - 3, y0 + 5, GOLD)                  # latch
    c.px(S_X1 - 2, y0 + 5, PALE)
    c.px(S_X1 - 3, y0 + 6, AMBER)


def south_leaf_open(c):
    """Leaf swung 90 degrees into the room, edge-on against the left post."""
    x = S_X0
    c.vline(x, 0, S_LEAF_Y1 - 3, WOOD_L)
    c.vline(x + 1, 0, S_LEAF_Y1 - 3, WOOD_M)
    c.vline(x + 2, 0, S_LEAF_Y1 - 3, WOOD_D)
    c.hline(x, x + 2, S_LEAF_Y1 - 2, DARK)
    c.px(x + 1, 4, GOLD)                          # latch


def south_leaf_half(c):
    """Leaf half swung: the hinge-side half of the board still covers the doorway."""
    y0, y1 = S_LEAF_Y0, S_LEAF_Y1 - 1
    x1 = S_X0 + 11
    c.rect(S_X0, y0, x1, y1, WOOD_M)
    c.hline(S_X0, x1, y0, WOOD_L)
    c.hline(S_X0, x1, y1, DARK)
    c.vline(S_X0, y0, y1, WOOD_L)
    c.vline(S_X0 + 5, y0 + 1, y1 - 1, WOOD_D)
    c.vline(x1, y0, y1, WOOD_D)
    c.vline(x1 + 1, y0 + 1, y1, EDGE)             # shadow on the opening
    c.px(x1 - 2, y0 + 5, GOLD)


def door_s(state):
    c = south_frame()
    if state == "closed":
        south_leaf_closed(c)
    elif state == "half":
        south_leaf_half(c)
    else:
        south_leaf_open(c)
    return c


# ================================================================ north doors (32x32)
# Keep the existing leaf art; give both states one shared, opaque frame (a casing cap now
# fills the rows that used to show the wall behind it).

def north_frame():
    c = Canvas(32, 32)
    # casing cap over the lintel
    c.hline(0, 31, 0, DARK)
    c.hline(0, 31, 1, WOOD_M)
    c.hline(0, 31, 2, WOOD_D)
    c.px(1, 1, WOOD_L)
    # lintel (from door_n_closed)
    c.hline(1, 30, 3, AMBER)
    c.hline(3, 28, 4, GOLD)
    c.hline(3, 28, 5, PALE)
    c.hline(3, 28, 6, WOOD_D)
    for y in range(3, 32):
        c.px(0, y, DARK)
        c.px(31, y, DARK)
        if y > 3:
            c.px(1, y, WOOD_L)
            c.px(30, y, WOOD_D)
        c.px(2, y, WOOD_M)
        c.px(29, y, WOOD_M)
    c.px(1, 3, WOOD_L)
    c.px(30, 3, WOOD_D)
    c.px(2, 3, WOOD_M)
    c.px(29, 3, WOOD_M)
    # sill
    c.hline(3, 28, 31, EDGE)
    return c


N_OPEN = (3, 7, 28, 30)


def door_n(state, src_closed, src_open):
    c = north_frame()
    x0, y0, x1, y1 = N_OPEN
    if state == "closed":
        c.paste(src_closed.crop((x0, y0, x1 + 1, y1 + 1)), x0, y0)
    elif state == "open":
        c.paste(src_open.crop((x0, y0, x1 + 1, y1 + 1)), x0, y0)
    else:
        # dark doorway from the open frame, leaf swung halfway: narrower than closed,
        # wider than open's edge-on strip, panels foreshortened
        c.paste(src_open.crop((x0, y0, x1 + 1, y1 + 1)), x0, y0)
        lx0, lx1 = 4, 15
        c.rect(x0, y0, lx1 + 1, 27, VOID)
        c.rect(lx0, y0, lx1, 27, WOOD_M)
        c.vline(lx0, y0, 27, WOOD_L)
        c.vline(lx1, y0, 27, WOOD_D)
        c.vline(lx1 + 1, y0, 27, EDGE)
        c.hline(lx0, lx1, 27, DARK)
        for (py0, py1) in ((10, 16), (20, 26)):
            c.rect(lx0 + 2, py0, lx1 - 2, py1, WOOD_D)
            c.rect(lx0 + 3, py0 + 1, lx1 - 3, py1 - 1, WOOD_H)
            c.hline(lx0 + 2, lx1 - 2, py1, DARK)
        c.px(lx1 - 1, 18, GOLD)
        c.px(lx1 - 1, 19, AMBER)
        c.vline(x0, y0, 27, WOOD_L)
    return c


# ================================================================ French doors (16x32)
# Glazed double doors in a side wall. The two leaves meet across the middle of the
# doorway (hinged at the north and south jambs); opening, each folds back against its
# jamb and the gap between them shows the backyard (from inside) or the lit room (from
# the yard).

FR_OPEN = (3, 5, 12, 28)


def french_frame(outside):
    c = side_frame()
    if outside:
        # the brick wall's door casing is the same wood; give the sill a dusting of snow
        c.hline(3, 12, 29, SNOW_B)
        c.hline(3, 12, 30, WOOD_M)
    return c


def night_view(c, x0, y0, x1, y1):
    """Looking down through the doorway at the snowy yard at night."""
    c.rect(x0, y0, x1, y1, SNOW_B)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = (x * 5 + y * 3) % 13
            if k == 0:
                c.px(x, y, "#8ca4ce")
            elif k == 7:
                c.px(x, y, SNOW)
    # footprints leading out
    for y in range(y0 + 4, y1 - 1, 5):
        c.px(x0 + 4, y, "#7892c0")
        c.px(x0 + 6, y + 2, "#7892c0")
    c.hline(x0, x1, y0, "#7892c0")                    # shadow under the lintel
    c.vline(x1, y0, y1, "#8ca4ce")


def room_view(c, x0, y0, x1, y1):
    """Looking through the doorway into the Dining Room: a dark opening, like the other
    doors, with the room's lamp light spilling over the sill."""
    side_void(c, x0, y0, x1, y1)
    c.hline(x0, x1, y1 - 2, "#965432")
    c.hline(x0, x1, y1 - 1, LIT_D)
    c.hline(x0, x1, y1, LIT)


def glazed_leaf(c, y0, y1, outside, hinge_top):
    """One glazed leaf between rows y0..y1, panes foreshortened with its height."""
    x0, _, x1, _ = FR_OPEN
    glass, glint, deep = (LIT, LIT_D, LIT_D) if outside else (NIGHT, SNOW_W, NIGHT_D)
    c.rect(x0, y0, x1, y1, WOOD_M)
    c.vline(x0, y0, y1, WOOD_L)
    c.vline(x1, y0, y1, WOOD_D)
    h = y1 - y0 + 1
    if h >= 5:
        gy0, gy1 = y0 + 1, y1 - 1
        c.rect(x0 + 2, gy0, x1 - 2, gy1, glass)
        c.vline(8, gy0, gy1, WOOD_D)                 # glazing bar
        if h >= 9:
            mid = (gy0 + gy1) // 2
            c.hline(x0 + 2, x1 - 2, mid, WOOD_D)
        if not outside:
            # snow seen through the lower panes of a closed leaf
            pass
        c.px(x0 + 3, gy0 + 1, glint)
        if h >= 9:
            c.px(x1 - 3, gy1 - 1, deep if outside else SNOW)
    # meeting edge (the leaf's free end) is darker; brass handle there
    free_y = y1 if hinge_top else y0
    c.hline(x0, x1, free_y, DARK)
    hy = y1 - 1 if hinge_top else y0 + 1
    if h >= 4:
        c.px(x1 - 2, hy, GOLD)
        c.px(x1 - 1, hy, PALE)


def french(state, outside):
    c = french_frame(outside)
    x0, y0, x1, y1 = FR_OPEN
    view = room_view if outside else night_view
    if state == "closed":
        top_h = (y1 - y0 + 1) // 2
        glazed_leaf(c, y0, y0 + top_h - 1, outside, hinge_top=True)
        glazed_leaf(c, y0 + top_h, y1, outside, hinge_top=False)
        if not outside:
            # snow outside, seen low through the bottom leaf's panes
            gy1 = y1 - 1
            c.rect(x0 + 2, gy1 - 3, 7, gy1, SNOW)
            c.rect(9, gy1 - 3, x1 - 2, gy1, SNOW)
            c.hline(x0 + 2, x1 - 2, gy1 - 4, SNOW_B)
            c.vline(8, gy1 - 4, gy1, WOOD_D)
        return c
    leaf_h = {"half": 7, "open": 4}[state]
    view(c, x0, y0, x1, y1)
    glazed_leaf(c, y0, y0 + leaf_h - 1, outside, hinge_top=True)
    glazed_leaf(c, y1 - leaf_h + 1, y1, outside, hinge_top=False)
    c.hline(x0, x1, y0 + leaf_h, EDGE)
    return c


# ================================================================ kitchen back door, outside
# A plain, solid board door in the manor's brick wall, seen from the backyard.

def door_ext_w(state):
    c = side_frame()
    c.hline(3, 12, 29, SNOW_B)            # snow on the step
    c.hline(3, 12, 30, WOOD_M)
    x0, y0, x1, y1 = SIDE_OPEN
    if state == "closed":
        plank_leaf(c, y0, y1)
        # iron strap hinges on the board door
        for hy in (y0 + 3, y1 - 4):
            c.hline(x0 + 1, x0 + 6, hy, "#3a3a4a")
            c.px(x0 + 1, hy + 1, "#3a3a4a")
        return c
    leaf_h = {"half": 11, "open": 5}[state]
    side_void(c, x0, y0, x1, y1)
    # kitchen light spilling from inside, low on the floor
    c.rect(x0 + 1, y1 - 3, x1 - 1, y1, "#4e3022")
    plank_leaf(c, y0, y0 + leaf_h - 1)
    c.hline(x0, x1, y0 + leaf_h, EDGE)
    return c



# ================================================================ dining chairs (16x32)
# Transcribed from the Dining Room preview (the artist drew the north/east/west chairs
# there), with the chandelier-glow dither removed so they sit in the same palette as
# chair_dining_s.png. The west-facing chair is the mirror of the east-facing one, as in
# the preview.

CHAIR_KEY = {
    "C": OUTLINE, "D": PALE, "E": WOOD_L, "F": WOOD_M, "G": WOOD_D, "H": DARK,
    "I": BURG_L, "B": BURG_M, "A": BURG_D, "g": WOOD_H,
}

CHAIR_E = [
    "................",
    "...CCC..........",
    "..CDDDC.........",
    "..CEFGC.........",
    "..CEFGCC........",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGC.......",
    "..CEFGHGCCCCCC..",
    "..CEFIIIIIIIIIC.",
    "..CEFBBBBBBBBBC.",
    "..CEFBBBBBBBBBC.",
    "..CEFBBBBBBBBBC.",
    "..CEFAAAAAAAAAC.",
    "..CEFFFFFFFFFFC.",
    "..CEFGGGGGGGGGC.",
    "..CEEGCCCCCCEGC.",
    "...CEGC....CEGC.",
    "...CEGC....CEGC.",
    "...CEGC....CEGC.",
    "...CEGC....CEGC.",
    "...CEGC....CEGC.",
    "...CEGC....CEGC.",
    "...CHHC....CHHC.",
    "....CC......CC..",
    "................",
]

CHAIR_N = [
    "................",
    "...CCCCCCCCCC...",
    "..CEDDDDDDDDGC..",
    "..CEFFFFFFFFGC..",
    "..CEFFFFFFFFGC..",
    "..CEFHHHHHEFGC..",
    "..CEFHGGGGEFGC..",
    "..CEFHgGgGEFGC..",
    "..CEFHGGGGEFGC..",
    "..CEFHGgGgEFGC..",
    "..CEFHGGGGEFGC..",
    "..CEFHgGgGEFGC..",
    "..CEFHGGGGEFGC..",
    "..CEFHGgGgEFGC..",
    "..CEFHGGGGEFGC..",
    "..CEFHgGgGEFGC..",
    "..CEFEEEEEEFGC..",
    "..CEFFFFFFFFGC..",
    "..CEFFFFFFFFGC..",
    "..CEFFFFFFFFGC..",
    "..CGGGGGGGGGGC..",
    "..CGGGGGGGGGGC..",
    "..CGGGGGGGGGGC..",
    "..CEGCCCCCCEGC..",
    "..CEGC....CEGC..",
    "..CEGC....CEGC..",
    "..CEGC....CEGC..",
    "..CEGC....CEGC..",
    "..CEGC....CEGC..",
    "..CHHC....CHHC..",
    "...CC......CC...",
    "................",
]


def chair(rows):
    c = Canvas(16, 32)
    c.grid(rows, CHAIR_KEY)
    return c


# ================================================================ library armchair (32x32)
# armchair_clara_s.png recoloured from lilac to the burgundy the library preview shows
# (same colours as armchair_e/armchair_w).

def armchair_s():
    src = load(os.path.join(SEATING, "armchair_clara_s.png"))
    return recolour(src, {"#744a8a": BURG_D, "#be94cc": BURG_L, "#9668a8": BURG_M})


# ================================================================ loveseats (32x32)
# The old loveseats were three equal bars (arm, cushion, arm) and read as a chest of
# drawers. These are cut from sofa_w.png, the pack's west-facing sofa: the same backrest
# along the east side and rolled arms top and bottom, with the arms trimmed and one long
# seat cushion between them.

LOVESEAT_ROWS = ([0, 1, 2, 3, 4, 5, 6, 7, 8, 10]         # backrest top, north arm
                 + list(range(11, 20)) + [34, 35, 36]    # seat cushion
                 + [37, 38, 39, 40, 41, 42, 44]          # south arm
                 + [45, 46, 47])                         # base


def loveseat_burgundy():
    src = load(os.path.join(SEATING, "sofa_w.png"))
    out = Image.new("RGBA", (32, 32))
    for y, sy in enumerate(LOVESEAT_ROWS):
        out.paste(src.crop((0, sy, 32, sy + 1)), (0, y))
    return out


def loveseat_clara():
    return recolour(loveseat_burgundy(), {
        BURG_D: "#744a8a", BURG_M: "#9668a8", BURG_L: "#be94cc", BURG_DD: "#543268"})


# ================================================================ bookshelf with a gap (32x32)
# bookshelf_tall.png with several books missing from the third shelf (a clue) and one
# left leaning into the gap, as in the library preview.

def bookshelf_gap():
    src = load(os.path.join(STORAGE, "bookshelf_tall.png"))
    c = Canvas(32, 32)
    c.paste(src)
    back = "#20161a"
    c.rect(16, 18, 25, 23, back)
    # leaning book, resting against the books on the right
    teal_l, teal_d = "#568c98", "#326874"
    for i, y in enumerate(range(19, 24)):
        x = 24 - i
        c.px(x, y, teal_l)
        c.px(x + 1, y, teal_d)
    c.px(25, 19, GOLD)
    c.px(20, 23, teal_d)
    # a shadow line where the missing books stood
    c.hline(16, 21, 23, "#36201c")
    return c


# ================================================================ south-wall window (32x16)
# A window in the bottom wall, seen from inside and above: the curtain rod and gathered
# curtain tops on the room side, the window frame's top edge and sill, and cold night
# light on the glass between them. Burgundy curtains for Edmund's Bedroom.

def window_s_curtains_burgundy():
    c = Canvas(32, 16)
    # frame top edge and sill run the full width
    c.hline(0, 31, 1, OUTLINE)
    c.hline(0, 31, 2, GOLD)
    c.hline(0, 31, 3, AMBER)
    # glass: night sky, snow light low in the panes
    c.rect(1, 4, 30, 10, NIGHT)
    c.rect(1, 9, 30, 10, SNOW)
    c.hline(1, 30, 8, SNOW_B)
    for (x, y) in ((5, 5), (12, 6), (19, 5), (26, 6), (9, 7)):
        c.px(x, y, SNOW_W)
    for x in (0, 15, 16, 31):
        c.vline(x, 4, 10, WOOD_M)
    c.vline(16, 4, 10, WOOD_D)
    c.vline(31, 4, 10, WOOD_D)
    c.hline(1, 30, 7, WOOD_M)                   # glazing bar
    c.hline(0, 31, 11, WOOD_L)                  # sill
    c.hline(0, 31, 12, WOOD_M)
    c.hline(0, 31, 13, OUTLINE)
    # curtains: tied back to the sides, gathered folds
    folds = [BURG_L, BURG_M, BURG_D, BURG_M]
    for x0, x1 in ((0, 6), (25, 31)):
        for x in range(x0, x1 + 1):
            col = folds[(x - x0) % 4]
            c.vline(x, 3, 12, col)
        c.vline(x0, 3, 12, BURG_DD)
        c.vline(x1, 3, 12, BURG_DD)
        c.hline(x0, x1, 13, OUTLINE)
        tie = 8
        c.hline(x0, x1, tie, GOLD)
    # rod with finials across the top
    c.hline(0, 31, 0, OUTLINE)
    c.hline(1, 30, 1, GOLD)
    c.px(0, 1, AMBER)
    c.px(31, 1, AMBER)
    c.hline(1, 30, 2, AMBER)
    return c


# ================================================================ main

def main():
    # doors: west, east (mirror), south
    for state in ("closed", "half", "open"):
        w = door_w(state)
        save(w, DOORS, f"door_w_{state}.png", opaque=True)
        save(mirror(w.im), DOORS, f"door_e_{state}.png", opaque=True)
        save(door_s(state), DOORS, f"door_s_{state}.png", opaque=True)
        # the Dining Room's French doors are on its east wall: mirror the west-wall drawing
        save(mirror(french(state, outside=False).im), DOORS, f"french_doors_interior_{state}.png", opaque=True)
        save(french(state, outside=True), DOORS, f"french_doors_exterior_{state}.png", opaque=True)
        save(door_ext_w(state), DOORS, f"door_ext_w_{state}.png", opaque=True)

    # north doors: the leaf art comes from the existing closed/open sprites (re-running is
    # safe: the opening area is copied through unchanged)
    src_closed = load(os.path.join(DOORS, "door_n_closed.png"))
    src_open = load(os.path.join(DOORS, "door_n_open.png"))
    for state in ("closed", "half", "open"):
        save(door_n(state, src_closed, src_open), DOORS, f"door_n_{state}.png", opaque=True)

    # windows
    save(window_s_curtains_burgundy(), WINDOWS, "window_s_curtains_burgundy.png")

    # furniture
    e = chair(CHAIR_E)
    save(e, SEATING, "chair_dining_e.png")
    save(mirror(e.im), SEATING, "chair_dining_w.png")
    save(chair(CHAIR_N), SEATING, "chair_dining_n.png")
    save(armchair_s(), SEATING, "armchair_s.png")
    save(loveseat_burgundy(), SEATING, "loveseat_w_burgundy.png")
    save(loveseat_clara(), SEATING, "loveseat_w_clara.png")
    save(bookshelf_gap(), STORAGE, "bookshelf_tall_gap.png")

    for path, size in WRITTEN:
        print(f"wrote {path} {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Builds the Godot room scenes for Blackwood Manor from each room's layout data.

For every room in ROOMS this reads game/maps/<room>/<room>_layout.json (sprites, collision,
doors, spawns, NPC and clue spots) plus <room>_tileset.png/.json, and writes
game/maps/<room>/<room>.tscn. Every room gets the same node tree and the shared Room script,
and doors are wired to each other from the CONNECTIONS table below.

The layout files don't store the floor grid, so each cell's tile is recovered from the room's
<room>_preview.png: the known sprites are layered over every candidate tile and the closest
match wins. Sprites that aren't in the project yet are skipped and listed in
tools/MISSING_ART.md; add the PNGs anywhere under game/shared_assets/ and run this again.
A furniture piece whose sprite is missing gets no collision (it would be an invisible wall),
and --check reports it as a PROBLEM. Doors work the same way: every connected door needs its
<base>_closed.png and <base>_open.png (plus <base>_half.png if it exists), or --check fails.

LAYOUT_PATCHES edits a room's layout after the floor has been matched to the preview, for
things the vendor layout gets wrong (windows on shared walls, misplaced chairs).

Usage (from the repo root):
    python3 tools/build_rooms.py            # write every scene in ROOMS
    python3 tools/build_rooms.py kitchen    # write only the named rooms
    python3 tools/build_rooms.py --check    # validate doors and spawns, and diff each room
                                            # against its preview (writes nothing in game/)

Requires Pillow.
"""

import argparse
import json
import os
import struct
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

REPO = Path(__file__).resolve().parent.parent
GAME = REPO / "game"
MAPS = GAME / "maps"
TOOLS = REPO / "tools"
TILE = 16

# Room key -> scene root node name. The order is the order rooms are built in.
ROOMS = {
    "main_hall": "MainHall",
    "dining_room": "DiningRoom",
    "kitchen": "Kitchen",
    "library_study": "LibraryStudy",
    "guest_room": "GuestRoom",
    "snowy_backyard": "SnowyBackyard",
    "master_bedroom": "MasterBedroom",
    "attached_bathroom": "AttachedBathroom",
    "upstairs_hallway": "UpstairsHallway",
    "curio_room": "CurioRoom",
    "guest_room_b": "GuestRoomB",
    "grand_study": "GrandStudy",
    "edmund_bedroom": "EdmundBedroom",
    "clara_bedroom": "ClaraBedroom",
}

# Two-way door links: ((room, door id), (room, door id)). A door that isn't listed here
# stays a solid wall.
CONNECTIONS = [
    (("main_hall", "D1"), ("library_study", "D1")),
    (("main_hall", "D2"), ("guest_room", "D1")),
    (("main_hall", "D3"), ("dining_room", "D1")),
    (("main_hall", "D4"), ("kitchen", "D1")),
    (("dining_room", "D2"), ("kitchen", "D2")),
    (("kitchen", "D3"), ("snowy_backyard", "D2")),
    (("dining_room", "D3"), ("snowy_backyard", "D1")),
    (("master_bedroom", "D2"), ("attached_bathroom", "D1")),
    (("upstairs_hallway", "D1"), ("curio_room", "D1")),
    (("upstairs_hallway", "D2"), ("guest_room_b", "D1")),
    (("upstairs_hallway", "D3"), ("grand_study", "D1")),
    (("upstairs_hallway", "D4"), ("edmund_bedroom", "D1")),
    (("upstairs_hallway", "D6"), ("clara_bedroom", "D1")),
    (("upstairs_hallway", "D7"), ("master_bedroom", "D1")),
    (("main_hall", "Stairs"), ("upstairs_hallway", "D5")),
]

# Doors that aren't in a room's layout data
EXTRA_DOORS = {
    # The grand staircase: walking up the steps between the railings goes upstairs.
    # It has no door cells; the wall behind the staircase stays solid
    "main_hall": [{
        "id": "Stairs", "wall": "N", "target": "Upstairs Hallway", "status": "open", "variant": "stairs",
        "door_tiles": [], "trigger_px": [136, 32, 48, 24], "arrive_here_tile": [10, 6],
    }],
    # West end of the hallway, leading to the Master Bedroom (rows 4-5 are clear)
    "upstairs_hallway": [{
        "id": "D7", "wall": "W", "target": "Master Bedroom", "status": "open",
        "door_tiles": [[0, 4], [0, 5]], "arrive_here_tile": [1, 4],
    }],
}

# Rooms small enough to show whole: the camera stays centred on the room instead of following
# the player, zooming out a little where the room is taller than the view
STATIC_CAMERA_ROOMS = {
    "guest_room", "attached_bathroom", "curio_room", "dining_room", "kitchen",
    "clara_bedroom", "edmund_bedroom", "master_bedroom",
}

# Furniture whose collision differs from its layout footprint: (room, id) -> [rects px]
COLLISION_OVERRIDES = {
    # Main Hall grand staircase: only the railings are solid, so the player can climb the steps
    ("main_hall", "ST"): [(112, 32, 24, 48), (184, 32, 24, 48)],
}

# Furniture that y-sorts at a different height than its footprint bottom: (room, id) -> y px.
# The staircase sorts at its top step so the player stays in front of it while climbing.
Y_SORT_OVERRIDES = {
    ("main_hall", "ST"): 32,
}

# Spawn points that aren't derived from a door: room -> {name: (x, y, facing)}
EXTRA_SPAWNS = {
    # Foot of the grand staircase, coming down from the Upstairs Hallway
    "main_hall": {"from_upstairs_hallway": (160, 110, "down")},
}

# Door sprite set by wall: the file name base. The generator looks for <base>_closed.png,
# <base>_open.png and (optional) <base>_half.png in game/shared_assets/architecture/doors/.
DEFAULT_DOOR_SPRITES = {"N": "door_n", "S": "door_s", "W": "door_w", "E": "door_e"}
# Room-specific door sprite bases: (room, door id) -> base
DOOR_SPRITE_OVERRIDES = {
    # Both sides of the French doors between the Dining Room and the backyard
    ("dining_room", "D3"): "french_doors_interior",
    ("snowy_backyard", "D1"): "french_doors_exterior",
    ("snowy_backyard", "D2"): "door_ext_w",
}

# Per-room fixes applied to the layout after the floor is matched against the preview (so
# the floor solver still sees the vendor layout the preview was drawn from). room -> patch:
#   "remove_decor": [ids]               drop decor items (no sprite, no tile overlay)
#   "decor" / "furniture": {id: change} change is any of:
#       "sprite": file name   "size": [w, h] sprite px   "pos": [x, y] sprite top-left px
#       "collision": [x, y, w, h] px   "footprint": [x, y, w, h] tiles
#       "origin": [x, y] px, the y-sort origin for a piece that is no longer tile-aligned
#   "tiles": {(x, y): (sx, sy)}         copy the floor tile from cell (sx, sy), used where the
#                                       tile under a removed window isn't plain wall
# An id that isn't in the room is an error.
LAYOUT_PATCHES = {
    # Windows on walls the room shares with another room come out
    "guest_room": {"remove_decor": ["WN2"]},
    "library_study": {"remove_decor": ["WN2"]},
    "curio_room": {"remove_decor": ["WN2"]},
    "guest_room_b": {"remove_decor": ["WN1", "WN2"]},
    "grand_study": {"remove_decor": ["WN1", "WN2"]},
    "edmund_bedroom": {
        "remove_decor": ["WN1", "WN2"],
        # The north window moves to the south wall beside the desk
        "decor": {"WI": {"sprite": "window_s_curtains_burgundy.png", "size": [32, 16], "pos": [32, 208]}},
    },
    "clara_bedroom": {
        "remove_decor": ["WN1", "W1"],
        "furniture": {
            # Down the east wall, 32px clear of the window; the lamp below it stays reachable
            "LV": {"pos": [208, 144], "collision": [208, 144, 32, 32], "footprint": [13, 9, 2, 2]},
        },
        # The vase stands on the tabletop instead of the table's stem
        "decor": {"T1": {"pos": [168, 116]}},
    },
    "upstairs_hallway": {"remove_decor": ["W1", "W2"]},
    # Chairs centred on the table (sprite 96x48 at (96,80), collision (96,96,96,32)): three a side
    # at x 104/136/168, one centred on each short end. Collision stays under the sprite's lower half.
    "dining_room": {"furniture": {
        "C1a": {"pos": [104, 64], "collision": [104, 80, 16, 16], "origin": [104, 96]},
        "C1b": {"pos": [136, 64], "collision": [136, 80, 16, 16], "origin": [136, 96]},
        "C1c": {"pos": [168, 64], "collision": [168, 80, 16, 16], "origin": [168, 96]},
        "C2a": {"pos": [104, 112], "collision": [104, 128, 16, 16], "origin": [104, 144]},
        "C2b": {"pos": [136, 112], "collision": [136, 128, 16, 16], "origin": [136, 144]},
        "C2c": {"pos": [168, 112], "collision": [168, 128, 16, 16], "origin": [168, 144]},
        "H1": {"pos": [80, 88], "collision": [80, 104, 16, 16], "origin": [80, 120]},
        "H2": {"pos": [192, 88], "collision": [192, 104, 16, 16], "origin": [192, 120]},
    }},
}

ENTER_DIRECTION = {"N": "up", "S": "down", "W": "left", "E": "right"}
ARRIVE_FACING = {"N": "down", "S": "up", "W": "right", "E": "left"}
PLAYER_SPEED = 80.0


# ---------------------------------------------------------------- asset lookup

class Assets:
    """Finds sprite PNGs by file name anywhere in a room folder or game/shared_assets."""

    def __init__(self):
        self.by_name = {}
        for root in [MAPS, GAME / "shared_assets"]:
            for path in sorted(root.rglob("*.png")):
                if path.name.endswith(("_preview.png", "_tileset.png")):
                    continue
                self.by_name.setdefault(path.name, []).append(path)
        self.missing = {}

    def find(self, sprite_ref, room):
        if not sprite_ref:
            return None
        name = os.path.basename(sprite_ref)
        paths = self.by_name.get(name, [])
        # Prefer the room's own copy, then the first one found
        for path in paths:
            if MAPS / room in path.parents:
                return path
        if paths:
            return paths[0]
        self.missing.setdefault(name, set()).add(room)
        return None


def res_path(path):
    return "res://" + path.relative_to(GAME).as_posix()


# ---------------------------------------------------------------- layout model

def load_layout(room):
    data = json.loads((MAPS / room / f"{room}_layout.json").read_text())
    data["doors"] = list(data["doors"]) + EXTRA_DOORS.get(room, [])
    size = data["size_tiles"]
    data["size_tiles"] = (size["w"], size["h"]) if isinstance(size, dict) else tuple(size)
    return data


def door_rect(door):
    """Pixel rect (x, y, w, h) covering a door's cells, or its trigger_px if it has one."""
    if "trigger_px" in door:
        return tuple(door["trigger_px"])
    xs = [c[0] for c in door["door_tiles"]]
    ys = [c[1] for c in door["door_tiles"]]
    x0, y0 = min(xs), min(ys)
    return (x0 * TILE, y0 * TILE, (max(xs) - x0 + 1) * TILE, (max(ys) - y0 + 1) * TILE)


def arrival_point(door, size_tiles):
    """Where the player's feet land when arriving through this door, and their facing."""
    x, y, w, h = door_rect(door)
    wall = door["wall"]
    if wall == "W":
        return (x + w + 8, y + h // 2 + 3), ARRIVE_FACING[wall]
    if wall == "E":
        return (x - 8, y + h // 2 + 3), ARRIVE_FACING[wall]
    if wall == "N":
        return (x + w // 2, y + h + 14), ARRIVE_FACING[wall]
    return (x + w // 2, y - 2), ARRIVE_FACING[wall]


def connection_map():
    links = {}
    for a, b in CONNECTIONS:
        links[a] = b
        links[b] = a
    return links


# ---------------------------------------------------------------- tiles

def load_tileset(room):
    meta = json.loads((MAPS / room / f"{room}_tileset.json").read_text())
    image = Image.open(MAPS / room / f"{room}_tileset.png").convert("RGBA")
    tiles = {}
    for name, cell in meta["tiles"].items():
        tiles[name] = (cell["col"], cell["row"], image.crop((cell["x"], cell["y"], cell["x"] + TILE, cell["y"] + TILE)))
    return tiles


def is_floor_tile(name):
    return not any(part in name for part in ("wall", "corner", "door", "rug", "fence", "garden", "ext_", "stair"))


FLIPS = {0: None, 1: Image.FLIP_LEFT_RIGHT, 2: Image.FLIP_TOP_BOTTOM, 3: Image.ROTATE_180}


def rug_tile(x, y, w, h, prefix):
    """9-slice rug tile name and flip alternative for cell (x, y) of a w x h rug."""
    left, right, top, bottom = x == 0, x == w - 1, y == 0, y == h - 1
    if (left or right) and (top or bottom):
        return prefix + "corner", (1 if right else 0) + (2 if bottom else 0)
    if top or bottom:
        return prefix + "edge_t", 2 if bottom else 0
    if left or right:
        return prefix + "edge_l", 1 if right else 0
    return prefix + "center", 0


def diff_score(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).sum)


def solve_floor(room, layout, tiles, overlay, rug_cells):
    """Picks a (tile name, flip) for every cell by matching the preview."""
    preview = Image.open(MAPS / room / f"{room}_preview.png").convert("RGBA")
    w, h = layout["size_tiles"]
    door_cells = {tuple(c) for d in layout["doors"] for c in d["door_tiles"]}
    floor_names = [n for n in tiles if is_floor_tile(n)]
    ring_names = [n for n in tiles if not is_floor_tile(n) and not n.startswith("rug")]
    grid = {}
    exact = 0
    for y in range(h):
        for x in range(w):
            box = (x * TILE, y * TILE, x * TILE + TILE, y * TILE + TILE)
            target = preview.crop(box)
            cover = overlay.crop(box)
            if (x, y) in rug_cells:
                grid[(x, y)] = rug_cells[(x, y)]
                continue
            interior = 1 <= x <= w - 2 and 2 <= y <= h - 2 and (x, y) not in door_cells

            def closest(names):
                best, best_score = None, None
                for name in names:
                    score = diff_score(Image.alpha_composite(tiles[name][2], cover), target)
                    if best_score is None or score < best_score:
                        best, best_score = name, score
                        if score == 0:
                            break
                return best, best_score

            if interior:
                best, best_score = closest(floor_names)
            else:
                # Edge cells are wall unless the preview shows an exact floor tile there
                # (the backyard's open edges); a missing sprite over a wall must not turn it to floor
                best, best_score = closest(ring_names + floor_names)
                if best_score and ring_names:
                    best, best_score = closest(ring_names)
            exact += best_score == 0
            grid[(x, y)] = (best, 0)
    return grid, exact


def door_tile_names(door):
    """Tile names for each cell of a door, by wall."""
    cells = sorted(door["door_tiles"], key=lambda c: (c[1], c[0]))
    wall = door["wall"]
    names = {}
    if wall in ("W", "E"):
        for i, c in enumerate(cells):
            names[tuple(c)] = f"door_{wall.lower()}_{'top' if i == 0 else 'bot'}"
    elif wall == "N" and cells:
        top = min(c[1] for c in cells)
        xs = sorted({c[0] for c in cells})
        for c in cells:
            row = "t" if c[1] == top else "b"
            col = "l" if c[0] == xs[0] else "r"
            names[tuple(c)] = f"door_n_{row}{col}"
    return names


# ---------------------------------------------------------------- scene writer

class Scene:
    def __init__(self):
        self.ext = {}
        self.sub = []
        self.nodes = []
        self.shapes = {}

    def ext_res(self, kind, path):
        key = (kind, path)
        if key not in self.ext:
            stem = Path(path).stem.replace(".", "_")
            self.ext[key] = f"{len(self.ext) + 1}_{stem}"
        return self.ext[key]

    def rect_shape(self, w, h):
        key = (w, h)
        if key not in self.shapes:
            sid = f"Rect_{w}x{h}"
            self.shapes[key] = sid
            self.sub.append(f'[sub_resource type="RectangleShape2D" id="{sid}"]\nsize = Vector2({w}, {h})\n')
        return self.shapes[key]

    def node(self, name, kind=None, parent=None, instance=None, groups=None, props=None):
        head = f'[node name="{name}"'
        if kind:
            head += f' type="{kind}"'
        if parent is not None:
            head += f' parent="{parent}"'
        if instance:
            head += f' instance=ExtResource("{instance}")'
        if groups:
            head += " groups=[" + ", ".join(f'"{g}"' for g in groups) + "]"
        head += "]"
        lines = [head] + [f"{k} = {v}" for k, v in (props or {}).items()]
        self.nodes.append("\n".join(lines) + "\n")

    def text(self):
        out = ["[gd_scene format=3]\n"]
        for (kind, path), rid in self.ext.items():
            out.append(f'[ext_resource type="{kind}" path="{path}" id="{rid}"]')
        out.append("")
        out.extend(self.sub)
        out.extend(self.nodes)
        return "\n".join(out).rstrip("\n") + "\n"


def vec(x, y):
    return f"Vector2({x:g}, {y:g})"


def gd_string(text):
    return json.dumps(str(text), ensure_ascii=False)


def safe_name(text):
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(text))


def apply_patches(room, layout, grid):
    """Applies LAYOUT_PATCHES[room] to the layout (and floor grid) in place."""
    patch = LAYOUT_PATCHES.get(room)
    if not patch:
        return
    known = {"remove_decor", "decor", "furniture", "tiles"}
    if set(patch) - known:
        raise SystemExit(f"{room}: unknown LAYOUT_PATCHES keys {sorted(set(patch) - known)}")
    lists = {"decor": layout["decor"], "furniture": layout["furniture"]}

    def find(kind, item_id):
        for item in lists[kind]:
            if item["id"] == item_id:
                return item
        raise SystemExit(f"{room}: LAYOUT_PATCHES names {kind} id {item_id!r}, which isn't in the layout")

    for item_id in patch.get("remove_decor", []):
        lists["decor"].remove(find("decor", item_id))
    keys = {"sprite": "sprite", "size": "sprite_size_px", "pos": "sprite_top_left_px", "origin": "origin_px"}
    for kind in ("decor", "furniture"):
        for item_id, change in patch.get(kind, {}).items():
            item = find(kind, item_id)
            for key, value in change.items():
                if key in keys:
                    item[keys[key]] = value
                elif key == "collision":
                    item["collision_rect_px"] = dict(zip("xywh", value))
                elif key == "footprint":
                    item["footprint_tiles"] = dict(zip("xywh", value))
                else:
                    raise SystemExit(f"{room} {item_id}: unknown LAYOUT_PATCHES change {key!r}")
    for cell, src in patch.get("tiles", {}).items():
        grid[cell] = grid[src]


def build_room(room, root_name, assets, links):
    layout = load_layout(room)
    w, h = layout["size_tiles"]
    tiles = load_tileset(room)
    scene = Scene()
    script = scene.ext_res("Script", "res://maps/room.gd")
    tileset_png = scene.ext_res("Texture2D", res_path(MAPS / room / f"{room}_tileset.png"))
    player = scene.ext_res("PackedScene", "res://entities/player/player.tscn")
    door_scene = scene.ext_res("PackedScene", "res://maps/door/door.tscn")
    touch = scene.ext_res("PackedScene", "res://ui/touch_controls/touch_controls.tscn")

    def texture(sprite_ref):
        path = assets.find(sprite_ref, room)
        return (path, scene.ext_res("Texture2D", res_path(path))) if path else (None, None)

    problems = []

    # Which doors lead somewhere
    active_doors = []
    for door in layout["doors"]:
        target = links.get((room, door["id"]))
        if target:
            active_doors.append((door, target))
    active_cells = {tuple(c) for d, _ in active_doors for c in d["door_tiles"]}

    # Door sprite sets. The V2 rooms draw their doors (and the backyard its French doors) as
    # decor; those items move onto the Door node, which keeps their position as sprite_offset.
    door_sprites = {}
    decor_doors = set()
    for door, _ in active_doors:
        if door.get("variant") == "stairs":
            continue
        base = DOOR_SPRITE_OVERRIDES.get((room, door["id"])) or DEFAULT_DOOR_SPRITES[door["wall"]]
        rect = door_rect(door)
        offset = (0, 0)
        for item in layout["decor"]:
            if not item.get("sprite"):
                continue
            stem = Path(item["sprite"]).stem
            ix, iy = item["sprite_top_left_px"]
            if (stem.startswith("door_") or stem == base) and rect[0] <= ix < rect[0] + rect[2] and rect[1] <= iy < rect[1] + rect[3]:
                decor_doors.add(item["id"])
                offset = (ix - rect[0], iy - rect[1])
        half = f"{base}_half.png"
        door_sprites[door["id"]] = {
            "closed": f"{base}_closed.png", "open": f"{base}_open.png",
            "half": half if half in assets.by_name else None, "offset": offset}

    # ---- sprites layered over the floor, used to match the preview
    rugs_as_tiles = {}
    for rug in layout["rugs"]:
        if not assets.find(rug.get("sprite"), room):
            r = rug["tile_rect"]
            prefix = f"rug_{rug['palette']}_"
            for yy in range(r["h"]):
                for xx in range(r["w"]):
                    name, flip = rug_tile(xx, yy, r["w"], r["h"], prefix)
                    if name in tiles:
                        rugs_as_tiles[(r["x"] + xx, r["y"] + yy)] = (name, flip)

    def make_overlay(skip_decor, draw_doors):
        """Every sprite layered over the floor, in draw order. skip_decor: ids left out."""
        overlay = Image.new("RGBA", (w * TILE, h * TILE), (0, 0, 0, 0))

        def paste(sprite_ref, top_left):
            path = assets.find(sprite_ref, room)
            if path:
                image = Image.open(path).convert("RGBA")
                overlay.alpha_composite(image, tuple(int(v) for v in top_left))

        for rug in layout["rugs"]:
            if assets.find(rug.get("sprite"), room):
                r = rug["tile_rect"]
                paste(rug["sprite"], (r["x"] * TILE, r["y"] * TILE))
        layers = {"floor": [], "wall": [], "top": [], "over": []}
        for item in layout["decor"]:
            if item["id"] not in skip_decor:
                layers.setdefault(item.get("layer", "wall"), []).append(item)
        for item in layers["floor"] + layers["wall"]:
            paste(item["sprite"], item["sprite_top_left_px"])
        if draw_doors:
            for door, _ in active_doors:
                sprites = door_sprites.get(door["id"])
                if sprites:
                    dx, dy, _, _ = door_rect(door)
                    paste(sprites["closed"], (dx + sprites["offset"][0], dy + sprites["offset"][1]))
        for item in sorted(layout["furniture"], key=lambda f: f.get("y_sort_px", 0)):
            if item.get("sprite"):
                paste(item["sprite"], item["sprite_top_left_px"])
        for item in layers["top"] + layers["over"]:
            paste(item["sprite"], item["sprite_top_left_px"])
        return overlay

    grid, exact = solve_floor(room, layout, tiles, make_overlay((), False), rugs_as_tiles)

    # Everything from here on uses the patched layout
    apply_patches(room, layout, grid)
    overlay = make_overlay(decor_doors, True)
    by_layer = {"floor": [], "wall": [], "top": [], "over": []}
    for item in layout["decor"]:
        by_layer.setdefault(item.get("layer", "wall"), []).append(item)

    # Doorway tiles for active doors that the preview drew as wall (e.g. a new door)
    for door, _ in active_doors:
        for cell, name in door_tile_names(door).items():
            if name in tiles and not grid[cell][0].startswith(("door", "ext_door")):
                grid[cell] = (name, 0)

    # A door sprite carries its own frame, so the doorway tile under it (which has a frame
    # baked in) is swapped for the plain wall beside the door; otherwise two doors show at once
    for door, _ in active_doors:
        sprites = door_sprites.get(door["id"])
        path = assets.find(sprites["closed"], room) if sprites else None
        if not path or door["wall"] == "N":
            continue
        dx, dy, _, _ = door_rect(door)
        sw, sh = Image.open(path).size
        sx, sy = dx + sprites["offset"][0], dy + sprites["offset"][1]
        cells = [tuple(c) for c in door["door_tiles"]]
        covered = [c for c in cells if sx < (c[0] + 1) * TILE and c[0] * TILE < sx + sw
                   and sy < (c[1] + 1) * TILE and c[1] * TILE < sy + sh]
        if not covered:
            continue
        along = (0, 1) if door["wall"] in ("W", "E") else (1, 0)
        lo = min(covered, key=lambda c: (c[1], c[0]))
        hi = max(covered, key=lambda c: (c[1], c[0]))
        # Nearest wall cell before the door along the wall, else the one after it
        for cell in [(lo[0] - along[0], lo[1] - along[1]), (hi[0] + along[0], hi[1] + along[1])]:
            name = grid.get(cell, ("", 0))[0]
            if name and not any(part in name for part in ("door", "corner")):
                for c in covered:
                    grid[c] = grid[cell]
                break

    # ---- TileSet
    atlas_lines = [f'[sub_resource type="TileSetAtlasSource" id="Atlas_room"]',
                   f'texture = ExtResource("{tileset_png}")', "texture_region_size = Vector2i(16, 16)"]
    flips_used = {}
    for (name, flip) in grid.values():
        if flip:
            flips_used.setdefault(name, set()).add(flip)
    for name, (col, row, _) in sorted(tiles.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        atlas_lines.append(f"{col}:{row}/0 = 0")
        for flip in sorted(flips_used.get(name, ())):
            atlas_lines.append(f"{col}:{row}/{flip} = {flip}")
            if flip & 1:
                atlas_lines.append(f"{col}:{row}/{flip}/flip_h = true")
            if flip & 2:
                atlas_lines.append(f"{col}:{row}/{flip}/flip_v = true")
    scene.sub.append("\n".join(atlas_lines) + "\n")
    scene.sub.append('[sub_resource type="TileSet" id="TileSet_room"]\nsources/0 = SubResource("Atlas_room")\n')

    data = bytearray(struct.pack("<H", 0))
    for y in range(h):
        for x in range(w):
            name, flip = grid[(x, y)]
            col, row, _ = tiles[name]
            data += struct.pack("<hhHHHH", x, y, 0, col, row, flip)
    tile_data = "PackedByteArray(" + ", ".join(str(b) for b in data) + ")"

    # ---- root and floor
    root_props = {"script": f'ExtResource("{script}")'}
    if room in STATIC_CAMERA_ROOMS:
        root_props["static_camera"] = "true"
    root_props["metadata/room_key"] = gd_string(room)
    root_props["metadata/size_tiles"] = f"Vector2i({w}, {h})"
    scene.node(root_name, "Node2D", props=root_props)
    scene.node("Floor", "TileMapLayer", ".", props={"tile_map_data": tile_data, "tile_set": 'SubResource("TileSet_room")'})

    # ---- rugs and floor decals
    scene.node("Rugs", "Node2D", ".")
    for i, rug in enumerate(layout["rugs"]):
        path, tex = texture(rug.get("sprite"))
        if tex:
            r = rug["tile_rect"]
            scene.node(f"Rug_{i + 1}", "Sprite2D", "Rugs", props={
                "position": vec(r["x"] * TILE, r["y"] * TILE), "texture": f'ExtResource("{tex}")', "centered": "false"})
    for item in by_layer["floor"]:
        path, tex = texture(item["sprite"])
        if tex:
            scene.node(safe_name(item["id"]), "Sprite2D", "Rugs", props={
                "position": vec(*item["sprite_top_left_px"]), "texture": f'ExtResource("{tex}")', "centered": "false"})

    # ---- wall decor (door sprites move to their Door)
    scene.node("WallDecor", "Node2D", ".")
    for item in by_layer["wall"]:
        if item["id"] in decor_doors:
            continue
        path, tex = texture(item["sprite"])
        if tex:
            scene.node(safe_name(item["id"]), "Sprite2D", "WallDecor", props={
                "position": vec(*item["sprite_top_left_px"]), "texture": f'ExtResource("{tex}")', "centered": "false"})

    # ---- doors
    scene.node("Doors", "Node2D", ".")
    for door, (target_room, target_door_id) in active_doors:
        dx, dy, dw, dh = door_rect(door)
        props = {
            "position": vec(dx, dy),
            "target_scene": gd_string(f"res://maps/{target_room}/{target_room}.tscn"),
            "target_spawn": gd_string(f"from_{room}"),
            "enter_direction": gd_string(ENTER_DIRECTION[door["wall"]]),
            "trigger_size": vec(dw, dh),
        }
        sprites = door_sprites.get(door["id"])
        if sprites:
            for key, prop in (("closed", "closed_texture"), ("open", "open_texture"), ("half", "half_texture")):
                if not sprites[key]:
                    continue
                _, tex = texture(sprites[key])
                if tex:
                    props[prop] = f'ExtResource("{tex}")'
                elif key != "half":
                    problems.append(f"{room} {door['id']}: door sprite {sprites[key]} not found")
            if sprites["offset"] != (0, 0):
                props["sprite_offset"] = vec(*sprites["offset"])
        props["metadata/door_id"] = gd_string(door["id"])
        props["metadata/leads_to"] = gd_string(target_room)
        scene.node(f"Door_{door['id']}", None, "Doors", instance=door_scene, props=props)

    # ---- furniture (y-sorted with the player)
    scene.node("Entities", "Node2D", ".", props={"y_sort_enabled": "true"})
    furniture_rects = {}
    blockers = []
    for item in layout["furniture"]:
        origin = furniture_origin(room, item)
        name = safe_name(item["id"])
        furniture_rects[name] = item
        scene.node(name, "Node2D", "Entities", props={
            "position": vec(*origin), "metadata/display_name": gd_string(item.get("name", item["id"]))})
        path, tex = texture(item.get("sprite"))
        if tex:
            sx, sy = item["sprite_top_left_px"]
            scene.node("Sprite", "Sprite2D", f"Entities/{name}", props={
                "position": vec(sx - origin[0], sy - origin[1]), "texture": f'ExtResource("{tex}")', "centered": "false"})
        rects = furniture_collision(room, item)
        if item.get("sprite") and not tex:
            # No art yet: a solid body with nothing drawn would be an invisible wall
            rects = []
            problems.append(f"{room} {item['id']}: sprite {os.path.basename(item['sprite'])} not found, so it has no collision")
        blockers += rects
        if rects:
            scene.node("Body", "StaticBody2D", f"Entities/{name}")
            for i, (cx, cy, cw, ch) in enumerate(rects):
                shape = scene.rect_shape(cw, ch)
                scene.node(f"Shape{i + 1 if i else ''}", "CollisionShape2D", f"Entities/{name}/Body", props={
                    "position": vec(cx + cw / 2 - origin[0], cy + ch / 2 - origin[1]), "shape": f'SubResource("{shape}")'})
    # Small items that sit on furniture sort with the piece they sit on
    for item in by_layer["top"]:
        path, tex = texture(item["sprite"])
        if not tex:
            continue
        ix, iy = item["sprite_top_left_px"]
        iw, ih = item.get("sprite_size_px", (16, 16))
        cx, cy = ix + iw / 2, iy + ih / 2
        host = None
        for name, f in furniture_rects.items():
            if not f.get("sprite"):
                continue
            fx, fy = f["sprite_top_left_px"]
            fw, fh = f["sprite_size_px"]
            if fx <= cx < fx + fw and fy <= cy < fy + fh:
                host = (name, f)
                break
        if host:
            name, f = host
            origin = furniture_origin(room, f)
            scene.node(f"Top_{safe_name(item['id'])}", "Sprite2D", f"Entities/{name}", props={
                "position": vec(ix - origin[0], iy - origin[1]), "texture": f'ExtResource("{tex}")', "centered": "false"})
        else:
            scene.node(f"Top_{safe_name(item['id'])}", "Sprite2D", "Entities", props={
                "position": vec(ix, iy), "texture": f'ExtResource("{tex}")', "centered": "false"})

    # ---- player
    spawns = room_spawns(room, layout, links)
    start = spawns["start"][0]
    scene.node("Player", None, "Entities", instance=player, props={"position": vec(*start), "speed": f"{PLAYER_SPEED:g}"})

    # ---- ceiling lights
    scene.node("Overhead", "Node2D", ".", props={"z_index": "20"})
    for item in by_layer["over"]:
        path, tex = texture(item["sprite"])
        if tex:
            scene.node(safe_name(item["id"]), "Sprite2D", "Overhead", props={
                "position": vec(*item["sprite_top_left_px"]), "texture": f'ExtResource("{tex}")', "centered": "false"})

    # ---- walls, with gaps at doors that lead somewhere
    scene.node("Walls", "StaticBody2D", ".")
    for i, (x, y, rw, rh) in enumerate(wall_rects(w, h, active_cells)):
        shape = scene.rect_shape(rw, rh)
        scene.node(f"Wall_{i}", "CollisionShape2D", "Walls", props={
            "position": vec(x + rw / 2, y + rh / 2), "shape": f'SubResource("{shape}")'})

    # ---- spawn points, NPC slots and clue spots
    scene.node("SpawnPoints", "Node2D", ".")
    for name, ((x, y), facing, note) in spawns.items():
        scene.node(name, "Marker2D", "SpawnPoints", groups=["spawn_points"], props={
            "position": vec(x, y), "metadata/facing": gd_string(facing), "metadata/note": gd_string(note)})
    scene.node("NpcSlots", "Node2D", ".")
    for slot in layout.get("npc_slots", []):
        tx, ty = slot["tile"]
        scene.node(f"Npc_{safe_name(slot['id'])}", "Marker2D", "NpcSlots", groups=["npc_slots"], props={
            "position": vec(tx * TILE + 8, ty * TILE + 15), "metadata/who": gd_string(slot.get("who") or "")})
    scene.node("ClueSpots", "Node2D", ".")
    for clue in layout.get("clue_areas", []):
        if clue.get("tile"):
            px = (clue["tile"][0] * TILE + 8, clue["tile"][1] * TILE + 8)
        elif clue.get("footprint_tiles"):
            f = clue["footprint_tiles"]
            px = ((f["x"] + f["w"] / 2) * TILE, (f["y"] + f["h"] / 2) * TILE)
        elif clue.get("rect_px"):
            r = clue["rect_px"]
            px = (r["x"] + r["w"] / 2, r["y"] + r["h"] / 2)
        else:
            continue
        scene.node(f"Clue_{safe_name(clue['id'])}", "Marker2D", "ClueSpots", groups=["clue_spots"], props={
            "position": vec(*px), "metadata/description": gd_string(clue.get("description", "")),
            "metadata/placeholder": "true"})

    scene.node("TouchControls", None, ".", instance=touch)
    return scene.text(), {"exact_cells": exact, "cells": w * h, "layout": layout, "spawns": spawns,
                          "active_doors": active_doors, "overlay": overlay, "grid": grid, "tiles": tiles,
                          "problems": problems, "blockers": blockers, "door_sprites": door_sprites}


def furniture_collision(room, item):
    """Collision rects (x, y, w, h) px the layout asks for, whether or not the sprite exists."""
    rects = COLLISION_OVERRIDES.get((room, item["id"]))
    if rects is None and item.get("collides", True) and item.get("collision_rect_px"):
        c = item["collision_rect_px"]
        rects = [(c["x"], c["y"], c["w"], c["h"])]
    return list(rects or [])


def furniture_origin(room, item):
    """Node origin for a piece of furniture: the bottom-left of its footprint, which is
    where it y-sorts against the player, unless Y_SORT_OVERRIDES or a patch's explicit
    origin_px moves it."""
    if "origin_px" in item:
        return tuple(item["origin_px"])
    ft = item["footprint_tiles"]
    y = Y_SORT_OVERRIDES.get((room, item["id"]), (ft["y"] + ft["h"]) * TILE)
    return (ft["x"] * TILE, y)


def _overlaps(item, rect):
    ix, iy = item["sprite_top_left_px"]
    iw, ih = item.get("sprite_size_px", (16, 16))
    x, y, w, h = rect
    return ix < x + w and x < ix + iw and iy < y + h and y < iy + ih


def room_spawns(room, layout, links):
    """name -> ((x, y), facing, note). Positions are the player's feet."""
    spawns = {}
    tx, ty = layout["player_spawn"]["tile"]
    spawns["start"] = ((tx * TILE + 8, ty * TILE + 15), "down", "default spawn when this room is the first scene")
    for door in layout["doors"]:
        target = links.get((room, door["id"]))
        if not target:
            continue
        point, facing = arrival_point(door, layout["size_tiles"])
        spawns[f"from_{target[0]}"] = (point, facing, f"arrive from {target[0]} through {door['id']}")
    for name, (x, y, facing) in EXTRA_SPAWNS.get(room, {}).items():
        spawns[name] = ((x, y), facing, "added by build_rooms.py")
    return spawns


def wall_rects(w, h, open_cells):
    """Merged collision rects for the wall ring (2-row north wall), skipping open door cells."""
    rects = []

    def run(cells, horizontal, fixed, thickness):
        start = None
        for i, cell in enumerate(cells + [None]):
            solid = cell is not None and cell not in open_cells
            if solid and start is None:
                start = i
            if not solid and start is not None:
                a, b = cells[start], cells[i - 1]
                if horizontal:
                    rects.append((a[0] * TILE, fixed * TILE, (b[0] - a[0] + 1) * TILE, thickness * TILE))
                else:
                    rects.append((fixed * TILE, a[1] * TILE, thickness * TILE, (b[1] - a[1] + 1) * TILE))
                start = None

    # North wall: a cell is open only if both rows are door cells
    north = [(x, 0) if not ((x, 0) in open_cells and (x, 1) in open_cells) else None for x in range(w)]
    start = None
    for x in range(w + 1):
        solid = x < w and north[x] is not None
        if solid and start is None:
            start = x
        if not solid and start is not None:
            rects.append((start * TILE, 0, (x - start) * TILE, 2 * TILE))
            start = None
    run([(x, h - 1) for x in range(w)], True, h - 1, 1)
    run([(0, y) for y in range(2, h - 1)], False, 0, 1)
    run([(w - 1, y) for y in range(2, h - 1)], False, w - 1, 1)
    return rects


# ---------------------------------------------------------------- checks

def render(info, room):
    """Composite of the floor grid plus the sprite overlay, to compare with the preview."""
    layout = info["layout"]
    w, h = layout["size_tiles"]
    image = Image.new("RGBA", (w * TILE, h * TILE))
    for (x, y), (name, flip) in info["grid"].items():
        tile = info["tiles"][name][2]
        if FLIPS[flip] is not None:
            tile = tile.transpose(FLIPS[flip])
        image.paste(tile, (x * TILE, y * TILE))
    image.alpha_composite(info["overlay"])
    return image


def check(results):
    problems = []
    rooms = {room: info for room, info in results.items()}
    for room, info in rooms.items():
        spawns = info["spawns"]
        for door, (target_room, _) in info["active_doors"]:
            if target_room not in rooms and not (MAPS / target_room / f"{target_room}.tscn").exists():
                problems.append(f"{room} {door['id']}: target scene {target_room} doesn't exist")
            elif target_room in rooms and f"from_{room}" not in rooms[target_room]["spawns"]:
                problems.append(f"{room} {door['id']}: {target_room} has no spawn from_{room}")
        # Spawns must not touch furniture collision, walls or door triggers
        problems += info["problems"]
        blockers = list(info["blockers"])
        active_cells = {tuple(c) for d, _ in info["active_doors"] for c in d["door_tiles"]}
        w, h = info["layout"]["size_tiles"]
        blockers += wall_rects(w, h, active_cells)
        triggers = [door_rect(d) for d, _ in info["active_doors"]]
        for name, ((x, y), _, _) in spawns.items():
            body = (x - 6, y - 6, 12, 6)
            for r in blockers:
                if _rect_hit(body, r):
                    problems.append(f"{room} spawn {name} at {(x, y)} overlaps collision {r}")
            for r in triggers:
                if _rect_hit(body, r):
                    problems.append(f"{room} spawn {name} at {(x, y)} is inside door trigger {r}")
    # Reachability from the Main Hall
    graph = {room: {t for _, (t, _) in info["active_doors"]} for room, info in rooms.items()}
    seen, todo = set(), ["main_hall"] if "main_hall" in rooms else []
    while todo:
        room = todo.pop()
        if room in seen:
            continue
        seen.add(room)
        todo.extend(graph.get(room, ()))
    unreachable = sorted(set(rooms) - seen)
    if unreachable:
        problems.append(f"not reachable from the Main Hall: {unreachable}")
    return problems


def _rect_hit(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def write_missing(assets):
    lines = ["# Missing room art", "",
             "Generated by `tools/build_rooms.py`. These sprites are referenced by the room layouts but",
             "aren't in the project yet, so the scenes leave them out. Rugs without a sprite are drawn",
             "from the room tileset's 9-slice rug tiles (no centre medallion). A furniture piece whose sprite",
             "is missing gets no collision, and a connected door whose closed or open sprite is missing",
             "has no sprite; `--check` reports both as problems. Add the PNGs anywhere under",
             "`game/shared_assets/` and run `python3 tools/build_rooms.py` again.", ""]
    if not assets.missing:
        lines.append("Nothing is missing.")
    else:
        lines += ["| Sprite | Used in |", "|---|---|"]
        for name, rooms in sorted(assets.missing.items()):
            lines.append(f"| `{name}` | {', '.join(sorted(rooms))} |")
    (TOOLS / "MISSING_ART.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rooms", nargs="*", help="room keys to build (default: all)")
    parser.add_argument("--check", action="store_true", help="validate and diff against previews, write nothing")
    parser.add_argument("--render-dir", help="with --check, save composite/preview side-by-sides here")
    args = parser.parse_args()

    selected = args.rooms or list(ROOMS)
    unknown = [r for r in selected if r not in ROOMS]
    if unknown:
        sys.exit(f"unknown rooms: {unknown}")

    assets = Assets()
    links = connection_map()
    results = {}
    # Every room is built so the missing-art list stays complete; only selected ones are written
    for room in ROOMS:
        text, info = build_room(room, ROOMS[room], assets, links)
        results[room] = info
        if room in selected and not args.check:
            (MAPS / room / f"{room}.tscn").write_text(text)
            print(f"{room}: {info['exact_cells']}/{info['cells']} floor cells match the preview exactly")

    if args.check:
        for room, info in results.items():
            preview = Image.open(MAPS / room / f"{room}_preview.png").convert("RGBA")
            image = render(info, room)
            diff = ImageChops.difference(image, preview).convert("L")
            same = diff.histogram()[0]
            total = preview.width * preview.height
            print(f"  {room}: {100 * same / total:.1f}% of pixels identical to the preview")
            if args.render_dir:
                out = Path(args.render_dir)
                out.mkdir(parents=True, exist_ok=True)
                pair = Image.new("RGBA", (preview.width * 2 + 8, preview.height), (0, 0, 0, 255))
                pair.paste(image, (0, 0))
                pair.paste(preview, (preview.width + 8, 0))
                pair.save(out / f"{room}.png")
        problems = check(results)
        for p in problems:
            print("PROBLEM:", p)
        print("missing sprites:", ", ".join(sorted(assets.missing)) or "none")
        sys.exit(1 if problems else 0)

    write_missing(assets)


if __name__ == "__main__":
    main()

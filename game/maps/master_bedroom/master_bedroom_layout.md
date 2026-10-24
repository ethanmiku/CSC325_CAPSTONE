# Master Bedroom - layout data

> **Proposed room size** - this room was not in the original six-room plan. Resize if the team prefers; see `room_dimensions.md`.

| | |
|---|---|
| Size | **18 x 14 tiles = 288 x 224 px** |
| Walkable interior | tiles x 1..16, y 2..12 (176 tiles, 143 walkable = 81%) |
| Wall style / floor | `master` / `parquet` |
| Tileset | `master_bedroom_tileset.png` (+ `master_bedroom_tileset.json` with every tile's cell) |
| Preview | `master_bedroom_preview.png` (288 x 224 px, 1:1) |

## Suggested player spawn
Tile **(7, 11)**. With a centred 32x32 `Sprite2D`, set the player node position to **(120, 177)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | S | [7, 13] .. [8, 13] | Upstairs landing / Main Hall staircase (PLACEHOLDER) | placeholder | 112, 208, 32, 16 | (7, 12) |
| D2 | E | [17, 4] .. [17, 5] | Attached Bathroom | open | 272, 64, 16, 32 | (16, 4) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| FP | Fireplace | (1, 2) 3x1 | `fireplace_lit.png` | (16, 16) |
| NS1 | Nightstand (lamp) | (6, 2) 1x1 | `nightstand_master.png` | (96, 16) |
| BD | Four-poster bed | (7, 2) 4x3 | `bed_large_master.png` | (112, 16) |
| NS2 | Nightstand (lamp) | (11, 2) 1x1 | `nightstand_master.png` | (176, 16) |
| WD | Grand wardrobe | (14, 2) 3x1 | `wardrobe_master.png` | (224, 0) |
| TR | Trunk at foot of bed | (8, 5) 2x1 | `trunk_master.png` | (128, 80) |
| CL | Chaise lounge | (2, 7) 3x1 | `chaise_master.png` | (32, 96) |
| AC | Armchair | (14, 7) 2x1 | `armchair_w.png` | (224, 96) |
| TS | Side table | (16, 7) 1x1 | `table_side.png` | (256, 96) |
| DR | Dresser | (2, 12) 3x1 | `dresser_master.png` | (32, 176) |
| VN | Vanity with mirror | (13, 12) 2x1 | `vanity_master.png` | (208, 160) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| W1 | W1 | wall | `window_snow_curtains_burgundy.png` | (64, 0) |
| W2 | W2 | wall | `window_snow_curtains_burgundy.png` | (192, 0) |
| P1 | P1 | wall | `painting_landscape.png` | (24, 0) |
| T1 | Jewelry box | top | `jewelry_box.png` | (56, 170) |
| X1 | Broken perfume bottle | floor | `glass_shards.png` | (192, 160) |
| X2 | Wine stain | floor | `wine_stain.png` | (96, 128) |
| CH | Chandelier | over | `chandelier_large.png` | (120, 118) |
| rug | plum rug (walkable) | floor | `rug_plum_10x6.png` | tile (4, 5) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Bed - e.g. under the pillows / mattress
- **C2** - Dresser - e.g. jewelry / letters
- **C3** - Vanity - e.g. perfume / hidden note
- **C4** - Wardrobe - e.g. hidden clothing
- **C5** - Nightstand - e.g. medicine / diary

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Fireplace (3x1); Nightstand (lamp) (1x1); Four-poster bed (4x3); Nightstand (lamp) (1x1); Grand wardrobe (3x1); Trunk at foot of bed (2x1); Chaise lounge (3x1); Armchair (2x1); Side table (1x1); Dresser (3x1); Vanity with mirror (2x1).
- D1 is a PLACEHOLDER link (Upstairs landing / Main Hall staircase (PLACEHOLDER)): wire it up only if the upstairs is built.

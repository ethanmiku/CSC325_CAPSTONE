# Attached Bathroom - layout data

> **Proposed room size** - this room was not in the original six-room plan. Resize if the team prefers; see `room_dimensions.md`.

| | |
|---|---|
| Size | **8 x 8 tiles = 128 x 128 px** |
| Walkable interior | tiles x 1..6, y 2..6 (30 tiles, 23 walkable = 77%) |
| Wall style / floor | `bath` / `bath` |
| Tileset | `attached_bathroom_tileset.png` (+ `attached_bathroom_tileset.json` with every tile's cell) |
| Preview | `attached_bathroom_preview.png` (128 x 128 px, 1:1) |

## Suggested player spawn
Tile **(2, 4)**. With a centred 32x32 `Sprite2D`, set the player node position to **(40, 65)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | W | [0, 4] .. [0, 5] | Master Bedroom | open | 0, 64, 16, 32 | (1, 4) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| WB | Washbasin | (1, 2) 2x1 | `washbasin.png` | (16, 16) |
| TL | Toilet | (3, 2) 1x1 | `toilet.png` | (48, 16) |
| TB | Clawfoot tub | (4, 2) 3x1 | `clawfoot_tub.png` | (64, 16) |
| CB | Cabinet | (6, 6) 1x1 | `bath_cabinet.png` | (96, 80) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| M1 | M1 | wall | `mirror_oval.png` | (24, 0) |
| WN | WN | wall | `window_small_frosted.png` | (96, 0) |
| TR | TR | wall | `towel_rail.png` | (48, 0) |
| SH | SH | wall | `bath_shelf.png` | (64, 1) |
| MT | Bath mat | floor | `bath_mat.png` | (64, 48) |
| X1 | Broken glass | floor | `glass_shards.png` | (48, 80) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Tub - e.g. something in the drain / water
- **C2** - Washbasin - e.g. hidden note / residue
- **C3** - Cabinet - e.g. medicine / missing bottle

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Washbasin (2x1); Toilet (1x1); Clawfoot tub (3x1); Cabinet (1x1).

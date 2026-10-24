# Snowy Backyard - layout data

| | |
|---|---|
| Size | **28 x 20 tiles = 448 x 320 px** |
| Walkable interior | tiles x 1..26, y 2..18 (442 tiles, 389 walkable = 88%) |
| Wall style / floor | `None` / `snow` |
| Tileset | `snowy_backyard_tileset.png` (+ `snowy_backyard_tileset.json` with every tile's cell) |
| Preview | `snowy_backyard_preview.png` (448 x 320 px, 1:1) |

## Suggested player spawn
Tile **(2, 12)**. With a centred 32x32 `Sprite2D`, set the player node position to **(40, 193)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | W | [0, 4] .. [0, 5] | Dining Room (OPTIONAL French doors) | optional | 0, 64, 16, 32 | (1, 4) |
| D2 | W | [0, 12] .. [0, 13] | Kitchen (back door) | open | 0, 192, 16, 32 | (1, 12) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| T1 | Bare tree | (7, 2) 1x1 | `tree_bare_small.png` | (104, 0) |
| T2 | Bare tree | (14, 2) 1x1 | `tree_bare_small.png` | (216, 0) |
| T3 | Bare tree | (21, 2) 1x1 | `tree_bare_small.png` | (328, 0) |
| T4 | Bare tree | (25, 5) 1x1 | `tree_bare_large.png` | (384, 32) |
| T5 | Bare tree | (25, 11) 1x1 | `tree_bare_large.png` | (384, 128) |
| T6 | Bare tree | (25, 16) 1x1 | `tree_bare_large.png` | (384, 208) |
| T7 | Bare tree | (7, 18) 1x1 | `tree_bare_large.png` | (96, 240) |
| T8 | Bare tree | (14, 18) 1x1 | `tree_bare_large.png` | (208, 240) |
| T9 | Bare tree | (21, 18) 1x1 | `tree_bare_large.png` | (320, 240) |
| T10 | Bare tree | (3, 8) 1x1 | `tree_bare_large.png` | (32, 80) |
| FT | Frozen fountain | (12, 9) 4x3 | `fountain_frozen.png` | (192, 128) |
| BN | Bench | (12, 5) 3x1 | `bench_garden.png` | (192, 80) |
| BS | Bench | (12, 14) 3x1 | `bench_garden.png` | (192, 224) |
| WP | Woodpile | (2, 15) 2x1 | `woodpile.png` | (32, 240) |
| FB10 | Snowy bush | (5, 7) 1x1 | `bush_snow.png` | (80, 112) |
| FB11 | Snowy bush | (6, 7) 1x1 | `bush_snow.png` | (96, 112) |
| FB12 | Snowy bush | (7, 7) 1x1 | `bush_snow.png` | (112, 112) |
| FB13 | Snowy bush | (8, 7) 1x1 | `bush_snow.png` | (128, 112) |
| FB20 | Snowy bush (berries) | (19, 12) 1x1 | `bush_snow_berries.png` | (304, 192) |
| FB21 | Snowy bush (berries) | (20, 12) 1x1 | `bush_snow_berries.png` | (320, 192) |
| FB22 | Snowy bush (berries) | (21, 12) 1x1 | `bush_snow_berries.png` | (336, 192) |
| FB23 | Snowy bush (berries) | (22, 12) 1x1 | `bush_snow_berries.png` | (352, 192) |
| DR1 | Snow drift | (21, 8) 2x1 | `snowdrift_wide.png` | (336, 128) |
| DR1b | Snow drift | (22, 9) 2x1 | `snowdrift_wide.png` | (352, 144) |
| DR2 | Snow drift | (5, 16) 2x1 | `snowdrift_wide.png` | (80, 256) |
| DR2b | Snow drift | (6, 17) 2x1 | `snowdrift_wide.png` | (96, 272) |
| SC | Snow-filled cart | (23, 16) 2x1 | `snow_cart.png` | (368, 240) |
| SH | Shovel | (10, 16) 1x1 | `shovel_stuck.png` | (160, 256) |
| L1 | Lamp post | (9, 6) 1x1 | `lamp_post.png` | (144, 64) |
| L2 | Lamp post | (19, 6) 1x1 | `lamp_post.png` | (304, 64) |
| L3 | Lamp post | (9, 14) 1x1 | `lamp_post.png` | (144, 192) |
| L4 | Lamp post | (19, 14) 1x1 | `lamp_post.png` | (304, 192) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| FD1 | French doors (lit) | wall | `french_doors_exterior.png` | (0, 64) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Woodpile - e.g. hidden tool / axe
- **C2** - Fountain - e.g. frozen object
- **C3** - Snow path - e.g. footprints
- **C4** - Snow drift - e.g. buried item

## NPC slots
- N1: Arthur Graves at tile (6, 14)
- N2: (open slot) at tile (20, 5)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Bare tree (1x1); Frozen fountain (4x3); Bench (3x1); Bench (3x1); Woodpile (2x1); Snowy bush (1x1); Snowy bush (1x1); Snowy bush (1x1); Snowy bush (1x1); Snowy bush (berries) (1x1); Snowy bush (berries) (1x1); Snowy bush (berries) (1x1); Snowy bush (berries) (1x1); Snow drift (2x1); Snow drift (2x1); Snow drift (2x1); Snow drift (2x1); Snow-filled cart (2x1); Shovel (1x1); Lamp post (1x1); Lamp post (1x1); Lamp post (1x1); Lamp post (1x1).
- Outdoor: the brick garden wall (north), the mansion wall (west), the picket fence (east and south) are solid. Snow, paths and footprints are walkable.
- D1 is OPTIONAL (Dining Room (OPTIONAL French doors)): can stay a decorative closed door.

# Kitchen - layout data

| | |
|---|---|
| Size | **16 x 12 tiles = 256 x 192 px** |
| Walkable interior | tiles x 1..14, y 2..10 (126 tiles, 96 walkable = 76%) |
| Wall style / floor | `kitchen` / `stone` |
| Tileset | `kitchen_tileset.png` (+ `kitchen_tileset.json` with every tile's cell) |
| Preview | `kitchen_preview.png` (256 x 192 px, 1:1) |

## Suggested player spawn
Tile **(2, 8)**. With a centred 32x32 `Sprite2D`, set the player node position to **(40, 129)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | W | [0, 8] .. [0, 9] | Main Hall | open | 0, 128, 16, 32 | (1, 8) |
| D2 | N | [12, 0] .. [13, 1] | Dining Room (service door) | open | 192, 0, 32, 32 | (12, 2) |
| D3 | E | [15, 4] .. [15, 5] | Snowy Backyard | open | 240, 64, 16, 32 | (14, 4) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| K7 | Pantry cabinet | (1, 2) 1x1 | `pantry_cabinet.png` | (16, 16) |
| K1 | Counter / cabinet | (2, 2) 2x1 | `kitchen_counter.png` | (32, 16) |
| K2 | Sink | (4, 2) 2x1 | `kitchen_sink.png` | (64, 16) |
| K4 | Stove | (6, 2) 2x1 | `stove_victorian.png` | (96, 16) |
| K3 | Prep counter | (8, 2) 2x1 | `kitchen_counter.png` | (128, 16) |
| K5 | Provisions shelf | (10, 2) 2x1 | `pots_shelf.png` | (160, 16) |
| K6 | Icebox | (14, 2) 1x1 | `icebox.png` | (224, 16) |
| IS | Kitchen island | (5, 5) 4x2 | `prep_island.png` | (80, 64) |
| ST | Staff table | (11, 8) 2x2 | `staff_table.png` | (176, 128) |
| K8 | Crate | (1, 10) 1x1 | `crate.png` | (16, 160) |
| K9 | Crates | (2, 10) 1x1 | `crate_stack.png` | (32, 144) |
| K11 | Sack | (3, 10) 1x1 | `sack.png` | (48, 160) |
| K12 | Barrel | (12, 10) 1x1 | `barrel.png` | (192, 160) |
| K10 | Wash tub | (13, 10) 2x1 | `wash_tub.png` | (208, 160) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| W1 | W1 | wall | `window_snow.png` | (64, 0) |
| WC1 | WC1 | wall | `wall_cabinet_pine.png` | (32, 0) |
| WC2 | WC2 | wall | `wall_cabinet_pine.png` | (128, 0) |
| PR | Hanging pots | wall | `pots_rack.png` | (88, 2) |
| X1 | Toppled chair | floor | `chair_toppled.png` | (144, 128) |
| X2 | Broken glass | floor | `glass_shards.png` | (112, 128) |
| CH | Lantern | over | `chandelier_small.png` | (96, 34) |
| rug | green rug (walkable) | floor | `rug_green_3x2.png` | tile (9, 3) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Stove - e.g. residue / pot
- **C2** - Island - e.g. knife block
- **C3** - Pantry - e.g. missing bottle
- **C4** - Back-door floor - e.g. tracks from outside
- **C5** - Broken glass - e.g. a dropped glass / vial

## NPC slots
- N1: Clara Whitmore at tile (3, 6)
- N2: (open slot) at tile (8, 9)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Pantry cabinet (1x1); Counter / cabinet (2x1); Sink (2x1); Stove (2x1); Prep counter (2x1); Provisions shelf (2x1); Icebox (1x1); Kitchen island (4x2); Staff table (2x2); Crate (1x1); Crates (1x1); Sack (1x1); Barrel (1x1); Wash tub (2x1).

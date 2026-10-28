# Main Hall - layout data

| | |
|---|---|
| Size | **20 x 16 tiles = 320 x 256 px** |
| Walkable interior | tiles x 1..18, y 2..14 (234 tiles, 196 walkable = 84%) |
| Wall style / floor | `burgundy` / `wood_dark` |
| Tileset | `main_hall_tileset.png` (+ `main_hall_tileset.json` with every tile's cell) |
| Preview | `main_hall_preview.png` (320 x 256 px, 1:1) |

## Suggested player spawn
Tile **(10, 12)**. With a centred 32x32 `Sprite2D`, set the player node position to **(168, 193)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | W | [0, 4] .. [0, 5] | Library / Study | open | 0, 64, 16, 32 | (1, 4) |
| D2 | W | [0, 11] .. [0, 12] | Guest Room | open | 0, 176, 16, 32 | (1, 11) |
| D3 | E | [19, 4] .. [19, 5] | Dining Room | open | 304, 64, 16, 32 | (18, 4) |
| D4 | E | [19, 11] .. [19, 12] | Kitchen | open | 304, 176, 16, 32 | (18, 11) |
| D5 | S | [8, 15] .. [11, 15] | Front entrance (blocked by snow) | blocked | 128, 240, 64, 16 | (8, 14) |
| D6 | N | [7, 0] .. [12, 1] | Upstairs / Master Bedroom (inaccessible in v1) | blocked | 112, 0, 96, 32 | (7, 2) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| F1 | Fireplace | (2, 2) 3x1 | `fireplace_lit.png` | (32, 16) |
| F3 | Grandfather clock | (6, 2) 1x1 | `grandfather_clock.png` | (96, 16) |
| ST | Grand staircase (blocked) | (7, 2) 6x3 | `grand_staircase.png` | (112, 0) |
| F4 | Potted plant | (13, 2) 1x1 | `plant_potted.png` | (208, 16) |
| F2 | Console table | (15, 2) 3x1 | `table_console.png` | (240, 16) |
| F5 | Bench | (3, 14) 3x1 | `bench_indoor.png` | (48, 224) |
| F6 | Bench | (14, 14) 3x1 | `bench_indoor.png` | (224, 224) |
| F7 | Coat stand | (7, 14) 1x1 | `coat_stand.png` | (112, 208) |
| F8 | Umbrella stand | (12, 14) 1x1 | `umbrella_stand.png` | (192, 224) |
| SD | Snow drift (blocks front door) | (8, 14) 4x1 | `invisible` | () |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| FD | Front doors, snowed in | wall | `front_door_snowed.png` | (128, 224) |
| P1 | P1 | wall | `painting_portrait.png` | (16, 0) |
| P2 | P2 | wall | `painting_landscape.png` | (40, 0) |
| S1 | S1 | wall | `wall_sconce.png` | (80, 2) |
| S2 | S2 | wall | `wall_sconce.png` | (224, 2) |
| P3 | P3 | wall | `painting_small.png` | (208, 0) |
| P4 | P4 | wall | `painting_landscape.png` | (248, 0) |
| P5 | Slashed portrait | wall | `painting_portrait_damaged.png` | (288, 0) |
| T1 | T1 | top | `candlestick.png` | (244, 10) |
| T2 | T2 | top | `vase_flowers.png` | (270, 12) |
| CH | Chandelier | over | `chandelier_large.png` | (136, 118) |
| rug | burgundy rug (walkable) | floor | `rug_burgundy_8x6.png` | tile (6, 6) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Fireplace - e.g. ashes / burnt paper
- **C2** - Console table - e.g. letters / guest ledger
- **C3** - Grandfather clock - e.g. stopped clock
- **C4** - Entry floor - e.g. wet footprints
- **C5** - Slashed portrait - e.g. something hidden behind it

## NPC slots
- N1: Victoria Blackwood at tile (3, 8)
- N2: Thomas Hale at tile (16, 8)
- N3: Dr. Elias Warren at tile (10, 9)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Fireplace (3x1); Grandfather clock (1x1); Grand staircase (blocked) (6x3); Potted plant (1x1); Console table (3x1); Bench (3x1); Bench (3x1); Coat stand (1x1); Umbrella stand (1x1); Snow drift (blocks front door) (4x1).
- D5 is BLOCKED in v1 (Front entrance (blocked by snow)): keep it solid.
- D6 is BLOCKED in v1 (Upstairs / Master Bedroom (inaccessible in v1)): keep it solid.

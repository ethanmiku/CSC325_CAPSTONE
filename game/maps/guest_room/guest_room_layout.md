# Guest Room - layout data

| | |
|---|---|
| Size | **14 x 10 tiles = 224 x 160 px** |
| Walkable interior | tiles x 1..12, y 2..8 (84 tiles, 61 walkable = 73%) |
| Wall style / floor | `guest` / `wood_light` |
| Tileset | `guest_room_tileset.png` (+ `guest_room_tileset.json` with every tile's cell) |
| Preview | `guest_room_preview.png` (224 x 160 px, 1:1) |

## Suggested player spawn
Tile **(12, 6)**. With a centred 32x32 `Sprite2D`, set the player node position to **(200, 97)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | E | [13, 6] .. [13, 7] | Main Hall | open | 208, 96, 16, 32 | (12, 6) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| N1s | Nightstand | (1, 2) 1x1 | `nightstand_guest.png` | (16, 16) |
| BD | Single bed (2x3) | (2, 2) 2x3 | `bed_single_2x3.png` | (32, 32) |
| N2s | Nightstand | (4, 2) 1x1 | `nightstand_guest.png` | (64, 16) |
| WD | Wardrobe | (8, 2) 2x1 | `wardrobe_guest.png` | (128, 0) |
| DK | Writing desk | (10, 2) 3x1 | `desk_small.png` | (160, 16) |
| CH | Desk chair | (11, 3) 1x1 | `chair_dining_s.png` | (176, 32) |
| DR | Dresser | (1, 8) 3x1 | `table_console.png` | (16, 112) |
| MR | Standing mirror | (4, 8) 1x1 | `standing_mirror.png` | (64, 112) |
| TR | Suitcase | (3, 5) 1x1 | `suitcase_closed.png` | (48, 80) |
| SO | Open suitcase | (9, 7) 1x1 | `suitcase_open.png` | (144, 112) |
| WS | Washstand | (7, 8) 1x1 | `table_side.png` | (112, 112) |
| AC | Armchair | (11, 8) 2x1 | `armchair_w.png` | (176, 112) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| W1 | W1 | wall | `window_snow_curtains_blue.png` | (80, 0) |
| S1 | S1 | wall | `wall_sconce.png` | (112, 2) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 80) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (208, 32) |
| P1 | P1 | wall | `painting_small.png` | (128, 0) |
| P2 | P2 | wall | `painting_landscape.png` | (184, 2) |
| T1 | Wilted flowers | top | `vase_wilted.png` | (24, 106) |
| CH2 | Lamp | over | `chandelier_small.png` | (96, 56) |
| rug | blue rug (walkable) | floor | `rug_blue_5x3.png` | tile (5, 4) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Bed - e.g. under mattress
- **C2** - Wardrobe - e.g. hidden clothing
- **C3** - Suitcase - e.g. luggage / documents
- **C4** - Writing desk - e.g. unsent letter

## NPC slots
- N1: (open slot) at tile (7, 6)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Nightstand (1x1); Single bed (2x3) (2x3); Nightstand (1x1); Wardrobe (2x1); Writing desk (3x1); Desk chair (1x1); Dresser (3x1); Standing mirror (1x1); Suitcase (1x1); Open suitcase (1x1); Washstand (1x1); Armchair (2x1).

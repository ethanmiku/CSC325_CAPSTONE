# Dining Room - layout data

| | |
|---|---|
| Size | **18 x 12 tiles = 288 x 192 px** |
| Walkable interior | tiles x 1..16, y 2..10 (144 tiles, 114 walkable = 79%) |
| Wall style / floor | `burgundy` / `wood_dark` |
| Tileset | `dining_room_tileset.png` (+ `dining_room_tileset.json` with every tile's cell) |
| Preview | `dining_room_preview.png` (288 x 192 px, 1:1) |

## Suggested player spawn
Tile **(2, 3)**. With a centred 32x32 `Sprite2D`, set the player node position to **(40, 49)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | W | [0, 3] .. [0, 4] | Main Hall | open | 0, 48, 16, 32 | (1, 3) |
| D2 | S | [12, 11] .. [13, 11] | Kitchen (service door) | open | 192, 176, 32, 16 | (12, 10) |
| D3 | E | [17, 3] .. [17, 4] | Snowy Backyard (OPTIONAL French doors) | optional | 272, 48, 16, 32 | (16, 3) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| F1 | Fireplace | (7, 2) 3x1 | `fireplace_lit.png` | (112, 16) |
| F2 | China cabinet | (12, 2) 2x1 | `display_cabinet.png` | (192, 16) |
| TB | Dining table (burgundy runner) | (6, 6) 6x2 | `dining_table_set.png` | (96, 80) |
| H1 | Chair (head, west) | (5, 6) 1x1 | `chair_dining_e.png` | (80, 80) |
| H2 | Chair (head, east) | (12, 7) 1x1 | `chair_dining_w.png` | (192, 96) |
| C1a | C1a | (6, 5) 1x1 | `chair_dining_s.png` | (96, 64) |
| C1b | C1b | (8, 5) 1x1 | `chair_dining_s.png` | (128, 64) |
| C1c | C1c | (10, 5) 1x1 | `chair_dining_s.png` | (160, 64) |
| C2a | C2a | (7, 8) 1x1 | `chair_dining_n.png` | (112, 112) |
| C2b | C2b | (9, 8) 1x1 | `chair_dining_n.png` | (144, 112) |
| C2c | C2c | (11, 8) 1x1 | `chair_dining_n.png` | (176, 112) |
| F3 | Sideboard | (2, 10) 3x1 | `sideboard.png` | (32, 144) |
| F4 | Serving cart | (14, 10) 2x1 | `serving_cart.png` | (224, 144) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| W1 | W1 | wall | `window_snow_curtains_burgundy.png` | (16, 0) |
| W2 | CRACKED window | wall | `window_cracked.png` | (64, 0) |
| W3 | W3 | wall | `window_snow_curtains_burgundy.png` | (240, 0) |
| P1 | P1 | wall | `painting_landscape.png` | (120, 0) |
| P2 | Slashed portrait | wall | `painting_portrait_damaged.png` | (160, 0) |
| P3 | P3 | wall | `painting_small.png` | (224, 0) |
| S1 | S1 | wall | `wall_sconce.png` | (96, 2) |
| S2 | S2 | wall | `wall_sconce.png` | (176, 2) |
| CW | CW | wall | `cobweb_corner.png` | (48, 16) |
| X1 | Wine stain | floor | `wine_stain.png` | (208, 128) |
| X2 | Glass under cracked window | floor | `glass_shards.png` | (64, 48) |
| X3 | Toppled chair | floor | `chair_toppled.png` | (224, 80) |
| CH | Chandelier | over | `chandelier_large.png` | (120, 78) |
| rug | burgundy rug (walkable) | floor | `rug_burgundy_10x6.png` | tile (4, 4) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Dining table - e.g. place settings / glass
- **C2** - Fireplace - e.g. burnt letter
- **C3** - Sideboard - e.g. decanter
- **C4** - China cabinet - e.g. missing item
- **C5** - Cracked window - e.g. how someone got in / out

## NPC slots
- N1: Marcus Blackwood at tile (3, 7)
- N2: Thomas Hale at tile (15, 6)
- N3: Clara Whitmore at tile (15, 9)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Fireplace (3x1); China cabinet (2x1); Dining table (burgundy runner) (6x2); Chair (head, west) (1x1); Chair (head, east) (1x1); C1a (1x1); C1b (1x1); C1c (1x1); C2a (1x1); C2b (1x1); C2c (1x1); Sideboard (3x1); Serving cart (2x1).
- D3 is OPTIONAL (Snowy Backyard (OPTIONAL French doors)): can stay a decorative closed door.

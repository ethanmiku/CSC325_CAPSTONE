# Guest Room B - layout data

| | |
|---|---|
| Size | **22 x 16 tiles = 352 x 256 px** |
| Walkable interior | tiles x 1..20, y 2..14 (260 tiles, 200 walkable = 77%) |
| Wall style / floor | `guest` / `wood_light` |
| Tileset | `guest_room_b_tileset.png` (+ `guest_room_b_tileset.json` with every tile's cell) |
| Preview | `guest_room_b_preview.png` (352 x 256 px, 1:1) |

## Suggested player spawn
Tile **(10, 12)**. With a centred 32x32 `Sprite2D`, set the player node position to **(168, 193)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | S | [10, 15] .. [11, 15] | Upstairs Hallway | open | 160, 240, 32, 16 | (10, 14) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| NS1 | Nightstand (bed 1) | (1, 2) 1x1 | `nightstand_guest.png` | (16, 16) |
| BD1 | Single bed 1 (blue) | (2, 2) 2x3 | `bed_single_blue.png` | (32, 32) |
| NS2 | Nightstand (bed 2) | (5, 2) 1x1 | `nightstand_guest.png` | (80, 16) |
| BD2 | Single bed 2 (green) | (6, 2) 2x3 | `bed_single_green.png` | (96, 32) |
| FP | Fireplace | (9, 2) 3x1 | `fireplace_lit.png` | (144, 16) |
| NS3 | Nightstand (bed 3) | (13, 2) 1x1 | `nightstand_guest.png` | (208, 16) |
| BD3 | Single bed 3 (ochre) | (14, 2) 2x3 | `bed_single_ochre.png` | (224, 32) |
| NS4 | Nightstand (bed 4) | (17, 2) 1x1 | `nightstand_guest.png` | (272, 16) |
| BD4 | Single bed 4 (plum) | (18, 2) 2x3 | `bed_single_plum.png` | (288, 32) |
| TR1 | Trunk (bed 1) | (2, 5) 2x1 | `trunk_master.png` | (32, 80) |
| TR2 | Trunk (bed 2) | (6, 5) 2x1 | `trunk_master.png` | (96, 80) |
| TR3 | Trunk (bed 3) | (14, 5) 2x1 | `trunk_master.png` | (224, 80) |
| TR4 | Trunk (bed 4) | (18, 5) 2x1 | `trunk_master.png` | (288, 80) |
| SF | Sofa | (9, 8) 3x1 | `sofa_s.png` | (144, 112) |
| TS | Tea table | (10, 9) 1x1 | `table_side.png` | (160, 128) |
| AE | Armchair (west) | (7, 9) 2x1 | `armchair_e.png` | (112, 128) |
| AW | Armchair (east) | (12, 9) 2x1 | `armchair_w.png` | (192, 128) |
| WD1 | Wardrobe 1 | (2, 14) 2x1 | `wardrobe_guest.png` | (32, 192) |
| WD2 | Wardrobe 2 | (5, 14) 2x1 | `wardrobe_guest.png` | (80, 192) |
| MR | Standing mirror | (8, 14) 1x1 | `standing_mirror.png` | (128, 208) |
| WS | Washstand | (13, 14) 1x1 | `table_side.png` | (208, 208) |
| DR | Dresser | (15, 14) 3x1 | `dresser_master.png` | (240, 208) |
| WD3 | Wardrobe 3 | (18, 14) 2x1 | `wardrobe_guest.png` | (288, 192) |
| PL1 | Potted plant | (1, 12) 1x1 | `plant_potted.png` | (16, 176) |
| PL2 | Potted plant | (20, 12) 1x1 | `plant_potted.png` | (320, 176) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| DS1 | Door to the hallway | wall | `door_s_closed.png` | (160, 240) |
| W1 | W1 | wall | `window_snow_curtains_blue.png` | (32, 0) |
| W2 | W2 | wall | `window_snow_curtains_green.png` | (96, 0) |
| W3 | W3 | wall | `window_snow_curtains_ochre.png` | (224, 0) |
| W4 | W4 | wall | `window_snow_curtains_plum.png` | (288, 0) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 112) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (336, 112) |
| P1 | P1 | wall | `painting_landscape.png` | (168, 0) |
| S1 | S1 | wall | `wall_sconce.png` | (128, 2) |
| S2 | S2 | wall | `wall_sconce.png` | (192, 2) |
| T1 | T1 | top | `candlestick.png` | (16, 17) |
| T2 | T2 | top | `candlestick.png` | (80, 17) |
| T3 | T3 | top | `candlestick.png` | (208, 17) |
| T4 | T4 | top | `candlestick.png` | (272, 17) |
| C1 | Chandelier | over | `chandelier_large.png` | (136, 76) |
| rug | o_sapphire rug (walkable) | floor | `rug_o_sapphire_13x6.png` | tile (4, 7) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Trunk at the foot of bed 3 - placeholder clue spot
- **C2** - Fireplace - placeholder clue spot
- **C3** - Wardrobe 1 - placeholder clue spot
- **C4** - Dresser - placeholder clue spot

## NPC slots
- N1: (open slot - guest 1) at tile (4, 10)
- N2: (open slot - guest 2) at tile (17, 10)
- N3: (open slot - guest 3) at tile (7, 12)
- N4: (open slot - guest 4) at tile (14, 12)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Nightstand (bed 1) (1x1); Single bed 1 (blue) (2x3); Nightstand (bed 2) (1x1); Single bed 2 (green) (2x3); Fireplace (3x1); Nightstand (bed 3) (1x1); Single bed 3 (ochre) (2x3); Nightstand (bed 4) (1x1); Single bed 4 (plum) (2x3); Trunk (bed 1) (2x1); Trunk (bed 2) (2x1); Trunk (bed 3) (2x1); Trunk (bed 4) (2x1); Sofa (3x1); Tea table (1x1); Armchair (west) (2x1); Armchair (east) (2x1); Wardrobe 1 (2x1); Wardrobe 2 (2x1); Standing mirror (1x1); Washstand (1x1); Dresser (3x1); Wardrobe 3 (2x1); Potted plant (1x1); Potted plant (1x1).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_hallway` | (176, 193) | UP | arrive from the hallway |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Upstairs Hallway) | `upstairs_hallway` | `from_guest_room_b` | 160, 224, 32, 32 | down |

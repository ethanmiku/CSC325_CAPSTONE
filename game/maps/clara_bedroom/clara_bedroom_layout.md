# Clara Blackwood's Bedroom - layout data

| | |
|---|---|
| Size | **16 x 14 tiles = 256 x 224 px** |
| Walkable interior | tiles x 1..14, y 2..12 (154 tiles, 120 walkable = 78%) |
| Wall style / floor | `clara` / `wood_dark` |
| Tileset | `clara_bedroom_tileset.png` (+ `clara_bedroom_tileset.json` with every tile's cell) |
| Preview | `clara_bedroom_preview.png` (256 x 224 px, 1:1) |

## Suggested player spawn
Tile **(7, 4)**. With a centred 32x32 `Sprite2D`, set the player node position to **(120, 65)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | N | [7, 0] .. [8, 1] | Upstairs Hallway | open | 112, 0, 32, 32 | (7, 2) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| WD | Wardrobe | (1, 2) 2x1 | `wardrobe_clara.png` | (16, 0) |
| VN | Vanity with mirror | (5, 2) 2x1 | `vanity_clara.png` | (80, 0) |
| NS1 | Nightstand (lamp) | (9, 2) 1x1 | `nightstand_clara.png` | (144, 16) |
| BD | Canopy bed | (10, 2) 3x3 | `bed_canopy_clara.png` | (160, 16) |
| NS2 | Nightstand (lamp) | (13, 2) 1x1 | `nightstand_clara.png` | (208, 16) |
| PL1 | Potted plant | (14, 4) 1x1 | `plant_potted.png` | (224, 48) |
| SC | Dressing screen | (1, 10) 3x1 | `dressing_screen.png` | (16, 144) |
| DK | Writing desk | (5, 12) 3x1 | `desk_clara.png` | (80, 176) |
| CH | Desk chair | (6, 11) 1x1 | `chair_clara_s.png` | (96, 160) |
| BK | Bookshelf | (10, 12) 2x1 | `bookshelf_tall.png` | (160, 176) |
| LP | Floor lamp | (13, 12) 1x1 | `floor_lamp.png` | (208, 176) |
| AC | Armchair | (9, 6) 2x1 | `armchair_clara_s.png` | (144, 80) |
| TT | Tea table | (10, 8) 2x1 | `table_round_clara.png` | (160, 112) |
| LV | Loveseat | (13, 7) 2x2 | `loveseat_w_clara.png` | (208, 112) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| DN1 | Door to the hallway | wall | `door_n_closed.png` | (112, 0) |
| W1 | W1 | wall | `window_snow_curtains_lilac.png` | (48, 0) |
| P1 | P1 | wall | `painting_landscape.png` | (168, 0) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 96) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (240, 80) |
| T2 | T2 | top | `candlestick.png` | (82, 180) |
| T1 | T1 | top | `vase_flowers.png` | (168, 122) |
| C1 | Chandelier | over | `chandelier_small.png` | (112, 92) |
| rug | o_lilac rug (walkable) | floor | `rug_o_lilac_8x6.png` | tile (3, 5) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Canopy bed - placeholder clue spot
- **C2** - Vanity - placeholder clue spot
- **C3** - Writing desk - placeholder clue spot
- **C4** - Wardrobe - placeholder clue spot

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Wardrobe (2x1); Vanity with mirror (2x1); Nightstand (lamp) (1x1); Canopy bed (3x3); Nightstand (lamp) (1x1); Potted plant (1x1); Dressing screen (3x1); Writing desk (3x1); Desk chair (1x1); Bookshelf (2x1); Floor lamp (1x1); Armchair (2x1); Tea table (2x1); Loveseat (2x2).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_hallway` | (128, 65) | DOWN | arrive from the hallway |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Upstairs Hallway) | `upstairs_hallway` | `from_clara_bedroom` | 112, 0, 32, 48 | up |

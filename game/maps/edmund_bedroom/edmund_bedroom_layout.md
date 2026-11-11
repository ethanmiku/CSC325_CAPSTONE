# Edmund Blackwood's Bedroom - layout data

| | |
|---|---|
| Size | **16 x 14 tiles = 256 x 224 px** |
| Walkable interior | tiles x 1..14, y 2..12 (154 tiles, 110 walkable = 71%) |
| Wall style / floor | `master` / `parquet` |
| Tileset | `edmund_bedroom_tileset.png` (+ `edmund_bedroom_tileset.json` with every tile's cell) |
| Preview | `edmund_bedroom_preview.png` (256 x 224 px, 1:1) |

## Suggested player spawn
Tile **(7, 4)**. With a centred 32x32 `Sprite2D`, set the player node position to **(120, 65)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | N | [7, 0] .. [8, 1] | Upstairs Hallway | open | 112, 0, 32, 32 | (7, 2) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| PL1 | Potted plant | (1, 2) 1x1 | `plant_potted.png` | (16, 16) |
| FP | Fireplace | (2, 2) 3x1 | `fireplace_lit.png` | (32, 16) |
| NS1 | Nightstand (lamp) | (9, 2) 1x1 | `nightstand_master.png` | (144, 16) |
| BD | Large four-poster bed | (10, 2) 4x3 | `bed_large_master.png` | (160, 16) |
| NS2 | Nightstand (lamp) | (14, 2) 1x1 | `nightstand_master.png` | (224, 16) |
| TR | Trunk at the foot of the bed | (11, 5) 2x1 | `trunk_master.png` | (176, 80) |
| DK | Writing desk | (1, 8) 4x2 | `writing_desk.png` | (16, 112) |
| CH | Desk chair | (2, 7) 1x1 | `chair_dining_s.png` | (32, 96) |
| WD | Grand wardrobe | (2, 12) 3x1 | `wardrobe_master.png` | (32, 160) |
| BK | Bookshelf | (6, 12) 2x1 | `bookshelf_tall.png` | (96, 176) |
| DR | Dresser | (9, 12) 3x1 | `dresser_master.png` | (144, 176) |
| LV | Loveseat | (13, 7) 2x2 | `loveseat_w_burgundy.png` | (208, 112) |
| TS | Side table | (12, 7) 1x1 | `table_side.png` | (192, 96) |
| LP | Floor lamp | (14, 10) 1x1 | `floor_lamp.png` | (224, 144) |
| MR | Standing mirror | (8, 12) 1x1 | `standing_mirror.png` | (128, 176) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| DN1 | Door to the hallway | wall | `door_n_closed.png` | (112, 0) |
| P1 | P1 | wall | `painting_landscape.png` | (40, 0) |
| P3 | Family crest | wall | `wall_crest.png` | (184, 0) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 96) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (240, 80) |
| T1 | T1 | top | `papers_pile.png` | (24, 124) |
| T2 | T2 | top | `inkwell_quill.png` | (56, 122) |
| WI | WI | wall | `window_snow_curtains_burgundy.png` | (80, 0) |
| P2 | P2 | wall | `painting_small.png` | (144, 0) |
| P4 | P4 | wall | `painting_small.png` | (16, 0) |
| T3 | T3 | top | `vase_flowers.png` | (192, 106) |
| C1 | Chandelier | over | `chandelier_large.png` | (104, 100) |
| rug | o_burgundy rug (walkable) | floor | `rug_o_burgundy_8x6.png` | tile (4, 5) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Bed - placeholder clue spot
- **C2** - Writing desk - placeholder clue spot
- **C3** - Dresser - placeholder clue spot
- **C4** - Fireplace - placeholder clue spot
- **C5** - Wardrobe - placeholder clue spot

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Potted plant (1x1); Fireplace (3x1); Nightstand (lamp) (1x1); Large four-poster bed (4x3); Nightstand (lamp) (1x1); Trunk at the foot of the bed (2x1); Writing desk (4x2); Desk chair (1x1); Grand wardrobe (3x1); Bookshelf (2x1); Dresser (3x1); Loveseat (2x2); Side table (1x1); Floor lamp (1x1); Standing mirror (1x1).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_hallway` | (128, 65) | DOWN | arrive from the hallway |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Upstairs Hallway) | `upstairs_hallway` | `from_edmund_bedroom` | 112, 0, 32, 48 | up |

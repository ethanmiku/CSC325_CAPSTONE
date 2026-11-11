# Grand Study - layout data

| | |
|---|---|
| Size | **24 x 18 tiles = 384 x 288 px** |
| Walkable interior | tiles x 1..22, y 2..16 (330 tiles, 275 walkable = 83%) |
| Wall style / floor | `study` / `parquet` |
| Tileset | `grand_study_tileset.png` (+ `grand_study_tileset.json` with every tile's cell) |
| Preview | `grand_study_preview.png` (384 x 288 px, 1:1) |

## Suggested player spawn
Tile **(11, 14)**. With a centred 32x32 `Sprite2D`, set the player node position to **(184, 225)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | S | [11, 17] .. [12, 17] | Upstairs Hallway | open | 176, 272, 32, 16 | (11, 16) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| B1 | Bookshelf (west) | (1, 2) 3x1 | `library_shelf_mahogany.png` | (16, 0) |
| B2 | Bookshelf (east) | (19, 2) 3x1 | `library_shelf_mahogany_b.png` | (304, 0) |
| FP | Fireplace | (10, 2) 3x1 | `fireplace_mahogany.png` | (160, 16) |
| LP0 | Floor lamp | (22, 2) 1x1 | `floor_lamp.png` | (352, 16) |
| DK | Large executive writing desk | (10, 9) 5x2 | `desk_executive.png` | (160, 128) |
| CH1 | Executive chair | (12, 8) 1x1 | `chair_executive_s.png` | (192, 112) |
| CH2 | Visitor chair | (11, 11) 1x1 | `chair_leather_n.png` | (176, 160) |
| CH3 | Visitor chair | (13, 11) 1x1 | `chair_leather_n.png` | (208, 160) |
| SA | Chesterfield (west) | (2, 8) 2x3 | `chesterfield_e.png` | (32, 128) |
| SB | Chesterfield (east) | (20, 8) 2x3 | `chesterfield_w.png` | (320, 128) |
| GL | Antique globe | (20, 5) 2x1 | `globe_grand.png` | (320, 64) |
| RA1 | Reading chair (west) | (1, 13) 2x1 | `armchair_leather_e.png` | (16, 192) |
| RT | Reading table | (3, 13) 1x1 | `table_side_mahogany.png` | (48, 192) |
| RA2 | Reading chair (east) | (4, 13) 2x1 | `armchair_leather_w.png` | (64, 192) |
| LP1 | Floor lamp | (6, 13) 1x1 | `floor_lamp.png` | (96, 192) |
| LP2 | Floor lamp | (17, 13) 1x1 | `floor_lamp.png` | (272, 192) |
| BS | Bookshelf (south-east) | (18, 14) 2x1 | `bookshelf_mahogany.png` | (288, 208) |
| DC | Decorative cabinet (decanters) | (2, 16) 2x1 | `cabinet_decanters.png` | (32, 224) |
| SBD | Mahogany sideboard | (19, 16) 3x1 | `sideboard_mahogany.png` | (304, 240) |
| CO1 | Column | (9, 16) 1x1 | `column_decor.png` | (144, 224) |
| CO2 | Column | (14, 16) 1x1 | `column_decor.png` | (224, 224) |
| PL1 | Potted plant | (1, 16) 1x1 | `plant_potted.png` | (16, 240) |
| CF | Candelabra | (22, 16) 1x1 | `candelabra_floor.png` | (352, 240) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| DS1 | Door to the hallway | wall | `door_s_closed.png` | (176, 272) |
| WG1 | WG1 | wall | `window_grand_snow_curtains_burgundy.png` | (96, 0) |
| WG2 | WG2 | wall | `window_grand_snow_curtains_burgundy.png` | (224, 0) |
| MP | Antique map | wall | `wall_map_antique.png` | (64, 0) |
| P1 | P1 | wall | `painting_landscape.png` | (168, 0) |
| P2 | P2 | wall | `painting_portrait_gentleman.png` | (144, 0) |
| P3 | P3 | wall | `painting_portrait_lady.png` | (208, 0) |
| P4 | P4 | wall | `painting_portrait_elder.png` | (272, 0) |
| P5 | P5 | wall | `painting_portrait_gentleman.png` | (288, 0) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 80) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (0, 176) |
| WN3 | WN3 | wall | `window_small_frosted.png` | (368, 80) |
| WN4 | WN4 | wall | `window_small_frosted.png` | (368, 208) |
| T0 | T0 | top | `desk_lamp.png` | (166, 124) |
| T1 | T1 | top | `papers_pile.png` | (190, 134) |
| T2 | T2 | top | `open_book.png` | (210, 138) |
| T3 | T3 | top | `inkwell_quill.png` | (230, 132) |
| T4 | T4 | top | `candlestick.png` | (48, 202) |
| C1 | Chandelier | over | `chandelier_large.png` | (168, 52) |
| rug | o_crimson rug (walkable) | floor | `rug_o_crimson_14x9.png` | tile (5, 5) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Large executive desk - placeholder clue spot
- **C2** - Fireplace - placeholder clue spot
- **C3** - Decorative cabinet - placeholder clue spot
- **C4** - Antique globe - placeholder clue spot
- **C5** - Bookshelf - placeholder clue spot

## NPC slots
- N1: (open slot) at tile (8, 12)
- N2: (open slot) at tile (16, 12)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Bookshelf (west) (3x1); Bookshelf (east) (3x1); Fireplace (3x1); Floor lamp (1x1); Large executive writing desk (5x2); Executive chair (1x1); Visitor chair (1x1); Visitor chair (1x1); Chesterfield (west) (2x3); Chesterfield (east) (2x3); Antique globe (2x1); Reading chair (west) (2x1); Reading table (1x1); Reading chair (east) (2x1); Floor lamp (1x1); Floor lamp (1x1); Bookshelf (south-east) (2x1); Decorative cabinet (decanters) (2x1); Mahogany sideboard (3x1); Column (1x1); Column (1x1); Potted plant (1x1); Candelabra (1x1).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_hallway` | (192, 225) | UP | arrive from the hallway |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Upstairs Hallway) | `upstairs_hallway` | `from_grand_study` | 176, 256, 32, 32 | down |

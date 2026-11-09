# Upstairs Hallway - layout data

| | |
|---|---|
| Size | **36 x 10 tiles = 576 x 160 px** |
| Walkable interior | tiles x 1..34, y 2..8 (238 tiles, 208 walkable = 87%) |
| Wall style / floor | `burgundy` / `wood_dark` |
| Tileset | `upstairs_hallway_tileset.png` (+ `upstairs_hallway_tileset.json` with every tile's cell) |
| Preview | `upstairs_hallway_preview.png` (576 x 160 px, 1:1) |

## Suggested player spawn
Tile **(17, 6)**. With a centred 32x32 `Sprite2D`, set the player node position to **(280, 97)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | N | [5, 0] .. [6, 1] | Curio Room | open | 80, 0, 32, 32 | (5, 2) |
| D2 | N | [17, 0] .. [18, 1] | Guest Room B | open | 272, 0, 32, 32 | (17, 2) |
| D3 | N | [29, 0] .. [30, 1] | Grand Study / Library | open | 464, 0, 32, 32 | (29, 2) |
| D4 | S | [5, 9] .. [6, 9] | Edmund Blackwood's Bedroom | open | 80, 144, 32, 16 | (5, 8) |
| D5 | S | [16, 9] .. [19, 9] | Stairs down to the Main Hall | open | 256, 144, 64, 16 | (16, 8) |
| D6 | S | [29, 9] .. [30, 9] | Clara Blackwood's Bedroom | open | 464, 144, 32, 16 | (29, 8) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| CK | Grandfather clock | (15, 2) 1x1 | `grandfather_clock.png` | (240, 16) |
| PL1 | Potted plant | (1, 2) 1x1 | `plant_potted.png` | (16, 16) |
| PL2 | Potted plant | (20, 2) 1x1 | `plant_potted.png` | (320, 16) |
| PL3 | Potted plant | (34, 2) 1x1 | `plant_potted.png` | (544, 16) |
| TB1 | Console table (west) | (10, 8) 3x1 | `table_console.png` | (160, 112) |
| TB2 | Console table (east) | (23, 8) 3x1 | `table_console.png` | (368, 112) |
| LP1 | Floor lamp | (2, 7) 1x1 | `floor_lamp.png` | (32, 96) |
| LP2 | Floor lamp | (33, 7) 1x1 | `floor_lamp.png` | (528, 96) |
| CD1 | Candelabra | (8, 8) 1x1 | `candelabra_floor.png` | (128, 112) |
| CD2 | Candelabra | (27, 8) 1x1 | `candelabra_floor.png` | (432, 112) |
| CO1 | Column | (14, 7) 1x1 | `column_decor.png` | (224, 80) |
| CO2 | Column | (21, 7) 1x1 | `column_decor.png` | (336, 80) |
| RL | Stair rail (west) | (15, 7) 1x2 | `invisible` | () |
| RR | Stair rail (east) | (20, 7) 1x2 | `invisible` | () |
| SE1 | Green velvet settee (west) | (10, 2) 2x1 | `settee_green_s.png` | (160, 16) |
| SE2 | Green velvet settee (east) | (24, 2) 2x1 | `settee_green_s.png` | (384, 16) |
| DC1 | Small display cabinet (west) | (12, 2) 2x1 | `display_cabinet.png` | (192, 16) |
| DC2 | Small display cabinet (east) | (22, 2) 2x1 | `display_cabinet.png` | (352, 16) |
| ST1 | Side table (west) | (9, 2) 1x1 | `table_side_mahogany.png` | (144, 16) |
| ST2 | Side table (east) | (26, 2) 1x1 | `table_side_mahogany.png` | (416, 16) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| RN | Burgundy carpet runner | floor | `runner_burgundy_32x3.png` | (32, 64) |
| ST | Staircase down to the Main Hall | wall | `stairwell_down.png` | (240, 112) |
| DN1 | Guest Room A door | wall | `door_n_closed.png` | (80, 0) |
| DN2 | Guest Room B door | wall | `door_n_closed.png` | (272, 0) |
| DN3 | Grand Study door | wall | `door_n_closed.png` | (464, 0) |
| DS1 | Edmund's Bedroom door | wall | `door_s_closed.png` | (80, 144) |
| DS2 | Clara's Bedroom door | wall | `door_s_closed.png` | (464, 144) |
| W1 | W1 | wall | `window_snow_curtains_burgundy.png` | (160, 0) |
| W2 | W2 | wall | `window_snow_curtains_burgundy.png` | (384, 0) |
| P1 | P1 | wall | `painting_portrait_lady.png` | (32, 0) |
| P2 | P2 | wall | `painting_portrait_gentleman.png` | (128, 0) |
| P5 | P5 | wall | `painting_portrait_lady.png` | (432, 0) |
| P6 | P6 | wall | `painting_portrait_gentleman.png` | (528, 0) |
| S1 | S1 | wall | `wall_sconce.png` | (64, 2) |
| S2 | S2 | wall | `wall_sconce.png` | (112, 2) |
| S3 | S3 | wall | `wall_sconce.png` | (256, 2) |
| S4 | S4 | wall | `wall_sconce.png` | (304, 2) |
| S5 | S5 | wall | `wall_sconce.png` | (448, 2) |
| S6 | S6 | wall | `wall_sconce.png` | (496, 2) |
| T1 | T1 | top | `candlestick.png` | (164, 106) |
| T2 | T2 | top | `vase_flowers.png` | (190, 108) |
| T3 | T3 | top | `candlestick.png` | (372, 106) |
| T4 | T4 | top | `vase_flowers.png` | (398, 108) |
| C1 | Chandelier | over | `chandelier_small.png` | (96, 56) |
| C2 | Chandelier | over | `chandelier_small.png` | (272, 56) |
| C3 | Chandelier | over | `chandelier_small.png` | (448, 56) |
| P3 | P3 | wall | `painting_small.png` | (200, 0) |
| P4 | P4 | wall | `painting_small.png` | (360, 0) |
| T5 | T5 | top | `candlestick.png` | (144, 17) |
| T6 | T6 | top | `vase_flowers.png` | (416, 17) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Grandfather clock - placeholder clue spot
- **C2** - West console table - placeholder clue spot
- **C3** - East console table - placeholder clue spot
- **C4** - West display cabinet - placeholder clue spot

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Grandfather clock (1x1); Potted plant (1x1); Potted plant (1x1); Potted plant (1x1); Console table (west) (3x1); Console table (east) (3x1); Floor lamp (1x1); Floor lamp (1x1); Candelabra (1x1); Candelabra (1x1); Column (1x1); Column (1x1); Stair rail (west) (1x2); Stair rail (east) (1x2); Green velvet settee (west) (2x1); Green velvet settee (east) (2x1); Small display cabinet (west) (2x1); Small display cabinet (east) (2x1); Side table (west) (1x1); Side table (east) (1x1).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_main_hall` | (288, 81) | UP | arrive from the Main Hall staircase (centre of the 4-wide stair opening) |
| `from_curio_room` | (96, 65) | DOWN | arrive from the Curio Room |
| `from_guest_room_b` | (288, 65) | DOWN | arrive from Guest Room B |
| `from_grand_study` | (480, 65) | DOWN | arrive from the Grand Study |
| `from_edmund_bedroom` | (96, 97) | UP | arrive from Edmund's Bedroom |
| `from_clara_bedroom` | (480, 97) | UP | arrive from Clara's Bedroom |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Curio Room) | `curio_room` | `from_hallway` | 80, 0, 32, 48 | up |
| D2 (Guest Room B) | `guest_room_b` | `from_hallway` | 272, 0, 32, 48 | up |
| D3 (Grand Study / Library) | `grand_study` | `from_hallway` | 464, 0, 32, 48 | up |
| D4 (Edmund Blackwood's Bedroom) | `edmund_bedroom` | `from_hallway` | 80, 128, 32, 32 | down |
| D5 (Stairs down to the Main Hall) | `main_hall` | `from_upstairs` | 256, 112, 64, 48 | down |
| D6 (Clara Blackwood's Bedroom) | `clara_bedroom` | `from_hallway` | 464, 128, 32, 32 | down |

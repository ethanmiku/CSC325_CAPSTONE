# Curio Room - layout data

| | |
|---|---|
| Size | **14 x 12 tiles = 224 x 192 px** |
| Walkable interior | tiles x 1..12, y 2..10 (108 tiles, 90 walkable = 83%) |
| Wall style / floor | `curio` / `wood_dark` |
| Tileset | `curio_room_tileset.png` (+ `curio_room_tileset.json` with every tile's cell) |
| Preview | `curio_room_preview.png` (224 x 192 px, 1:1) |

## Suggested player spawn
Tile **(6, 8)**. With a centred 32x32 `Sprite2D`, set the player node position to **(104, 129)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | S | [6, 11] .. [7, 11] | Upstairs Hallway | open | 96, 176, 32, 16 | (6, 10) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| CA1 | Glass display cabinet (artifacts) | (1, 2) 2x1 | `curio_cabinet_artifacts.png` | (16, 0) |
| BU | Marble bust on pedestal | (3, 2) 1x1 | `statue_bust.png` | (48, 16) |
| SF | Bronze figure on pedestal | (10, 2) 1x1 | `statue_figure.png` | (160, 16) |
| CA2 | Glass display cabinet (antique masks) | (11, 2) 2x1 | `curio_cabinet_masks.png` | (176, 0) |
| TB | Glass-topped display table | (6, 6) 2x1 | `display_table_glass.png` | (96, 80) |
| UR1 | Urn on pedestal | (2, 6) 1x1 | `pedestal_urn.png` | (32, 80) |
| UR2 | Urn on pedestal | (11, 6) 1x1 | `pedestal_urn.png` | (176, 80) |
| LC | Lectern with an open manuscript | (3, 8) 1x1 | `lectern_manuscript.png` | (48, 112) |
| TS1 | Side table with a glass dome | (9, 8) 1x1 | `table_side_mahogany.png` | (144, 112) |
| CA3 | Glass display cabinet (books and manuscripts) | (1, 10) 2x1 | `curio_cabinet_manuscripts.png` | (16, 128) |
| CA4 | Glass display cabinet (heirlooms) | (11, 10) 2x1 | `curio_cabinet_artifacts.png` | (176, 128) |
| CF1 | Candelabra | (1, 5) 1x1 | `candelabra_floor.png` | (16, 64) |
| CF2 | Candelabra | (12, 5) 1x1 | `candelabra_floor.png` | (192, 64) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| DS1 | Door to the hallway | wall | `door_s_closed.png` | (96, 176) |
| MB | Wall board of antique masks | wall | `wall_mask_board.png` | (88, 0) |
| P1 | P1 | wall | `painting_portrait_elder.png` | (64, 0) |
| P2 | P2 | wall | `painting_portrait_lady.png` | (144, 0) |
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 96) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (208, 96) |
| T1 | T1 | top | `glass_dome_bird.png` | (144, 122) |
| C1 | Chandelier | over | `chandelier_small.png` | (96, 36) |
| rug | o_plum rug (walkable) | floor | `rug_o_plum_8x5.png` | tile (3, 4) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Glass display table - placeholder clue spot
- **C2** - Cabinet of antique masks - placeholder clue spot
- **C3** - Lectern with the open manuscript - placeholder clue spot

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Glass display cabinet (artifacts) (2x1); Marble bust on pedestal (1x1); Bronze figure on pedestal (1x1); Glass display cabinet (antique masks) (2x1); Glass-topped display table (2x1); Urn on pedestal (1x1); Urn on pedestal (1x1); Lectern with an open manuscript (1x1); Side table with a glass dome (1x1); Glass display cabinet (books and manuscripts) (2x1); Glass display cabinet (heirlooms) (2x1); Candelabra (1x1); Candelabra (1x1).

## Named spawn points (use these for every transition)
| spawn name | Godot position (px, centred 32x32 sprite) | facing | used when |
|---|---|---|---|
| `from_hallway` | (112, 129) | UP | arrive from the hallway |

## Where each door leads (Pokemon-style: press the interact button in front of the door)
| door | goes to scene | arrives at spawn | interaction zone px (x, y, w, h) | player must face |
|---|---|---|---|---|
| D1 (Upstairs Hallway) | `upstairs_hallway` | `from_curio_room` | 96, 160, 32, 32 | down |

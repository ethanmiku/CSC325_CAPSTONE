# Library / Study - layout data

| | |
|---|---|
| Size | **22 x 14 tiles = 352 x 224 px** |
| Walkable interior | tiles x 1..20, y 2..12 (220 tiles, 171 walkable = 78%) |
| Wall style / floor | `library` / `parquet` |
| Tileset | `library_study_tileset.png` (+ `library_study_tileset.json` with every tile's cell) |
| Preview | `library_study_preview.png` (352 x 224 px, 1:1) |

## Suggested player spawn
Tile **(20, 9)**. With a centred 32x32 `Sprite2D`, set the player node position to **(328, 145)** so the feet sit on the bottom edge of that tile.

## Doors / transitions
| id | wall | tiles | target | status | transition rect (px: x, y, w, h) | arrive at tile |
|---|---|---|---|---|---|---|
| D1 | E | [21, 9] .. [21, 10] | Main Hall | lockable | 336, 144, 16, 32 | (20, 9) |

## Furniture (collides)
| id | what | footprint tiles (x, y, w x h) | sprite | sprite top-left px |
|---|---|---|---|---|
| B1 | Bookshelf | (1, 2) 2x1 | `bookshelf_tall.png` | (16, 16) |
| B2 | Bookshelf | (3, 2) 2x1 | `bookshelf_tall.png` | (48, 16) |
| B3 | Bookshelf | (5, 2) 2x1 | `bookshelf_tall.png` | (80, 16) |
| B4 | Bookshelf (gap: missing book) | (7, 2) 2x1 | `bookshelf_tall_gap.png` | (112, 16) |
| B5 | Bookshelf | (12, 2) 2x1 | `bookshelf_tall.png` | (192, 16) |
| B6 | Bookshelf | (14, 2) 2x1 | `bookshelf_tall.png` | (224, 16) |
| B7 | Bookshelf | (16, 2) 2x1 | `bookshelf_tall.png` | (256, 16) |
| B8 | Bookshelf | (18, 2) 2x1 | `bookshelf_tall.png` | (288, 16) |
| F1 | Fireplace | (9, 2) 3x1 | `fireplace_lit.png` | (144, 16) |
| F2 | Globe stand | (20, 2) 1x1 | `globe_stand.png` | (320, 16) |
| LD | Rolling ladder | (6, 3) 1x1 | `library_ladder.png` | (96, 32) |
| SA1 | Free-standing stack A | (3, 5) 2x1 | `bookshelf_tall.png` | (48, 64) |
| SA2 | Free-standing stack A | (5, 5) 2x1 | `bookshelf_tall.png` | (80, 64) |
| SA3 | Free-standing stack A | (7, 5) 2x1 | `bookshelf_tall.png` | (112, 64) |
| SB1 | Free-standing stack B | (13, 5) 2x1 | `bookshelf_tall.png` | (208, 64) |
| SB2 | Free-standing stack B | (15, 5) 2x1 | `bookshelf_tall.png` | (240, 64) |
| SB3 | Free-standing stack B | (17, 5) 2x1 | `bookshelf_tall.png` | (272, 64) |
| DK | Writing desk | (9, 8) 4x2 | `writing_desk.png` | (144, 112) |
| CH1 | Desk chair | (10, 7) 1x1 | `chair_dining_s.png` | (160, 96) |
| A1 | Armchair | (1, 11) 2x1 | `armchair_s.png` | (16, 160) |
| A3 | Side table | (3, 11) 1x1 | `table_side.png` | (48, 160) |
| A2 | Armchair | (4, 11) 2x1 | `armchair_s.png` | (64, 160) |
| DC | Display case | (17, 12) 2x1 | `display_cabinet.png` | (272, 176) |

## Decoration (no collision)
| id | what | layer | sprite | top-left px |
|---|---|---|---|---|
| WN1 | WN1 | wall | `window_small_frosted.png` | (0, 80) |
| WN2 | WN2 | wall | `window_small_frosted.png` | (336, 64) |
| P1 | P1 | wall | `painting_landscape.png` | (152, 0) |
| T1 | T1 | top | `papers_pile.png` | (152, 117) |
| T2 | T2 | top | `open_book.png` | (176, 122) |
| T3 | T3 | top | `inkwell_quill.png` | (194, 117) |
| T4 | T4 | top | `candelabra_table.png` | (48, 150) |
| X1 | Broken glass by display case | floor | `glass_shards.png` | (256, 176) |
| X2 | Toppled chair | floor | `chair_toppled.png` | (224, 144) |
| X3 | Dropped books | floor | `books_stack.png` | (96, 144) |
| CH | Chandelier | over | `chandelier_large.png` | (152, 84) |
| rug | green rug (walkable) | floor | `rug_green_6x4.png` | tile (8, 7) |

## Potential clue areas
These are *spots* where a clue sprite could be dropped; what goes there is decided by the clue system.

- **C1** - Desk - e.g. hidden letter / drawer
- **C2** - Fireplace - e.g. burnt papers
- **C3** - Bookshelf gap - e.g. out-of-place / missing book
- **C4** - Display case - e.g. locked item
- **C5** - Globe stand - e.g. secret compartment

## NPC slots
- N1: Dr. Elias Warren at tile (7, 8)
- N2: (open slot) at tile (16, 8)

## Collision notes
- Solid: the whole wall ring (north 2 rows, side columns, south row) except the door tiles listed under "doors".
- Furniture collides on its FOOTPRINT only (the bottom row(s) of each sprite). The part of a sprite above the footprint is drawn OVER the player when the player stands behind it, so walk-behind works without extra code.
- Decor in "decor" (paintings, windows, sconces, items lying on tables, floor stains, glass, rugs) has NO collision.
- Ceiling lights (layer "over") are drawn above everything and never collide.
- Solid furniture here: Bookshelf (2x1); Bookshelf (2x1); Bookshelf (2x1); Bookshelf (gap: missing book) (2x1); Bookshelf (2x1); Bookshelf (2x1); Bookshelf (2x1); Bookshelf (2x1); Fireplace (3x1); Globe stand (1x1); Rolling ladder (1x1); Free-standing stack A (2x1); Free-standing stack A (2x1); Free-standing stack A (2x1); Free-standing stack B (2x1); Free-standing stack B (2x1); Free-standing stack B (2x1); Writing desk (4x2); Desk chair (1x1); Armchair (2x1); Side table (1x1); Armchair (2x1); Display case (2x1).
- D1 can be LOCKED: swap the open doorway for door_e_locked.png (see previews/library_study_preview_LOCKED_DOOR_variant.png).

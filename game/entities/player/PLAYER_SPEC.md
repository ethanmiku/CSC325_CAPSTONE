# Blackwood Manor - Player Sprite Pack

## Files

| File | Description |
|---|---|
| `player_walk.png` | Full walk sheet, 96 x 128 px, transparent PNG (RGBA) |
| `player_idle.png` | Four idle poses in a row, 128 x 32 px, transparent PNG (RGBA) |
| `player_preview.png` | Enlarged (8x) review image WITH labels. For viewing only - do not import. |
| `PLAYER_SPEC.md` | This file |

## Dimensions

| Property | Value |
|---|---|
| Frame size | 32 x 32 px |
| Sheet size | 96 x 128 px (3 columns x 4 rows = 12 frames) |
| Idle strip size | 128 x 32 px (4 frames in one row) |
| Format | PNG, 32-bit RGBA, real alpha transparency (pixels are either fully transparent or fully opaque - no anti-aliasing, no semi-transparent edges) |
| Character height | 26 px tall, 16 px wide drawing area, centered in the frame |
| Ground line | The planted foot's bottom edge always sits on pixel row 30 of the frame (1 px of empty space below it), in every frame |

## Sprite Sheet Layout (`player_walk.png`)

Rows are directions, columns are animation frames:

| | Col 0 (x=0) | Col 1 (x=32) | Col 2 (x=64) | |
|---|---|---|---|---|
| **Row 0 DOWN** | Idle | Step A | Step B | (y = 0) |
| **Row 1 LEFT** | Idle | Step A | Step B | (y = 32) |
| **Row 2 RIGHT** | Idle | Step A | Step B | (y = 64) |
| **Row 3 UP** | Idle | Step A | Step B | (y = 96) |

Direction order: DOWN, LEFT, RIGHT, UP

Frame index in a Godot Sprite2D / SpriteFrames sheet = `row * 3 + column`

- **DOWN:** 0 idle, 1 step A, 2 step B
- **LEFT:** 3 idle, 4 step A, 5 step B
- **RIGHT:** 6 idle, 7 step A, 8 step B
- **UP:** 9 idle, 10 step A, 11 step B

`player_idle.png` order (left to right): DOWN, LEFT, RIGHT, UP (identical to column 0 of each row of the walk sheet).

What changes between frames:

- Step frames lift the body 1 px (a small bounce).
- One leg is planted on the ground line while the opposite boot is raised 1 px.
- Arms swing opposite to the legs (the arm on the opposite side to the leading leg swings forward). In the side views the near arm swings forward or back.
- Head, hair, scarf, coat, and colors are unchanged.

> **Note:** the RIGHT row is the LEFT row flipped horizontally (standard for this style), so the hair cowlick appears on the opposite side. You may use either the RIGHT row or `flip_h` on the LEFT animation - the result is the same.

## Suggested Godot 4 Setup (AnimatedSprite2D)

1. Import `player_walk.png` into the project.
2. Add an AnimatedSprite2D node and create a new SpriteFrames resource.
3. In the SpriteFrames panel, click "Add Frames from Sprite Sheet" and choose `player_walk.png`. Set Horizontal = 3 and Vertical = 4, then select all 12 frames. (Or build the animations below by selecting individual cells.)
4. Create these animations. Frame order matters; "walk" cycles use a 4-step loop that returns to idle between steps:

| Animation | Frames (row,col) | FPS | Loop |
|---|---|---|---|
| `idle_down` | (0,0) | 1 | off |
| `idle_left` | (1,0) | 1 | off |
| `idle_right` | (2,0) | 1 | off |
| `idle_up` | (3,0) | 1 | off |
| `walk_down` | (0,1) (0,0) (0,2) (0,0) | 8 | on |
| `walk_left` | (1,1) (1,0) (1,2) (1,0) | 8 | on |
| `walk_right` | (2,1) (2,0) (2,2) (2,0) | 8 | on |
| `walk_up` | (3,1) (3,0) (3,2) (3,0) | 8 | on |

Recommended walk FPS: 8 (usable range 6-10; lower looks heavier, higher looks hurried).

**Tip:** if your movement speed is very fast or slow, scale the AnimatedSprite2D `speed_scale` rather than changing the frame order.

**Positioning tip:** the feet are on row 30 of a 32 px frame. With the default centered sprite, setting Offset to (0, -15) puts the node's origin at the character's feet, which is convenient for y-sorting and for a small foot-level collision shape.

## Import Notes (pixel art)

- **Texture filter: Nearest.** Set it on the node (CanvasItem > Texture > Filter = Nearest) or project-wide at Project Settings > Rendering > Textures > Canvas Textures > Default Texture Filter = Nearest. Otherwise the pixels will look blurry.
- **Import tab for the PNGs:** Compress Mode = Lossless, Mipmaps = off, Fix Alpha Border = off (not needed for hard-edged pixel art).
- Consider enabling Project Settings > Rendering > 2D > Snap 2D Transforms to Pixel, and an integer viewport scale (e.g. 2x/3x/4x) to keep pixels square.
- Match the tile scale of your mansion assets: the sprite is 32 x 32 px with a 26 px tall character. If your tiles use a different base size, scale by whole numbers only.
- If your existing animation setup expects different frame sizes or row order, tell the art side and the sheet can be re-exported to match.

BLACKWOOD MANOR - EVE APPLETON SPRITE PACK (final)
==================================================

Eve Appleton, former housekeeper at Blackwood Manor and now owner of the pawnshop in town.
Look: long wavy copper-red hair (partly pinned up under her hat, loose waves framing her face and falling
past her shoulders and down her back), emerald-green eyes and a warm, knowing smile. She wears a wide-brimmed
black-brown Victorian winter hat with a burgundy ribbon, a small gold brooch (front and sides), a small emerald
feather and a ribbon bow at the back. A fitted dark forest-green winter coat with a cream fur collar and cuffs
is worn over her emerald dress, which shows in a V at the front and below the hem. A burgundy scarf is wrapped
at her neck, with dark winter boots. Nothing about the sprite says she is guilty or supernatural.
She is drawn 3 px taller than Arlen (hat included).

FILES
-----
eve_walk.png      Full walk sheet, 96 x 128 px, transparent PNG (RGBA)
eve_idle.png      Four idle poses in a row, 128 x 32 px, transparent PNG (RGBA)
eve_preview.png   Enlarged (9x) review image WITH labels. For viewing only - do not import.
eve_reference_sheet.png   Four-direction idle reference sheet (10x, labelled). For viewing only - do not import.
eve_palette.json  Hex colors used and what each is for
README.txt          This file

DIMENSIONS (same frame layout as the protagonist and the other NPC packs)
-------------------------------------------------------------------------
Frame size:        32 x 32 px
Sheet size:        96 x 128 px  (3 columns x 4 rows = 12 frames)
Idle strip size:   128 x 32 px  (4 frames in one row)
Format:            PNG, 32-bit RGBA, binary alpha (pixels fully transparent or fully opaque)
Character size:    about 16 px wide body; the hat brim is 22 px wide (it extends past the body), 29 px tall in idle (30 px on step frames: 1 px bounce)
Arlen is 26 px, so Eve (hat included) stands 3 px taller. Frames are still 32 x 32.
Ground line:       the feet always end on pixel row 30 of the frame (checked in all 12 frames)

SHEET LAYOUT (eve_walk.png)
------------------------------
Rows are directions, columns are frames. Direction order: DOWN, LEFT, RIGHT, UP.
Frame index = row * 3 + column

  DOWN : 0 idle, 1 step A, 2 step B
  LEFT : 3 idle, 4 step A, 5 step B
  RIGHT: 6 idle, 7 step A, 8 step B
  UP   : 9 idle, 10 step A, 11 step B

eve_idle.png order (left to right): DOWN, LEFT, RIGHT, UP (same as column 0 of each row).
RIGHT is the LEFT row mirrored horizontally. Use either the RIGHT row or flip_h on the LEFT animation.

GODOT 4 SETUP (AnimatedSprite2D) - same as the protagonist
---------------------------------------------------------
1. Project Settings > Rendering > Textures > Default Texture Filter = Nearest; import with the 2D Pixel preset.
2. AnimatedSprite2D with a new SpriteFrames; "Add Frames from Sprite Sheet" > eve_walk.png,
   Horizontal = 3, Vertical = 4.
3. Animations:

   Animation     Frames (row,col)                         FPS   Loop
   idle_down     (0,0)                                    1     off
   idle_left     (1,0)                                    1     off
   idle_right    (2,0)                                    1     off
   idle_up       (3,0)                                    1     off
   walk_down     (0,1) (0,0) (0,2) (0,0)                  8     on
   walk_left     (1,1) (1,0) (1,2) (1,0)                  8     on
   walk_right    (2,1) (2,0) (2,2) (2,0)                  8     on
   walk_up       (3,1) (3,0) (3,2) (3,0)                  8     on

Placement: for a centred Sprite2D, put the node at (tx*16+8, ty*16+1) for tile (tx, ty), same as the
protagonist (the feet are on row 30, so the formula does not change for taller sprites).
Give the collision rectangle the same feet-level size as other characters (roughly 12 x 8 px) and Y-sort as usual.

NOT TESTED IN GODOT YET. Please try the animation setup on one NPC first.

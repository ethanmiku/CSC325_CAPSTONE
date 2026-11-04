# Main screen asset pack

Five reusable Godot 4 scenes based on Figma's **Main Screen**, node `1:6`:

1. `background.tscn` — original mansion texture, blur shader and readability gradient. Stretch to fill its parent.
2. `title.tscn` — editable Blackwood Manor title and subtitle using Jacquard 24 and Silkscreen.
3. `menu_button.tscn` — 200 × 38 Button with gold accent, normal/hover/pressed/focus/disabled styles. Change `text` and connect `pressed`.
4. `login_panel.tscn` — username/password fields, login button and status label. Connect `login_requested(username, password)` to authentication. Supports `autofill()` and `set_status()`.
5. `account_card.tscn` — 168 × 65 Button. Exported role, username, password and accent properties support both Figma test-account variants. Connect `pressed` to autofill.

Open `main_screen_preview.tscn` and press F6 to inspect the assembled 874 × 402 layout. Use an 874 × 402 viewport with canvas-items stretch to preserve the reference layout. The five components can also be instanced independently. The existing game startup scene is unchanged.

The preview wires account autofill and login submission feedback. Menu buttons remain locked as in the logged-out Figma frame. Authentication and gameplay routing must be supplied by the host game; the displayed credentials are prototype examples.

`preview.png` is a Godot-rendered reference. `render_preview.gd` regenerates it when run with Godot's `--script` argument using a graphics renderer.

Source: https://www.figma.com/design/zzwNNu4B3vjq5VeYKZuX4K/MurderMystery-Prototype?node-id=1-6

The mansion image was downloaded directly from the supplied Figma design. Fonts are bundled with their SIL Open Font License files in `fonts/`.

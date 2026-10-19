# Evidence discovery — Issue #25

This feature implements local evidence investigation for the mobile game. Movement
is being developed separately. The existing player scene and script are untouched.
The stationary demo is a test fixture, not a replacement player controller.

## Responsibilities and behavior

- Godot owns proximity checks, the on-screen Interact button, evidence content,
  result presentation, and discoveries during the current game run.
- Each object can contain one `EvidenceData` resource or no useful evidence.
- The nearest enabled, visible, valid object within `interaction_range` is selected.
  The distance is measured in world units from the Interactor origin to the
  EvidenceObject origin, inclusively. Equal distances use scene-path order.
- A tap completes investigation immediately. An evidence object displays its name
  and description. An empty object displays `No useful evidence was found.`
- Range is rechecked at the moment of the tap. While the result panel is open,
  additional investigation is blocked. Close restores interaction.
- Investigation captures the evidence resource and display text before notifying
  signal listeners, so a listener can remove the world object without losing the
  result or causing an invalid-node access.
- `EvidenceState` records a stable evidence ID once and emits `evidence_discovered`
  only for a first discovery. Reinvestigation displays `Already discovered` and
  the same content. IDs remain discovered when levels or objects are recreated.
- The state lives in memory. It is cleared on application restart or an explicit
  `EvidenceState.reset()` at the start of a new game. Do not reset it on every
  level load. This issue does not implement disk saves or cross-device persistence.

There are no evidence HTTP requests, Django changes, migrations, or database
dependencies. Persistent server saves first need an agreed player identity,
case/playthrough model, and save/load contract. AI dialogue is not used to create
or unlock evidence.

## Integrating with the movement work

1. Instance `res://entities/player/interactor.tscn` as a child of the actual 2D
   player. Its origin should match the player's interaction point; normally its
   local position is `(0, 0)`. Adjust `interaction_range` in the Inspector.
2. Instance `res://ui/evidence_display.tscn` in the level or player scene. Assign
   its exported **Interactor** property to that player's Interactor node. Keep
   one evidence display and one active interactor per local player.
3. Place evidence objects in the same world canvas. No player group, physics body,
   collision layer, movement method, keyboard binding, or backend is required.
4. The touch UI calls `interactor.investigate()`. Another future Interact control
   can call that same method rather than implementing a second discovery path.
5. If movement should stop while reading, connect
   `interactor.display_open_changed(is_open)` to the movement controller's own
   input-enable logic. The evidence feature does not pause the scene tree or
   change player velocity. A controller processing touch in `_input()` should
   also respect this state; a GUI panel alone does not block that callback.
6. If the player is replaced, recreate the evidence display with the new
   Interactor reference. If the old interactor exits, its display disables itself.
   Removing the display also dismisses any open investigation on a surviving
   Interactor. A replacement display can investigate normally; discovery state
   is retained, so already discovered evidence can still be reread.

For other gameplay modals, set `interactor.enabled = false` while they own input.
The scene-path tie break makes targeting deterministic; it does not implement
target cycling. Keep investigation points distinct and reachable in level design.
Range checks do not test walls or line of sight; add that only if the team specifies
it. They scan the evidence group each frame, appropriate for this small project.

The display uses standard Godot GUI buttons with mouse-from-touch emulation
enabled, so desktop clicks and mobile taps share the same interaction path.
The evidence canvas scales independently of the world: the shorter viewport edge
maps to 390 UI units, with 64-unit buttons. This keeps buttons readable in portrait
and landscape without changing the player's coordinates or the project's viewport
configuration. The result text scrolls, while Close remains outside the scroll area.

## Authoring objects

1. Instance `res://entities/evidence/evidence_object.tscn` into a level.
2. Set **Object Name** to the world object's label (for example, `Desk`). Add the
   object's artwork as children, or place this node under existing artwork. The
   component itself intentionally has no placeholder sprite or collision shape.
3. Set **Evidence** to **New EvidenceData** for a clue-bearing object. Fill in:
   - `evidence_id`: a stable, case-sensitive ID, such as `case_01_torn_note`;
   - `evidence_name`: the clue's title, such as `Torn Note`;
   - `description`: the information the player should read.
4. Leave **Evidence** empty for an object containing no useful evidence.
5. Leave **Enabled** on unless gameplay should temporarily make the object
   unavailable. Hidden, disabled, deleted, or invalid objects cannot be selected.

Use a different ID for each distinct clue. Multiple instances representing the
same clue should share an ID and content. Discovery state is never written onto
the content resource, which may be shared between instances. Whitespace-only
fields and IDs with surrounding whitespace are invalid; malformed evidence is
excluded from investigation and warns on scene startup rather than pretending
to be an intentionally empty object. The demo note is sample content only.

## Manual acceptance test

Open `game/project.godot` in Godot 4.7 and run
`game/maps/evidence_demo.tscn` with **F6** (Run Current Scene). No main scene is
assigned by this change. A desktop mouse can click the same controls as touch.

The player marker remains stationary. Use the scenario dropdown to arrange the
test objects; these controls exist only in the demo.

| Action | Expected result | Acceptance criterion |
| --- | --- | --- |
| Select **Evidence in range**, then tap **Interact**. | `Torn Note` and its description appear. Discovery count becomes 1. | AC1, AC2 |
| Tap Interact repeatedly while the panel is open. | No additional discovery; one panel stays open. | AC2 |
| Close and investigate again. | Same details plus `Already discovered`; count stays 1. | AC1, AC2 |
| Select **Empty object in range**, then Interact. | `Vase` and `No useful evidence was found.` appear; count is unchanged. | AC3 |
| Select **Nothing in range**. | Interact is disabled and the prompt says no object is in range. | AC1 range guard |
| Select **Two objects in range**. | The nearer note is selected; one tap investigates one object. | AC1, AC2 |
| Tap **Reset**, then investigate the note again. | It counts as a first discovery in a new run. | AC2 state lifecycle |

Also check the UI on a mobile device in portrait and landscape, with long evidence
text and a device cutout/navigation area. The sample demo's authoring controls are
not production HUD controls. No mobile export presets are supplied by this issue.

After the movement work is integrated, verify approaching and leaving objects,
tapping Interact after releasing the movement control, and interaction while a
movement touch is held. Standard GUI buttons use emulated mouse input; simultaneous
joystick and Interact touches need joint verification with the chosen movement
controls. Verify that the player's input handling respects the open result panel.
Actual device behavior and that combined movement flow cannot be established by
the stationary demo or headless tests alone.

## Automated checks

Use a Godot 4.7 executable. From the repository root in PowerShell:

```powershell
$godotExe = 'C:\path\to\Godot_v4.7.2-stable_win64_console.exe'
& $godotExe --headless --path game --editor --import --rendering-method gl_compatibility
& $godotExe --headless --path game --script res://tests/test_evidence.gd
```

The import registers GDScript classes on a fresh checkout. The test command exits
with status 1 on a failed check and 0 on success. No extra test plugin is required.
The rendering override is only for headless import and does not change the project's
Mobile renderer setting.

The suite instantiates the real scenes and autoload. It checks range boundaries,
stale and freed targets, first/repeated discoveries, empty and invalid objects,
hidden/disabled objects, nearest-target selection and ties, state after level
recreation, reset, modal locking, actual GUI mouse input, simulated screen-touch
events, portrait/landscape button bounds and sizes, long-text scrolling, and demo
scene wiring. Regression checks also cover immediate object removal from
display-opening/discovery callbacks and immediate/deferred removal and replacement
of an open display. It performs no network calls or persistent game-state writes.

Verified with Godot **4.7.2**: **95 checks, 0 failures**. These are headless logic
and input/layout checks, not a visual review or a physical-device test.

Relevant Godot documentation:
[touch input](https://docs.godotengine.org/en/stable/tutorials/inputs/input_examples.html#touch-events),
[autoload state](https://docs.godotengine.org/en/stable/tutorials/scripting/singletons_autoload.html),
and [command-line execution](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).

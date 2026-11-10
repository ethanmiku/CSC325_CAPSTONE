# Moves the player between rooms: fades the screen to black, swaps the current room scene
# for the destination and fades back in. Doors call go_to(), and the new room asks for the
# spawn point the player should appear at with take_pending_spawn().
extends CanvasLayer

signal transition_started(scene_path: String, spawn_name: String)
signal transition_finished(scene_path: String, spawn_name: String)

### Variables ###
const FADE_TIME = 0.25

var _pending_spawn := ""
var _busy := false
var _fade: ColorRect

### Functions ###
func _ready() -> void:
	layer = 100
	process_mode = Node.PROCESS_MODE_ALWAYS

	_fade = ColorRect.new()
	_fade.name = "Fade"
	_fade.color = Color.BLACK
	_fade.modulate.a = 0.0
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_fade)

# True while a fade or scene change is running. Doors ignore the player during this time
func is_busy() -> bool:
	return _busy

# Fades out, loads scene_path and fades back in. The new room places the player at the
# SpawnPoints child named spawn_name. Calls made while a transition is running are ignored
func go_to(scene_path: String, spawn_name: String) -> void:
	if _busy:
		return
	if not ResourceLoader.exists(scene_path):
		push_error("RoomTransition: scene not found: %s" % scene_path)
		return

	_busy = true
	transition_started.emit(scene_path, spawn_name)
	# Swallow taps while the screen is dark so the joystick can't be grabbed mid-fade
	_fade.mouse_filter = Control.MOUSE_FILTER_STOP
	# The old room's joystick must stop pressing the movement actions. Hiding it also stops it
	# taking input, and the fade above covers the rest of the screen
	for controls in get_tree().get_nodes_in_group("touch_controls"):
		controls.set_enabled(false)
	_set_players_enabled(false)

	await _fade_to(1.0)

	_pending_spawn = spawn_name
	var error := get_tree().change_scene_to_file(scene_path)
	if error != OK:
		# Stay in the old room and hand control back instead of waiting for a scene that never comes
		push_error("RoomTransition: couldn't load %s (error %d)" % [scene_path, error])
		_pending_spawn = ""
		for controls in get_tree().get_nodes_in_group("touch_controls"):
			controls.set_enabled(true)
		await _finish()
		return
	await get_tree().scene_changed

	# A joystick release swallowed by the fade must not carry on walking the new player.
	# The new player stays frozen until the fade-in is done
	# Freeze first: freezing the player releases the actions too, which would undo a held key
	_set_players_enabled(false)
	_release_movement_actions()
	await _finish()
	transition_finished.emit(scene_path, spawn_name)

# Returns the spawn name the next room should use and clears it. Empty on a cold start
func take_pending_spawn() -> String:
	var spawn := _pending_spawn
	_pending_spawn = ""
	return spawn

# Fades back in and hands control back to the player
func _finish() -> void:
	await _fade_to(0.0)
	_set_players_enabled(true)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_busy = false

func _set_players_enabled(enabled: bool) -> void:
	for player in get_tree().get_nodes_in_group("player"):
		player.set_controls_enabled(enabled)

# Releases the movement actions, then presses again any whose keyboard key is really still
# down, so holding a key through a door keeps walking but a joystick that is gone can't
func _release_movement_actions() -> void:
	for action in ["left", "right", "up", "down"]:
		Input.action_release(action)
		for event in InputMap.action_get_events(action):
			var key := event as InputEventKey
			if key == null:
				continue
			if (key.physical_keycode != KEY_NONE and Input.is_physical_key_pressed(key.physical_keycode)) \
					or (key.keycode != KEY_NONE and Input.is_key_pressed(key.keycode)):
				Input.action_press(action)
				break

func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "modulate:a", alpha, FADE_TIME)
	await tween.finished

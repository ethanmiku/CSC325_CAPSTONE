# Walks the player through every door of every room and checks where they arrive.
#
# Run from the repo root:
#   godot --headless --path game res://tests/room_walk_test.tscn
#   godot --headless --path game res://tests/room_walk_test.tscn -- kitchen main_hall
#
# With no room names it first checks a cold start (the main scene is the Main Hall and the
# player starts at the start spawn, and walking straight up climbs the stairs), then tests
# every room scene in res://maps/. For each door it loads the room at that door's arrival
# spawn, holds the movement key toward the door, and checks the player lands in the target
# room on the expected spawn. Exits with code 1 if anything fails.
extends Node

### Variables ###
const TIMEOUT = 4.0
# Furniture that is deliberately only a collider, with no sprite: room key -> node names
const SPRITELESS = {"main_hall": ["SD"], "upstairs_hallway": ["RL", "RR"]}
# A door this far (px) from the player must be shut
const FAR_PX = 64.0
# Long enough for the door's swing animation to finish
const SETTLE = 0.3
const OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}

var _passes := 0
var _failures := 0

### Functions ###
func _ready() -> void:
	# Stay alive across scene changes: this node is no longer the current scene
	get_tree().current_scene = null
	await get_tree().process_frame

	var rooms := OS.get_cmdline_user_args()
	if rooms.is_empty():
		await _check_cold_start()
		rooms = _all_rooms()
	for room in rooms:
		await _check_room_art(room)
		await _check_camera(room)
		await _walk_room(room)
	if rooms.has("kitchen") or rooms.size() > 1:
		await _check_no_drift("kitchen" if rooms.has("kitchen") else rooms[0])

	print("RESULT passes=%d failures=%d" % [_passes, _failures])
	get_tree().quit(1 if _failures else 0)

func _all_rooms() -> PackedStringArray:
	var rooms := PackedStringArray()
	for dir in DirAccess.get_directories_at("res://maps"):
		if not ResourceLoader.exists(_scene_path(dir)):
			continue
		# Only room scenes (the door and movement test scenes live under maps/ too)
		var scene: Node = load(_scene_path(dir)).instantiate()
		if scene is Room:
			rooms.append(dir)
		scene.free()
	return rooms

func _scene_path(room: String) -> String:
	return "res://maps/%s/%s.tscn" % [room, room]

func _check_cold_start() -> void:
	var main: String = ProjectSettings.get_setting("application/run/main_scene")
	get_tree().change_scene_to_file(main)
	await get_tree().scene_changed
	await get_tree().physics_frame
	var scene := get_tree().current_scene
	var player: Node2D = get_tree().get_first_node_in_group("player")
	var start := scene.get_node_or_null("SpawnPoints/start")
	if scene.name != "MainHall" or start == null or player.global_position != start.global_position:
		_fail("cold start: %s in %s, player at %s" % [main, scene.name, player.global_position])
		return
	_pass("cold start: %s, player at %s facing %s" % [scene.name, player.global_position, player.get_facing()])

	Input.action_press("up")
	var arrived := await _wait_for_transition()
	Input.action_release("up")
	var key: String = get_tree().current_scene.get_meta("room_key", "") if arrived else ""
	if key == "upstairs_hallway":
		_pass("cold start: walking up from the start climbs to upstairs_hallway")
	else:
		_fail("cold start: walking up from the start didn't reach upstairs_hallway (%s)" % key)

func _walk_room(room: String) -> void:
	if not await _load_room(room, "start"):
		_fail("%s: couldn't load" % room)
		return
	var doors := []
	for door in get_tree().get_nodes_in_group("doors"):
		doors.append({"name": door.name, "target": door.target_scene, "spawn": door.target_spawn,
			"direction": door.enter_direction})

	for door in doors:
		var target_room: String = door.target.get_file().get_basename()
		var arrival := "from_" + target_room
		if not await _load_room(room, arrival):
			_fail("%s: couldn't load at %s" % [room, arrival])
			continue
		var marker := get_tree().current_scene.get_node_or_null("SpawnPoints/" + arrival)
		var player: Node2D = get_tree().get_first_node_in_group("player")
		if marker == null or player.global_position.distance_to(marker.global_position) > 0.5:
			_fail("%s: player isn't on spawn %s" % [room, arrival])
			continue
		await _check_door_sprite(room, door)

		Input.action_press(door.direction)
		var arrived := await _wait_for_transition()
		Input.action_release(door.direction)
		if not arrived:
			_fail("%s %s: walking %s never went through the door" % [room, door.name, door.direction])
			continue

		var scene := get_tree().current_scene
		var key: String = scene.get_meta("room_key", "")
		var spawn := scene.get_node_or_null("SpawnPoints/" + door.spawn)
		var new_player: Node2D = get_tree().get_first_node_in_group("player")
		if key != target_room:
			_fail("%s %s: arrived in %s, expected %s" % [room, door.name, key, target_room])
		elif spawn == null:
			_fail("%s %s: %s has no spawn %s" % [room, door.name, target_room, door.spawn])
		elif new_player.global_position.distance_to(spawn.global_position) > 20.0:
			_fail("%s %s: arrived at %s, spawn is at %s" % [room, door.name, new_player.global_position, spawn.global_position])
		else:
			_pass("%s %s -> %s/%s" % [room, door.name, target_room, door.spawn])

func _load_room(room: String, spawn: String) -> bool:
	RoomTransition.go_to(_scene_path(room), spawn)
	return await _wait_for_transition()

# The player has just arrived beside this door: it should swing open, then swing shut once the
# player walks a tile away from it
func _check_door_sprite(room: String, info: Dictionary) -> void:
	var door: Door = get_tree().current_scene.get_node("Doors/" + info.name)
	var sprite: Sprite2D = door.get_node("Sprite")
	if door.closed_texture == null:
		return
	var label := "%s %s" % [room, info.name]
	await get_tree().create_timer(SETTLE).timeout
	if door.open_texture and door.open_texture != door.closed_texture:
		if sprite.texture != door.open_texture or not door.is_open():
			_fail("%s: not open while the player stands next to it" % label)
			return
	elif door.closed_texture.resource_path.contains("_open"):
		_fail("%s: its closed sprite is an open door (%s)" % [label, door.closed_texture.resource_path.get_file()])
		return
	var away: String = OPPOSITE[info.direction]
	Input.action_press(away)
	await get_tree().create_timer(0.5).timeout
	Input.action_release(away)
	await get_tree().create_timer(SETTLE).timeout
	if sprite.texture != door.closed_texture or door.is_open():
		_fail("%s: still open after walking away" % label)
	else:
		_pass("%s: open beside it, closed after walking away" % label)

# Every textured door has distinct closed and open art, shows closed while the player is far
# away (also right after the room loads), and every furniture collider has a sprite
func _check_room_art(room: String) -> void:
	if not await _load_room(room, "start"):
		_fail("%s: couldn't load for the art check" % room)
		return
	var scene := get_tree().current_scene
	var player: Node2D = get_tree().get_first_node_in_group("player")
	var far_doors := []
	for door: Door in get_tree().get_nodes_in_group("doors"):
		if door.closed_texture == null:
			continue
		var label := "%s %s" % [room, door.name]
		if door.open_texture == null or door.open_texture == door.closed_texture:
			_fail("%s: open and closed textures aren't distinct" % label)
			continue
		var center := door.global_position + door.trigger_size / 2.0
		if player.global_position.distance_to(center) < FAR_PX:
			continue
		far_doors.append(door)
		if door.get_node("Sprite").texture != door.closed_texture:
			_fail("%s: not closed right after the room loaded" % label)
	await get_tree().create_timer(SETTLE).timeout
	for door: Door in far_doors:
		if door.get_node("Sprite").texture != door.closed_texture or door.is_open():
			_fail("%s %s: open while the player is far away" % [room, door.name])
		else:
			_pass("%s %s: distinct textures, closed while the player is far away" % [room, door.name])

	var entities := scene.get_node_or_null("Entities")
	if entities == null:
		return
	var missing := []
	for node in entities.get_children():
		if node.get_node_or_null("Body") is StaticBody2D and node.get_node_or_null("Sprite") == null \
				and not SPRITELESS.get(room, []).has(str(node.name)):
			missing.append(str(node.name))
	if missing.is_empty():
		_pass("%s: every furniture collider has a sprite" % room)
	else:
		_fail("%s: furniture without a Sprite: %s" % [room, ", ".join(missing)])

# A static_camera room shows the whole room, centred, and the view doesn't move with the
# player. Every other room keeps the player in the middle of the view
func _check_camera(room: String) -> void:
	if not await _load_room(room, "start"):
		_fail("%s: couldn't load for the camera check" % room)
		return
	var scene: Room = get_tree().current_scene
	var player: Node2D = get_tree().get_first_node_in_group("player")
	var camera: Camera2D = player.get_node("Camera2D")
	var centers := []
	for marker in scene.get_node("SpawnPoints").get_children():
		player.global_position = marker.global_position
		await get_tree().physics_frame
		await get_tree().process_frame
		await get_tree().process_frame
		# What is really on screen: the world point drawn at the middle of the viewport
		var view := get_viewport()
		centers.append(view.get_canvas_transform().affine_inverse() * (view.get_visible_rect().size / 2.0))

	if not scene.static_camera:
		if centers[-1].distance_to(player.global_position) > 1.0:
			_fail("%s: the camera isn't on the player (%s, player %s)" % [room, centers[-1], player.global_position])
		else:
			_pass("%s: the camera follows the player" % room)
		return
	var room_size := scene.get_room_size()
	var view_world := get_viewport().get_visible_rect().size / camera.zoom
	for center: Vector2 in centers:
		if center.distance_to(room_size / 2.0) > 0.01:
			_fail("%s: the fixed camera is at %s, the room's centre is %s" % [room, center, room_size / 2.0])
			return
	if view_world.x < room_size.x or view_world.y < room_size.y:
		_fail("%s: the fixed camera shows %s of a %s room" % [room, view_world, room_size])
	else:
		_pass("%s: the camera stays centred and shows the whole room" % room)

# A movement action that is still held (or pressed again) while a transition runs must not
# leave the player in the new room walking by itself
func _check_no_drift(room: String) -> void:
	if not await _load_room(room, "start"):
		_fail("drift: couldn't load %s" % room)
		return
	var old_scene := get_tree().current_scene
	Input.action_press("down")
	RoomTransition.go_to(_scene_path(room), "start")
	await get_tree().create_timer(0.1).timeout
	# A joystick whose release the fade swallowed keeps pressing the action
	Input.action_press("down")
	var moved_during_fade_in := false
	while RoomTransition.is_busy():
		await get_tree().process_frame
		var current: Node2D = get_tree().get_first_node_in_group("player")
		if get_tree().current_scene != old_scene and current and not current.get_move_direction().is_zero_approx():
			moved_during_fade_in = true
	var player: Node2D = get_tree().get_first_node_in_group("player")
	var start := player.global_position
	var drifted := false
	for i in 10:
		await get_tree().physics_frame
		if not player.get_move_direction().is_zero_approx() or not player.velocity.is_zero_approx():
			drifted = true
	Input.action_release("down")
	if drifted or player.global_position.distance_to(start) > 0.5:
		_fail("drift: the player kept walking after the transition")
	elif moved_during_fade_in:
		_fail("drift: the player moved before the fade-in finished")
	else:
		_pass("drift: nothing held through a transition moves the new player")

# Waits for a RoomTransition to start and finish. False if none starts within TIMEOUT
func _wait_for_transition() -> bool:
	var waited := 0.0
	while not RoomTransition.is_busy() and waited < TIMEOUT:
		await get_tree().process_frame
		waited += get_process_delta_time()
	if not RoomTransition.is_busy():
		return false
	while RoomTransition.is_busy():
		await get_tree().process_frame
	await get_tree().physics_frame
	return true

func _pass(message: String) -> void:
	_passes += 1
	print("PASS ", message)

func _fail(message: String) -> void:
	_failures += 1
	print("FAIL ", message)

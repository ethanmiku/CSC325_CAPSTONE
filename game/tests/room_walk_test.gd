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
		await _walk_room(room)

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

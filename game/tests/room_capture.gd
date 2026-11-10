# Saves screenshots of every room for checking art, doors and furniture by eye.
#
# Run from the repo root (it needs a window, so not --headless):
#   godot --path game res://tests/room_capture.tscn -- /tmp/room_captures
#   godot --path game res://tests/room_capture.tscn -- /tmp/room_captures kitchen main_hall
#   godot --path game res://tests/room_capture.tscn -- /tmp/room_captures --game-camera
#
# For each room it saves <room>.png with the player on the start spawn (every door should be
# closed), then <room>_<door>.png with the player standing just inside each door (that door
# should be open). The whole room is in frame in every picture, unless --game-camera is given:
# then the pictures use the camera the player sees.
extends Node

### Variables ###
# Long enough for a door to finish opening or closing
const SETTLE_TIME = 0.5

var _out_dir := ""
var _game_camera := false

### Functions ###
func _ready() -> void:
	# Stay alive across scene changes: this node is no longer the current scene
	get_tree().current_scene = null
	await get_tree().process_frame

	var args := Array(OS.get_cmdline_user_args())
	_game_camera = args.has("--game-camera")
	args.erase("--game-camera")
	if args.is_empty():
		push_error("room_capture: pass an output folder after --")
		get_tree().quit(1)
		return
	_out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(_out_dir)
	var rooms := PackedStringArray(args.slice(1))
	if rooms.is_empty():
		rooms = _all_rooms()
	for room in rooms:
		await _capture_room(room)
	get_tree().quit(0)

func _all_rooms() -> PackedStringArray:
	var rooms := PackedStringArray()
	for dir in DirAccess.get_directories_at("res://maps"):
		if not ResourceLoader.exists(_scene_path(dir)):
			continue
		var scene: Node = load(_scene_path(dir)).instantiate()
		if scene is Room:
			rooms.append(dir)
		scene.free()
	return rooms

func _scene_path(room: String) -> String:
	return "res://maps/%s/%s.tscn" % [room, room]

func _capture_room(room: String) -> void:
	RoomTransition.go_to(_scene_path(room), "start")
	await RoomTransition.transition_finished
	var scene: Room = get_tree().current_scene
	var player: Node2D = get_tree().get_first_node_in_group("player")
	if not _game_camera:
		_frame_whole_room(scene)
	var touch := scene.get_node_or_null("TouchControls")
	if touch:
		touch.visible = false

	await _save(room)
	for door in get_tree().get_nodes_in_group("doors"):
		# The spawn beside a door is the one the room on its far side sends the player to
		var target_room: String = door.target_scene.get_file().get_basename()
		var marker := scene.get_node_or_null("SpawnPoints/from_" + target_room) as Marker2D
		if marker == null:
			continue
		player.global_position = marker.global_position
		player.face(str(marker.get_meta("facing", "down")))
		await _save("%s_%s" % [room, door.name])

# Replaces the player's follow camera with one that shows the whole room at a whole-number zoom
func _frame_whole_room(scene: Room) -> void:
	var room_size := scene.get_room_size()
	var view := get_viewport().get_visible_rect().size
	var camera := Camera2D.new()
	camera.position = room_size / 2.0
	var zoom := maxf(1.0, floorf(minf(view.x / room_size.x, view.y / room_size.y)))
	camera.zoom = Vector2(zoom, zoom)
	scene.add_child(camera)
	camera.make_current()

func _save(file_name: String) -> void:
	await get_tree().create_timer(SETTLE_TIME).timeout
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	image.save_png(_out_dir.path_join(file_name + ".png"))
	print("saved ", file_name)

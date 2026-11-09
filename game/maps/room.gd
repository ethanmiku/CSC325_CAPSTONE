# Base script for every room scene. When the room loads it puts the player on the spawn point
# the last door asked for (or default_spawn on a fresh start), and keeps the camera on the room
# at the same pixel scale in every room so walking between rooms never changes the zoom.
#
# Expects: the room size in tiles as the "size_tiles" metadata on the root node, Marker2D spawn
# points under SpawnPoints (with optional "facing" metadata), and a Player instance somewhere
# in the scene.
extends Node2D
class_name Room

### Variables ###
const TILE_PX = 16
# How many world pixels tall the view is, whatever the screen size
const VIEW_HEIGHT_PX = 180.0

@export var default_spawn := "start"

var _player: Node2D
var _camera: Camera2D

### Functions ###
func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player")
	if _player == null:
		push_warning("%s: no player in the scene" % name)
		return
	_camera = _player.get_node_or_null("Camera2D")
	_place_player()
	if _camera:
		get_viewport().size_changed.connect(_fit_camera)
		_fit_camera()
		_camera.reset_smoothing()

# The room's size in pixels, walls included
func get_room_size() -> Vector2:
	var tiles: Vector2i = get_meta("size_tiles", Vector2i(20, 16))
	return Vector2(tiles * TILE_PX)

# Returns the spawn marker the player should start on: the one the last door named,
# otherwise default_spawn
func get_spawn_marker() -> Marker2D:
	var spawn_name := RoomTransition.take_pending_spawn()
	if spawn_name.is_empty():
		spawn_name = default_spawn
	var marker := get_node_or_null("SpawnPoints/" + spawn_name) as Marker2D
	if marker == null:
		push_warning("%s: no spawn point named '%s', using '%s'" % [name, spawn_name, default_spawn])
		marker = get_node_or_null("SpawnPoints/" + default_spawn) as Marker2D
	return marker

func _place_player() -> void:
	var marker := get_spawn_marker()
	if marker == null:
		return
	_player.global_position = marker.global_position
	_player.face(str(marker.get_meta("facing", "down")).to_lower())

# Zooms so the view is VIEW_HEIGHT_PX world pixels tall, and limits the camera to the room.
# A room narrower or shorter than the view is centred on that axis over the clear color
func _fit_camera() -> void:
	var view_size := get_viewport().get_visible_rect().size
	var zoom := maxf(1.0, view_size.y / VIEW_HEIGHT_PX)
	_camera.zoom = Vector2(zoom, zoom)

	var view_world := view_size / zoom
	var room := get_room_size()
	if room.x >= view_world.x:
		_camera.limit_left = 0
		_camera.limit_right = int(room.x)
	else:
		_camera.limit_left = floori((room.x - view_world.x) / 2.0)
		_camera.limit_right = _camera.limit_left + ceili(view_world.x)
	if room.y >= view_world.y:
		_camera.limit_top = 0
		_camera.limit_bottom = int(room.y)
	else:
		_camera.limit_top = floori((room.y - view_world.y) / 2.0)
		_camera.limit_bottom = _camera.limit_top + ceili(view_world.y)

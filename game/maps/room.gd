# Base script for every room scene. When the room loads it puts the player on the spawn point
# the last door asked for (or default_spawn on a fresh start), and keeps the camera at the same
# pixel scale in the rooms it follows the player through. In static_camera rooms the camera
# stays centred on the room and shows all of it.
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
# True in rooms small enough to show whole: the camera sits on the room's centre instead of
# following the player
@export var static_camera := false

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

# Follow rooms: zooms so the view is VIEW_HEIGHT_PX world pixels tall, with no limits, so the
# camera stays on the player. Static rooms: zooms out just enough to show the whole room and
# pins the camera to the room's centre with its limits
func _fit_camera() -> void:
	var view_size := get_viewport().get_visible_rect().size
	if not static_camera:
		var zoom := maxf(1.0, view_size.y / VIEW_HEIGHT_PX)
		_camera.zoom = Vector2(zoom, zoom)
		return

	var room := get_room_size()
	var fit := minf(view_size.y / maxf(VIEW_HEIGHT_PX, room.y), view_size.x / room.x)
	_camera.zoom = Vector2(fit, fit)
	# Limits as wide as the view leave the camera nowhere to go, whatever the player does
	var view_world := view_size / fit
	_camera.limit_left = floori((room.x - view_world.x) / 2.0)
	_camera.limit_right = _camera.limit_left + ceili(view_world.x)
	_camera.limit_top = floori((room.y - view_world.y) / 2.0)
	_camera.limit_bottom = _camera.limit_top + ceili(view_world.y)

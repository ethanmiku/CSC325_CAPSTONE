# Main Hall: the room the player starts in. Keeps the camera zoomed in on the pixel art
# and inside the room's walls.
extends Node2D

### Variables ###
const ROOM_SIZE = Vector2(320, 256)
const MIN_CAMERA_ZOOM = 4.0

@onready var _camera: Camera2D = $World/Player/Camera2D

### Functions ###
func _ready() -> void:
	_camera.limit_right = int(ROOM_SIZE.x)
	_camera.limit_bottom = int(ROOM_SIZE.y)
	_camera.limit_left = 0
	_camera.limit_top = 0
	get_viewport().size_changed.connect(_fit_camera)
	_fit_camera()

# Zooms in on the pixel art, but never so far out that the view goes past the room's walls
func _fit_camera() -> void:
	var view_size := get_viewport().get_visible_rect().size
	var zoom := maxf(MIN_CAMERA_ZOOM, maxf(view_size.x / ROOM_SIZE.x, view_size.y / ROOM_SIZE.y))
	_camera.zoom = Vector2(zoom, zoom)

# A walk-through door. The door sprite opens while the player is close, and walking into the
# doorway (moving in enter_direction) fades to target_scene and places the player at the
# SpawnPoints child named target_spawn.
#
# The node's position is the top-left corner of the doorway cells; trigger_size is their size.
@tool
extends Area2D
class_name Door

### Variables ###
const DIRECTIONS = {
	"up": Vector2.UP,
	"down": Vector2.DOWN,
	"left": Vector2.LEFT,
	"right": Vector2.RIGHT,
}
# How far into the room the door starts opening, and how thick the strip at the
# room's outer edge is that stops the player walking off the map
const APPROACH_DEPTH = 16.0
const EDGE_DEPTH = 2.0
# Pause on the open door before the fade starts
const OPEN_DELAY = 0.12

@export_file("*.tscn") var target_scene := ""
@export var target_spawn := ""
# The way the player walks to go through: "up" for a north-wall door, "left" for a west-wall door
@export_enum("up", "down", "left", "right") var enter_direction := "up":
	set(value):
		enter_direction = value
		_apply_layout()
@export var trigger_size := Vector2(32, 16):
	set(value):
		trigger_size = value
		_apply_layout()
@export var closed_texture: Texture2D:
	set(value):
		closed_texture = value
		_apply_layout()
@export var open_texture: Texture2D
# Sprite top-left, relative to the doorway's top-left
@export var sprite_offset := Vector2.ZERO:
	set(value):
		sprite_offset = value
		_apply_layout()
# A locked door stays shut and solid
@export var locked := false:
	set(value):
		locked = value
		_apply_layout()

@onready var _sprite: Sprite2D = $Sprite
@onready var _trigger: CollisionShape2D = $Trigger
@onready var _approach: Area2D = $Approach
@onready var _approach_shape: CollisionShape2D = $Approach/Shape
@onready var _blocker_shape: CollisionShape2D = $Blocker/Shape

var _player: Node2D
var _near := false
var _entering := false

### Functions ###
func _ready() -> void:
	_apply_layout()
	if Engine.is_editor_hint():
		return
	add_to_group("doors")
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_approach.body_entered.connect(_on_approach_changed.bind(true))
	_approach.body_exited.connect(_on_approach_changed.bind(false))

func _physics_process(_delta: float) -> void:
	if Engine.is_editor_hint() or _player == null or _entering or locked:
		return
	if RoomTransition.is_busy():
		return
	# Only go through when walking into the door, not when sliding past its edge
	var moving: Vector2 = _player.get_move_direction()
	if moving.dot(DIRECTIONS[enter_direction]) > 0.5:
		_enter()

func _enter() -> void:
	_entering = true
	_show_open(true)
	await get_tree().create_timer(OPEN_DELAY).timeout
	RoomTransition.go_to(target_scene, target_spawn)

func _on_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		_player = body

func _on_body_exited(body: Node) -> void:
	if body == _player:
		_player = null

func _on_approach_changed(body: Node, inside: bool) -> void:
	if not body.is_in_group("player"):
		return
	_near = inside
	if not _entering:
		_show_open(inside and not locked)

func _show_open(open: bool) -> void:
	if _sprite == null:
		return
	_sprite.texture = open_texture if open and open_texture else closed_texture

# Sizes the trigger, approach zone and edge blocker from the exports
func _apply_layout() -> void:
	if not is_node_ready():
		return
	var into: Vector2 = DIRECTIONS[enter_direction]
	var room_side := -into

	_sprite.texture = closed_texture
	_sprite.position = sprite_offset

	_trigger.shape = _rect_shape(trigger_size)
	_trigger.position = trigger_size / 2.0

	# Approach: the doorway plus one tile on the room side
	var approach_size := trigger_size + room_side.abs() * APPROACH_DEPTH
	var approach_pos := trigger_size / 2.0 + room_side * APPROACH_DEPTH / 2.0
	_approach_shape.shape = _rect_shape(approach_size)
	_approach_shape.position = approach_pos

	# Blocker: a thin strip on the outer edge, or the whole doorway when locked
	var depth := trigger_size.dot(into.abs())
	var strip := depth if locked else EDGE_DEPTH
	var blocker_size := trigger_size - into.abs() * (depth - strip)
	var blocker_pos := trigger_size / 2.0 + into * (depth - strip) / 2.0
	_blocker_shape.shape = _rect_shape(blocker_size)
	_blocker_shape.position = blocker_pos

func _rect_shape(size: Vector2) -> RectangleShape2D:
	var shape := RectangleShape2D.new()
	shape.size = size
	return shape

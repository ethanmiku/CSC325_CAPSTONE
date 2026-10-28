extends CharacterBody2D

### Variables ###
const INTERACT_REACH = 14.0
const FACING_VECTORS = {
	"down": Vector2.DOWN,
	"left": Vector2.LEFT,
	"right": Vector2.RIGHT,
	"up": Vector2.UP,
}

@export var speed := 500.0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _interact_ray: RayCast2D = $InteractRay

var _direction := Vector2.ZERO
var _facing := "down"
var _controls_enabled := true

### Functions ###
func _physics_process(delta: float) -> void:
	process_movement()
	move_and_slide()
	update_animation()

func process_movement() -> void:
	if _controls_enabled:
		_direction = Input.get_vector("left", "right", "up", "down")
	else:
		_direction = Vector2.ZERO

	velocity = _direction * speed

# Plays the walk animation for the direction being moved, or idles facing the last direction
func update_animation() -> void:
	if _direction.is_zero_approx():
		_sprite.play("idle_" + _facing)
		return

	if absf(_direction.x) >= absf(_direction.y):
		_facing = "right" if _direction.x > 0 else "left"
	else:
		_facing = "down" if _direction.y > 0 else "up"

	_interact_ray.target_position = FACING_VECTORS[_facing] * INTERACT_REACH
	_sprite.play("walk_" + _facing)

# Freezes the player in place, e.g. while a dialogue box is open
func set_controls_enabled(enabled: bool) -> void:
	_controls_enabled = enabled
	if not enabled:
		# A joystick hidden mid-drag may never send its release, so clear the actions here
		for action in ["left", "right", "up", "down"]:
			Input.action_release(action)

# Returns the interactable node directly in front of the player, or null
func get_interact_target() -> Node:
	var collider := _interact_ray.get_collider()
	if collider is Node and collider.is_in_group("interactable"):
		return collider
	return null

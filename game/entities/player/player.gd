extends CharacterBody2D

### Variables ###
const SPEED = 500.0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

var _direction := Vector2.ZERO
var _facing := "down"

### Functions ###
func _physics_process(delta: float) -> void:
	process_movement()
	move_and_slide()
	update_animation()

func process_movement() -> void:
	_direction = Input.get_vector("left", "right", "up", "down")

	velocity = _direction * SPEED

# Plays the walk animation for the direction being moved, or idles facing the last direction
func update_animation() -> void:
	if _direction.is_zero_approx():
		_sprite.play("idle_" + _facing)
		return

	if absf(_direction.x) >= absf(_direction.y):
		_facing = "right" if _direction.x > 0 else "left"
	else:
		_facing = "down" if _direction.y > 0 else "up"

	_sprite.play("walk_" + _facing)

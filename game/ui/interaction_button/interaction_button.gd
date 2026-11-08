# Bottom-right "!" button for interacting with whatever the player is facing
extends CanvasLayer
class_name InteractionButton

signal pressed

### Variables ###
const DIMMED = Color(1, 1, 1, 0.4)

@onready var _button: Button = $Button

### Functions ###
func _ready() -> void:
	_button.pressed.connect(pressed.emit)
	set_available(false)

# Greys the button out when there is nothing to interact with
func set_available(available: bool) -> void:
	_button.disabled = not available
	_button.modulate = Color.WHITE if available else DIMMED

func set_shown(shown: bool) -> void:
	visible = shown

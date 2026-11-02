# Shows on-screen touch controls when the left side of the screen is clicked/touched
extends CanvasLayer
class_name TouchControls

# This should be left set to true to show the joystick on desktop
@export var force_show_joystick := true

# Whether the joystick is always drawn or only appears while being touched
@export var joystick_visibility_mode: VirtualJoystick.VisibilityMode = VirtualJoystick.VISIBILITY_WHEN_TOUCHED:
	set(value):
		joystick_visibility_mode = value
		if is_node_ready():
			_joystick.visibility_mode = value

@onready var _joystick: VirtualJoystick = $VirtualJoystick

func _ready() -> void:
	_joystick.visibility_mode = joystick_visibility_mode
	visible = force_show_joystick or DisplayServer.is_touchscreen_available()

func set_enabled(enabled: bool) -> void:
	visible = enabled and (force_show_joystick or DisplayServer.is_touchscreen_available())

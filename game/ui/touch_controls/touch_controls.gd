# Shows on-screen touch controls on touch devices; hides them otherwise.
extends CanvasLayer
class_name TouchControls

# This should be left set to true, as the joystick only appears
# when the left side of the screen is touched or clicked
@export var force_show_joystick := true

func _ready() -> void:
	visible = force_show_joystick or DisplayServer.is_touchscreen_available()

func set_enabled(enabled: bool) -> void:
	visible = enabled and (force_show_joystick or DisplayServer.is_touchscreen_available())

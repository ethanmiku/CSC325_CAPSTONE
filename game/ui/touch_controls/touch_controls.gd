# Shows on-screen touch controls on touch devices; hides them otherwise.
extends CanvasLayer
class_name TouchControls

# set to true for the joystick to appear on desktop
@export var force_show_joystick := false # should be set to false unless we are testing

func _ready() -> void:
	visible = force_show_joystick or DisplayServer.is_touchscreen_available()

func set_enabled(enabled: bool) -> void:
	visible = enabled and (force_show_joystick or DisplayServer.is_touchscreen_available())

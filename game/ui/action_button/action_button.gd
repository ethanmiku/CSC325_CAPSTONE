# Circular "!" button that interaction zones show/hide; emits pressed when tapped/clicked
extends CanvasLayer
class_name ActionButton

signal pressed

# Length of the "pop" animation when the button appears (0 disables it)
@export var pop_duration := 0.12

@onready var _button: Button = $Button

func _ready() -> void:
	_button.pressed.connect(pressed.emit)
	_button.pivot_offset = _button.size / 2.0
	# Hidden until a zone calls show_button(), unless running this scene on its own (F6)
	visible = get_tree().current_scene == self

func show_button() -> void:
	if visible:
		return
	show()
	if pop_duration > 0.0:
		_button.scale = Vector2.ZERO
		create_tween().tween_property(_button, "scale", Vector2.ONE, pop_duration) \
			.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

func hide_button() -> void:
	hide()

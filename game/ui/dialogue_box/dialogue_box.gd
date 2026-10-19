# Undertale-style dialogue box with two modes:
# - full: text spans the whole box, tap/accept to finish the text then close
# - prompts: text on the left, suggested prompts in the right 25%
extends CanvasLayer
class_name DialogueBox

signal prompt_selected(index: int)
signal closed

# Typewriter speed for the main text (0 shows the text instantly)
@export var chars_per_second := 30.0

# Whether the prompts column is shown; open() sets this based on the prompts passed in
@export var show_prompts := false:
	set(value):
		show_prompts = value
		if is_node_ready():
			_divider.visible = value
			_prompts.visible = value

@onready var _box: Panel = $Box
@onready var _main_text: Label = %MainText
@onready var _divider: ColorRect = %Divider
@onready var _prompts: VBoxContainer = %Prompts

var _text_tween: Tween

func _ready() -> void:
	show_prompts = show_prompts
	_connect_prompts()
	_box.gui_input.connect(_on_box_gui_input)
	# Hidden until open() is called, unless running this scene on its own (F6)
	if get_tree().current_scene == self:
		_show_text(_main_text.text)
	else:
		hide()

# open(text) shows the full box; open(text, prompts) shows the box with prompts
func open(text: String = "* placeholder for now", prompts: PackedStringArray = []) -> void:
	show_prompts = not prompts.is_empty()
	if show_prompts:
		_set_prompts(prompts)
	_show_text(text)

func close() -> void:
	hide()
	closed.emit()

func _show_text(text: String) -> void:
	show()
	_reveal_text(text)
	if show_prompts and _prompts.get_child_count() > 0:
		_prompts.get_child(0).grab_focus()

func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_accept"):
		_advance()
		get_viewport().set_input_as_handled()

func _on_box_gui_input(event: InputEvent) -> void:
	# Touches arrive as emulated mouse clicks, so only mouse buttons are handled here
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_advance()
		_box.accept_event()

# First press finishes the typewriter; the next press closes the full box.
# The prompts box stays open until the caller closes it after a prompt is picked.
func _advance() -> void:
	if _text_tween and _text_tween.is_running():
		_text_tween.kill()
		_main_text.visible_ratio = 1.0
	elif not show_prompts:
		close()

func _set_prompts(prompts: PackedStringArray) -> void:
	for child in _prompts.get_children():
		_prompts.remove_child(child)
		child.queue_free()
	for prompt in prompts:
		# Styling comes from the Theme on Box, so a plain Button matches the placeholders
		var button := Button.new()
		button.text = "* " + prompt
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_prompts.add_child(button)
	_connect_prompts()

func _connect_prompts() -> void:
	for i in _prompts.get_child_count():
		var button: Button = _prompts.get_child(i)
		button.pressed.connect(prompt_selected.emit.bind(i))

func _reveal_text(text: String) -> void:
	_main_text.text = text
	if _text_tween:
		_text_tween.kill()
	if chars_per_second <= 0.0:
		_main_text.visible_ratio = 1.0
		return
	_main_text.visible_ratio = 0.0
	_text_tween = create_tween()
	_text_tween.tween_property(_main_text, "visible_ratio", 1.0, text.length() / chars_per_second)

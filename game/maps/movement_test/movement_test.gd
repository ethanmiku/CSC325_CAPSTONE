# Checkerboard movement and NPC dialogue playtest.
extends Node2D

@export var tile_size: int = 128
@export var grid_color_a: Color = Color(0.85, 0.85, 0.85)
@export var grid_color_b: Color = Color(0.65, 0.65, 0.65)
@export var area_size: Vector2 = Vector2(4096, 4096)

@onready var _player = $Player
@onready var _touch_controls: TouchControls = $TouchControls
@onready var _interact_button: InteractionButton = $InteractionButton
@onready var _dialogue_box: DialogueBox = $DialogueBox

var _npc_id := ""

func _ready() -> void:
	queue_redraw()
	_interact_button.pressed.connect(_interact)
	_dialogue_box.question_submitted.connect(_ask_question)
	_dialogue_box.closed.connect(_close_conversation)

func _physics_process(_delta: float) -> void:
	_interact_button.set_available(
		not _dialogue_box.is_open() and _player.get_interact_target() != null
	)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_accept") and not event.is_echo() and not _dialogue_box.is_open():
		_interact()

func _interact() -> void:
	if _dialogue_box.is_open():
		return
	var target: Node = _player.get_interact_target()
	if target == null:
		return
	_npc_id = target.get_meta("npc_id")
	_player.set_controls_enabled(false)
	_touch_controls.set_enabled(false)
	_interact_button.set_shown(false)
	_dialogue_box.open(target.name)

func _ask_question(question: String) -> void:
	_dialogue_box.show_loading()
	var result := await ClaudeDialogue.send_message(_npc_id, question)
	if result.ok:
		_dialogue_box.show_reply(result.reply)
	else:
		_dialogue_box.show_error(result.message)

func _close_conversation() -> void:
	_npc_id = ""
	_player.set_controls_enabled(true)
	_touch_controls.set_enabled(true)
	_interact_button.set_shown(true)

func _draw() -> void:
	var half := area_size / 2.0
	var cols := int(area_size.x / tile_size)
	var rows := int(area_size.y / tile_size)
	for y in rows:
		for x in cols:
			var color := grid_color_a if (x + y) % 2 == 0 else grid_color_b
			var pos := Vector2(-half.x + x * tile_size, -half.y + y * tile_size)
			draw_rect(Rect2(pos, Vector2(tile_size, tile_size)), color)

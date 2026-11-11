# NPC conversation playtest with Arthur and Clara.
extends Node2D

@onready var _player = $Player
@onready var _touch_controls: TouchControls = $TouchControls
@onready var _interact_button: InteractionButton = $InteractionButton
@onready var _dialogue_box: DialogueBox = $DialogueBox

var _npc_id := ""

func _ready() -> void:
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

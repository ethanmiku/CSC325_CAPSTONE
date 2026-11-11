# Bottom-of-screen question input and paginated NPC replies.
extends CanvasLayer
class_name DialogueBox

signal closed
signal question_submitted(question: String)

### Variables ###
const LOADING_DOT_INTERVAL = 0.4

@export var characters_per_second := 30.0

@onready var _panel: PanelContainer = $Panel
@onready var _speaker: Label = $Panel/Margin/VBox/Speaker
@onready var _body: Label = $Panel/Margin/VBox/Body
@onready var _question_row: HBoxContainer = $Panel/Margin/VBox/QuestionRow
@onready var _question: LineEdit = $Panel/Margin/VBox/QuestionRow/Question
@onready var _send: Button = $Panel/Margin/VBox/QuestionRow/Send
@onready var _continue: Button = $Panel/Margin/VBox/Actions/Continue
@onready var _close: Button = $Panel/Margin/VBox/Actions/Close

var _loading := false
var _loading_time := 0.0
var _loading_base := ""

var _pages := PackedStringArray()
var _page := 0
var _typing := false
var _typed := 0.0

### Functions ###
func _ready() -> void:
	visible = false
	_panel.gui_input.connect(_on_panel_gui_input)
	_question.text_submitted.connect(_submit_question)
	_send.pressed.connect(func() -> void: _submit_question(_question.text))
	_continue.pressed.connect(advance)
	_close.pressed.connect(close)

func _process(delta: float) -> void:
	# Cycles the dots on "<speaker> is responding..." while waiting
	if _loading:
		_loading_time += delta
		_body.text = _loading_base + ".".repeat(int(_loading_time / LOADING_DOT_INTERVAL) % 3 + 1)
		return

	if _typing:
		_typed += delta * characters_per_second
		if _typed >= _body.text.length():
			_finish_page()
		else:
			_body.visible_characters = int(_typed)

func is_open() -> bool:
	return visible

func open(speaker: String) -> void:
	_speaker.text = speaker
	_question.clear()
	visible = true
	_show_question("Ask %s a question." % speaker)

func _submit_question(text: String) -> void:
	if not visible or not _question_row.visible:
		return
	var question := text.strip_edges()
	if not question.is_empty():
		question_submitted.emit(question)

func show_loading() -> void:
	_loading = true
	_question_row.hide()
	_close.disabled = true
	_loading_time = 0.0
	_loading_base = "%s is responding" % _speaker.text
	_body.text = _loading_base + "."
	_body.visible_characters = -1
	_continue.visible = false

func show_reply(text: String) -> void:
	_question.clear()
	# Wait for layout so pages wrap at the right width.
	await get_tree().process_frame
	_loading = false
	_close.disabled = false
	_pages = _paginate(text)
	_show_page(0)

func show_error(message: String) -> void:
	_show_question(message)

func _show_question(message: String) -> void:
	_loading = false
	_typing = false
	_body.text = message
	_body.visible_characters = -1
	_continue.hide()
	_close.disabled = false
	_question_row.show()
	_question.grab_focus()

# Finish typing, show the next page, or return to question input.
func advance() -> void:
	if not visible or not _continue.visible:
		return

	if _typing:
		_finish_page()
	elif _page + 1 < _pages.size():
		_show_page(_page + 1)
	else:
		_show_question(_body.text)

func close() -> void:
	if not visible or _loading:
		return
	visible = false
	_loading = false
	_typing = false
	closed.emit()

func _show_page(index: int) -> void:
	_page = index
	_body.text = _pages[index]
	_body.visible_characters = 0
	_typed = 0.0
	_typing = true
	_continue.show()
	_continue.grab_focus()

func _finish_page() -> void:
	_body.visible_characters = -1
	_typing = false

# Splits text into pages of max_lines_visible lines, wrapped the same way the body label wraps
func _paginate(text: String) -> PackedStringArray:
	var paragraph := TextParagraph.new()
	paragraph.width = _body.size.x
	paragraph.break_flags = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	paragraph.add_string(text, _body.get_theme_font("font"), _body.get_theme_font_size("font_size"))

	var pages := PackedStringArray()
	var line_count := paragraph.get_line_count()
	for first_line in range(0, line_count, _body.max_lines_visible):
		var last_line := mini(first_line + _body.max_lines_visible, line_count) - 1
		var start := paragraph.get_line_range(first_line).x
		var end := paragraph.get_line_range(last_line).y
		pages.append(text.substr(start, end - start).strip_edges())

	if pages.is_empty():
		pages.append(text)
	return pages

# Mouse only: touches arrive as emulated mouse events, so also handling
# InputEventScreenTouch would advance twice per tap
func _on_panel_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_panel.accept_event()
		advance()

class_name EvidenceDisplay
extends CanvasLayer

@export var interactor: EvidenceInteractor

@onready var interact_button: Button = %InteractButton
@onready var target_label: Label = %TargetLabel
@onready var modal: Control = %Modal
@onready var title_label: Label = %TitleLabel
@onready var description_label: Label = %DescriptionLabel
@onready var status_label: Label = %StatusLabel
@onready var close_button: Button = %CloseButton
@onready var description_scroll: ScrollContainer = %DescriptionScroll


func _ready() -> void:
	get_viewport().size_changed.connect(_resize_ui)
	_resize_ui()
	modal.hide()
	interact_button.pressed.connect(_on_interact_pressed)
	close_button.pressed.connect(_on_close_pressed)
	if interactor == null:
		push_warning("EvidenceDisplay needs an Interactor assigned in the Inspector.")
		_update_target(null)
		return
	interactor.target_changed.connect(_update_target)
	interactor.investigation_completed.connect(_show_result)
	interactor.display_open_changed.connect(_on_display_open_changed)
	interactor.tree_exiting.connect(_on_interactor_exiting)
	interactor.refresh_target()
	_update_target(interactor.target)


func _exit_tree() -> void:
	if not is_instance_valid(interactor):
		return
	# Disconnect before dismissing: the child controls are already leaving the
	# tree and must not receive the resulting target/display updates.
	if interactor.target_changed.is_connected(_update_target):
		interactor.target_changed.disconnect(_update_target)
	if interactor.investigation_completed.is_connected(_show_result):
		interactor.investigation_completed.disconnect(_show_result)
	if interactor.display_open_changed.is_connected(_on_display_open_changed):
		interactor.display_open_changed.disconnect(_on_display_open_changed)
	if interactor.tree_exiting.is_connected(_on_interactor_exiting):
		interactor.tree_exiting.disconnect(_on_interactor_exiting)
	if interactor.is_inside_tree():
		interactor.dismiss()


func _resize_ui() -> void:
	# Keep controls readable in either orientation without changing world scaling.
	# The shorter screen edge represents 390 UI units; buttons are 64 units tall.
	var viewport_size := get_viewport().get_visible_rect().size
	var ui_scale := minf(viewport_size.x, viewport_size.y) / 390.0
	scale = Vector2.ONE * ui_scale
	$Root.size = viewport_size / ui_scale


func _update_target(target: EvidenceObject) -> void:
	var available := is_instance_valid(target)
	interact_button.disabled = not available
	target_label.text = "Investigate: %s" % target.object_name if available else "No object in range"


func _on_interact_pressed() -> void:
	if is_instance_valid(interactor):
		interactor.investigate()


func _show_result(title: String, description: String, already_discovered: bool) -> void:
	title_label.text = title
	description_label.text = description
	status_label.text = "Already discovered" if already_discovered else ""
	status_label.visible = already_discovered
	description_scroll.scroll_vertical = 0
	modal.show()
	close_button.grab_focus()


func _on_close_pressed() -> void:
	if is_instance_valid(interactor):
		interactor.dismiss()
	modal.hide()
	close_button.release_focus()


func _on_display_open_changed(is_open: bool) -> void:
	if not is_open:
		modal.hide()


func _on_interactor_exiting() -> void:
	modal.hide()
	_update_target(null)

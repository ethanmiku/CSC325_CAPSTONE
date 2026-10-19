extends Node2D
## Stationary acceptance-test fixture, not a player movement implementation.

@onready var interactor: EvidenceInteractor = $PlayerStandIn/Interactor
@onready var clue: EvidenceObject = $Clue
@onready var empty_object: EvidenceObject = $EmptyObject
@onready var scenario: OptionButton = %Scenario
@onready var count_label: Label = %CountLabel


func _ready() -> void:
	scenario.add_item("Evidence in range")
	scenario.add_item("Empty object in range")
	scenario.add_item("Nothing in range")
	scenario.add_item("Two objects in range")
	scenario.item_selected.connect(_select_scenario)
	%ResetButton.pressed.connect(_reset_discoveries)
	get_node("/root/EvidenceState").evidence_discovered.connect(_on_discovered)
	get_viewport().size_changed.connect(_layout_objects)
	_select_scenario(0)
	_update_count()


func _select_scenario(index: int) -> void:
	clue.enabled = index != 1
	empty_object.enabled = index == 1 or index == 3
	_layout_objects()
	interactor.refresh_target()


func _layout_objects() -> void:
	$PlayerStandIn.position = get_viewport_rect().size * Vector2(0.5, 0.56)
	clue.position = $PlayerStandIn.position + Vector2(60, 0)
	empty_object.position = $PlayerStandIn.position + Vector2(-80, 0)
	if scenario.selected == 2:
		clue.position = $PlayerStandIn.position + Vector2(0, -130)
	queue_redraw()


func _reset_discoveries() -> void:
	get_node("/root/EvidenceState").reset()
	_update_count()


func _on_discovered(_evidence: EvidenceData) -> void:
	_update_count()


func _update_count() -> void:
	count_label.text = "Discovered: %d" % get_node("/root/EvidenceState").discovered_count()


func _draw() -> void:
	if not is_instance_valid(interactor):
		return
	var origin: Vector2 = $PlayerStandIn.position
	draw_circle(origin, interactor.interaction_range, Color(0.25, 0.55, 0.7, 0.14))
	draw_arc(origin, interactor.interaction_range, 0, TAU, 64, Color(0.4, 0.7, 0.8), 2.0)
	draw_circle(origin, 14, Color(0.5, 0.85, 1.0))
	draw_string(ThemeDB.fallback_font, origin + Vector2(-25, 40), "Player", HORIZONTAL_ALIGNMENT_LEFT, -1, 18)
	for object: EvidenceObject in [clue, empty_object]:
		if object.enabled:
			draw_rect(Rect2(object.position - Vector2(12, 12), Vector2(24, 24)), Color(1.0, 0.8, 0.4))
			draw_string(ThemeDB.fallback_font, object.position + Vector2(-24, -24), object.object_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 18)

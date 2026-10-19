class_name EvidenceInteractor
extends Node2D
## Attach at the player's interaction origin. Movement remains owned by the player.

signal target_changed(target: EvidenceObject)
signal investigation_completed(title: String, description: String, already_discovered: bool)
signal display_open_changed(is_open: bool)

@export_range(1.0, 1000.0, 1.0) var interaction_range: float = 96.0
@export var enabled: bool = true

var target: EvidenceObject
var is_display_open: bool = false


func _process(_delta: float) -> void:
	refresh_target()


func refresh_target() -> void:
	var nearest: EvidenceObject = null
	var nearest_distance: float = interaction_range * interaction_range
	if enabled and not is_display_open:
		for node in get_tree().get_nodes_in_group(EvidenceObject.GROUP):
			var candidate := node as EvidenceObject
			if candidate == null or not candidate.can_investigate():
				continue
			var distance := global_position.distance_squared_to(candidate.global_position)
			if distance > nearest_distance:
				continue
			# Stable tie break: overlapping objects must not flicker between targets.
			if distance == nearest_distance and nearest != null:
				if String(candidate.get_path()) >= String(nearest.get_path()):
					continue
			nearest = candidate
			nearest_distance = distance
	if (target != null and not is_instance_valid(target)) or target != nearest:
		target = nearest
		target_changed.emit(target)


func investigate() -> bool:
	if is_display_open or not enabled:
		return false
	# Recheck range on the tap, including movement since the last frame.
	refresh_target()
	if not is_instance_valid(target):
		return false
	var selected := target
	# Signal listeners may immediately remove the world object. Keep the resource
	# and display text before notifying listeners, and don't read the node again.
	var evidence := selected.evidence
	var title := selected.object_name
	var description := "No useful evidence was found."
	if evidence != null:
		title = evidence.evidence_name
		description = evidence.description
	var already_discovered := false
	_set_display_open(true)
	if evidence != null:
		var state := get_node("/root/EvidenceState")
		already_discovered = not state.discover(evidence)
	investigation_completed.emit(title, description, already_discovered)
	return true


func dismiss() -> void:
	_set_display_open(false)


func _set_display_open(value: bool) -> void:
	if is_display_open == value:
		return
	is_display_open = value
	refresh_target()
	display_open_changed.emit(value)

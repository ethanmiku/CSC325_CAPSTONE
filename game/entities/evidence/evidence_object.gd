class_name EvidenceObject
extends Node2D
## Place this node at the object's investigation point and add your own artwork.
## A null evidence resource deliberately represents an object with no useful clue.

const GROUP: StringName = &"evidence_objects"

@export var object_name: String = "Object"
@export var evidence: EvidenceData
@export var enabled: bool = true


func _enter_tree() -> void:
	add_to_group(GROUP)


func _ready() -> void:
	if evidence != null and not evidence.is_valid():
		push_warning("Invalid evidence on %s: supply an ID, name, and description." % get_path())


func can_investigate() -> bool:
	return (
		enabled and is_visible_in_tree() and not is_queued_for_deletion()
		and (evidence == null or evidence.is_valid())
	)

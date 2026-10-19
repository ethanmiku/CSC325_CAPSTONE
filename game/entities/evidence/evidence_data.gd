class_name EvidenceData
extends Resource
## Authored clue content. Discovery state belongs to EvidenceState, not this resource.

@export var evidence_id: StringName
@export var evidence_name: String = ""
@export_multiline var description: String = ""


func is_valid() -> bool:
	return (
		not String(evidence_id).strip_edges().is_empty()
		and String(evidence_id) == String(evidence_id).strip_edges()
		and not evidence_name.strip_edges().is_empty()
		and not description.strip_edges().is_empty()
	)

extends Node
## One local playthrough. Survives scene changes; does not write to disk or Django.

signal evidence_discovered(evidence: EvidenceData)
signal discoveries_reset

var _discovered: Dictionary = {}


func discover(evidence: EvidenceData) -> bool:
	if evidence == null or not evidence.is_valid() or is_discovered(evidence.evidence_id):
		return false
	_discovered[evidence.evidence_id] = true
	evidence_discovered.emit(evidence)
	return true


func is_discovered(evidence_id: StringName) -> bool:
	return _discovered.has(evidence_id)


func discovered_count() -> int:
	return _discovered.size()


func reset() -> void:
	_discovered.clear()
	discoveries_reset.emit()

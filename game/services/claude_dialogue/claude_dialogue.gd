# Sends NPC dialogue to the Django backend, which generates replies with Claude.
# Registered as the ClaudeDialogue autoload. See backend/docs/dialogue-api.md for the contract.
extends Node

### Variables ###
const MAX_HISTORY_ENTRIES = 20
const MAX_HISTORY_CHARS = 20000

# 127.0.0.1 only reaches a backend running on the same computer as the game
# TODO: this needs to be configured somewhere more accesible instead of being hardcoded
@export var base_url := "http://127.0.0.1:8000"

var _http: HTTPRequest
var _pending := false
# npc_id -> Array of {role, content}, kept as completed user/assistant exchanges
var _history := {}

### Functions ###
func _ready() -> void:
	_http = HTTPRequest.new()
	_http.timeout = 60.0
	add_child(_http)

func is_pending() -> bool:
	return _pending

func reset_history(npc_id: String) -> void:
	_history.erase(npc_id)

# Awaitable. Returns {ok = true, reply} or {ok = false, code, message}
func send_message(npc_id: String, message: String) -> Dictionary:
	if _pending:
		return _error("request_pending", "A dialogue request is already in progress.")

	var history: Array = _history.get(npc_id, [])
	var body := JSON.stringify({"npc_id": npc_id, "message": message, "history": history})
	var headers := PackedStringArray(["Content-Type: application/json", "Accept: application/json"])

	var err := _http.request(base_url + "/api/dialogue/message/", headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		return _error("network_error", "Could not start the request (error %d)." % err)

	_pending = true
	var response: Array = await _http.request_completed
	_pending = false

	var result: int = response[0]
	var status: int = response[1]

	if result == HTTPRequest.RESULT_TIMEOUT:
		return _error("timeout", "The backend took too long to respond.")
	if result != HTTPRequest.RESULT_SUCCESS:
		return _error("network_error", "Could not reach the backend at %s." % base_url)

	var data = JSON.parse_string((response[3] as PackedByteArray).get_string_from_utf8())
	if not data is Dictionary:
		return _error("invalid_response", "The backend returned HTTP %d without JSON." % status)
	if status != 200:
		var api_error: Dictionary = data.get("error", {})
		return _error(api_error.get("code", "http_%d" % status), api_error.get("message", ""))

	var reply: String = data.get("reply", "")
	_append_exchange(npc_id, message, reply)
	return {"ok": true, "reply": reply}

# Only successful exchanges are kept, trimmed oldest-first to the backend's limits
func _append_exchange(npc_id: String, message: String, reply: String) -> void:
	var history: Array = _history.get(npc_id, [])
	history.append({"role": "user", "content": message})
	history.append({"role": "assistant", "content": reply})

	while history.size() > MAX_HISTORY_ENTRIES or _history_chars(history) > MAX_HISTORY_CHARS:
		history = history.slice(2)

	_history[npc_id] = history

func _history_chars(history: Array) -> int:
	var total := 0
	for entry in history:
		total += entry["content"].length()
	return total

func _error(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}

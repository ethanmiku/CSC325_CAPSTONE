# Sends NPC dialogue to the Django backend, which generates replies with Claude.
# Registered as the ClaudeDialogue autoload. See backend/docs/dialogue-api.md for the contract.
extends Node

### Variables ###
# 127.0.0.1 only reaches a backend running on the same computer as the game
# TODO: this needs to be configured somewhere more accesible instead of being hardcoded
@export var base_url := "http://127.0.0.1:8000"

var _http: HTTPRequest
var _pending := false
var _game_session_id: String

### Functions ###
func _ready() -> void:
	# The autoload lives for the entire playthrough, including scene changes.
	_game_session_id = _generate_session_id()
	_http = HTTPRequest.new()
	_http.timeout = 60.0
	add_child(_http)

func is_pending() -> bool:
	return _pending

# Awaitable. Returns {ok = true, reply} or {ok = false, code, message}
func send_message(npc_id: String, message: String) -> Dictionary:
	if _pending:
		return _error("request_pending", "A dialogue request is already in progress.")

	var body := JSON.stringify({
		"game_session_id": _game_session_id,
		"npc_id": npc_id,
		"message": message,
	})
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
	return {"ok": true, "reply": reply}

func _generate_session_id() -> String:
	var bytes := Crypto.new().generate_random_bytes(16)
	# Set the UUID version to 4 and the variant to RFC 9562.
	bytes[6] = (bytes[6] & 0x0f) | 0x40
	bytes[8] = (bytes[8] & 0x3f) | 0x80
	var hex := bytes.hex_encode()
	return "%s-%s-%s-%s-%s" % [
		hex.substr(0, 8), hex.substr(8, 4), hex.substr(12, 4),
		hex.substr(16, 4), hex.substr(20, 12),
	]

func _error(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}

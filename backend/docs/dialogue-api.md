# NPC Dialogue API Contract

Status: health and dialogue endpoints implemented locally. Real Claude generation
requires the configuration below; automated tests use mocked Claude responses.

## Scope

The first milestone supports a local Godot client talking to one predefined NPC
through Django. Django generates replies using Claude. NPC definitions and case
facts are stored in backend code; the generated dialogue is dynamic.

Conversation persistence, player accounts, game sessions, clue unlocks, streaming,
and NPC management endpoints are outside this milestone. No new MongoDB models or
migrations are required for dialogue. Existing Django configuration still requires
the database environment variables described in the backend setup guides.

## Connection and conventions

- Local base URL: `http://127.0.0.1:8000`.
- Use the trailing slash shown on each endpoint.
- Request bodies use `Content-Type: application/json`.
- Responses use JSON. Clients should send `Accept: application/json`.
- Requests and responses use UTF-8.
- The local MVP endpoints do not require login, cookies, or a CSRF token.
- Godot calls Django only. The Claude API key stays on the backend.

This contract targets a local desktop demo. Hosting and browser-export integration
will be addressed in a later milestone.

### Claude configuration

Install the updated `backend/requirements.txt` in the project virtual environment.
Add these values to your existing `backend/.env`, without overwriting your Django
or MongoDB settings:

```dotenv
ANTHROPIC_API_KEY=your-actual-api-key
ANTHROPIC_MODEL=your-selected-available-model-id
```

Use a model ID available to your Claude API account. Restart Django after changing
the environment file. Missing or placeholder values produce `503 ai_unavailable`;
the health endpoint remains usable. Never commit the actual API key.

The backend requests at most 300 output tokens, uses a 30-second SDK network
timeout, and disables SDK retries. The Godot client's timeout should allow extra
time beyond the backend timeout to receive a JSON error response.

## GET /api/health/

Checks whether the Django API is reachable. Does not call Claude or query MongoDB,
and does not establish whether either external service is available.

No request body is required.

### Success: 200 OK

```json
{
  "status": "ok"
}
```

## POST /api/dialogue/message/

Generates one NPC reply. The endpoint is stateless: Godot supplies previous turns
with each request, and Django does not save the conversation.

### Request

```json
{
  "npc_id": "butler",
  "message": "Where were you last night?",
  "history": []
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `npc_id` | String | Required. Exact, case-sensitive NPC identifier. The only supported value in this milestone is `butler`. |
| `message` | String | Required. Trim leading and trailing whitespace; reject if empty after trimming. Maximum 1,000 characters before trimming. |
| `history` | Array | Required. Use `[]` for the first turn. Maximum 20 entries (10 completed exchanges). |

Each history entry contains exactly these fields:

| Field | Type | Rules |
| --- | --- | --- |
| `role` | String | Either `user` or `assistant`. |
| `content` | String | Nonempty after trimming. Maximum 4,000 characters before trimming. |

Additional validation rules:

- The request body must be a JSON object. Unknown fields are rejected, including
  unknown fields in history entries.
- Nonempty history must consist of completed exchanges: start with `user`,
  alternate roles, and end with `assistant`. Its entry count must be even.
- The current `message` must not also appear as a new, unanswered history entry.
- Combined history content must not exceed 20,000 characters before trimming.
- Field values are validated as their stated JSON types; values are not coerced
  from numbers, booleans, or null.
- Django supplies NPC instructions and case facts. Clients cannot send a `system`
  role, choose a model, or override those instructions.

For valid input, Django constructs the Claude request using backend NPC
instructions, the supplied history in order, and the current message as the final
user turn. These instructions guide dialogue; they do not guarantee factual
consistency or authorize changes to game state.

### Success: 200 OK

```json
{
  "npc_id": "butler",
  "reply": "I was in the kitchen preparing dinner."
}
```

`reply` is nonempty text intended for display. Its wording varies between requests.
The backend uses a short output-token budget and limits successful replies to
4,000 characters so they can be reused in history. If generated output cannot be
returned within that limit, return `502` with `ai_invalid_response`.

No conversation ID, session ID, or game-state changes are returned.

### Follow-up example

```json
{
  "npc_id": "butler",
  "message": "Was anyone with you?",
  "history": [
    {
      "role": "user",
      "content": "Where were you last night?"
    },
    {
      "role": "assistant",
      "content": "I was in the kitchen preparing dinner."
    }
  ]
}
```

Godot keeps history separately for each NPC. After a successful request, append the
submitted player message and returned reply as a completed exchange. Before the
next request, remove the oldest complete exchanges until both history limits are
satisfied. Keep at most 10 exchanges, with no more than 20,000 content characters.

On failure, do not append either turn to committed conversation history. Preserve
the player's input so they can retry. Disable additional sends while a request is
pending. Do not automatically retry dialogue requests: a timed-out request may
already have reached Claude, and repeating it can generate another reply and cost.

Resetting a conversation clears its history in Godot; no reset endpoint is needed.
History is lost when the game closes. Client-supplied history is not authoritative
evidence of game progress.

## Error responses

Application errors use this envelope:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request contains invalid fields.",
    "details": {
      "message": ["This field must not be empty."]
    }
  }
}
```

`code` is a stable machine-readable value. `message` is readable text and may
change. `details` is optional; for validation errors it maps field paths (such as
`history.0.role`) to arrays of messages. Use `body` for whole-request errors.
Godot should branch on HTTP status and `code`, not on the wording of messages.

| HTTP status | Code | Meaning |
| --- | --- | --- |
| 400 | `invalid_request` | Malformed JSON, missing fields, incorrect types, or violated input/history limits. |
| 404 | `npc_not_found` | A structurally valid request names an unsupported NPC. |
| 405 | `method_not_allowed` | The route does not support the HTTP method. |
| 406 | `not_acceptable` | The requested response format does not allow JSON. |
| 415 | `unsupported_media_type` | A request body uses an unsupported content type. |
| 502 | `ai_invalid_response` | Claude returned no usable text or a reply exceeding the response limit. |
| 503 | `ai_unavailable` | Claude configuration is missing, the provider is rate limited/unavailable, or the backend cannot connect to it. |
| 504 | `ai_timeout` | The backend's Claude request timed out. |
| 500 | `internal_error` | An unexpected backend failure occurred. |

Validate structure and field limits before resolving the NPC and calling Claude.
Invalid requests must not trigger paid generation. Error responses must not expose
API keys, NPC prompts, stack traces, or raw provider error bodies.

Clients must also handle network failures and non-JSON responses, which can occur
outside the Django API. A health response alone does not guarantee that a dialogue
request will succeed.


## Manual request examples (PowerShell)

These examples assume Django is running locally. Dialogue generation also requires
valid Claude configuration and API access. They do not require Godot.

### Health

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/api/health/'
```

### First message

```powershell
$dialogueRequest = @{
    npc_id = 'butler'
    message = 'Where were you last night?'
    history = @()
}

$dialogueReply = Invoke-RestMethod `
    -Method Post `
    -Uri 'http://127.0.0.1:8000/api/dialogue/message/' `
    -ContentType 'application/json' `
    -Body ($dialogueRequest | ConvertTo-Json -Depth 5)

$dialogueReply
```

### Follow-up using the actual first reply

```powershell
$followUpRequest = @{
    npc_id = 'butler'
    message = 'Was anyone with you?'
    history = @(
        @{ role = 'user'; content = $dialogueRequest.message }
        @{ role = 'assistant'; content = $dialogueReply.reply }
    )
}

Invoke-RestMethod `
    -Method Post `
    -Uri 'http://127.0.0.1:8000/api/dialogue/message/' `
    -ContentType 'application/json' `
    -Body ($followUpRequest | ConvertTo-Json -Depth 5)
```

## MVP acceptance checks

- Health returns `200` without making a Claude call or database query.
- A valid first message returns a nonempty generated reply for `butler`.
- A follow-up includes the previous exchange in the Claude request.
- Invalid input returns a documented error without calling Claude.
- Unknown NPCs and simulated provider failures return the documented errors.
- Godot can consume the contract without access to backend secrets.

Automated backend tests should mock Claude. A separate real API smoke test checks
credentials and connectivity; generated wording is not an exact-match test target.

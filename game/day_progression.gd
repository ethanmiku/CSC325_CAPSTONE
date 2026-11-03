extends Control

var current_day: int = 1
var discovered_clues: Array[String] = []
var triggered_events: Array[String] = []

# Placeholder content for testing.
var daily_clues: Dictionary = {
	1: "Torn note",
	2: "Muddy footprint",
	3: "Hidden key"
}

var scheduled_events: Dictionary = {
	2: {
		"id": "day_2_argument",
		"description": "An argument breaks out between two suspects."
	},
	3: {
		"id": "day_3_crime_scene",
		"description": "A new crime scene becomes available."
	}
}

var event_history: Array[String] = []

@onready var day_label: Label = $VBoxContainer/DayLabel
@onready var end_day_button: Button = $VBoxContainer/EndDayButton
@onready var objective_checkbox: CheckBox = $VBoxContainer/ObjectiveCheckBox
@onready var status_label: Label = $VBoxContainer/StatusLabel
@onready var clues_label: Label = $VBoxContainer/CluesLabel
@onready var events_label: Label = $VBoxContainer/EventsLabel


func _ready() -> void:
	end_day_button.pressed.connect(_on_end_day_pressed)
	objective_checkbox.toggled.connect(_on_objective_toggled)

	_start_day()
	_update_clues_display()
	_update_events_display()


func _start_day() -> void:
	day_label.text = "Day %d" % current_day
	objective_checkbox.set_pressed_no_signal(false)

	if not daily_clues.has(current_day):
		objective_checkbox.disabled = true
		objective_checkbox.text = "No more prototype activities"
		end_day_button.disabled = true
		status_label.text = "Prototype complete! Your discoveries are kept."
		return

	var clue_name: String = daily_clues[current_day]
	var already_found: bool = discovered_clues.has(clue_name)

	objective_checkbox.text = "Find clue: %s" % clue_name
	objective_checkbox.set_pressed_no_signal(already_found)
	objective_checkbox.disabled = already_found
	end_day_button.disabled = false

	if already_found:
		status_label.text = "Today's clue is recorded. You can end the day."
	else:
		status_label.text = "Find today's clue before ending the day."

	_trigger_day_event()


func _on_objective_toggled(is_checked: bool) -> void:
	if not is_checked or not daily_clues.has(current_day):
		return

	var clue_name: String = daily_clues[current_day]

	if not discovered_clues.has(clue_name):
		discovered_clues.append(clue_name)

	objective_checkbox.disabled = true
	_update_clues_display()
	status_label.text = "Clue recorded! You can now end the day."


func _on_end_day_pressed() -> void:
	if not daily_clues.has(current_day):
		return

	var required_clue: String = daily_clues[current_day]

	if not discovered_clues.has(required_clue):
		status_label.text = "You cannot end the day yet. Find: %s." % required_clue
		return

	current_day += 1
	_start_day()


func _trigger_day_event() -> void:
	if not scheduled_events.has(current_day):
		return

	var event_data: Dictionary = scheduled_events[current_day]
	var event_id: String = event_data["id"]
	var description: String = event_data["description"]

	# Prevent the same event from triggering more than once.
	if triggered_events.has(event_id):
		return

	triggered_events.append(event_id)
	event_history.append("Day %d: %s" % [current_day, description])
	_update_events_display()


func _update_clues_display() -> void:
	if discovered_clues.is_empty():
		clues_label.text = "Discovered clues: None"
	else:
		clues_label.text = "Discovered clues:\n" + "\n".join(discovered_clues)


func _update_events_display() -> void:
	if event_history.is_empty():
		events_label.text = "Events: None yet"
	else:
		events_label.text = "Event history:\n" + "\n".join(event_history)

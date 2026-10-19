extends SceneTree
## Run after an editor import; see game/docs/evidence-discovery.md.

const OBJECT_SCENE = preload("res://entities/evidence/evidence_object.tscn")
const INTERACTOR_SCENE = preload("res://entities/player/interactor.tscn")
const DISPLAY_SCENE = preload("res://ui/evidence_display.tscn")

var failures: int = 0
var checks: int = 0
var discoveries: int = 0
var results: int = 0
var world: Node2D
var interactor: EvidenceInteractor
var object: EvidenceObject
var display: EvidenceDisplay
var state: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	state = root.get_node("EvidenceState")
	state.evidence_discovered.connect(_on_discovered)
	_test_range_and_discovery()
	_test_empty_and_invalid()
	_test_selection()
	_test_object_lifetime()
	await _test_object_removed_during_investigation()
	await _test_display_replacement()
	await _test_display_input()
	await _test_touch_and_layout()
	await _test_demo()
	_cleanup()
	print("Evidence tests: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)


func _check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error(message)


func _fixture() -> void:
	_cleanup()
	state.reset()
	discoveries = 0
	results = 0
	world = Node2D.new()
	root.add_child(world)
	interactor = INTERACTOR_SCENE.instantiate()
	world.add_child(interactor)
	interactor.investigation_completed.connect(_on_result)
	object = OBJECT_SCENE.instantiate()
	object.name = "AClue"
	object.object_name = "Desk"
	object.evidence = _evidence()
	world.add_child(object)


func _evidence() -> EvidenceData:
	var data := EvidenceData.new()
	data.evidence_id = &"test_note"
	data.evidence_name = "Torn Note"
	data.description = "Meet me in the study."
	return data


func _cleanup() -> void:
	if is_instance_valid(world):
		world.free()
	if is_instance_valid(display):
		display.free()


func _on_discovered(_data: EvidenceData) -> void:
	discoveries += 1


func _on_result(_title: String, _description: String, _already_discovered: bool) -> void:
	results += 1


func _test_range_and_discovery() -> void:
	_fixture()
	object.position.x = interactor.interaction_range + 1
	_check(not interactor.investigate(), "Out-of-range objects cannot be investigated")
	_check(state.discovered_count() == 0 and results == 0, "Out-of-range attempts have no effects")
	object.position.x = interactor.interaction_range
	_check(interactor.investigate(), "The range boundary is inclusive")
	_check(state.is_discovered(&"test_note"), "First investigation records the evidence ID")
	_check(discoveries == 1 and results == 1, "First investigation emits one discovery and result")
	_check(not interactor.investigate(), "Open result blocks repeated investigations")
	interactor.dismiss()
	_check(interactor.investigate(), "Evidence can be reread")
	_check(discoveries == 1 and state.discovered_count() == 1, "Rereading never duplicates discovery")
	interactor.dismiss()
	interactor.refresh_target()
	object.position.x += 1
	_check(not interactor.investigate(), "Tap rechecks range even if the previous target is stale")
	object.position = Vector2.ZERO
	interactor.enabled = false
	_check(not interactor.investigate(), "Disabled interactor cannot investigate")
	interactor.enabled = true
	state.reset()
	_check(not state.is_discovered(&"test_note"), "New-game reset clears IDs")
	_check(interactor.investigate() and discoveries == 2, "Evidence can be discovered in a new run")


func _test_empty_and_invalid() -> void:
	_fixture()
	object.evidence = null
	_check(interactor.investigate(), "Objects without evidence are investigable")
	_check(state.discovered_count() == 0 and discoveries == 0, "Empty objects do not record discoveries")
	interactor.dismiss()
	for field in ["evidence_id", "evidence_name", "description"]:
		var invalid := _evidence()
		invalid.set(field, "   ")
		object.evidence = invalid
		_check(not interactor.investigate(), "Blank %s prevents investigation" % field)
		_check(not state.discover(invalid), "Invalid %s cannot enter discovery state" % field)
	_check(not state.discover(null), "Null evidence cannot enter discovery state")
	object.evidence = _evidence()
	object.hide()
	_check(not interactor.investigate(), "Hidden objects cannot be investigated")
	object.show()
	object.enabled = false
	_check(not interactor.investigate(), "Disabled objects cannot be investigated")


func _test_selection() -> void:
	_fixture()
	var second: EvidenceObject = OBJECT_SCENE.instantiate()
	second.name = "BEmpty"
	world.add_child(second)
	object.position.x = 30
	second.position.x = 10
	interactor.refresh_target()
	_check(interactor.target == second, "Select the nearest object")
	second.position.x = -30
	interactor.refresh_target()
	_check(interactor.target == object, "Equal distances use stable scene-path order")
	_check(interactor.investigate() and results == 1, "One tap investigates only one overlapping target")
	_check(discoveries == 1, "Only selected evidence is discovered")


func _test_object_lifetime() -> void:
	_fixture()
	interactor.investigate()
	interactor.dismiss()
	# Destroy the whole level, then recreate objects with the same authored ID.
	world.free()
	world = Node2D.new()
	root.add_child(world)
	interactor = INTERACTOR_SCENE.instantiate()
	world.add_child(interactor)
	object = OBJECT_SCENE.instantiate()
	object.evidence = _evidence()
	world.add_child(object)
	_check(interactor.investigate(), "Recreated objects remain readable")
	_check(discoveries == 1 and state.discovered_count() == 1, "Discovery survives level recreation")
	interactor.dismiss()
	object.free()
	_check(not interactor.investigate(), "Freed targets are discarded safely")


func _test_object_removed_during_investigation() -> void:
	for signal_name in ["display_open_changed", "evidence_discovered"]:
		_fixture()
		display = DISPLAY_SCENE.instantiate()
		display.interactor = interactor
		root.add_child(display)
		# Immediate frees reproduce the review failure, unlike deferred queue_free().
		var remove_object := func(_value): object.free()
		if signal_name == "display_open_changed":
			interactor.display_open_changed.connect(remove_object, CONNECT_ONE_SHOT)
		else:
			state.evidence_discovered.connect(remove_object, CONNECT_ONE_SHOT)
		_check(interactor.investigate(), "Investigation completes if %s frees the object" % signal_name)
		_check(not is_instance_valid(object), "The %s listener actually freed the object" % signal_name)
		_check(display.modal.visible, "Object removal still displays the result")
		_check(display.title_label.text == "Torn Note", "Object removal preserves the evidence title")
		_check(display.description_label.text == "Meet me in the study.", "Object removal preserves the description")
		_check(discoveries == 1 and state.discovered_count() == 1, "Object removal records exactly one discovery")
		await _tap(display.close_button)
		_check(not interactor.is_display_open and not display.modal.visible, "Result remains dismissible after object removal")
		_check(display.interact_button.disabled, "Freed object cannot be investigated again")


func _test_display_replacement() -> void:
	for deferred in [false, true]:
		_fixture()
		display = DISPLAY_SCENE.instantiate()
		display.interactor = interactor
		root.add_child(display)
		_check(interactor.investigate() and display.modal.visible, "Open evidence before replacing the display")
		if deferred:
			display.queue_free()
		else:
			display.free()
		await process_frame
		await process_frame
		_check(not is_instance_valid(display), "The old display was freed")
		_check(not interactor.is_display_open, "Removing the display releases the interaction lock")
		_check(state.discovered_count() == 1, "Removing the display preserves discovery state")
		display = DISPLAY_SCENE.instantiate()
		display.interactor = interactor
		root.add_child(display)
		_check(not display.modal.visible and not display.interact_button.disabled, "Replacement display starts ready for interaction")
		await _tap(display.interact_button)
		_check(display.modal.visible and display.status_label.text == "Already discovered", "Replacement display can reread evidence")
		_check(discoveries == 1, "Replacing the display does not duplicate discovery")
		await _tap(display.close_button)
		_check(not interactor.is_display_open and not display.modal.visible, "Replacement display can dismiss evidence normally")


func _test_display_input() -> void:
	_fixture()
	display = DISPLAY_SCENE.instantiate()
	display.interactor = interactor
	root.add_child(display)
	await process_frame
	await process_frame
	_check(not display.interact_button.disabled, "UI enables Interact for an in-range target")
	_check(display.target_label.text == "Investigate: Desk", "UI identifies the selected object")
	await _click(display.interact_button)
	_check(display.modal.visible, "Actual button input opens the panel")
	_check(display.title_label.text == "Torn Note", "Panel shows evidence name")
	_check(display.description_label.text == "Meet me in the study.", "Panel shows description")
	_check(not display.status_label.visible, "First discovery is not labeled as a repeat")
	_check(display.interact_button.disabled, "Interact is disabled while panel is open")
	await _click(display.close_button)
	_check(not display.modal.visible and not interactor.is_display_open, "Close dismisses and unlocks interaction")
	await _click(display.interact_button)
	_check(display.status_label.visible and display.status_label.text == "Already discovered", "Reread is labeled")
	_check(discoveries == 1, "UI reread does not emit another discovery")
	await _click(display.close_button)
	object.evidence = null
	await _click(display.interact_button)
	_check(display.title_label.text == "Desk", "Empty result names the investigated object")
	_check(display.description_label.text == "No useful evidence was found.", "Empty result has the required message")
	_check(not display.status_label.visible, "Empty result clears the previous repeat label")
	await _click(display.close_button)
	object.position.x = 500
	await process_frame
	_check(display.interact_button.disabled, "Leaving range disables Interact")
	world.free()
	_check(not display.modal.visible and display.interact_button.disabled, "Removing player safely disables UI")


func _click(button: Button) -> void:
	var location := button.get_global_transform_with_canvas() * (button.size / 2.0)
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = location
		event.global_position = location
		event.pressed = pressed
		root.push_input(event, true)
		await process_frame


func _test_touch_and_layout() -> void:
	_fixture()
	display = DISPLAY_SCENE.instantiate()
	display.interactor = interactor
	root.add_child(display)
	var original_size := root.size
	for viewport_size: Vector2i in [Vector2i(390, 844), Vector2i(844, 390)]:
		root.size = viewport_size
		await process_frame
		await process_frame
		var screen := Rect2(Vector2.ZERO, Vector2(viewport_size))
		_check(screen.encloses(_screen_rect(display.interact_button)), "Interact fits viewport %s" % viewport_size)
		_check(_screen_rect(display.interact_button).size.y >= 63, "Interact has a touch-sized target")
		await _tap(display.interact_button)
		_check(display.modal.visible, "Touch input opens panel at %s" % viewport_size)
		_check(screen.encloses(_screen_rect(display.close_button)), "Close fits viewport %s" % viewport_size)
		await _tap(display.close_button)
		_check(not display.modal.visible and not interactor.is_display_open, "Touch closes panel at %s" % viewport_size)
	_check(discoveries == 1, "Touch reread does not duplicate discovery")
	object.evidence.description = "A long description for scroll testing. ".repeat(250)
	await _tap(display.interact_button)
	await process_frame
	_check(display.description_scroll.get_v_scroll_bar().max_value > display.description_scroll.size.y, "Long evidence text can scroll")
	_check(_screen_rect(display.close_button).end.y <= root.size.y, "Long text keeps Close on screen")
	await _tap(display.close_button)
	root.size = original_size
	await process_frame


func _tap(button: Button) -> void:
	# Containers finish relayout after a modal becomes visible or the window rotates.
	await process_frame
	await process_frame
	var location := _screen_rect(button).get_center()
	for pressed in [true, false]:
		var event := InputEventScreenTouch.new()
		event.index = 0
		event.position = location
		event.pressed = pressed
		Input.parse_input_event(event)
		await process_frame
	await process_frame
	await process_frame


func _screen_rect(control: Control) -> Rect2:
	return root.get_final_transform() * control.get_global_transform_with_canvas() * Rect2(Vector2.ZERO, control.size)


func _test_demo() -> void:
	_cleanup()
	state.reset()
	world = load("res://maps/evidence_demo.tscn").instantiate()
	root.add_child(world)
	await process_frame
	var demo_interactor: EvidenceInteractor = world.get_node("PlayerStandIn/Interactor")
	_check(demo_interactor.investigate(), "Demo wires the player stand-in to evidence")
	_check(world.get_node("EvidenceDisplay").modal.visible, "Demo wires interaction to UI")
	demo_interactor.dismiss()
	var options: OptionButton = world.get_node("DemoControls/Margin/Content/Scenario")
	options.select(1)
	options.item_selected.emit(1)
	_check(demo_interactor.investigate(), "Demo empty-object scenario is in range")
	_check(world.get_node("EvidenceDisplay").description_label.text == "No useful evidence was found.", "Demo empty scenario displays required text")
	demo_interactor.dismiss()
	options.select(2)
	options.item_selected.emit(2)
	_check(not demo_interactor.investigate(), "Demo out-of-range scenario rejects interaction")

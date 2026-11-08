
extends Control

@onready var master_slider: HSlider = $VBoxContainer/MasterVolumeSlider
@onready var sfx_slider: HSlider = $VBoxContainer/SFXVolumeSlider


@onready var test_button: Button = $VBoxContainer/TestSoundButton
@onready var test_sfx_player: AudioStreamPlayer = $TestSFXPlayer
@onready var restore_button: Button = $VBoxContainer/RestoreDefaultsButton
@onready var dialogue_speed_option: OptionButton = $VBoxContainer/DialogueSpeedOption
@onready var sfx_toggle: CheckBox = $VBoxContainer/SFXToggle

var dialogue_speed: float = 0.03
func _ready() -> void:
	master_slider.value_changed.connect(_on_master_volume_changed)
	sfx_slider.value_changed.connect(_on_sfx_volume_changed)
	test_button.pressed.connect(_on_test_sound_pressed)
	restore_button.pressed.connect(_on_restore_defaults_pressed)
	dialogue_speed_option.item_selected.connect(_on_dialogue_speed_selected)
	sfx_toggle.toggled.connect(_on_sfx_toggled)
		
func _on_master_volume_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(0, linear_to_db(value / 100.0))

func _on_sfx_volume_changed(value: float) -> void:
	var sfx_bus = AudioServer.get_bus_index("SFX")
	if sfx_bus != -1:
		AudioServer.set_bus_volume_db(sfx_bus, linear_to_db(value / 100.0))

func _on_test_sound_pressed() -> void:
	test_sfx_player.play()

func _on_restore_defaults_pressed() -> void:
	master_slider.value = 100
	sfx_slider.value = 100
	dialogue_speed_option.select(1)
	dialogue_speed = 0.03
	sfx_toggle.button_pressed = true
func _on_dialogue_speed_selected(index: int) -> void:
	match index:
		0:
			dialogue_speed = 0.06
		1:
			dialogue_speed = 0.03
		2:
			dialogue_speed = 0.01

	print("Dialogue speed: ", dialogue_speed)
func _on_sfx_toggled(enabled: bool) -> void:
	var sfx_bus = AudioServer.get_bus_index("SFX")
	if sfx_bus != -1:
		AudioServer.set_bus_mute(sfx_bus, not enabled)

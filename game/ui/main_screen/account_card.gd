extends Button
## Prototype credentials only. Route pressed to the login panel's autofill method.
@export var account_role := "DEVELOPER"
@export var username := "dev_admin"
@export var password := "blackwood#dev"
@export var accent := Color("33ad9e")

func _ready() -> void:
	$Role.text = account_role
	$Role.add_theme_color_override("font_color", accent)
	$Username.text = "user  " + username
	$Password.text = "pass  " + password
	for state in ["normal", "hover", "pressed", "focus"]:
		var style := get_theme_stylebox(state).duplicate() as StyleBoxFlat
		style.border_color = accent
		add_theme_stylebox_override(state, style)

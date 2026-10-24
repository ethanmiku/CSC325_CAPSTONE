extends Control
## UI only: connect login_requested to your authentication service.
signal login_requested(username: String, password: String)

func _ready() -> void:
	$LogIn.pressed.connect(_submit)
	$Password.text_submitted.connect(func(_text: String): _submit())

func autofill(username: String, password: String) -> void:
	$Username.text = username
	$Password.text = password

func set_status(message: String, is_error := false) -> void:
	$Status.text = message
	$Status.add_theme_color_override("font_color", Color("e38787") if is_error else Color("33ad9e"))

func _submit() -> void:
	login_requested.emit($Username.text, $Password.text)

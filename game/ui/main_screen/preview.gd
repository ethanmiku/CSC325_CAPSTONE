extends Control
## Preview wiring: real authentication and gameplay routing belong to the host game.
signal menu_requested(action: String)

func _ready() -> void:
	for card in [$Developer, $Player]:
		card.pressed.connect(func(): $Login.autofill(card.username, card.password))
	$Login.login_requested.connect(func(_username: String, _password: String):
		$Login.set_status("Connect login_requested to authentication"))
	for button in [$NewGame, $Continue, $Settings]:
		button.pressed.connect(func(): menu_requested.emit(button.text))

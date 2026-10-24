extends SceneTree

func _initialize() -> void:
	root.size = Vector2i(874, 402)
	root.content_scale_size = Vector2i(874, 402)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var screen := load("res://ui/main_screen/main_screen_preview.tscn") as PackedScene
	root.add_child(screen.instantiate())
	_capture.call_deferred()

func _capture() -> void:
	for frame in range(12):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://ui/main_screen/preview.png")
	quit()

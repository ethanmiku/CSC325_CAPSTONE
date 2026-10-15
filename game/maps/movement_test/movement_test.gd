# Makes a checkerboard map on movement_test.tscn to visibly see that the player is moving
extends Node2D

@export var tile_size: int = 128
@export var grid_color_a: Color = Color(0.85, 0.85, 0.85)
@export var grid_color_b: Color = Color(0.65, 0.65, 0.65)
@export var area_size: Vector2 = Vector2(4096, 4096)

func _ready() -> void:
	queue_redraw()

func _draw() -> void:
	var half := area_size / 2.0
	var cols := int(area_size.x / tile_size)
	var rows := int(area_size.y / tile_size)
	for y in rows:
		for x in cols:
			var color := grid_color_a if (x + y) % 2 == 0 else grid_color_b
			var pos := Vector2(-half.x + x * tile_size, -half.y + y * tile_size)
			draw_rect(Rect2(pos, Vector2(tile_size, tile_size)), color)

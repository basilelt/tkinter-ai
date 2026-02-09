## ItemCard — Reusable UI component for displaying a loot item
extends PanelContainer

signal item_pressed(item_data: Dictionary)

var _item_data: Dictionary = {}
var _icon_rect: ColorRect
var _name_label: Label
var _rarity_label: Label
var _quantity_label: Label

func _ready() -> void:
	_build_ui()

func setup(item_data: Dictionary, quantity: int = 1) -> void:
	_item_data = item_data
	if not is_inside_tree():
		await ready
	_update_display(quantity)

func _build_ui() -> void:
	custom_minimum_size = Vector2(150, 180)
	mouse_filter = Control.MOUSE_FILTER_STOP

	# Rarity-colored panel style
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.15, 0.14, 0.22)
	style.border_color = Color(0.3, 0.3, 0.4)
	style.set_border_width_all(2)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(8)
	add_theme_stylebox_override("panel", style)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	add_child(vbox)

	# Icon placeholder (colored shape)
	var icon_container := CenterContainer.new()
	icon_container.custom_minimum_size = Vector2(0, 80)
	vbox.add_child(icon_container)

	_icon_rect = ColorRect.new()
	_icon_rect.custom_minimum_size = Vector2(64, 64)
	_icon_rect.size = Vector2(64, 64)
	icon_container.add_child(_icon_rect)

	# Item name
	_name_label = Label.new()
	_name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_label.add_theme_font_size_override("font_size", 13)
	_name_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.95))
	_name_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	_name_label.custom_minimum_size = Vector2(0, 32)
	vbox.add_child(_name_label)

	# Rarity
	_rarity_label = Label.new()
	_rarity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_rarity_label.add_theme_font_size_override("font_size", 11)
	vbox.add_child(_rarity_label)

	# Quantity badge
	_quantity_label = Label.new()
	_quantity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_quantity_label.add_theme_font_size_override("font_size", 11)
	_quantity_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.75))
	vbox.add_child(_quantity_label)

	# Click handler
	gui_input.connect(_on_gui_input)

func _update_display(quantity: int) -> void:
	if _item_data.is_empty():
		return

	var rarity: int = int(_item_data.get("rarity", 0))
	var rarity_color: Color = ItemDatabase.RARITY_COLORS.get(rarity, Color.GRAY) as Color
	var rarity_light: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.GRAY) as Color

	# Update border color to match rarity
	var style := get_theme_stylebox("panel").duplicate() as StyleBoxFlat
	style.border_color = rarity_color
	match rarity:
		ItemDatabase.Rarity.LEGENDARY:
			style.set_border_width_all(3)
			style.bg_color = Color(0.2, 0.16, 0.08)
		ItemDatabase.Rarity.EPIC:
			style.set_border_width_all(3)
			style.bg_color = Color(0.18, 0.1, 0.22)
		ItemDatabase.Rarity.RARE:
			style.bg_color = Color(0.1, 0.14, 0.22)
		_:
			style.bg_color = Color(0.15, 0.14, 0.18)
	add_theme_stylebox_override("panel", style)

	# Icon color
	_icon_rect.color = _item_data.get("icon_color", Color.WHITE) as Color

	# Name
	_name_label.text = str(_item_data.get("name", "Unknown"))

	# Rarity text
	var rarity_name: String = str(ItemDatabase.RARITY_NAMES.get(rarity, "Common"))
	_rarity_label.text = rarity_name
	_rarity_label.add_theme_color_override("font_color", rarity_light)

	# Quantity
	if quantity > 1:
		_quantity_label.text = "x%d" % quantity
		_quantity_label.visible = true
	else:
		_quantity_label.visible = false

func _on_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		AudioManager.play_sfx("button_click")
		item_pressed.emit(_item_data)

func get_item_data() -> Dictionary:
	return _item_data

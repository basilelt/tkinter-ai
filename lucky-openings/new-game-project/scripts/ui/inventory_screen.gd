## InventoryScreen — View collected items with filtering and item details
extends Control

signal navigate_to(screen_name: String)

var _grid: GridContainer
var _filter_buttons: Dictionary = {}
var _current_filter: int = -1  # -1 = all
var _detail_popup: PanelContainer
var _items_count_label: Label
var _completion_label: Label

const ItemCardScript = preload("res://scripts/ui/item_card.gd")

func _ready() -> void:
	_build_ui()
	_refresh_grid()
	GameManager.inventory_changed.connect(_refresh_grid)

func _build_ui() -> void:
	# Background
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.08, 0.07, 0.14)
	add_child(bg)

	var main_vbox := VBoxContainer.new()
	main_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	main_vbox.set_anchor_and_offset(SIDE_LEFT, 0.0, 15)
	main_vbox.set_anchor_and_offset(SIDE_RIGHT, 1.0, -15)
	main_vbox.set_anchor_and_offset(SIDE_TOP, 0.0, 15)
	main_vbox.set_anchor_and_offset(SIDE_BOTTOM, 1.0, -15)
	main_vbox.add_theme_constant_override("separation", 10)
	add_child(main_vbox)

	# ── Top bar ──
	var top_bar := HBoxContainer.new()
	top_bar.add_theme_constant_override("separation", 10)
	main_vbox.add_child(top_bar)

	var back_btn := Button.new()
	back_btn.text = "← Back"
	back_btn.custom_minimum_size = Vector2(80, 40)
	_style_small_button(back_btn, Color(0.4, 0.38, 0.55))
	back_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		navigate_to.emit("main_menu"))
	top_bar.add_child(back_btn)

	var title := Label.new()
	title.text = "📦 INVENTORY"
	title.add_theme_font_size_override("font_size", 24)
	title.add_theme_color_override("font_color", Color(0.39, 0.71, 0.96))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	top_bar.add_child(title)

	# Completion label
	_completion_label = Label.new()
	_completion_label.add_theme_font_size_override("font_size", 14)
	_completion_label.add_theme_color_override("font_color", Color(0.6, 0.58, 0.7))
	top_bar.add_child(_completion_label)

	# ── Filter row ──
	var filter_scroll := ScrollContainer.new()
	filter_scroll.custom_minimum_size = Vector2(0, 44)
	filter_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	main_vbox.add_child(filter_scroll)

	var filter_row := HBoxContainer.new()
	filter_row.add_theme_constant_override("separation", 6)
	filter_scroll.add_child(filter_row)

	# "All" filter
	var all_btn := _create_filter_button("All", -1, Color(0.5, 0.48, 0.65))
	filter_row.add_child(all_btn)
	_filter_buttons[-1] = all_btn

	# Category filters
	for cat in ItemDatabase.CATEGORY_NAMES:
		var cat_name: String = ItemDatabase.CATEGORY_NAMES[cat]
		var colors := [Color(0.8, 0.5, 0.2), Color(0.3, 0.85, 0.4), Color(1.0, 0.3, 0.5),
			Color(0.5, 0.8, 1.0), Color(0.7, 0.5, 0.3)]
		var color: Color = colors[cat] if cat < colors.size() else Color.GRAY
		var btn := _create_filter_button(cat_name, cat, color)
		filter_row.add_child(btn)
		_filter_buttons[cat] = btn

	# ── Items count ──
	_items_count_label = Label.new()
	_items_count_label.add_theme_font_size_override("font_size", 13)
	_items_count_label.add_theme_color_override("font_color", Color(0.5, 0.48, 0.6))
	main_vbox.add_child(_items_count_label)

	# ── Scrollable grid ──
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	main_vbox.add_child(scroll)

	_grid = GridContainer.new()
	_grid.columns = 4
	_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_grid.add_theme_constant_override("h_separation", 8)
	_grid.add_theme_constant_override("v_separation", 8)
	scroll.add_child(_grid)

func _create_filter_button(text: String, filter_id: int, color: Color) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(70, 34)
	btn.toggle_mode = true
	btn.button_pressed = (filter_id == _current_filter)
	_style_small_button(btn, color)
	btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		_current_filter = filter_id
		_update_filter_visuals()
		_refresh_grid())
	return btn

func _update_filter_visuals() -> void:
	for fid in _filter_buttons:
		_filter_buttons[fid].button_pressed = (fid == _current_filter)

func _refresh_grid() -> void:
	# Clear existing cards
	for child in _grid.get_children():
		child.queue_free()

	var entries := GameManager.inventory.duplicate()

	# Sort by rarity (Legendary first)
	entries.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var item_a := ItemDatabase.get_item(str(a.get("item_id", "")))
		var item_b := ItemDatabase.get_item(str(b.get("item_id", "")))
		return int(item_a.get("rarity", 0)) > int(item_b.get("rarity", 0)))

	var displayed := 0
	for entry: Dictionary in entries:
		var item_data := ItemDatabase.get_item(str(entry.get("item_id", "")))
		if item_data.is_empty():
			continue

		# Category filter
		if _current_filter >= 0 and item_data.get("category", -1) != _current_filter:
			continue

		var card := PanelContainer.new()
		card.set_script(ItemCardScript)
		_grid.add_child(card)
		card.setup(item_data, int(entry.get("quantity", 1)))
		card.item_pressed.connect(_on_item_pressed)
		displayed += 1

	# Update counts
	_items_count_label.text = "%d unique items | %d total" % [
		GameManager.get_total_unique_items(), GameManager.get_total_items()]
	_completion_label.text = "%.1f%%" % GameManager.get_completion_percentage()

	# Empty state
	if displayed == 0:
		var empty := Label.new()
		empty.text = "No items yet!\nOpen some boxes to get started."
		empty.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		empty.add_theme_font_size_override("font_size", 16)
		empty.add_theme_color_override("font_color", Color(0.5, 0.48, 0.6))
		_grid.add_child(empty)

func _on_item_pressed(item_data: Dictionary) -> void:
	_show_item_detail(item_data)

func _show_item_detail(item_data: Dictionary) -> void:
	if _detail_popup:
		_detail_popup.queue_free()

	var rarity: int = int(item_data.get("rarity", 0))
	var rarity_color: Color = ItemDatabase.RARITY_COLORS.get(rarity, Color.GRAY) as Color
	var rarity_light: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.GRAY) as Color
	var quantity := GameManager.get_item_count(str(item_data.get("id", "")))

	_detail_popup = PanelContainer.new()
	_detail_popup.set_anchors_preset(Control.PRESET_CENTER)
	_detail_popup.custom_minimum_size = Vector2(340, 320)
	_detail_popup.position -= Vector2(170, 160)

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.09, 0.18, 0.98)
	style.border_color = rarity_color
	style.set_border_width_all(3)
	style.set_corner_radius_all(14)
	style.set_content_margin_all(20)
	_detail_popup.add_theme_stylebox_override("panel", style)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	_detail_popup.add_child(vbox)

	# Icon
	var icon_center := CenterContainer.new()
	vbox.add_child(icon_center)
	var icon := ColorRect.new()
	icon.custom_minimum_size = Vector2(80, 80)
	icon.color = item_data.get("icon_color", Color.WHITE)
	icon_center.add_child(icon)

	# Name
	var name_label := Label.new()
	name_label.text = item_data.get("name", "Unknown")
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 22)
	name_label.add_theme_color_override("font_color", rarity_light)
	vbox.add_child(name_label)

	# Rarity
	var rarity_label := Label.new()
	rarity_label.text = str(ItemDatabase.RARITY_NAMES.get(rarity, "Common"))
	rarity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rarity_label.add_theme_font_size_override("font_size", 14)
	rarity_label.add_theme_color_override("font_color", rarity_color)
	vbox.add_child(rarity_label)

	# Description
	var desc := Label.new()
	desc.text = str(item_data.get("description", ""))
	desc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD
	desc.add_theme_font_size_override("font_size", 14)
	desc.add_theme_color_override("font_color", Color(0.7, 0.68, 0.8))
	vbox.add_child(desc)

	# Quantity
	var qty_label := Label.new()
	qty_label.text = "Owned: x%d" % quantity
	qty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	qty_label.add_theme_font_size_override("font_size", 14)
	qty_label.add_theme_color_override("font_color", Color(0.6, 0.58, 0.7))
	vbox.add_child(qty_label)

	# Buttons
	var btn_row := HBoxContainer.new()
	btn_row.add_theme_constant_override("separation", 10)
	btn_row.alignment = BoxContainer.ALIGNMENT_CENTER
	vbox.add_child(btn_row)

	if quantity > 1:  # Can sell duplicates
		var sell_btn := Button.new()
		var sell_val: int = int(item_data.get("sell_value", 0))
		if quantity >= 3:
			sell_val = int(sell_val * 1.5)
		sell_btn.text = "Sell (🪙 %d)" % sell_val
		sell_btn.custom_minimum_size = Vector2(130, 40)
		_style_small_button(sell_btn, Color(0.9, 0.4, 0.3))
		sell_btn.pressed.connect(func():
			AudioManager.play_sfx("sell_item")
			GameManager.sell_item(str(item_data.get("id", "")))
			_detail_popup.queue_free()
			_detail_popup = null
			_refresh_grid())
		btn_row.add_child(sell_btn)

	var close_btn := Button.new()
	close_btn.text = "Close"
	close_btn.custom_minimum_size = Vector2(100, 40)
	_style_small_button(close_btn, Color(0.4, 0.38, 0.55))
	close_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		_detail_popup.queue_free()
		_detail_popup = null)
	btn_row.add_child(close_btn)

	add_child(_detail_popup)

	# Entrance animation
	_detail_popup.scale = Vector2(0.8, 0.8)
	_detail_popup.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(_detail_popup, "scale", Vector2.ONE, 0.2)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(_detail_popup, "modulate:a", 1.0, 0.15)

func _style_small_button(btn: Button, color: Color) -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(color.r * 0.3, color.g * 0.3, color.b * 0.3, 0.9)
	style.border_color = color
	style.set_border_width_all(1)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(6)
	btn.add_theme_stylebox_override("normal", style)

	var hover := style.duplicate() as StyleBoxFlat
	hover.bg_color = Color(color.r * 0.45, color.g * 0.45, color.b * 0.45, 0.95)
	btn.add_theme_stylebox_override("hover", hover)

	var pressed := style.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(color.r * 0.55, color.g * 0.55, color.b * 0.55, 1.0)
	btn.add_theme_stylebox_override("pressed", pressed)

	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color", Color(0.9, 0.88, 0.95))

func refresh() -> void:
	_refresh_grid()

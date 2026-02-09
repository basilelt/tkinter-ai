## OpeningResult — Post-opening overlay showing the revealed item
extends Control

signal open_another_pressed
signal back_to_menu_pressed
signal view_inventory_pressed

var _item_data: Dictionary = {}
var _is_new: bool = false
var _box_level: int = 1
var _box_xp: int = 0
var _box_xp_needed: int = 5
var _leveled_up: bool = false

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP  # Block clicks through

func show_result(item: Dictionary, is_new: bool = false, box_level: int = 1,
		box_xp: int = 0, box_xp_needed: int = 5, leveled_up: bool = false) -> void:
	_item_data = item
	_is_new = is_new
	_box_level = box_level
	_box_xp = box_xp
	_box_xp_needed = box_xp_needed
	_leveled_up = leveled_up
	_build_ui()
	_play_entrance_animation()

func _build_ui() -> void:
	# Clear previous
	for child in get_children():
		child.queue_free()

	var rarity: int = int(_item_data.get("rarity", 0))
	var rarity_color: Color = ItemDatabase.RARITY_COLORS.get(rarity, Color.GRAY) as Color
	var rarity_light: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.GRAY) as Color
	var rarity_name: String = str(ItemDatabase.RARITY_NAMES.get(rarity, "Common"))

	# Semi-transparent background
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.7)
	dim.name = "Dim"
	add_child(dim)

	# Main container
	var center := VBoxContainer.new()
	center.set_anchors_preset(Control.PRESET_CENTER)
	center.custom_minimum_size = Vector2(400, 500)
	center.position -= Vector2(200, 250)
	center.add_theme_constant_override("separation", 16)
	center.name = "Content"
	add_child(center)

	# ── Rarity banner ──
	var banner := PanelContainer.new()
	var banner_style := StyleBoxFlat.new()
	banner_style.bg_color = Color(rarity_color.r * 0.4, rarity_color.g * 0.4,
		rarity_color.b * 0.4, 0.95)
	banner_style.border_color = rarity_color
	banner_style.set_border_width_all(2)
	banner_style.set_corner_radius_all(10)
	banner_style.set_content_margin_all(10)
	banner.add_theme_stylebox_override("panel", banner_style)
	center.add_child(banner)

	var banner_label := Label.new()
	banner_label.text = "★ %s ★" % rarity_name.to_upper()
	banner_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner_label.add_theme_font_size_override("font_size", 28)
	banner_label.add_theme_color_override("font_color", rarity_light)
	banner_label.name = "BannerLabel"
	banner.add_child(banner_label)

	# NEW badge
	if _is_new:
		var new_label := Label.new()
		new_label.text = "✨ NEW! ✨"
		new_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		new_label.add_theme_font_size_override("font_size", 22)
		new_label.add_theme_color_override("font_color", Color(0.3, 1.0, 0.5))
		new_label.name = "NewBadge"
		center.add_child(new_label)
	else:
		var dupe_label := Label.new()
		var sell_val: int = int(_item_data.get("sell_value", 0))
		var qty: int = GameManager.get_item_count(str(_item_data.get("id", "")))
		if qty >= 3:
			sell_val = int(sell_val * 1.5)
		dupe_label.text = "Duplicate (Sell for 🪙 %d)" % sell_val
		dupe_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		dupe_label.add_theme_font_size_override("font_size", 14)
		dupe_label.add_theme_color_override("font_color", Color(0.6, 0.58, 0.7))
		center.add_child(dupe_label)

	# ── Item icon ──
	var icon_center := CenterContainer.new()
	center.add_child(icon_center)
	var icon := ColorRect.new()
	icon.custom_minimum_size = Vector2(100, 100)
	icon.color = _item_data.get("icon_color", Color.WHITE) as Color
	icon.name = "ItemIcon"
	icon_center.add_child(icon)

	# ── Item name ──
	var name_label := Label.new()
	name_label.text = str(_item_data.get("name", "Unknown"))
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 24)
	name_label.add_theme_color_override("font_color", rarity_light)
	name_label.name = "ItemName"
	center.add_child(name_label)

	# ── Description ──
	var desc := Label.new()
	desc.text = str(_item_data.get("description", ""))
	desc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD
	desc.add_theme_font_size_override("font_size", 14)
	desc.add_theme_color_override("font_color", Color(0.7, 0.68, 0.8))
	center.add_child(desc)

	# ── Category ──
	var category: int = int(_item_data.get("category", 0))
	var cat_label := Label.new()
	cat_label.text = str(ItemDatabase.CATEGORY_NAMES.get(category, "Unknown"))
	cat_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cat_label.add_theme_font_size_override("font_size", 12)
	cat_label.add_theme_color_override("font_color", Color(0.5, 0.48, 0.6))
	center.add_child(cat_label)

	# ── Level-up celebration banner ──
	if _leveled_up:
		var lvl_banner := PanelContainer.new()
		var lvl_style := StyleBoxFlat.new()
		lvl_style.bg_color = Color(0.15, 0.4, 0.1, 0.95)
		lvl_style.border_color = Color(0.3, 1.0, 0.3)
		lvl_style.set_border_width_all(2)
		lvl_style.set_corner_radius_all(8)
		lvl_style.set_content_margin_all(8)
		lvl_banner.add_theme_stylebox_override("panel", lvl_style)
		lvl_banner.name = "LevelUpBanner"
		center.add_child(lvl_banner)

		var tier_name: String = GameManager.get_tier_name_for_level()
		var lvl_label := Label.new()
		lvl_label.text = "🎉 LEVEL UP! Lv.%d — %s" % [_box_level, tier_name]
		lvl_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lvl_label.add_theme_font_size_override("font_size", 18)
		lvl_label.add_theme_color_override("font_color", Color(0.3, 1.0, 0.5))
		lvl_banner.add_child(lvl_label)

	# ── Buttons ──
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 10)
	center.add_child(spacer)

	var btn_container := VBoxContainer.new()
	btn_container.add_theme_constant_override("separation", 10)
	btn_container.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	center.add_child(btn_container)

	var open_btn := _create_button("⚡  Next  →", Color(1.0, 0.65, 0.0), true)
	open_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		open_another_pressed.emit())
	btn_container.add_child(open_btn)

	var shop_btn := _create_button("🏠  Menu", Color(0.39, 0.71, 0.96), false)
	shop_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		back_to_menu_pressed.emit())
	btn_container.add_child(shop_btn)

	var inv_btn := _create_button("📦  Inventory", Color(0.5, 0.48, 0.65), false)
	inv_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		view_inventory_pressed.emit())
	btn_container.add_child(inv_btn)

func _create_button(text: String, color: Color, primary: bool = false) -> Button:
	var btn := Button.new()
	btn.text = text
	var btn_height: int = 60 if primary else 44
	var font_sz: int = 22 if primary else 16
	btn.custom_minimum_size = Vector2(280, btn_height)

	var style := StyleBoxFlat.new()
	var bg_mult: float = 0.45 if primary else 0.3
	style.bg_color = Color(color.r * bg_mult, color.g * bg_mult, color.b * bg_mult, 0.95)
	style.border_color = color
	style.set_border_width_all(3 if primary else 2)
	style.set_corner_radius_all(12 if primary else 10)
	style.set_content_margin_all(10)
	btn.add_theme_stylebox_override("normal", style)

	var hover := style.duplicate() as StyleBoxFlat
	hover.bg_color = Color(color.r * 0.55, color.g * 0.55, color.b * 0.55, 0.98)
	btn.add_theme_stylebox_override("hover", hover)

	var pressed := style.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(color.r * 0.6, color.g * 0.6, color.b * 0.6)
	btn.add_theme_stylebox_override("pressed", pressed)

	btn.add_theme_font_size_override("font_size", font_sz)
	btn.add_theme_color_override("font_color", Color(0.95, 0.93, 1.0))

	return btn

func _play_entrance_animation() -> void:
	var dim := get_node_or_null("Dim")
	var content := get_node_or_null("Content")
	if not dim or not content:
		return

	# Fade in dim
	dim.modulate.a = 0.0
	var dim_tween := create_tween()
	dim_tween.tween_property(dim, "modulate:a", 1.0, 0.3)

	# Scale + fade content
	content.scale = Vector2(0.5, 0.5)
	content.modulate.a = 0.0
	var content_tween := create_tween()
	content_tween.tween_property(content, "scale", Vector2.ONE, 0.4)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	content_tween.parallel().tween_property(content, "modulate:a", 1.0, 0.25)

	# Banner slide-in
	var banner_label = content.get_node_or_null("BannerLabel")
	if banner_label:
		pass  # The whole content is already animated

	# Rarity-specific extras
	var rarity2: int = int(_item_data.get("rarity", 0))
	if rarity2 >= ItemDatabase.Rarity.EPIC:
		# Pulsing glow on icon
		var icon = get_node_or_null("Content/ItemIcon")
		if icon:
			var pulse := create_tween().set_loops(0)
			pulse.tween_property(icon, "modulate:a", 0.7, 0.5)
			pulse.tween_property(icon, "modulate:a", 1.0, 0.5)

func play_exit_animation() -> void:
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.2)
	tween.tween_callback(queue_free)

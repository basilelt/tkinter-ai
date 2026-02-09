## ShopScreen — Buy and open loot boxes of different tiers
extends Control

signal navigate_to(screen_name: String)
signal open_box_requested(tier: int)

var _coins_label: Label
var _box_buttons: Dictionary = {}  # tier -> Button
var _drop_rates_popup: PanelContainer

func _ready() -> void:
	_build_ui()
	GameManager.coins_changed.connect(_on_coins_changed)
	_on_coins_changed(GameManager.coins)

func _build_ui() -> void:
	# Background
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.08, 0.07, 0.14)
	add_child(bg)

	# Main layout
	var main_vbox := VBoxContainer.new()
	main_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	main_vbox.set_anchor_and_offset(SIDE_LEFT, 0.0, 20)
	main_vbox.set_anchor_and_offset(SIDE_RIGHT, 1.0, -20)
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
	_style_button(back_btn, Color(0.4, 0.38, 0.55))
	back_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		navigate_to.emit("main_menu"))
	top_bar.add_child(back_btn)

	var title := Label.new()
	title.text = "🎁 LOOT SHOP"
	title.add_theme_font_size_override("font_size", 26)
	title.add_theme_color_override("font_color", Color(1.0, 0.84, 0.31))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	top_bar.add_child(title)

	var coin_box := HBoxContainer.new()
	coin_box.add_theme_constant_override("separation", 4)
	top_bar.add_child(coin_box)

	var coin_icon := Label.new()
	coin_icon.text = "🪙"
	coin_icon.add_theme_font_size_override("font_size", 20)
	coin_box.add_child(coin_icon)

	_coins_label = Label.new()
	_coins_label.text = "0"
	_coins_label.add_theme_font_size_override("font_size", 20)
	_coins_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.31))
	coin_box.add_child(_coins_label)

	# ── Scrollable box cards ──
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	main_vbox.add_child(scroll)

	var grid := VBoxContainer.new()
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("separation", 16)
	scroll.add_child(grid)

	# Create a card for each tier
	for tier in [LootTable.BoxTier.COMMON, LootTable.BoxTier.RARE,
			LootTable.BoxTier.EPIC, LootTable.BoxTier.LEGENDARY]:
		var card := _create_box_card(tier)
		grid.add_child(card)

	# ── Pity info ──
	var pity_label := Label.new()
	pity_label.text = "Pity: Epic in %d opens | Legendary in %d opens" % [
		LootTable.PITY_EPIC_THRESHOLD - GameManager.pity_counter_epic,
		LootTable.PITY_LEGENDARY_THRESHOLD - GameManager.pity_counter_legendary]
	pity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pity_label.add_theme_font_size_override("font_size", 12)
	pity_label.add_theme_color_override("font_color", Color(0.5, 0.48, 0.6))
	main_vbox.add_child(pity_label)

func _create_box_card(tier: int) -> PanelContainer:
	var info := LootTable.get_box_info(tier)
	var box_color: Color = info.get("color", Color.WHITE) as Color
	var box_light: Color = info.get("color_light", Color.WHITE) as Color
	var tier_name: String = str(info.get("name", "Box"))
	var cost: int = int(info.get("cost", 0))
	var bulk_cost: int = int(info.get("bulk_cost", 0))

	var card := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(box_color.r * 0.15, box_color.g * 0.15, box_color.b * 0.15, 0.9)
	style.border_color = box_color
	style.set_border_width_all(2)
	style.set_corner_radius_all(12)
	style.set_content_margin_all(16)
	card.add_theme_stylebox_override("panel", style)

	var hbox := HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 16)
	card.add_child(hbox)

	# Box preview (colored rect as placeholder for 3D preview)
	var box_preview := ColorRect.new()
	box_preview.custom_minimum_size = Vector2(80, 80)
	box_preview.color = box_color

	# Round the preview
	var preview_container := PanelContainer.new()
	var pstyle := StyleBoxFlat.new()
	pstyle.bg_color = box_color
	pstyle.set_corner_radius_all(8)
	preview_container.add_theme_stylebox_override("panel", pstyle)
	preview_container.custom_minimum_size = Vector2(80, 80)

	# Add a centered icon
	var box_icon := Label.new()
	box_icon.text = "📦"
	box_icon.add_theme_font_size_override("font_size", 36)
	box_icon.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box_icon.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	box_icon.size_flags_vertical = Control.SIZE_EXPAND_FILL
	preview_container.add_child(box_icon)

	hbox.add_child(preview_container)

	# Info column
	var info_vbox := VBoxContainer.new()
	info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info_vbox.add_theme_constant_override("separation", 4)
	hbox.add_child(info_vbox)

	var name_label := Label.new()
	name_label.text = tier_name
	name_label.add_theme_font_size_override("font_size", 20)
	name_label.add_theme_color_override("font_color", box_light)
	info_vbox.add_child(name_label)

	# Drop rate preview
	var rates_btn := Button.new()
	rates_btn.text = "View Drop Rates ▾"
	rates_btn.flat = true
	rates_btn.add_theme_font_size_override("font_size", 12)
	rates_btn.add_theme_color_override("font_color", Color(0.6, 0.58, 0.7))
	rates_btn.pressed.connect(func(): _show_drop_rates(tier))
	info_vbox.add_child(rates_btn)

	# Button row
	var btn_row := HBoxContainer.new()
	btn_row.add_theme_constant_override("separation", 8)
	info_vbox.add_child(btn_row)

	# Single buy
	var buy_btn := Button.new()
	buy_btn.text = "🪙 %d" % cost
	buy_btn.custom_minimum_size = Vector2(100, 44)
	_style_button(buy_btn, box_color)
	buy_btn.pressed.connect(func(): _on_buy_pressed(tier))
	btn_row.add_child(buy_btn)
	_box_buttons[tier] = buy_btn

	# Bulk buy (10x)
	var bulk_btn := Button.new()
	bulk_btn.text = "10x 🪙 %d" % bulk_cost
	bulk_btn.custom_minimum_size = Vector2(130, 44)
	_style_button(bulk_btn, Color(box_color.r * 0.8, box_color.g * 0.8, box_color.b * 0.8))
	bulk_btn.pressed.connect(func(): _on_bulk_buy_pressed(tier))
	btn_row.add_child(bulk_btn)

	return card

func _style_button(btn: Button, color: Color) -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(color.r * 0.4, color.g * 0.4, color.b * 0.4, 0.95)
	style.border_color = color
	style.set_border_width_all(1)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(8)
	btn.add_theme_stylebox_override("normal", style)

	var hover := style.duplicate() as StyleBoxFlat
	hover.bg_color = Color(color.r * 0.55, color.g * 0.55, color.b * 0.55, 1.0)
	btn.add_theme_stylebox_override("hover", hover)

	var pressed := style.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(color.r * 0.65, color.g * 0.65, color.b * 0.65, 1.0)
	btn.add_theme_stylebox_override("pressed", pressed)

	var disabled := style.duplicate() as StyleBoxFlat
	disabled.bg_color = Color(0.15, 0.14, 0.2, 0.6)
	disabled.border_color = Color(0.3, 0.28, 0.35)
	btn.add_theme_stylebox_override("disabled", disabled)

	btn.add_theme_font_size_override("font_size", 15)
	btn.add_theme_color_override("font_color", Color(0.95, 0.93, 1.0))

func _on_buy_pressed(tier: int) -> void:
	var info := LootTable.get_box_info(tier)
	if not GameManager.can_afford(int(info.get("cost", 0))):
		AudioManager.play_sfx("error")
		return
	AudioManager.play_sfx("button_click")
	open_box_requested.emit(tier)

func _on_bulk_buy_pressed(tier: int) -> void:
	var info := LootTable.get_box_info(tier)
	if not GameManager.can_afford(int(info.get("bulk_cost", 0))):
		AudioManager.play_sfx("error")
		return
	AudioManager.play_sfx("button_click")
	# For bulk, we'll open them one by one through the main scene
	for i in 10:
		open_box_requested.emit(tier)

func _show_drop_rates(tier: int) -> void:
	if _drop_rates_popup:
		_drop_rates_popup.queue_free()

	var info := LootTable.get_box_info(tier)
	var weights: Dictionary = info.get("weights", {}) as Dictionary

	_drop_rates_popup = PanelContainer.new()
	_drop_rates_popup.set_anchors_preset(Control.PRESET_CENTER)
	_drop_rates_popup.custom_minimum_size = Vector2(300, 250)
	_drop_rates_popup.position -= Vector2(150, 125)

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.09, 0.18, 0.98)
	style.border_color = info.get("color", Color.WHITE) as Color
	style.set_border_width_all(2)
	style.set_corner_radius_all(12)
	style.set_content_margin_all(16)
	_drop_rates_popup.add_theme_stylebox_override("panel", style)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	_drop_rates_popup.add_child(vbox)

	var title := Label.new()
	title.text = "%s Drop Rates" % str(info.get("name", "Box"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", info.get("color_light", Color.WHITE) as Color)
	vbox.add_child(title)

	var sep := HSeparator.new()
	vbox.add_child(sep)

	for rarity in weights:
		var hbox := HBoxContainer.new()
		var rarity_name: String = str(ItemDatabase.RARITY_NAMES.get(rarity, "?"))
		var rarity_color: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.WHITE) as Color
		var percentage: float = weights[rarity]

		var name_lbl := Label.new()
		name_lbl.text = rarity_name
		name_lbl.add_theme_color_override("font_color", rarity_color)
		name_lbl.add_theme_font_size_override("font_size", 16)
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hbox.add_child(name_lbl)

		var pct_lbl := Label.new()
		pct_lbl.text = "%.0f%%" % percentage
		pct_lbl.add_theme_color_override("font_color", rarity_color)
		pct_lbl.add_theme_font_size_override("font_size", 16)
		hbox.add_child(pct_lbl)

		vbox.add_child(hbox)

		# Visual bar
		var bar_bg := ColorRect.new()
		bar_bg.custom_minimum_size = Vector2(0, 6)
		bar_bg.color = Color(0.2, 0.18, 0.3)
		vbox.add_child(bar_bg)

		var bar_fill := ColorRect.new()
		bar_fill.custom_minimum_size = Vector2(percentage / 100.0 * 260, 6)
		bar_fill.color = rarity_color * 0.8
		bar_fill.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		vbox.add_child(bar_fill)

	# Close button
	var close_btn := Button.new()
	close_btn.text = "Close"
	close_btn.custom_minimum_size = Vector2(100, 36)
	_style_button(close_btn, Color(0.4, 0.38, 0.55))
	close_btn.pressed.connect(func():
		AudioManager.play_sfx("button_click")
		_drop_rates_popup.queue_free()
		_drop_rates_popup = null)
	vbox.add_child(close_btn)

	add_child(_drop_rates_popup)

	# Entrance animation
	_drop_rates_popup.scale = Vector2(0.8, 0.8)
	_drop_rates_popup.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(_drop_rates_popup, "scale", Vector2.ONE, 0.2)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(_drop_rates_popup, "modulate:a", 1.0, 0.15)

func _on_coins_changed(new_total: int) -> void:
	if _coins_label:
		_coins_label.text = str(new_total)
	# Update button states
	for tier in _box_buttons:
		var info := LootTable.get_box_info(tier)
		_box_buttons[tier].disabled = not GameManager.can_afford(int(info.get("cost", 0)))

func refresh() -> void:
	_on_coins_changed(GameManager.coins)

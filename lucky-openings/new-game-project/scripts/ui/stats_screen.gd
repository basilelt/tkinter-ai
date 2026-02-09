## StatsScreen — Opening history, totals, and luck statistics
extends Control

signal navigate_to(screen_name: String)

func _ready() -> void:
	_build_ui()
	GameManager.stats_changed.connect(_build_ui)

func _build_ui() -> void:
	# Clear existing children on refresh
	for child in get_children():
		child.queue_free()

	# Background
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.08, 0.07, 0.14)
	add_child(bg)

	var main_vbox := VBoxContainer.new()
	main_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	main_vbox.set_anchor_and_offset(SIDE_LEFT, 0.0, 20)
	main_vbox.set_anchor_and_offset(SIDE_RIGHT, 1.0, -20)
	main_vbox.set_anchor_and_offset(SIDE_TOP, 0.0, 15)
	main_vbox.set_anchor_and_offset(SIDE_BOTTOM, 1.0, -15)
	main_vbox.add_theme_constant_override("separation", 12)
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
	title.text = "📊 STATISTICS"
	title.add_theme_font_size_override("font_size", 24)
	title.add_theme_color_override("font_color", Color(0.81, 0.58, 0.85))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	top_bar.add_child(title)

	# Spacer for alignment
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(80, 0)
	top_bar.add_child(spacer)

	# ── Scrollable content ──
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	main_vbox.add_child(scroll)

	var content := VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 16)
	scroll.add_child(content)

	# ── Economy Stats ──
	_add_section_title(content, "💰 Economy")
	_add_stat_row(content, "Total Coins Earned", str(GameManager.total_coins_earned),
		Color(1.0, 0.84, 0.31))
	_add_stat_row(content, "Total Coins Spent", str(GameManager.total_coins_spent),
		Color(0.9, 0.4, 0.3))
	_add_stat_row(content, "Current Balance", str(GameManager.coins),
		Color(0.3, 0.85, 0.4))
	_add_stat_row(content, "Collection", "%.1f%% (%d/%d)" % [
		GameManager.get_completion_percentage(),
		GameManager.get_total_unique_items(),
		ItemDatabase.get_all_items().size()],
		Color(0.39, 0.71, 0.96))

	# ── Box Opening Stats ──
	_add_section_title(content, "📦 Boxes Opened")

	var total_boxes := GameManager.get_total_boxes()
	_add_stat_row(content, "Total", str(total_boxes), Color(0.8, 0.78, 0.9))

	var tiers := [
		[LootTable.BoxTier.COMMON, "Common", Color(0.62, 0.62, 0.62)],
		[LootTable.BoxTier.RARE, "Rare", Color(0.13, 0.59, 0.95)],
		[LootTable.BoxTier.EPIC, "Epic", Color(0.61, 0.15, 0.69)],
		[LootTable.BoxTier.LEGENDARY, "Legendary", Color(1.0, 0.6, 0.0)],
	]

	for tier_info in tiers:
		var count: int = int(GameManager.total_boxes_opened.get(tier_info[0], 0))
		_add_stat_row(content, tier_info[1], str(count), tier_info[2])

		# Visual bar
		if total_boxes > 0:
			var bar_container := HBoxContainer.new()
			bar_container.add_theme_constant_override("separation", 0)
			content.add_child(bar_container)

			var bar_bg := ColorRect.new()
			bar_bg.custom_minimum_size = Vector2(0, 8)
			bar_bg.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			bar_bg.color = Color(0.15, 0.14, 0.22)
			bar_container.add_child(bar_bg)

			var bar_fill := ColorRect.new()
			var pct := float(count) / float(total_boxes)
			bar_fill.custom_minimum_size = Vector2(pct * 400, 8)
			bar_fill.color = tier_info[2] * 0.8
			bar_fill.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
			# Overlay the fill on top
			bar_fill.position.y = 0
			bar_container.add_child(bar_fill)

	# ── Pity System ──
	_add_section_title(content, "🍀 Luck Status")
	var pity_epic_remaining := LootTable.PITY_EPIC_THRESHOLD - GameManager.pity_counter_epic
	var pity_legend_remaining := LootTable.PITY_LEGENDARY_THRESHOLD - GameManager.pity_counter_legendary
	_add_stat_row(content, "Next Epic Guarantee",
		"%d opens away" % pity_epic_remaining if pity_epic_remaining > 0 else "READY!",
		Color(0.61, 0.15, 0.69))
	_add_stat_row(content, "Next Legendary Guarantee",
		"%d opens away" % pity_legend_remaining if pity_legend_remaining > 0 else "READY!",
		Color(1.0, 0.6, 0.0))

	var streak := GameManager.get_lucky_streak()
	if streak >= 2:
		_add_stat_row(content, "🔥 Lucky Streak", "%dx Rare+" % streak,
			Color(1.0, 0.4, 0.1))

	# ── Best Pull ──
	var best := GameManager.get_best_pull()
	if not best.is_empty():
		var best_item := ItemDatabase.get_item(str(best.get("item_id", "")))
		if not best_item.is_empty():
			_add_section_title(content, "🏆 Best Pull")
			var rarity: int = int(best_item.get("rarity", 0))
			var best_name: String = str(best_item.get("name", "?"))
			var rarity_display: String = str(ItemDatabase.RARITY_NAMES.get(rarity, "Common"))
			var rarity_col: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.WHITE) as Color
			_add_stat_row(content, best_name, rarity_display, rarity_col)

	# ── Recent History ──
	_add_section_title(content, "📜 Recent Opens (Last 20)")
	var history := GameManager.get_last_n_history(20)
	if history.is_empty():
		var empty := Label.new()
		empty.text = "No history yet..."
		empty.add_theme_font_size_override("font_size", 14)
		empty.add_theme_color_override("font_color", Color(0.4, 0.38, 0.5))
		content.add_child(empty)
	else:
		for entry: Dictionary in history:
			var item_data := ItemDatabase.get_item(str(entry.get("item_id", "")))
			if item_data.is_empty():
				continue
			var rarity: int = int(item_data.get("rarity", 0))
			var rarity_color: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(rarity, Color.GRAY) as Color
			var tier_name: String = LootTable.tier_to_string(int(entry.get("box_tier", 0)))

			var hbox := HBoxContainer.new()
			hbox.add_theme_constant_override("separation", 8)
			content.add_child(hbox)

			var dot := Label.new()
			dot.text = "●"
			dot.add_theme_color_override("font_color", rarity_color)
			dot.add_theme_font_size_override("font_size", 12)
			hbox.add_child(dot)

			var name_lbl := Label.new()
			name_lbl.text = str(item_data.get("name", "?"))
			name_lbl.add_theme_color_override("font_color", rarity_color)
			name_lbl.add_theme_font_size_override("font_size", 13)
			name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			hbox.add_child(name_lbl)

			var tier_lbl := Label.new()
			tier_lbl.text = tier_name
			tier_lbl.add_theme_font_size_override("font_size", 11)
			tier_lbl.add_theme_color_override("font_color", Color(0.5, 0.48, 0.6))
			hbox.add_child(tier_lbl)

func _add_section_title(parent: VBoxContainer, text: String) -> void:
	var sep := HSeparator.new()
	parent.add_child(sep)

	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 18)
	label.add_theme_color_override("font_color", Color(0.8, 0.78, 0.9))
	parent.add_child(label)

func _add_stat_row(parent: VBoxContainer, label_text: String,
		value_text: String, value_color: Color) -> void:
	var hbox := HBoxContainer.new()
	parent.add_child(hbox)

	var label := Label.new()
	label.text = label_text
	label.add_theme_font_size_override("font_size", 15)
	label.add_theme_color_override("font_color", Color(0.65, 0.62, 0.75))
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(label)

	var value := Label.new()
	value.text = value_text
	value.add_theme_font_size_override("font_size", 15)
	value.add_theme_color_override("font_color", value_color)
	hbox.add_child(value)

func _style_button(btn: Button, color: Color) -> void:
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

	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color", Color(0.9, 0.88, 0.95))

func refresh() -> void:
	_build_ui()

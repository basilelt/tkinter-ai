## MainMenu — Title screen with navigation buttons and coin display
extends Control

signal navigate_to(screen_name: String)

var _level_label: Label

func _ready() -> void:
	_build_ui()

func _build_ui() -> void:
	# Full-screen background gradient
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.08, 0.07, 0.14)
	add_child(bg)

	# Main layout
	var main_vbox := VBoxContainer.new()
	main_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	main_vbox.set_anchor_and_offset(SIDE_LEFT, 0.0, 30)
	main_vbox.set_anchor_and_offset(SIDE_RIGHT, 1.0, -30)
	main_vbox.set_anchor_and_offset(SIDE_TOP, 0.0, 20)
	main_vbox.set_anchor_and_offset(SIDE_BOTTOM, 1.0, -20)
	main_vbox.add_theme_constant_override("separation", 10)
	add_child(main_vbox)

	# ── Top bar: Box Level ──
	var top_bar := _create_top_bar()
	main_vbox.add_child(top_bar)

	# ── Spacer ──
	var spacer_top := Control.new()
	spacer_top.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer_top.custom_minimum_size = Vector2(0, 60)
	main_vbox.add_child(spacer_top)

	# ── Title ──
	var title_container := VBoxContainer.new()
	title_container.add_theme_constant_override("separation", 4)
	main_vbox.add_child(title_container)

	var title_glow := Label.new()
	title_glow.text = "✦ LUCKY OPENINGS ✦"
	title_glow.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_glow.add_theme_font_size_override("font_size", 40)
	title_glow.add_theme_color_override("font_color", Color(1.0, 0.84, 0.31))
	title_container.add_child(title_glow)

	var subtitle := Label.new()
	subtitle.text = "Test Your Luck!"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 18)
	subtitle.add_theme_color_override("font_color", Color(0.7, 0.65, 0.9))
	title_container.add_child(subtitle)

	# ── Animated title glow ──
	var glow_tween := create_tween().set_loops()
	glow_tween.tween_property(title_glow, "modulate:a", 0.7, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	glow_tween.tween_property(title_glow, "modulate:a", 1.0, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	# ── Spacer ──
	var spacer_mid := Control.new()
	spacer_mid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer_mid.custom_minimum_size = Vector2(0, 40)
	main_vbox.add_child(spacer_mid)

	# ── Menu Buttons ──
	var button_container := VBoxContainer.new()
	button_container.add_theme_constant_override("separation", 16)
	button_container.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	main_vbox.add_child(button_container)

	var btn_open := _create_menu_button("📦  TAP TO OPEN", Color(1.0, 0.65, 0.0))
	btn_open.custom_minimum_size = Vector2(320, 80)
	btn_open.add_theme_font_size_override("font_size", 26)
	btn_open.pressed.connect(func(): _navigate("opening"))
	button_container.add_child(btn_open)

	# Pulsing glow on the open button
	var btn_pulse := create_tween().set_loops()
	btn_pulse.tween_property(btn_open, "modulate", Color(1.0, 0.9, 0.7), 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	btn_pulse.tween_property(btn_open, "modulate", Color.WHITE, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	var btn_inventory := _create_menu_button("📦  Inventory", Color(0.39, 0.71, 0.96))
	btn_inventory.pressed.connect(func(): _navigate("inventory"))
	button_container.add_child(btn_inventory)

	var btn_stats := _create_menu_button("📊  Stats", Color(0.81, 0.58, 0.85))
	btn_stats.pressed.connect(func(): _navigate("stats"))
	button_container.add_child(btn_stats)

	# ── Bottom spacer ──
	var spacer_bottom := Control.new()
	spacer_bottom.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer_bottom.custom_minimum_size = Vector2(0, 30)
	main_vbox.add_child(spacer_bottom)

	# ── Version label ──
	var version := Label.new()
	version.text = "v1.0.0"
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	version.add_theme_font_size_override("font_size", 12)
	version.add_theme_color_override("font_color", Color(0.4, 0.38, 0.5))
	main_vbox.add_child(version)

func _create_top_bar() -> HBoxContainer:
	var bar := HBoxContainer.new()
	bar.add_theme_constant_override("separation", 8)

	var star_icon := Label.new()
	star_icon.text = "⭐"
	star_icon.add_theme_font_size_override("font_size", 24)
	bar.add_child(star_icon)

	_level_label = Label.new()
	var tier_name: String = GameManager.get_tier_name_for_level()
	_level_label.text = "Box Lv.%d — %s" % [GameManager.box_level, tier_name]
	_level_label.add_theme_font_size_override("font_size", 20)
	_level_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.31))
	_level_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.add_child(_level_label)

	return bar

func _create_menu_button(text: String, color: Color) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(320, 60)

	var style := StyleBoxFlat.new()
	style.bg_color = Color(color.r * 0.3, color.g * 0.3, color.b * 0.3, 0.9)
	style.border_color = color
	style.set_border_width_all(2)
	style.set_corner_radius_all(12)
	style.set_content_margin_all(12)
	btn.add_theme_stylebox_override("normal", style)

	var hover_style := style.duplicate() as StyleBoxFlat
	hover_style.bg_color = Color(color.r * 0.4, color.g * 0.4, color.b * 0.4, 0.95)
	btn.add_theme_stylebox_override("hover", hover_style)

	var pressed_style := style.duplicate() as StyleBoxFlat
	pressed_style.bg_color = Color(color.r * 0.5, color.g * 0.5, color.b * 0.5, 1.0)
	btn.add_theme_stylebox_override("pressed", pressed_style)

	btn.add_theme_font_size_override("font_size", 20)
	btn.add_theme_color_override("font_color", Color(0.95, 0.93, 1.0))
	btn.add_theme_color_override("font_hover_color", Color(1.0, 1.0, 1.0))

	return btn

func _navigate(screen: String) -> void:
	AudioManager.play_sfx("button_click")
	navigate_to.emit(screen)

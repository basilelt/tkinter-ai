## Main Scene — Root state machine managing screen navigation and 3D opening viewport
extends Node

# ── Preloaded scripts ─────────────────────────────────────────────
const MainMenuScript = preload("res://scripts/ui/main_menu.gd")
const InventoryScript = preload("res://scripts/ui/inventory_screen.gd")
const StatsScript = preload("res://scripts/ui/stats_screen.gd")
const OpeningResultScript = preload("res://scripts/ui/opening_result.gd")
const LootBox3DScript = preload("res://scripts/loot_box/loot_box_3d.gd")

# ── Layer references ──────────────────────────────────────────────
var _bg_layer: CanvasLayer          # Layer 0 — background
var _screen_layer: CanvasLayer      # Layer 1 — active UI screen
var _overlay_layer: CanvasLayer     # Layer 2 — popups/overlays
var _viewport_container: SubViewportContainer
var _viewport: SubViewport
var _loot_box_3d: Node3D
var _current_screen: Control
var _current_screen_name: String = ""
var _transition_rect: ColorRect     # For fade transitions
var _pending_tier: int = -1
var _level_hud: Control             # Box level + XP bar during opening

func _ready() -> void:
	_build_layer_structure()
	_build_3d_viewport()
	_navigate_to("main_menu")
	AudioManager.play_music("main_theme")

# ── Layer & scene structure ───────────────────────────────────────
func _build_layer_structure() -> void:
	# Background layer
	_bg_layer = CanvasLayer.new()
	_bg_layer.layer = 0
	add_child(_bg_layer)

	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.08, 0.07, 0.14)
	_bg_layer.add_child(bg)

	# Screen layer
	_screen_layer = CanvasLayer.new()
	_screen_layer.layer = 1
	add_child(_screen_layer)

	# Overlay layer
	_overlay_layer = CanvasLayer.new()
	_overlay_layer.layer = 2
	add_child(_overlay_layer)

	# Transition rect (on top of everything)
	var transition_layer := CanvasLayer.new()
	transition_layer.layer = 10
	add_child(transition_layer)

	_transition_rect = ColorRect.new()
	_transition_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_transition_rect.color = Color(0, 0, 0, 0)
	_transition_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	transition_layer.add_child(_transition_rect)

func _build_3d_viewport() -> void:
	# SubViewport for 3D loot box rendering
	_viewport_container = SubViewportContainer.new()
	_viewport_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	_viewport_container.stretch = true
	_viewport_container.visible = false  # Hidden until opening

	_viewport = SubViewport.new()
	_viewport.size = Vector2i(720, 1280)
	_viewport.render_target_update_mode = SubViewport.UPDATE_WHEN_VISIBLE
	_viewport.transparent_bg = true
	_viewport_container.add_child(_viewport)

	# Create the 3D loot box scene
	_loot_box_3d = Node3D.new()
	_loot_box_3d.set_script(LootBox3DScript)
	_viewport.add_child(_loot_box_3d)
	_loot_box_3d.opening_complete.connect(_on_opening_complete)

	_bg_layer.add_child(_viewport_container)

# ── Navigation ────────────────────────────────────────────────────
func _navigate_to(screen_name: String) -> void:
	if screen_name == _current_screen_name:
		return

	# Fade out
	var tween := create_tween()
	_transition_rect.mouse_filter = Control.MOUSE_FILTER_STOP
	tween.tween_property(_transition_rect, "color:a", 1.0, 0.15)
	tween.tween_callback(func():
		_swap_screen(screen_name)
		# Fade in
		var fade_in := create_tween()
		fade_in.tween_property(_transition_rect, "color:a", 0.0, 0.15)
		fade_in.tween_callback(func():
			_transition_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE)
	)

func _swap_screen(screen_name: String) -> void:
	# Remove old screen
	if _current_screen:
		_current_screen.queue_free()
		_current_screen = null

	# Clear overlays
	for child in _overlay_layer.get_children():
		child.queue_free()

	# Hide 3D viewport (unless opening)
	_viewport_container.visible = false

	_current_screen_name = screen_name

	match screen_name:
		"main_menu":
			_current_screen = _create_main_menu()
			AudioManager.play_music("main_theme")
		"inventory":
			_current_screen = _create_inventory()
		"stats":
			_current_screen = _create_stats()
		"opening":
			_start_opening_view()
			return
		_:
			_current_screen = _create_main_menu()

	if _current_screen:
		_current_screen.set_anchors_preset(Control.PRESET_FULL_RECT)
		_screen_layer.add_child(_current_screen)

# ── Screen factories ──────────────────────────────────────────────
func _create_main_menu() -> Control:
	var screen := Control.new()
	screen.set_script(MainMenuScript)
	screen.navigate_to.connect(_navigate_to)
	return screen

func _create_inventory() -> Control:
	var screen := Control.new()
	screen.set_script(InventoryScript)
	screen.navigate_to.connect(_navigate_to)
	return screen

func _create_stats() -> Control:
	var screen := Control.new()
	screen.set_script(StatsScript)
	screen.navigate_to.connect(_navigate_to)
	return screen

# ── Clicker Opening Flow ────────────────────────────────────────────

func _start_opening_view() -> void:
	# Show 3D viewport
	_viewport_container.visible = true

	# Remove UI screen
	if _current_screen:
		_current_screen.queue_free()
		_current_screen = null

	_pending_tier = GameManager.get_current_tier()

	# Add level HUD at top
	_build_level_hud()

	# Add a "Tap to Open" label
	var tap_label := Label.new()
	tap_label.text = "Tap the box to open!"
	tap_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tap_label.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	tap_label.position.y -= 100
	tap_label.position.x -= 150
	tap_label.custom_minimum_size = Vector2(300, 40)
	tap_label.add_theme_font_size_override("font_size", 20)
	tap_label.add_theme_color_override("font_color", Color(0.8, 0.78, 0.9, 0.8))
	tap_label.name = "TapLabel"
	_screen_layer.add_child(tap_label)

	# Pulse the label
	var pulse := create_tween().set_loops()
	pulse.tween_property(tap_label, "modulate:a", 0.4, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pulse.tween_property(tap_label, "modulate:a", 1.0, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	# Play tension music
	AudioManager.play_music("opening_tension")

	# Prepare and show the loot box
	_loot_box_3d.reset()
	_loot_box_3d.prepare_box(_pending_tier)

var _pending_item: Dictionary = {}
var _last_result: Dictionary = {}  # Stores {item, leveled_up, tier}

func _start_clicker_next() -> void:
	# Roll using clicker system (free, grants XP)
	_last_result = GameManager.clicker_open()
	if _last_result.is_empty():
		return

	_pending_item = _last_result.get("item", {}) as Dictionary
	_pending_tier = int(_last_result.get("tier", 0))

	# Clear old overlays
	for child in _overlay_layer.get_children():
		child.queue_free()

	# Clear screen layer
	for child in _screen_layer.get_children():
		child.queue_free()

	# Rebuild level HUD (reflects new XP/level)
	_build_level_hud()

	# Reset and auto-open
	_loot_box_3d.reset()
	_loot_box_3d.open_with_item(_pending_item)

func _on_opening_complete(item: Dictionary) -> void:
	# Wait a beat for the visual to settle
	await get_tree().create_timer(0.5).timeout

	# Remove tap label, keep HUD
	for child in _screen_layer.get_children():
		if child.name != "LevelHUD":
			child.queue_free()

	# Play victory sting for epic+
	var rarity: int = int(item.get("rarity", 0))
	if rarity >= ItemDatabase.Rarity.EPIC:
		AudioManager.play_music("victory_sting", 0.2)

	# If this was the first open (from tap), do the clicker roll now
	if _last_result.is_empty():
		_last_result = GameManager.clicker_open()
		if _last_result.is_empty():
			return
		# Update HUD with XP gained
		_update_level_hud()

	var leveled_up: bool = _last_result.get("leveled_up", false) as bool

	# Show result overlay
	var result_overlay := Control.new()
	result_overlay.set_script(OpeningResultScript)
	result_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay_layer.add_child(result_overlay)

	var is_new: bool = GameManager.is_item_new(str(item.get("id", "")))
	result_overlay.show_result(item, is_new, GameManager.box_level,
		GameManager.box_xp, GameManager.xp_for_level(GameManager.box_level), leveled_up)

	# Connect result buttons
	result_overlay.open_another_pressed.connect(func():
		result_overlay.play_exit_animation()
		await get_tree().create_timer(0.25).timeout
		_last_result = {}
		_start_clicker_next())

	result_overlay.back_to_menu_pressed.connect(func():
		result_overlay.play_exit_animation()
		await get_tree().create_timer(0.3).timeout
		_navigate_to("main_menu"))

	result_overlay.view_inventory_pressed.connect(func():
		result_overlay.play_exit_animation()
		await get_tree().create_timer(0.3).timeout
		_navigate_to("inventory"))

# ── Level HUD (shown during opening) ─────────────────────────────
var _hud_level_label: Label
var _hud_xp_bar: ProgressBar
var _hud_xp_label: Label

func _build_level_hud() -> void:
	# Remove old HUD
	var old := _screen_layer.get_node_or_null("LevelHUD")
	if old:
		old.queue_free()

	var hud := VBoxContainer.new()
	hud.name = "LevelHUD"
	hud.set_anchors_preset(Control.PRESET_TOP_WIDE)
	hud.set_anchor_and_offset(SIDE_LEFT, 0.0, 20)
	hud.set_anchor_and_offset(SIDE_RIGHT, 1.0, -20)
	hud.set_anchor_and_offset(SIDE_TOP, 0.0, 15)
	hud.add_theme_constant_override("separation", 4)
	_screen_layer.add_child(hud)

	# Level label
	_hud_level_label = Label.new()
	_hud_level_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hud_level_label.add_theme_font_size_override("font_size", 20)
	_hud_level_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.31))
	hud.add_child(_hud_level_label)

	# XP progress bar
	var bar_container := CenterContainer.new()
	hud.add_child(bar_container)

	_hud_xp_bar = ProgressBar.new()
	_hud_xp_bar.custom_minimum_size = Vector2(260, 16)
	_hud_xp_bar.show_percentage = false
	var bar_bg := StyleBoxFlat.new()
	bar_bg.bg_color = Color(0.15, 0.14, 0.22, 0.85)
	bar_bg.set_corner_radius_all(6)
	_hud_xp_bar.add_theme_stylebox_override("background", bar_bg)
	var bar_fill := StyleBoxFlat.new()
	bar_fill.bg_color = Color(1.0, 0.84, 0.31, 0.9)
	bar_fill.set_corner_radius_all(6)
	_hud_xp_bar.add_theme_stylebox_override("fill", bar_fill)
	bar_container.add_child(_hud_xp_bar)

	# XP text
	_hud_xp_label = Label.new()
	_hud_xp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hud_xp_label.add_theme_font_size_override("font_size", 13)
	_hud_xp_label.add_theme_color_override("font_color", Color(0.75, 0.72, 0.85))
	hud.add_child(_hud_xp_label)

	_update_level_hud()

func _update_level_hud() -> void:
	var tier_name: String = GameManager.get_tier_name_for_level()
	_hud_level_label.text = "⭐ Box Lv.%d — %s" % [GameManager.box_level, tier_name]
	var needed: int = GameManager.xp_for_level(GameManager.box_level)
	_hud_xp_bar.max_value = needed
	_hud_xp_bar.value = GameManager.box_xp
	_hud_xp_label.text = "%d / %d XP" % [GameManager.box_xp, needed]

## LootBox3D — Controls the 3D loot box opening animation sequence
extends Node3D

signal opening_complete(item: Dictionary)
signal tap_to_open_ready

# ── Node references (assigned in _ready) ──────────────────────────
var _camera: Camera3D
var _box_base: MeshInstance3D
var _box_lid: MeshInstance3D
var _item_reveal: MeshInstance3D
var _starburst: GPUParticles3D
var _crackle: GPUParticles3D
var _shower: GPUParticles3D
var _rocket_trail: GPUParticles3D
var _starburst_2: GPUParticles3D   # second burst for epic+
var _sparkle_ambient: GPUParticles3D
var _fill_light: OmniLight3D

# ── State ─────────────────────────────────────────────────────────
var _current_item: Dictionary = {}
var _current_rarity: int = ItemDatabase.Rarity.COMMON
var _is_opening := false
var _waiting_for_tap := false
var _box_tier: int = LootTable.BoxTier.COMMON

# ── Constants ─────────────────────────────────────────────────────
const BOX_SIZE := Vector3(1.0, 1.0, 1.0)
const LID_HEIGHT := 0.15
const CAMERA_POS := Vector3(0, 2.5, 4.5)
const CAMERA_LOOK := Vector3(0, 0.3, 0)

# ── Lifecycle ─────────────────────────────────────────────────────
func _ready() -> void:
	_build_scene()
	_setup_particles()

func _input(event: InputEvent) -> void:
	if _waiting_for_tap:
		if event is InputEventScreenTouch and event.pressed:
			_waiting_for_tap = false
			_start_open_sequence()
		elif event is InputEventMouseButton and event.pressed:
			_waiting_for_tap = false
			_start_open_sequence()

# ── Public API ────────────────────────────────────────────────────

## Set up and show the box for a given tier, ready for tap
func prepare_box(tier: int) -> void:
	_box_tier = tier
	_is_opening = false
	_waiting_for_tap = false

	# Reset positions
	_box_lid.rotation_degrees = Vector3.ZERO
	_box_lid.position = Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0)
	_item_reveal.visible = false

	# Color the box per tier
	var tier_info := LootTable.get_box_info(tier)
	var box_color: Color = tier_info.get("color", Color.WHITE) as Color
	var box_color_light: Color = tier_info.get("color_light", Color.WHITE) as Color

	_apply_box_material(box_color, box_color_light)

	# Start ambient sparkles
	_sparkle_ambient.emitting = true

	# Start idle float animation
	_start_idle_float()

	# Ready for tap
	_waiting_for_tap = true
	tap_to_open_ready.emit()

## Open the box revealing the given item
func open_with_item(item: Dictionary) -> void:
	_current_item = item
	_current_rarity = int(item.get("rarity", ItemDatabase.Rarity.COMMON))
	prepare_box(_box_tier)
	# Wait briefly then auto-trigger (if calling directly, skipping tap)
	await get_tree().create_timer(0.5).timeout
	_waiting_for_tap = false
	_start_open_sequence()

# ── Scene Construction (procedural) ──────────────────────────────
func _build_scene() -> void:
	# Camera
	_camera = Camera3D.new()
	_camera.position = CAMERA_POS
	_camera.fov = 50.0
	add_child(_camera)
	_camera.look_at(CAMERA_LOOK)
	_camera.current = true

	# Environment
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.08, 0.07, 0.14)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.2, 0.18, 0.3)
	env.ambient_light_energy = 0.6
	env.glow_enabled = true
	env.glow_intensity = 0.8
	env.glow_strength = 1.0
	env.glow_bloom = 0.3
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	env.tonemap_mode = Environment.TONE_MAPPER_ACES

	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)

	# Key light
	var dir_light := DirectionalLight3D.new()
	dir_light.rotation_degrees = Vector3(-45, 30, 0)
	dir_light.light_color = Color(1.0, 0.95, 0.9)
	dir_light.light_energy = 1.2
	dir_light.shadow_enabled = true
	add_child(dir_light)

	# Fill light (changes color per rarity)
	_fill_light = OmniLight3D.new()
	_fill_light.position = Vector3(0, 2, 2)
	_fill_light.light_color = Color(0.5, 0.5, 0.7)
	_fill_light.light_energy = 0.8
	_fill_light.omni_range = 8.0
	add_child(_fill_light)

	# Floor plane (subtle)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(20, 20)
	floor_mesh.mesh = plane
	floor_mesh.position = Vector3(0, -0.8, 0)
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.1, 0.09, 0.15)
	floor_mat.metallic = 0.3
	floor_mat.roughness = 0.8
	floor_mesh.material_override = floor_mat
	add_child(floor_mesh)

	# Box base
	_box_base = MeshInstance3D.new()
	var box_mesh := BoxMesh.new()
	box_mesh.size = BOX_SIZE
	_box_base.mesh = box_mesh
	_box_base.position = Vector3(0, 0, 0)
	add_child(_box_base)

	# Box lid (separate piece for opening animation)
	_box_lid = MeshInstance3D.new()
	var lid_mesh := BoxMesh.new()
	lid_mesh.size = Vector3(BOX_SIZE.x * 1.05, LID_HEIGHT, BOX_SIZE.z * 1.05)
	_box_lid.mesh = lid_mesh
	_box_lid.position = Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0)
	add_child(_box_lid)

	# Item reveal (hidden initially)
	_item_reveal = MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.35
	sphere.height = 0.7
	_item_reveal.mesh = sphere
	_item_reveal.position = Vector3(0, 0, 0)
	_item_reveal.visible = false
	add_child(_item_reveal)

func _setup_particles() -> void:
	# Spark mesh used by firework nodes
	var spark_mesh := SphereMesh.new()
	spark_mesh.radius = 0.025
	spark_mesh.height = 0.05

	var tiny_mesh := SphereMesh.new()
	tiny_mesh.radius = 0.012
	tiny_mesh.height = 0.024

	# Rocket trail
	_rocket_trail = GPUParticles3D.new()
	_rocket_trail.amount = 30
	_rocket_trail.one_shot = true
	_rocket_trail.explosiveness = 0.0
	_rocket_trail.lifetime = 0.6
	_rocket_trail.emitting = false
	_rocket_trail.draw_pass_1 = tiny_mesh
	_rocket_trail.position = Vector3(0, -0.5, 0)
	add_child(_rocket_trail)

	# Starburst (main explosion)
	_starburst = GPUParticles3D.new()
	_starburst.amount = 120
	_starburst.one_shot = true
	_starburst.explosiveness = 1.0
	_starburst.lifetime = 2.0
	_starburst.emitting = false
	_starburst.draw_pass_1 = spark_mesh
	_starburst.position = Vector3(0, 1.0, 0)
	add_child(_starburst)

	# Second starburst (offset, for epic+)
	_starburst_2 = GPUParticles3D.new()
	_starburst_2.amount = 80
	_starburst_2.one_shot = true
	_starburst_2.explosiveness = 1.0
	_starburst_2.lifetime = 2.0
	_starburst_2.emitting = false
	_starburst_2.draw_pass_1 = spark_mesh
	_starburst_2.position = Vector3(0.8, 1.5, -0.3)
	add_child(_starburst_2)

	# Crackle (secondary pops)
	_crackle = GPUParticles3D.new()
	_crackle.amount = 60
	_crackle.one_shot = true
	_crackle.explosiveness = 0.7
	_crackle.lifetime = 1.5
	_crackle.emitting = false
	_crackle.draw_pass_1 = tiny_mesh
	_crackle.position = Vector3(0, 1.2, 0)
	add_child(_crackle)

	# Shower (falling sparks rain)
	_shower = GPUParticles3D.new()
	_shower.amount = 50
	_shower.one_shot = true
	_shower.explosiveness = 0.0
	_shower.lifetime = 3.0
	_shower.emitting = false
	_shower.draw_pass_1 = tiny_mesh
	_shower.position = Vector3(0, 2.5, 0)
	add_child(_shower)

	# Ambient sparkles (pre-opening)
	_sparkle_ambient = GPUParticles3D.new()
	_sparkle_ambient.amount = 20
	_sparkle_ambient.one_shot = false
	_sparkle_ambient.explosiveness = 0.0
	_sparkle_ambient.lifetime = 3.0
	_sparkle_ambient.emitting = false
	var sparkle_mesh := SphereMesh.new()
	sparkle_mesh.radius = 0.015
	sparkle_mesh.height = 0.03
	_sparkle_ambient.draw_pass_1 = sparkle_mesh
	_sparkle_ambient.process_material = ParticleEffects.create_ambient_sparkle_material()
	_sparkle_ambient.position = Vector3(0, 0.5, 0)
	add_child(_sparkle_ambient)

# ── Materials ─────────────────────────────────────────────────────
func _apply_box_material(base_color: Color, light_color: Color) -> void:
	var box_mat := StandardMaterial3D.new()
	box_mat.albedo_color = base_color
	box_mat.metallic = 0.85
	box_mat.roughness = 0.2
	box_mat.emission_enabled = true
	box_mat.emission = light_color * 0.3
	box_mat.emission_energy_multiplier = 0.5
	_box_base.material_override = box_mat

	var lid_mat := StandardMaterial3D.new()
	lid_mat.albedo_color = light_color
	lid_mat.metallic = 0.9
	lid_mat.roughness = 0.15
	lid_mat.emission_enabled = true
	lid_mat.emission = light_color * 0.4
	lid_mat.emission_energy_multiplier = 0.6
	_box_lid.material_override = lid_mat

	# Fill light matches box color
	_fill_light.light_color = light_color
	_fill_light.light_energy = 0.8

func _apply_item_material(item: Dictionary) -> void:
	var mat := StandardMaterial3D.new()
	var color: Color = item.get("icon_color", Color.WHITE) as Color
	mat.albedo_color = color
	mat.metallic = 0.7
	mat.roughness = 0.25
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 1.5
	_item_reveal.material_override = mat

# ── Animations ────────────────────────────────────────────────────

func _start_idle_float() -> void:
	var tween := create_tween().set_loops()
	tween.tween_property(_box_base, "position:y", 0.15, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(_box_base, "position:y", -0.05, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	var lid_tween := create_tween().set_loops()
	lid_tween.tween_property(_box_lid, "position:y",
		BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0 + 0.15, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	lid_tween.tween_property(_box_lid, "position:y",
		BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0 - 0.05, 1.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	# Gentle rotation
	var rot_tween := create_tween().set_loops()
	rot_tween.tween_property(_box_base, "rotation_degrees:y", 360.0, 8.0)\
		.set_trans(Tween.TRANS_LINEAR).from(0.0)

func _start_open_sequence() -> void:
	if _is_opening:
		return
	_is_opening = true

	# Stop ambient effects
	_sparkle_ambient.emitting = false

	# Kill any existing idle tweens by creating new ones that take control
	# Phase 1: Shake
	AudioManager.play_sfx("box_shake")
	await _play_shake_animation()

	# Phase 2: Burst open
	AudioManager.play_sfx("box_open")
	await _play_burst_open()

	# Phase 3: Reveal item
	await _play_item_reveal()

	_is_opening = false

func _play_shake_animation() -> void:
	# Center the box first
	var center_tween := create_tween()
	center_tween.tween_property(_box_base, "position", Vector3.ZERO, 0.2)
	center_tween.parallel().tween_property(_box_lid, "position",
		Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0), 0.2)
	center_tween.parallel().tween_property(_box_base, "rotation_degrees", Vector3.ZERO, 0.2)
	await center_tween.finished

	# Light intensifies during shake
	var light_tween := create_tween()
	light_tween.tween_property(_fill_light, "light_energy", 2.5, 0.6)

	# Emission pulse
	if _box_base.material_override is StandardMaterial3D:
		var emit_tween := create_tween()
		emit_tween.tween_property(_box_base.material_override,
			"emission_energy_multiplier", 2.0, 0.6)

	# Shake sequence
	var shake_tween := create_tween()
	var shake_intensity := 0.04
	var shake_count := 12
	for i in shake_count:
		var t := float(i) / float(shake_count)
		var intensity := shake_intensity * (1.0 + t * 2.0)  # Intensifies
		var offset := Vector3(
			randf_range(-intensity, intensity),
			randf_range(-intensity * 0.3, intensity * 0.3),
			randf_range(-intensity, intensity)
		)
		shake_tween.tween_property(_box_base, "position", offset, 0.05)
		shake_tween.parallel().tween_property(_box_lid, "position",
			Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0) + offset, 0.05)
	shake_tween.tween_property(_box_base, "position", Vector3.ZERO, 0.05)
	shake_tween.parallel().tween_property(_box_lid, "position",
		Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0), 0.05)
	await shake_tween.finished

	# Camera shake
	var cam_tween := create_tween()
	var cam_base := _camera.position
	for i in 6:
		var shk := 0.05 * (1.0 - float(i) / 6.0)
		cam_tween.tween_property(_camera, "position",
			cam_base + Vector3(randf_range(-shk, shk), randf_range(-shk, shk), 0), 0.04)
	cam_tween.tween_property(_camera, "position", cam_base, 0.04)
	await cam_tween.finished

func _play_burst_open() -> void:
	# ── Configure firework materials for this rarity ──
	var rarity_enum: ItemDatabase.Rarity = _current_rarity as ItemDatabase.Rarity
	_starburst.process_material = ParticleEffects.create_starburst_material(rarity_enum)
	_starburst_2.process_material = ParticleEffects.create_starburst_material(rarity_enum)
	_crackle.process_material = ParticleEffects.create_crackle_material(rarity_enum)
	_shower.process_material = ParticleEffects.create_shower_material(rarity_enum)
	var base_color: Color = ItemDatabase.RARITY_COLORS.get(_current_rarity, Color.WHITE) as Color
	_rocket_trail.process_material = ParticleEffects.create_rocket_trail_material(base_color)

	# Scale particle counts by rarity
	match _current_rarity:
		ItemDatabase.Rarity.LEGENDARY:
			_starburst.amount = 200
			_starburst_2.amount = 150
			_crackle.amount = 100
			_shower.amount = 80
			_rocket_trail.amount = 40
		ItemDatabase.Rarity.EPIC:
			_starburst.amount = 150
			_starburst_2.amount = 100
			_crackle.amount = 70
			_shower.amount = 60
			_rocket_trail.amount = 35
		ItemDatabase.Rarity.RARE:
			_starburst.amount = 100
			_starburst_2.amount = 0
			_crackle.amount = 50
			_shower.amount = 40
			_rocket_trail.amount = 25
		_:
			_starburst.amount = 60
			_starburst_2.amount = 0
			_crackle.amount = 30
			_shower.amount = 20
			_rocket_trail.amount = 20

	# ── Phase A: Rocket trail shoots upward ──
	_rocket_trail.restart()
	_rocket_trail.emitting = true

	# Quick upward tween of rocket trail position
	var rocket_tween := create_tween()
	_rocket_trail.position = Vector3(0, -0.3, 0)
	rocket_tween.tween_property(_rocket_trail, "position:y", 1.2, 0.35)\
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)

	# Lid starts flying open at the same time
	var lid_tween := create_tween()
	lid_tween.tween_property(_box_lid, "rotation_degrees:x", -120.0, 0.4)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	lid_tween.parallel().tween_property(_box_lid, "position:y",
		BOX_SIZE.y / 2.0 + LID_HEIGHT + 0.3, 0.4)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

	await rocket_tween.finished

	# ── Phase B: Main starburst explosion ──
	AudioManager.play_sfx("confetti")
	_starburst.restart()
	_starburst.emitting = true
	_rocket_trail.emitting = false

	# Flash light bright
	var flash_color: Color = ItemDatabase.RARITY_COLORS_LIGHT.get(
		_current_rarity, Color.WHITE) as Color
	var flash_tween := create_tween()
	flash_tween.tween_property(_fill_light, "light_color", flash_color, 0.05)
	flash_tween.tween_property(_fill_light, "light_energy", 6.0, 0.05)
	flash_tween.tween_property(_fill_light, "light_energy", 2.0, 0.4)

	# ── Phase C: Crackle pops after short delay ──
	await get_tree().create_timer(0.25).timeout
	_crackle.restart()
	_crackle.emitting = true

	# ── Phase D: Second burst for Epic+ ──
	if _current_rarity >= ItemDatabase.Rarity.EPIC:
		await get_tree().create_timer(0.2).timeout
		_starburst_2.restart()
		_starburst_2.emitting = true
		AudioManager.play_sfx("confetti", 0.0, 0.9)

		# Legendary: triple burst with shower
		if _current_rarity == ItemDatabase.Rarity.LEGENDARY:
			await get_tree().create_timer(0.25).timeout
			_starburst.position = Vector3(-0.6, 0.8, 0.2)
			_starburst.restart()
			_starburst.emitting = true
			AudioManager.play_sfx("confetti", 0.0, 0.8)

	# ── Phase E: Golden shower rain ──
	await get_tree().create_timer(0.2).timeout
	_shower.restart()
	_shower.emitting = true

	# Reset starburst position for next use
	_starburst.position = Vector3(0, 1.0, 0)

	await lid_tween.finished

func _play_item_reveal() -> void:
	# Set up item visual
	_apply_item_material(_current_item)
	_item_reveal.position = Vector3(0, 0, 0)
	_item_reveal.scale = Vector3(0.01, 0.01, 0.01)
	_item_reveal.visible = true

	# Play reveal SFX
	AudioManager.play_reveal_sfx(_current_rarity)

	# Rise + scale up + spin
	var tween := create_tween()
	tween.tween_property(_item_reveal, "position:y", 1.8, 1.0)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(_item_reveal, "scale",
		Vector3(1.0, 1.0, 1.0), 0.8)\
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(_item_reveal, "rotation_degrees:y",
		720.0, 1.5)\
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT).from(0.0)

	# Emission pulse on item
	if _item_reveal.material_override is StandardMaterial3D:
		var pulse := create_tween().set_loops(3)
		pulse.tween_property(_item_reveal.material_override,
			"emission_energy_multiplier", 3.0, 0.3)
		pulse.tween_property(_item_reveal.material_override,
			"emission_energy_multiplier", 1.0, 0.3)

	await tween.finished

	# Gentle floating after reveal
	var float_tween := create_tween().set_loops()
	float_tween.tween_property(_item_reveal, "position:y", 2.0, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	float_tween.tween_property(_item_reveal, "position:y", 1.6, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	var spin_tween := create_tween().set_loops()
	spin_tween.tween_property(_item_reveal, "rotation_degrees:y", 360.0, 4.0)\
		.set_trans(Tween.TRANS_LINEAR).from(0.0)

	# Signal completion
	opening_complete.emit(_current_item)

## Reset everything for next opening
func reset() -> void:
	_is_opening = false
	_waiting_for_tap = false
	_item_reveal.visible = false
	_starburst.emitting = false
	_starburst_2.emitting = false
	_crackle.emitting = false
	_shower.emitting = false
	_rocket_trail.emitting = false
	_sparkle_ambient.emitting = false
	_starburst.position = Vector3(0, 1.0, 0)
	_box_lid.rotation_degrees = Vector3.ZERO
	_box_lid.position = Vector3(0, BOX_SIZE.y / 2.0 + LID_HEIGHT / 2.0, 0)
	_box_base.position = Vector3.ZERO
	_box_base.rotation_degrees = Vector3.ZERO
	_fill_light.light_energy = 0.8

## Particle effect configurations — fireworks-style loot box openings
class_name ParticleEffects
extends RefCounted

## ── Firework starburst (the main explosion) ──
static func create_starburst_material(rarity: ItemDatabase.Rarity) -> ParticleProcessMaterial:
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = 0.1

	# Explode outward in all directions
	mat.direction = Vector3(0, 0, 0)
	mat.spread = 180.0
	mat.initial_velocity_min = 4.0
	mat.initial_velocity_max = 9.0
	mat.gravity = Vector3(0, -3.0, 0)

	# Sparks spin and tumble
	mat.angular_velocity_min = -540.0
	mat.angular_velocity_max = 540.0

	# Scale: start big, shrink
	mat.scale_min = 0.02
	mat.scale_max = 0.06

	# Heavy damping so sparks slow and droop
	mat.damping_min = 2.0
	mat.damping_max = 5.0

	# Color ramp: bright flash → rarity color → fade to dark
	var base_color: Color = ItemDatabase.RARITY_COLORS[rarity] as Color
	var light_color: Color = ItemDatabase.RARITY_COLORS_LIGHT[rarity] as Color
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 1.0, 1.0, 1.0))  # White-hot flash
	grad.add_point(0.1, light_color)
	grad.add_point(0.4, base_color)
	grad.add_point(0.7, Color(base_color.r * 0.6, base_color.g * 0.6, base_color.b * 0.6, 0.7))
	grad.add_point(1.0, Color(base_color.r * 0.2, base_color.g * 0.2, base_color.b * 0.2, 0.0))
	var grad_tex := GradientTexture1D.new()
	grad_tex.gradient = grad
	mat.color_ramp = grad_tex

	# Scale by rarity
	match rarity:
		ItemDatabase.Rarity.LEGENDARY:
			mat.initial_velocity_max = 14.0
			mat.scale_max = 0.10
		ItemDatabase.Rarity.EPIC:
			mat.initial_velocity_max = 11.0
			mat.scale_max = 0.08
		ItemDatabase.Rarity.RARE:
			mat.initial_velocity_max = 9.0
			mat.scale_max = 0.06
		_:
			mat.initial_velocity_max = 6.0

	return mat

## ── Firework crackle / secondary sparks (delayed smaller pops) ──
static func create_crackle_material(rarity: ItemDatabase.Rarity) -> ParticleProcessMaterial:
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = 0.8

	mat.direction = Vector3(0, 0, 0)
	mat.spread = 180.0
	mat.initial_velocity_min = 1.0
	mat.initial_velocity_max = 3.5
	mat.gravity = Vector3(0, -4.0, 0)

	mat.scale_min = 0.008
	mat.scale_max = 0.02
	mat.damping_min = 1.0
	mat.damping_max = 3.0

	var base_color: Color = ItemDatabase.RARITY_COLORS_LIGHT[rarity] as Color
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 1.0, 0.8, 1.0))
	grad.add_point(0.15, base_color)
	grad.add_point(0.5, Color(base_color.r, base_color.g, base_color.b, 0.5))
	grad.add_point(1.0, Color(base_color.r * 0.3, base_color.g * 0.3, base_color.b * 0.3, 0.0))
	var grad_tex := GradientTexture1D.new()
	grad_tex.gradient = grad
	mat.color_ramp = grad_tex
	return mat

## ── Shower / falling sparks (golden rain cascading down) ──
static func create_shower_material(rarity: ItemDatabase.Rarity) -> ParticleProcessMaterial:
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	mat.emission_box_extents = Vector3(3.0, 0.1, 2.0)

	mat.direction = Vector3(0, -1, 0)
	mat.spread = 15.0
	mat.initial_velocity_min = 1.0
	mat.initial_velocity_max = 3.0
	mat.gravity = Vector3(0, -2.5, 0)

	mat.scale_min = 0.005
	mat.scale_max = 0.015
	mat.angular_velocity_min = -180.0
	mat.angular_velocity_max = 180.0
	mat.damping_min = 0.5
	mat.damping_max = 1.5

	var light_color: Color = ItemDatabase.RARITY_COLORS_LIGHT[rarity] as Color
	var grad := Gradient.new()
	grad.set_color(0, Color(light_color.r, light_color.g, light_color.b, 0.0))
	grad.add_point(0.1, light_color)
	grad.add_point(0.6, Color(light_color.r, light_color.g, light_color.b, 0.6))
	grad.add_point(1.0, Color(light_color.r * 0.4, light_color.g * 0.4, light_color.b * 0.4, 0.0))
	var grad_tex := GradientTexture1D.new()
	grad_tex.gradient = grad
	mat.color_ramp = grad_tex
	return mat

## ── Rocket trail (upward streak before explosion) ──
static func create_rocket_trail_material(color: Color) -> ParticleProcessMaterial:
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_POINT
	mat.direction = Vector3(0, -1, 0)
	mat.spread = 8.0
	mat.initial_velocity_min = 0.5
	mat.initial_velocity_max = 1.5
	mat.gravity = Vector3(0, -0.5, 0)
	mat.scale_min = 0.01
	mat.scale_max = 0.025
	mat.damping_min = 2.0
	mat.damping_max = 4.0

	var grad := Gradient.new()
	grad.set_color(0, Color(color.r, color.g, color.b, 1.0))
	grad.add_point(0.4, Color(color.r, color.g, color.b, 0.8))
	grad.add_point(1.0, Color(color.r, color.g, color.b, 0.0))
	var grad_tex := GradientTexture1D.new()
	grad_tex.gradient = grad
	mat.color_ramp = grad_tex
	return mat

## ── Ambient sparkle material (used before opening) ──
static func create_ambient_sparkle_material() -> ParticleProcessMaterial:
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	mat.emission_box_extents = Vector3(1.0, 0.8, 1.0)

	mat.direction = Vector3(0, 1, 0)
	mat.spread = 180.0
	mat.initial_velocity_min = 0.2
	mat.initial_velocity_max = 0.8
	mat.gravity = Vector3(0, 0.3, 0)
	mat.scale_min = 0.01
	mat.scale_max = 0.03
	mat.angular_velocity_min = -90.0
	mat.angular_velocity_max = 90.0

	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 0.95, 0.7, 0.0))
	grad.add_point(0.3, Color(1.0, 0.95, 0.7, 0.8))
	grad.add_point(0.7, Color(1.0, 0.85, 0.5, 0.8))
	grad.add_point(1.0, Color(1.0, 0.8, 0.3, 0.0))
	var grad_tex := GradientTexture1D.new()
	grad_tex.gradient = grad
	mat.color_ramp = grad_tex
	return mat

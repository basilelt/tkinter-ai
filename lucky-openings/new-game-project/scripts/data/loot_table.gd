## Loot Tables — weighted drop-rate tables for each box tier
class_name LootTable
extends RefCounted

# ── Box tier definitions ──────────────────────────────────────────
enum BoxTier { COMMON, RARE, EPIC, LEGENDARY }

const BOX_DATA := {
	BoxTier.COMMON: {
		"name": "Common Box",
		"cost": 100,
		"bulk_cost": 900,          # 10-pack (10% discount)
		"color": Color(0.62, 0.62, 0.62),
		"color_light": Color(0.75, 0.78, 0.8),
		"weights": {
			ItemDatabase.Rarity.COMMON: 70.0,
			ItemDatabase.Rarity.RARE: 22.0,
			ItemDatabase.Rarity.EPIC: 7.0,
			ItemDatabase.Rarity.LEGENDARY: 1.0,
		},
	},
	BoxTier.RARE: {
		"name": "Rare Box",
		"cost": 300,
		"bulk_cost": 2700,
		"color": Color(0.13, 0.59, 0.95),
		"color_light": Color(0.39, 0.71, 0.96),
		"weights": {
			ItemDatabase.Rarity.COMMON: 40.0,
			ItemDatabase.Rarity.RARE: 40.0,
			ItemDatabase.Rarity.EPIC: 16.0,
			ItemDatabase.Rarity.LEGENDARY: 4.0,
		},
	},
	BoxTier.EPIC: {
		"name": "Epic Box",
		"cost": 800,
		"bulk_cost": 7200,
		"color": Color(0.61, 0.15, 0.69),
		"color_light": Color(0.81, 0.58, 0.85),
		"weights": {
			ItemDatabase.Rarity.COMMON: 15.0,
			ItemDatabase.Rarity.RARE: 35.0,
			ItemDatabase.Rarity.EPIC: 35.0,
			ItemDatabase.Rarity.LEGENDARY: 15.0,
		},
	},
	BoxTier.LEGENDARY: {
		"name": "Legendary Box",
		"cost": 2000,
		"bulk_cost": 18000,
		"color": Color(1.0, 0.60, 0.0),
		"color_light": Color(1.0, 0.84, 0.31),
		"weights": {
			ItemDatabase.Rarity.COMMON: 5.0,
			ItemDatabase.Rarity.RARE: 20.0,
			ItemDatabase.Rarity.EPIC: 40.0,
			ItemDatabase.Rarity.LEGENDARY: 35.0,
		},
	},
}

# ── Pity system constants ─────────────────────────────────────────
const PITY_EPIC_THRESHOLD := 30       # Guaranteed Epic after 30 opens without one
const PITY_LEGENDARY_THRESHOLD := 100 # Guaranteed Legendary after 100 opens

# ── Roll logic ────────────────────────────────────────────────────

## Roll a rarity based on weighted drop rates (with optional pity override).
## Returns an ItemDatabase.Rarity value.
static func roll_rarity(box_tier: BoxTier, pity_counter_epic: int = 0,
		pity_counter_legendary: int = 0) -> ItemDatabase.Rarity:
	# Pity overrides
	if pity_counter_legendary >= PITY_LEGENDARY_THRESHOLD:
		return ItemDatabase.Rarity.LEGENDARY
	if pity_counter_epic >= PITY_EPIC_THRESHOLD:
		return ItemDatabase.Rarity.EPIC

	var tier_data: Dictionary = BOX_DATA[box_tier] as Dictionary
	var weights: Dictionary = tier_data.get("weights", {}) as Dictionary
	var total_weight := 0.0
	for w in weights.values():
		total_weight += float(w)

	var roll := randf() * total_weight
	var cumulative := 0.0
	for rarity in weights:
		cumulative += float(weights[rarity])
		if roll <= cumulative:
			return int(rarity) as ItemDatabase.Rarity

	# Fallback (should never reach here)
	return ItemDatabase.Rarity.COMMON

## Pick a random item of the given rarity.
static func pick_item(rarity: ItemDatabase.Rarity) -> Dictionary:
	var pool := ItemDatabase.get_items_by_rarity(rarity)
	if pool.is_empty():
		return {}
	return pool[randi() % pool.size()]

## Full roll: determine rarity then pick a random item from that rarity.
## Returns the item Dictionary.
static func roll_box(box_tier: BoxTier, pity_epic: int = 0,
		pity_legendary: int = 0) -> Dictionary:
	var rarity := roll_rarity(box_tier, pity_epic, pity_legendary)
	return pick_item(rarity)

## Get box info Dictionary for a tier
static func get_box_info(tier: BoxTier) -> Dictionary:
	return BOX_DATA.get(tier, {})

## Convert tier name string to enum
static func tier_from_string(s: String) -> BoxTier:
	match s.to_lower():
		"common": return BoxTier.COMMON
		"rare": return BoxTier.RARE
		"epic": return BoxTier.EPIC
		"legendary": return BoxTier.LEGENDARY
		_: return BoxTier.COMMON

## Convert enum to display string
static func tier_to_string(tier: BoxTier) -> String:
	match tier:
		BoxTier.COMMON: return "Common"
		BoxTier.RARE: return "Rare"
		BoxTier.EPIC: return "Epic"
		BoxTier.LEGENDARY: return "Legendary"
		_: return "Common"

## Item Database — defines all ~80 loot items
class_name ItemDatabase
extends RefCounted

# ── Rarity constants ──────────────────────────────────────────────
enum Rarity { COMMON, RARE, EPIC, LEGENDARY }

const RARITY_NAMES := {
	Rarity.COMMON: "Common",
	Rarity.RARE: "Rare",
	Rarity.EPIC: "Epic",
	Rarity.LEGENDARY: "Legendary",
}

const RARITY_COLORS := {
	Rarity.COMMON: Color(0.62, 0.62, 0.62),       # #9e9e9e
	Rarity.RARE: Color(0.13, 0.59, 0.95),          # #2196f3
	Rarity.EPIC: Color(0.61, 0.15, 0.69),          # #9c27b0
	Rarity.LEGENDARY: Color(1.0, 0.60, 0.0),       # #ff9800
}

const RARITY_COLORS_LIGHT := {
	Rarity.COMMON: Color(0.69, 0.75, 0.77),        # #b0bec5
	Rarity.RARE: Color(0.39, 0.71, 0.96),          # #64b5f6
	Rarity.EPIC: Color(0.81, 0.58, 0.85),          # #ce93d8
	Rarity.LEGENDARY: Color(1.0, 0.84, 0.31),      # #ffd54f
}

# ── Category constants ────────────────────────────────────────────
enum Category { SKIN, BOOST, EMOTE, GEM, COLLECTIBLE }

const CATEGORY_NAMES := {
	Category.SKIN: "Skins",
	Category.BOOST: "Boosts",
	Category.EMOTE: "Emotes",
	Category.GEM: "Gems",
	Category.COLLECTIBLE: "Collectibles",
}

# ── Item structure ────────────────────────────────────────────────
# Each item is a Dictionary with keys:
#   id: String, name: String, description: String,
#   rarity: Rarity, category: Category,
#   icon_color: Color, sell_value: int

static var _items: Array[Dictionary] = []
static var _items_by_id: Dictionary = {}
static var _initialized := false

static func _ensure_init() -> void:
	if _initialized:
		return
	_initialized = true
	_build_database()
	for item: Dictionary in _items:
		_items_by_id[str(item.get("id", ""))] = item

static func get_all_items() -> Array[Dictionary]:
	_ensure_init()
	return _items

static func get_item(id: String) -> Dictionary:
	_ensure_init()
	return _items_by_id.get(id, {})

static func get_items_by_rarity(rarity: Rarity) -> Array[Dictionary]:
	_ensure_init()
	var result: Array[Dictionary] = []
	for item: Dictionary in _items:
		if int(item.get("rarity", -1)) == rarity:
			result.append(item)
	return result

static func get_items_by_category(category: Category) -> Array[Dictionary]:
	_ensure_init()
	var result: Array[Dictionary] = []
	for item: Dictionary in _items:
		if int(item.get("category", -1)) == category:
			result.append(item)
	return result

# ── Database builder ──────────────────────────────────────────────
static func _build_database() -> void:
	# ───────── SKINS (20) ─────────
	_add("skin_default_white", "Arctic Frost", "A pristine white box skin that shimmers like fresh snow.",
		Rarity.COMMON, Category.SKIN, Color(0.9, 0.95, 1.0), 25)
	_add("skin_forest_green", "Forest Guardian", "An earthy green skin with leaf patterns.",
		Rarity.COMMON, Category.SKIN, Color(0.2, 0.65, 0.3), 25)
	_add("skin_sunset_orange", "Sunset Blaze", "Warm orange tones of a desert sunset.",
		Rarity.COMMON, Category.SKIN, Color(0.95, 0.5, 0.15), 25)
	_add("skin_ocean_teal", "Deep Ocean", "Cool teal inspired by the ocean depths.",
		Rarity.COMMON, Category.SKIN, Color(0.0, 0.59, 0.53), 25)
	_add("skin_dusty_pink", "Rose Quartz", "Soft pink like polished quartz crystal.",
		Rarity.COMMON, Category.SKIN, Color(0.86, 0.56, 0.64), 25)
	_add("skin_chrome_silver", "Chrome Plated", "Reflective silver with a mirror finish.",
		Rarity.RARE, Category.SKIN, Color(0.75, 0.75, 0.8), 75)
	_add("skin_sapphire_blue", "Sapphire Edge", "Deep blue sapphire gem-cut pattern.",
		Rarity.RARE, Category.SKIN, Color(0.06, 0.25, 0.7), 75)
	_add("skin_ruby_red", "Ruby Inferno", "Blazing red with internal glow.",
		Rarity.RARE, Category.SKIN, Color(0.8, 0.05, 0.1), 75)
	_add("skin_emerald_cut", "Emerald Facets", "Green emerald with geometric facets.",
		Rarity.RARE, Category.SKIN, Color(0.2, 0.72, 0.35), 75)
	_add("skin_neon_cyber", "Neon Circuit", "Cyberpunk neon with circuit board lines.",
		Rarity.RARE, Category.SKIN, Color(0.0, 1.0, 0.8), 75)
	_add("skin_void_purple", "Void Walker", "Swirling purple void energy.",
		Rarity.EPIC, Category.SKIN, Color(0.4, 0.0, 0.7), 200)
	_add("skin_plasma_blue", "Plasma Core", "Electric blue plasma containment field.",
		Rarity.EPIC, Category.SKIN, Color(0.1, 0.5, 1.0), 200)
	_add("skin_lava_flow", "Molten Core", "Cracked obsidian with flowing lava veins.",
		Rarity.EPIC, Category.SKIN, Color(1.0, 0.3, 0.0), 200)
	_add("skin_galaxy_swirl", "Galactic Spiral", "A miniature galaxy spinning on the box.",
		Rarity.EPIC, Category.SKIN, Color(0.3, 0.1, 0.6), 200)
	_add("skin_frost_fire", "Frost & Fire", "Half frozen, half burning — dual element.",
		Rarity.EPIC, Category.SKIN, Color(0.4, 0.7, 1.0), 200)
	_add("skin_dragon_scale", "Dragon Scale", "Iridescent dragon scales that shift color.",
		Rarity.LEGENDARY, Category.SKIN, Color(0.85, 0.2, 0.1), 500)
	_add("skin_celestial_gold", "Celestial Dawn", "Divine golden light with angelic motifs.",
		Rarity.LEGENDARY, Category.SKIN, Color(1.0, 0.85, 0.3), 500)
	_add("skin_shadow_monarch", "Shadow Monarch", "Dark tendrils of shadow royalty.",
		Rarity.LEGENDARY, Category.SKIN, Color(0.15, 0.0, 0.2), 500)
	_add("skin_prismatic", "Prismatic Flux", "Every color at once — shifts constantly.",
		Rarity.LEGENDARY, Category.SKIN, Color(1.0, 0.5, 0.8), 500)
	_add("skin_ancient_relic", "Ancient Relic", "Weathered gold with glowing runes.",
		Rarity.LEGENDARY, Category.SKIN, Color(0.7, 0.55, 0.2), 500)

	# ───────── BOOSTS (15) ─────────
	_add("boost_coin_1m", "Quick Cash", "2x coin earnings for 1 minute.",
		Rarity.COMMON, Category.BOOST, Color(1.0, 0.85, 0.2), 15)
	_add("boost_coin_5m", "Cash Flow", "2x coin earnings for 5 minutes.",
		Rarity.COMMON, Category.BOOST, Color(1.0, 0.9, 0.3), 25)
	_add("boost_luck_1m", "Lucky Penny", "+5% rare drop chance for 1 minute.",
		Rarity.COMMON, Category.BOOST, Color(0.3, 0.85, 0.4), 20)
	_add("boost_coin_15m", "Golden Hour", "2x coin earnings for 15 minutes.",
		Rarity.RARE, Category.BOOST, Color(1.0, 0.75, 0.0), 75)
	_add("boost_luck_5m", "Four-Leaf Clover", "+10% rare drop chance for 5 minutes.",
		Rarity.RARE, Category.BOOST, Color(0.1, 0.8, 0.3), 75)
	_add("boost_xp_5m", "Knowledge Scroll", "3x XP for 5 minutes.",
		Rarity.RARE, Category.BOOST, Color(0.4, 0.6, 1.0), 75)
	_add("boost_luck_15m", "Rabbit's Foot", "+15% rare drop chance for 15 minutes.",
		Rarity.RARE, Category.BOOST, Color(0.2, 0.9, 0.5), 100)
	_add("boost_mega_coin", "Midas Touch", "5x coin earnings for 5 minutes.",
		Rarity.EPIC, Category.BOOST, Color(1.0, 0.65, 0.0), 200)
	_add("boost_mega_luck", "Horseshoe", "+25% rare drop chance for 10 minutes.",
		Rarity.EPIC, Category.BOOST, Color(0.0, 1.0, 0.5), 200)
	_add("boost_double_drop", "Double Down", "Guaranteed double item from next box.",
		Rarity.EPIC, Category.BOOST, Color(0.9, 0.3, 0.9), 250)
	_add("boost_pity_reset", "Fate's Hand", "Instantly fills pity counter to 90%.",
		Rarity.EPIC, Category.BOOST, Color(0.6, 0.0, 0.8), 300)
	_add("boost_jackpot", "Jackpot Mode", "10x coins + 30% luck for 15 minutes.",
		Rarity.LEGENDARY, Category.BOOST, Color(1.0, 0.9, 0.0), 500)
	_add("boost_guaranteed_epic", "Epic Promise", "Next box guarantees Epic or better.",
		Rarity.LEGENDARY, Category.BOOST, Color(0.7, 0.2, 0.9), 500)
	_add("boost_auto_open", "Auto Opener", "Automatically opens 10 boxes at once.",
		Rarity.LEGENDARY, Category.BOOST, Color(0.2, 0.8, 1.0), 500)
	_add("boost_coin_rain", "Coin Rain", "Rains 1000 bonus coins over 5 minutes.",
		Rarity.LEGENDARY, Category.BOOST, Color(1.0, 0.8, 0.0), 500)

	# ───────── EMOTES / EFFECTS (15) ─────────
	_add("emote_thumbs_up", "Thumbs Up", "A classic positive gesture.",
		Rarity.COMMON, Category.EMOTE, Color(1.0, 0.8, 0.4), 15)
	_add("emote_sparkle", "Sparkle Pop", "A burst of small sparkles.",
		Rarity.COMMON, Category.EMOTE, Color(1.0, 1.0, 0.6), 15)
	_add("emote_confetti_small", "Party Popper", "A small confetti burst.",
		Rarity.COMMON, Category.EMOTE, Color(0.9, 0.3, 0.5), 20)
	_add("emote_fireworks", "Fireworks", "A colorful fireworks display.",
		Rarity.RARE, Category.EMOTE, Color(1.0, 0.4, 0.2), 75)
	_add("emote_rainbow", "Rainbow Arc", "A shimmering rainbow arcs overhead.",
		Rarity.RARE, Category.EMOTE, Color(0.5, 0.8, 1.0), 75)
	_add("emote_lightning", "Thunder Strike", "A dramatic lightning bolt.",
		Rarity.RARE, Category.EMOTE, Color(1.0, 1.0, 0.3), 75)
	_add("emote_shockwave", "Shockwave", "An expanding energy ring.",
		Rarity.RARE, Category.EMOTE, Color(0.3, 0.7, 1.0), 85)
	_add("emote_tornado", "Whirlwind", "A mini tornado swirls around the box.",
		Rarity.EPIC, Category.EMOTE, Color(0.5, 0.9, 0.7), 200)
	_add("emote_meteor", "Meteor Shower", "Meteors rain down around the reveal.",
		Rarity.EPIC, Category.EMOTE, Color(1.0, 0.4, 0.1), 200)
	_add("emote_dragon_roar", "Dragon's Roar", "A spectral dragon circles the item.",
		Rarity.EPIC, Category.EMOTE, Color(0.8, 0.2, 0.0), 250)
	_add("emote_black_hole", "Singularity", "A mini black hole warps space around the reveal.",
		Rarity.EPIC, Category.EMOTE, Color(0.1, 0.0, 0.2), 250)
	_add("emote_supernova", "Supernova", "A blinding stellar explosion effect.",
		Rarity.LEGENDARY, Category.EMOTE, Color(1.0, 0.95, 0.8), 500)
	_add("emote_phoenix", "Phoenix Rise", "A phoenix erupts in flames.",
		Rarity.LEGENDARY, Category.EMOTE, Color(1.0, 0.5, 0.0), 500)
	_add("emote_aurora", "Aurora Borealis", "Northern lights dance across the screen.",
		Rarity.LEGENDARY, Category.EMOTE, Color(0.2, 0.9, 0.6), 500)
	_add("emote_galaxy_burst", "Big Bang", "The universe expands from the box.",
		Rarity.LEGENDARY, Category.EMOTE, Color(0.6, 0.3, 1.0), 500)

	# ───────── GEMS / CURRENCIES (10) ─────────
	_add("gem_copper_pouch", "Copper Pouch", "A small pouch of 50 bonus coins.",
		Rarity.COMMON, Category.GEM, Color(0.72, 0.45, 0.2), 10)
	_add("gem_silver_pouch", "Silver Pouch", "A pouch of 100 bonus coins.",
		Rarity.COMMON, Category.GEM, Color(0.75, 0.75, 0.78), 20)
	_add("gem_gold_pouch", "Gold Pouch", "A hefty pouch of 250 bonus coins.",
		Rarity.RARE, Category.GEM, Color(1.0, 0.84, 0.0), 50)
	_add("gem_ruby_shard", "Ruby Shard", "Trade 3 shards for a guaranteed Rare box.",
		Rarity.RARE, Category.GEM, Color(0.9, 0.1, 0.2), 75)
	_add("gem_sapphire_shard", "Sapphire Shard", "Trade 3 shards for a guaranteed Epic box.",
		Rarity.RARE, Category.GEM, Color(0.1, 0.3, 0.9), 100)
	_add("gem_emerald_shard", "Emerald Shard", "Trade 5 shards for +20% luck permanently.",
		Rarity.EPIC, Category.GEM, Color(0.15, 0.8, 0.3), 200)
	_add("gem_diamond_chunk", "Diamond Chunk", "500 bonus coins + a sparkle trail.",
		Rarity.EPIC, Category.GEM, Color(0.7, 0.9, 1.0), 200)
	_add("gem_platinum_bar", "Platinum Bar", "1000 bonus coins — pure wealth.",
		Rarity.EPIC, Category.GEM, Color(0.85, 0.85, 0.9), 300)
	_add("gem_cosmic_crystal", "Cosmic Crystal", "2000 bonus coins + temporary legendary luck.",
		Rarity.LEGENDARY, Category.GEM, Color(0.6, 0.2, 1.0), 500)
	_add("gem_philosophers_stone", "Philosopher's Stone", "5000 bonus coins — the ultimate treasure.",
		Rarity.LEGENDARY, Category.GEM, Color(0.9, 0.7, 0.0), 500)

	# ───────── COLLECTIBLES (20) ─────────
	_add("col_wooden_trophy", "Wooden Trophy", "Everyone starts somewhere. A humble beginning.",
		Rarity.COMMON, Category.COLLECTIBLE, Color(0.55, 0.35, 0.17), 15)
	_add("col_lucky_coin", "Lucky Coin", "A worn coin with a clover on one side.",
		Rarity.COMMON, Category.COLLECTIBLE, Color(0.8, 0.65, 0.2), 15)
	_add("col_dice_pair", "Lucky Dice", "A pair of dice that always seem warm.",
		Rarity.COMMON, Category.COLLECTIBLE, Color(0.95, 0.95, 0.95), 20)
	_add("col_rabbit_figure", "Rabbit Figurine", "A small jade rabbit for luck.",
		Rarity.COMMON, Category.COLLECTIBLE, Color(0.4, 0.75, 0.5), 20)
	_add("col_compass", "Treasure Compass", "Always points toward the next rare drop.",
		Rarity.COMMON, Category.COLLECTIBLE, Color(0.7, 0.5, 0.3), 25)
	_add("col_bronze_medal", "Bronze Medal", "Third place is still on the podium!",
		Rarity.RARE, Category.COLLECTIBLE, Color(0.8, 0.5, 0.2), 75)
	_add("col_silver_medal", "Silver Medal", "So close to gold, yet so far.",
		Rarity.RARE, Category.COLLECTIBLE, Color(0.8, 0.8, 0.85), 75)
	_add("col_crystal_ball", "Crystal Ball", "Peer into the future of your next pull.",
		Rarity.RARE, Category.COLLECTIBLE, Color(0.6, 0.7, 1.0), 80)
	_add("col_ancient_scroll", "Ancient Scroll", "Contains forgotten wisdom about loot odds.",
		Rarity.RARE, Category.COLLECTIBLE, Color(0.85, 0.75, 0.5), 85)
	_add("col_enchanted_feather", "Enchanted Feather", "It floats slightly upward when released.",
		Rarity.RARE, Category.COLLECTIBLE, Color(0.4, 0.8, 0.9), 90)
	_add("col_gold_medal", "Gold Medal", "The champion's reward. First place!",
		Rarity.EPIC, Category.COLLECTIBLE, Color(1.0, 0.84, 0.0), 200)
	_add("col_mystic_orb", "Mystic Orb", "Swirls with mysterious inner energy.",
		Rarity.EPIC, Category.COLLECTIBLE, Color(0.5, 0.2, 0.8), 200)
	_add("col_time_piece", "Temporal Pocket Watch", "Ticks backward. Time is relative.",
		Rarity.EPIC, Category.COLLECTIBLE, Color(0.75, 0.65, 0.35), 225)
	_add("col_star_map", "Celestial Star Map", "Maps the constellations of fortune.",
		Rarity.EPIC, Category.COLLECTIBLE, Color(0.1, 0.15, 0.4), 225)
	_add("col_phoenix_feather", "Phoenix Feather", "Warm to the touch. Regenerates luck.",
		Rarity.EPIC, Category.COLLECTIBLE, Color(1.0, 0.4, 0.1), 250)
	_add("col_crown_kings", "Crown of Kings", "Worn by the luckiest of all openers.",
		Rarity.LEGENDARY, Category.COLLECTIBLE, Color(1.0, 0.85, 0.0), 500)
	_add("col_infinity_gem", "Infinity Gem", "Contains boundless cosmic energy.",
		Rarity.LEGENDARY, Category.COLLECTIBLE, Color(0.5, 0.0, 1.0), 500)
	_add("col_golden_goose", "Golden Goose", "Lays a golden egg every session.",
		Rarity.LEGENDARY, Category.COLLECTIBLE, Color(1.0, 0.9, 0.3), 500)
	_add("col_world_tree_seed", "World Tree Seed", "Grows into unimaginable fortune.",
		Rarity.LEGENDARY, Category.COLLECTIBLE, Color(0.3, 0.7, 0.2), 500)
	_add("col_pandoras_box", "Pandora's Box", "All the world's luck, sealed within.",
		Rarity.LEGENDARY, Category.COLLECTIBLE, Color(0.4, 0.15, 0.5), 500)

static func _add(id: String, item_name: String, description: String,
		rarity: Rarity, category: Category, icon_color: Color, sell_value: int) -> void:
	_items.append({
		"id": id,
		"name": item_name,
		"description": description,
		"rarity": rarity,
		"category": category,
		"icon_color": icon_color,
		"sell_value": sell_value,
	})

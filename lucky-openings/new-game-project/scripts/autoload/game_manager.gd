## GameManager — Singleton autoload managing player state, economy, persistence
extends Node

# ── Signals ───────────────────────────────────────────────────────
signal coins_changed(new_total: int)
signal inventory_changed()
signal stats_changed()
signal box_level_changed(new_level: int, new_tier: int)
signal box_xp_changed(xp: int, xp_needed: int)

# ── Constants ─────────────────────────────────────────────────────
const SAVE_PATH := "user://save_data.json"
const STARTING_COINS := 500
const PASSIVE_COINS_PER_TICK := 10       # Every tick interval
const PASSIVE_TICK_INTERVAL := 12.0      # Seconds between ticks (10 coins/12s ≈ 50/min)
const PASSIVE_CAP := 1000                # Max passive coins per session
const DAILY_BONUS := 200
const DAILY_BONUS_COOLDOWN := 86400      # 24 hours in seconds

# ── Player State ──────────────────────────────────────────────────
var coins: int = STARTING_COINS:
	set(value):
		coins = value
		coins_changed.emit(coins)

## inventory: Array of { "item_id": String, "quantity": int, "first_obtained": int }
var inventory: Array[Dictionary] = []

## opening_history: Array of { "item_id": String, "rarity": int, "box_tier": int, "timestamp": int }
var opening_history: Array[Dictionary] = []

var total_coins_earned: int = 0
var total_coins_spent: int = 0
var total_boxes_opened: Dictionary = {
	LootTable.BoxTier.COMMON: 0,
	LootTable.BoxTier.RARE: 0,
	LootTable.BoxTier.EPIC: 0,
	LootTable.BoxTier.LEGENDARY: 0,
}

## Pity counters — count opens since last Epic/Legendary
var pity_counter_epic: int = 0
var pity_counter_legendary: int = 0

## Daily login
var last_daily_claim_timestamp: int = 0

## Passive earning
var _passive_earned_this_session: int = 0

## Lucky streak
var _consecutive_rare_plus: int = 0

## Box level progression (clicker system)
var box_level: int = 1
var box_xp: int = 0

## XP needed to reach next level.  Formula: 3 + level * 2
func xp_for_level(level: int) -> int:
	return 3 + level * 2

## Which loot-table tier the current box level maps to
func get_current_tier() -> int:
	if box_level >= 21:
		return LootTable.BoxTier.LEGENDARY
	elif box_level >= 11:
		return LootTable.BoxTier.EPIC
	elif box_level >= 6:
		return LootTable.BoxTier.RARE
	else:
		return LootTable.BoxTier.COMMON

func get_tier_name_for_level() -> String:
	return LootTable.tier_to_string(get_current_tier() as LootTable.BoxTier)

## Grant XP after an open and check for level-up. Returns true if leveled up.
func add_open_xp(rarity: int) -> bool:
	# More XP for rarer pulls
	var xp_gain := 1
	match rarity:
		ItemDatabase.Rarity.RARE: xp_gain = 2
		ItemDatabase.Rarity.EPIC: xp_gain = 4
		ItemDatabase.Rarity.LEGENDARY: xp_gain = 8
	box_xp += xp_gain

	var needed := xp_for_level(box_level)
	var leveled := false
	while box_xp >= needed:
		box_xp -= needed
		box_level += 1
		leveled = true
		needed = xp_for_level(box_level)
		box_level_changed.emit(box_level, get_current_tier())

	box_xp_changed.emit(box_xp, xp_for_level(box_level))
	return leveled

# ── Lifecycle ─────────────────────────────────────────────────────
func _ready() -> void:
	load_game()
	# Set up passive coin timer
	var timer := Timer.new()
	timer.wait_time = PASSIVE_TICK_INTERVAL
	timer.autostart = true
	timer.timeout.connect(_on_passive_tick)
	add_child(timer)

# ── Economy ───────────────────────────────────────────────────────
func add_coins(amount: int) -> void:
	coins += amount
	total_coins_earned += amount

func spend_coins(amount: int) -> bool:
	if coins < amount:
		return false
	coins -= amount
	total_coins_spent += amount
	return true

func can_afford(amount: int) -> bool:
	return coins >= amount

# ── Box operations ────────────────────────────────────────────────

## Buy and open a loot box. Returns the rolled item Dictionary, or {} if can't afford.
func buy_and_open_box(tier: LootTable.BoxTier) -> Dictionary:
	var info := LootTable.get_box_info(tier)
	if not spend_coins(int(info.get("cost", 0))):
		return {}
	return _do_open_box(tier)

## Open a box for free (infinite/clicker mode). Returns rolled item.
func free_open_box(tier: LootTable.BoxTier) -> Dictionary:
	return _do_open_box(tier)

## Clicker open — uses current box level tier, free, grants XP. Returns {item, leveled_up}.
func clicker_open() -> Dictionary:
	var tier: int = get_current_tier()
	var item := _do_open_box(tier as LootTable.BoxTier)
	if item.is_empty():
		return {}
	var rarity: int = int(item.get("rarity", 0))
	var leveled: bool = add_open_xp(rarity)
	return {"item": item, "leveled_up": leveled, "tier": tier}

## Open a box (assumes already paid). Returns rolled item.
func _do_open_box(tier: LootTable.BoxTier) -> Dictionary:
	var item := LootTable.roll_box(tier, pity_counter_epic, pity_counter_legendary)
	if item.is_empty():
		return {}

	# Update pity counters
	var rarity: int = int(item.get("rarity", 0))
	if rarity >= ItemDatabase.Rarity.LEGENDARY:
		pity_counter_legendary = 0
		pity_counter_epic = 0
	elif rarity >= ItemDatabase.Rarity.EPIC:
		pity_counter_epic = 0
		pity_counter_legendary += 1
	else:
		pity_counter_epic += 1
		pity_counter_legendary += 1

	# Lucky streak
	if rarity >= ItemDatabase.Rarity.RARE:
		_consecutive_rare_plus += 1
	else:
		_consecutive_rare_plus = 0

	# Add to inventory
	var item_id: String = str(item.get("id", ""))
	_add_to_inventory(item_id)

	# Record history
	opening_history.append({
		"item_id": item_id,
		"rarity": rarity,
		"box_tier": tier,
		"timestamp": int(Time.get_unix_time_from_system()),
	})

	# Update box counter
	total_boxes_opened[tier] = int(total_boxes_opened.get(tier, 0)) + 1

	# Apply instant gem rewards
	_apply_gem_reward(item)

	stats_changed.emit()
	save_game()
	return item

## Check for lucky streak bonus
func get_lucky_streak() -> int:
	return _consecutive_rare_plus

## Check if item is new (not previously in inventory)
func is_item_new(item_id: String) -> bool:
	for entry: Dictionary in inventory:
		if str(entry.get("item_id", "")) == item_id and int(entry.get("quantity", 0)) > 1:
			return false
	# If quantity is exactly 1 now (just added), it's new
	for entry: Dictionary in inventory:
		if str(entry.get("item_id", "")) == item_id and int(entry.get("quantity", 0)) == 1:
			return true
	return false

# ── Inventory ─────────────────────────────────────────────────────
func _add_to_inventory(item_id: String) -> void:
	for entry: Dictionary in inventory:
		if str(entry.get("item_id", "")) == item_id:
			entry["quantity"] = int(entry.get("quantity", 0)) + 1
			inventory_changed.emit()
			return
	# New item
	inventory.append({
		"item_id": item_id,
		"quantity": 1,
		"first_obtained": int(Time.get_unix_time_from_system()),
	})
	inventory_changed.emit()

func get_inventory_entry(item_id: String) -> Dictionary:
	for entry: Dictionary in inventory:
		if str(entry.get("item_id", "")) == item_id:
			return entry
	return {}

func get_item_count(item_id: String) -> int:
	var entry := get_inventory_entry(item_id)
	return entry.get("quantity", 0) as int

func get_total_unique_items() -> int:
	return inventory.size()

func get_total_items() -> int:
	var total := 0
	for entry: Dictionary in inventory:
		total += int(entry.get("quantity", 0))
	return total

func sell_item(item_id: String) -> int:
	var entry := get_inventory_entry(item_id)
	if entry.is_empty() or int(entry.get("quantity", 0)) <= 0:
		return 0
	var item_data := ItemDatabase.get_item(item_id)
	if item_data.is_empty():
		return 0

	var sell_value: int = int(item_data.get("sell_value", 0))
	# Duplicate bonus: 3rd+ copy gives 50% more
	if int(entry.get("quantity", 0)) >= 3:
		sell_value = int(sell_value * 1.5)

	entry["quantity"] = int(entry.get("quantity", 0)) - 1
	if int(entry.get("quantity", 0)) <= 0:
		inventory.erase(entry)

	add_coins(sell_value)
	inventory_changed.emit()
	save_game()
	return sell_value

# ── Gem instant rewards ───────────────────────────────────────────
func _apply_gem_reward(item: Dictionary) -> void:
	var bonus := 0
	var gem_id: String = str(item.get("id", ""))
	match gem_id:
		"gem_copper_pouch": bonus = 50
		"gem_silver_pouch": bonus = 100
		"gem_gold_pouch": bonus = 250
		"gem_diamond_chunk": bonus = 500
		"gem_platinum_bar": bonus = 1000
		"gem_cosmic_crystal": bonus = 2000
		"gem_philosophers_stone": bonus = 5000
	if bonus > 0:
		add_coins(bonus)

# ── Daily Login ───────────────────────────────────────────────────
func can_claim_daily() -> bool:
	var now := int(Time.get_unix_time_from_system())
	return (now - last_daily_claim_timestamp) >= DAILY_BONUS_COOLDOWN

func claim_daily_bonus() -> int:
	if not can_claim_daily():
		return 0
	last_daily_claim_timestamp = int(Time.get_unix_time_from_system())
	add_coins(DAILY_BONUS)
	save_game()
	return DAILY_BONUS

# ── Passive Coins ─────────────────────────────────────────────────
func _on_passive_tick() -> void:
	if _passive_earned_this_session >= PASSIVE_CAP:
		return
	var amount := mini(PASSIVE_COINS_PER_TICK, PASSIVE_CAP - _passive_earned_this_session)
	_passive_earned_this_session += amount
	add_coins(amount)

# ── Stats helpers ─────────────────────────────────────────────────
func get_total_boxes() -> int:
	var total := 0
	for count in total_boxes_opened.values():
		total += count
	return total

func get_last_n_history(n: int) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var start := maxi(0, opening_history.size() - n)
	for i in range(start, opening_history.size()):
		result.append(opening_history[i])
	result.reverse()
	return result

func get_best_pull() -> Dictionary:
	var best: Dictionary = {}
	var best_rarity := -1
	for entry: Dictionary in opening_history:
		var entry_rarity: int = int(entry.get("rarity", 0))
		if entry_rarity > best_rarity:
			best_rarity = entry_rarity
			best = entry
	return best

func get_completion_percentage() -> float:
	var total_items := ItemDatabase.get_all_items().size()
	if total_items == 0:
		return 0.0
	return float(get_total_unique_items()) / float(total_items) * 100.0

# ── Persistence ───────────────────────────────────────────────────
func save_game() -> void:
	var data := {
		"coins": coins,
		"inventory": _serialize_inventory(),
		"opening_history": _serialize_history(),
		"total_coins_earned": total_coins_earned,
		"total_coins_spent": total_coins_spent,
		"total_boxes_opened": _serialize_box_counts(),
		"pity_counter_epic": pity_counter_epic,
		"pity_counter_legendary": pity_counter_legendary,
		"last_daily_claim_timestamp": last_daily_claim_timestamp,
		"box_level": box_level,
		"box_xp": box_xp,
		"version": 2,
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))

func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return
	var data = JSON.parse_string(file.get_as_text())
	if not data is Dictionary:
		return

	coins = int(data.get("coins", STARTING_COINS))
	total_coins_earned = int(data.get("total_coins_earned", 0))
	total_coins_spent = int(data.get("total_coins_spent", 0))
	pity_counter_epic = int(data.get("pity_counter_epic", 0))
	pity_counter_legendary = int(data.get("pity_counter_legendary", 0))
	last_daily_claim_timestamp = int(data.get("last_daily_claim_timestamp", 0))
	box_level = int(data.get("box_level", 1))
	box_xp = int(data.get("box_xp", 0))

	_deserialize_inventory(data.get("inventory", []))
	_deserialize_history(data.get("opening_history", []))
	_deserialize_box_counts(data.get("total_boxes_opened", {}))

# Serialization helpers
func _serialize_inventory() -> Array:
	var arr := []
	for entry: Dictionary in inventory:
		arr.append({
			"item_id": str(entry.get("item_id", "")),
			"quantity": int(entry.get("quantity", 0)),
			"first_obtained": int(entry.get("first_obtained", 0)),
		})
	return arr

func _deserialize_inventory(arr: Variant) -> void:
	inventory.clear()
	if arr is Array:
		for entry in arr:
			if entry is Dictionary:
				inventory.append({
					"item_id": str(entry.get("item_id", "")),
					"quantity": int(entry.get("quantity", 0)),
					"first_obtained": int(entry.get("first_obtained", 0)),
				})

func _serialize_history() -> Array:
	var arr := []
	for entry: Dictionary in opening_history:
		arr.append({
			"item_id": str(entry.get("item_id", "")),
			"rarity": int(entry.get("rarity", 0)),
			"box_tier": int(entry.get("box_tier", 0)),
			"timestamp": int(entry.get("timestamp", 0)),
		})
	return arr

func _deserialize_history(arr: Variant) -> void:
	opening_history.clear()
	if arr is Array:
		for entry in arr:
			if entry is Dictionary:
				opening_history.append({
					"item_id": str(entry.get("item_id", "")),
					"rarity": int(entry.get("rarity", 0)),
					"box_tier": int(entry.get("box_tier", 0)),
					"timestamp": int(entry.get("timestamp", 0)),
				})

func _serialize_box_counts() -> Dictionary:
	var d := {}
	for tier in total_boxes_opened:
		d[str(tier)] = total_boxes_opened[tier]
	return d

func _deserialize_box_counts(d: Variant) -> void:
	if d is Dictionary:
		for key in d:
			var tier := int(key)
			total_boxes_opened[tier] = int(d[key])

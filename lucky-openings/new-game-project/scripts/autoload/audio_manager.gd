## AudioManager — Singleton autoload for SFX and music playback
extends Node

# ── Audio players ─────────────────────────────────────────────────
var _music_player: AudioStreamPlayer
var _sfx_player: AudioStreamPlayer
var _sfx_player_2: AudioStreamPlayer   # Secondary for overlapping SFX
var _current_music_track: String = ""

# ── Preloaded SFX cache ──────────────────────────────────────────
var _sfx_cache: Dictionary = {}

# ── SFX file mapping ─────────────────────────────────────────────
const SFX_MAP := {
	"button_click": "res://assets/audio/sfx/button_click.ogg",
	"coin_clink": "res://assets/audio/sfx/coin_clink.ogg",
	"box_shake": "res://assets/audio/sfx/box_shake.ogg",
	"box_open": "res://assets/audio/sfx/box_open.ogg",
	"item_reveal_common": "res://assets/audio/sfx/item_reveal_common.ogg",
	"item_reveal_rare": "res://assets/audio/sfx/item_reveal_rare.ogg",
	"item_reveal_epic": "res://assets/audio/sfx/item_reveal_epic.ogg",
	"item_reveal_legendary": "res://assets/audio/sfx/item_reveal_legendary.ogg",
	"confetti": "res://assets/audio/sfx/confetti.ogg",
	"sell_item": "res://assets/audio/sfx/sell_item.ogg",
	"error": "res://assets/audio/sfx/error.ogg",
	"whoosh": "res://assets/audio/sfx/whoosh.ogg",
}

const MUSIC_MAP := {
	"main_theme": "res://assets/audio/music/main_theme.ogg",
	"opening_tension": "res://assets/audio/music/opening_tension.ogg",
	"victory_sting": "res://assets/audio/music/victory_sting.ogg",
}

# ── Lifecycle ─────────────────────────────────────────────────────
func _ready() -> void:
	# Music player
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = &"Music"
	_music_player.volume_db = -5.0
	add_child(_music_player)

	# SFX players
	_sfx_player = AudioStreamPlayer.new()
	_sfx_player.bus = &"SFX"
	_sfx_player.max_polyphony = 4
	add_child(_sfx_player)

	_sfx_player_2 = AudioStreamPlayer.new()
	_sfx_player_2.bus = &"SFX"
	_sfx_player_2.max_polyphony = 4
	add_child(_sfx_player_2)

	# Preload available SFX
	_preload_audio()

# ── Preloading ────────────────────────────────────────────────────
func _preload_audio() -> void:
	for key in SFX_MAP:
		var path: String = SFX_MAP[key]
		if ResourceLoader.exists(path):
			_sfx_cache[key] = load(path)

# ── SFX ───────────────────────────────────────────────────────────

## Play a named SFX. Silently does nothing if the audio file doesn't exist.
func play_sfx(sfx_name: String, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	var stream = _sfx_cache.get(sfx_name)
	if not stream:
		# Try to load on demand
		var path = SFX_MAP.get(sfx_name, "")
		if path != "" and ResourceLoader.exists(path):
			stream = load(path)
			_sfx_cache[sfx_name] = stream
	if not stream:
		return  # Audio file not available — silent fallback

	# Use secondary player if primary is busy
	var player := _sfx_player
	if player.playing:
		player = _sfx_player_2

	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.play()

## Play the item reveal SFX based on rarity
func play_reveal_sfx(rarity: int) -> void:
	match rarity:
		ItemDatabase.Rarity.COMMON:
			play_sfx("item_reveal_common")
		ItemDatabase.Rarity.RARE:
			play_sfx("item_reveal_rare")
		ItemDatabase.Rarity.EPIC:
			play_sfx("item_reveal_epic")
		ItemDatabase.Rarity.LEGENDARY:
			play_sfx("item_reveal_legendary")

# ── Music ─────────────────────────────────────────────────────────

## Play background music with optional cross-fade
func play_music(track_name: String, fade_duration: float = 0.5) -> void:
	if track_name == _current_music_track and _music_player.playing:
		return  # Already playing

	var path = MUSIC_MAP.get(track_name, "")
	if path == "" or not ResourceLoader.exists(path):
		return

	var stream = load(path)
	_current_music_track = track_name

	if _music_player.playing and fade_duration > 0:
		# Cross-fade: fade out then switch
		var tween := create_tween()
		tween.tween_property(_music_player, "volume_db", -40.0, fade_duration)
		tween.tween_callback(func():
			_music_player.stream = stream
			_music_player.volume_db = -5.0
			_music_player.play()
		)
	else:
		_music_player.stream = stream
		_music_player.volume_db = -5.0
		_music_player.play()

## Stop music with optional fade
func stop_music(fade_duration: float = 0.5) -> void:
	if not _music_player.playing:
		return
	_current_music_track = ""
	if fade_duration > 0:
		var tween := create_tween()
		tween.tween_property(_music_player, "volume_db", -40.0, fade_duration)
		tween.tween_callback(func(): _music_player.stop())
	else:
		_music_player.stop()

# ── Volume control ────────────────────────────────────────────────
func set_music_volume(db: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), db)

func set_sfx_volume(db: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), db)

func set_master_volume(db: float) -> void:
	AudioServer.set_bus_volume_db(0, db)

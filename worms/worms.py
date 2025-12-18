"""
Worms-like game in Tkinter
- Procedural terrain generation (smooth hills)
- Player controlled worm with weapons & special powers
- AI enemies
- Destructible terrain
"""

import tkinter as tk
import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Constants
WIDTH = 1200
HEIGHT = 700
TERRAIN_HEIGHT = 500
GRAVITY = 0.3
FRICTION = 0.95
WORM_RADIUS = 12
PROJECTILE_RADIUS = 4

# Colors
SKY_COLOR = "#87CEEB"
TERRAIN_COLOR = "#8B4513"
TERRAIN_GRASS = "#228B22"
PLAYER_COLOR = "#FF6B6B"
ENEMY_COLOR = "#6BCB77"
PROJECTILE_COLOR = "#FFD93D"
EXPLOSION_COLOR = "#FF4500"
WATER_COLOR = "#1E90FF"


def smoothstep(t):
    """Smooth interpolation function"""
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t


def generate_terrain(width: int, height: int, seed: int = None) -> List[int]:
    """Generate smooth procedural terrain using interpolated control points"""
    if seed:
        random.seed(seed)
    else:
        random.seed()
    
    # Create control points for smooth hills
    num_control_points = 12
    control_points = []
    
    base_height = height - 250
    
    for i in range(num_control_points + 1):
        x = int(i * width / num_control_points)
        # Vary height for interesting terrain
        if i == 0 or i == num_control_points:
            y = base_height + random.randint(-30, 30)
        else:
            y = base_height + random.randint(-120, 80)
        control_points.append((x, y))
    
    # Interpolate between control points
    terrain = []
    for x in range(width):
        # Find surrounding control points
        for i in range(len(control_points) - 1):
            if control_points[i][0] <= x <= control_points[i + 1][0]:
                x1, y1 = control_points[i]
                x2, y2 = control_points[i + 1]
                
                # Normalized position between points
                if x2 - x1 > 0:
                    t = (x - x1) / (x2 - x1)
                else:
                    t = 0
                
                # Smooth interpolation
                t = smoothstep(t)
                y = lerp(y1, y2, t)
                
                # Add small undulation
                y += math.sin(x * 0.02) * 15
                y += math.sin(x * 0.05) * 5
                
                terrain.append(int(max(100, min(height - 60, y))))
                break
    
    # Ensure terrain covers full width
    while len(terrain) < width:
        terrain.append(terrain[-1] if terrain else base_height)
    
    return terrain


@dataclass
class Vector2:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vector2(self.x / l, self.y / l)
        return Vector2(0, 0)


class Worm:
    def __init__(self, x: float, y: float, color: str, name: str, is_player: bool = False):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.color = color
        self.name = name
        self.is_player = is_player
        self.health = 100
        self.max_health = 100
        self.alive = True
        self.on_ground = False
        self.aim_angle = -45  # degrees, -90 is up
        self.power = 50
        self.selected_weapon = "bazooka"
        self.weapons = {
            "bazooka": {"damage": 35, "radius": 40, "count": 999},
            "grenade": {"damage": 45, "radius": 50, "count": 5},
            "airstrike": {"damage": 30, "radius": 35, "count": 2},
            "teleport": {"damage": 0, "radius": 0, "count": 2},
        }
        # Special powers
        self.shield_active = False
        self.shield_turns = 0
        self.double_damage = False
        self.double_damage_turns = 0
        self.jetpack_fuel = 0
    
    def update(self, terrain: List[int]):
        if not self.alive:
            return
        
        # Update power states
        if self.shield_turns > 0:
            self.shield_turns -= 1
            if self.shield_turns <= 0:
                self.shield_active = False
        
        if self.double_damage_turns > 0:
            self.double_damage_turns -= 1
            if self.double_damage_turns <= 0:
                self.double_damage = False
        
        # Apply gravity (reduced if jetpack)
        if self.jetpack_fuel > 0:
            self.vel.y += GRAVITY * 0.3
        else:
            self.vel.y += GRAVITY
        
        # Apply velocity
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        
        # Terrain collision
        self.on_ground = False
        if 0 <= int(self.pos.x) < len(terrain):
            ground_y = terrain[int(self.pos.x)]
            if self.pos.y + WORM_RADIUS >= ground_y:
                self.pos.y = ground_y - WORM_RADIUS
                self.vel.y = 0
                self.vel.x *= FRICTION
                self.on_ground = True
        
        # Screen bounds
        self.pos.x = max(WORM_RADIUS, min(WIDTH - WORM_RADIUS, self.pos.x))
        
        # Water death
        if self.pos.y > HEIGHT - 30:
            self.health = 0
            self.alive = False
    
    def jump(self):
        if self.on_ground:
            self.vel.y = -8
            self.vel.x = 3 if self.aim_angle > -90 else -3
    
    def use_jetpack(self):
        if self.jetpack_fuel > 0:
            self.vel.y -= 1.5
            self.jetpack_fuel -= 1
    
    def move(self, direction: int, terrain: List[int]):
        """Move left (-1) or right (1)"""
        if self.on_ground:
            target_x = int(self.pos.x + direction * 5)
            if 0 <= target_x < len(terrain):
                current_y = terrain[int(self.pos.x)]
                target_y = terrain[target_x]
                if current_y - target_y < 20:
                    self.vel.x = direction * 2
    
    def take_damage(self, damage: int):
        if self.shield_active:
            damage = damage // 2  # Shield reduces damage by half
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False


class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float, weapon_type: str, is_airstrike: bool = False):
        self.pos = Vector2(x, y)
        self.vel = Vector2(vx, vy)
        self.weapon_type = weapon_type
        self.active = True
        self.timer = 0
        self.trail = []
        self.is_airstrike = is_airstrike
    
    def update(self, terrain: List[int]) -> Optional[Tuple[float, float]]:
        """Update projectile, return explosion position if hit"""
        if not self.active:
            return None
        
        # Store trail
        self.trail.append((self.pos.x, self.pos.y))
        if len(self.trail) > 20:
            self.trail.pop(0)
        
        # Apply gravity
        if not self.is_airstrike:
            self.vel.y += GRAVITY * 0.8
        
        # Update position
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        
        # Grenade timer
        if self.weapon_type == "grenade":
            self.timer += 1
            if self.timer > 120:
                self.active = False
                return (self.pos.x, self.pos.y)
            
            # Bounce on terrain
            if 0 <= int(self.pos.x) < len(terrain):
                if self.pos.y >= terrain[int(self.pos.x)]:
                    self.pos.y = terrain[int(self.pos.x)] - 2
                    self.vel.y *= -0.5
                    self.vel.x *= 0.7
        else:
            # Explode on impact
            if 0 <= int(self.pos.x) < len(terrain):
                if self.pos.y >= terrain[int(self.pos.x)]:
                    self.active = False
                    return (self.pos.x, self.pos.y)
        
        # Screen bounds
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT:
            self.active = False
            return None
        
        return None


class PowerUp:
    def __init__(self, x: float, y: float, power_type: str):
        self.pos = Vector2(x, y)
        self.power_type = power_type
        self.active = True
        self.bob_offset = random.uniform(0, math.pi * 2)
        
        self.colors = {
            "health": "#FF69B4",
            "shield": "#00BFFF",
            "double_damage": "#FF4500",
            "jetpack": "#9370DB",
        }
        self.symbols = {
            "health": "+",
            "shield": "◆",
            "double_damage": "★",
            "jetpack": "▲",
        }
    
    def update(self, frame: int):
        self.bob_offset = math.sin(frame * 0.1) * 5


class Explosion:
    def __init__(self, x: float, y: float, radius: float, damage: int):
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.frame = 0
        self.max_frames = 20
        self.active = True
    
    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.active = False


class Game:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Worms - Tkinter Edition")
        
        # Main frame
        self.main_frame = tk.Frame(root, bg="#222")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls panel (visible on the left)
        self.create_controls_panel()
        
        # Canvas
        self.canvas = tk.Canvas(self.main_frame, width=WIDTH, height=HEIGHT, bg=SKY_COLOR)
        self.canvas.pack(side=tk.RIGHT)
        
        # Game state
        self.terrain = generate_terrain(WIDTH, HEIGHT)
        self.worms: List[Worm] = []
        self.projectiles: List[Projectile] = []
        self.explosions: List[Explosion] = []
        self.powerups: List[PowerUp] = []
        
        self.current_turn = 0
        self.turn_time = 30 * 60
        self.time_left = self.turn_time
        self.game_state = "playing"
        self.wind = random.uniform(-2, 2)
        self.frame_count = 0
        self.teleport_mode = False
        
        # Create worms and powerups
        self.spawn_worms()
        self.spawn_powerups()
        
        # Info bar
        self.create_info_bar()
        
        # Input handling
        self.keys_pressed = set()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<space>", self.fire)
        self.root.bind("<Return>", self.end_turn)
        self.root.bind("<r>", self.restart_game)
        self.root.bind("1", lambda e: self.select_weapon("bazooka"))
        self.root.bind("2", lambda e: self.select_weapon("grenade"))
        self.root.bind("3", lambda e: self.select_weapon("airstrike"))
        self.root.bind("4", lambda e: self.select_weapon("teleport"))
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Start game loop
        self.update()
    
    def create_controls_panel(self):
        """Create a visible controls panel on the left"""
        self.controls_frame = tk.Frame(self.main_frame, bg="#1a1a2e", width=200)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.controls_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(self.controls_frame, text="CONTROLES", 
                        fg="#00d4ff", bg="#1a1a2e", font=("Arial", 14, "bold"))
        title.pack(pady=15)
        
        # Controls list
        controls = [
            ("-- DEPLACEMENT --", "#ff6b6b"),
            ("<- ->", "Gauche / Droite"),
            ("W", "Sauter"),
            ("", ""),
            ("-- VISEE --", "#ffd93d"),
            ("Haut/Bas", "Ajuster l'angle"),
            ("+ -", "Puissance"),
            ("", ""),
            ("-- ARMES --", "#6bcb77"),
            ("1", "Bazooka"),
            ("2", "Grenade"),
            ("3", "Frappe aerienne"),
            ("4", "Teleportation"),
            ("", ""),
            ("-- ACTIONS --", "#a855f7"),
            ("ESPACE", "Tirer"),
            ("ENTREE", "Fin du tour"),
            ("R", "Recommencer"),
            ("", ""),
            ("-- POUVOIRS --", "#ec4899"),
            ("Coeur", "Vie (+30)"),
            ("Losange", "Bouclier"),
            ("Etoile", "Double degats"),
            ("Triangle", "Jetpack"),
        ]
        
        for item in controls:
            if len(item[0]) > 0 and item[0].startswith("--"):
                # Section header
                lbl = tk.Label(self.controls_frame, text=item[0],
                              fg=item[1], bg="#1a1a2e", font=("Arial", 9, "bold"))
                lbl.pack(pady=(10, 2))
            elif item[0] == "":
                continue
            else:
                frame = tk.Frame(self.controls_frame, bg="#1a1a2e")
                frame.pack(fill=tk.X, padx=10, pady=1)
                
                key_lbl = tk.Label(frame, text=item[0], fg="#ffd700", bg="#2d2d44",
                                  font=("Consolas", 9, "bold"), width=8)
                key_lbl.pack(side=tk.LEFT, padx=(0, 5))
                
                desc_lbl = tk.Label(frame, text=item[1], fg="#ffffff", bg="#1a1a2e",
                                   font=("Arial", 9), anchor="w")
                desc_lbl.pack(side=tk.LEFT, fill=tk.X)
    
    def create_info_bar(self):
        """Create top info bar"""
        self.info_frame = tk.Frame(self.root, bg="#16213e", height=40)
        self.info_frame.pack(fill=tk.X, side=tk.TOP, before=self.main_frame)
        
        self.turn_label = tk.Label(self.info_frame, text="Tour: Player", 
                                  fg="#00d4ff", bg="#16213e", font=("Arial", 12, "bold"))
        self.turn_label.pack(side=tk.LEFT, padx=15)
        
        self.time_label = tk.Label(self.info_frame, text="30s", 
                                  fg="#ffd93d", bg="#16213e", font=("Arial", 12, "bold"))
        self.time_label.pack(side=tk.LEFT, padx=15)
        
        self.weapon_label = tk.Label(self.info_frame, text="Bazooka | 50%", 
                                    fg="#6bcb77", bg="#16213e", font=("Arial", 12, "bold"))
        self.weapon_label.pack(side=tk.LEFT, padx=15)
        
        self.health_label = tk.Label(self.info_frame, text="100 HP", 
                                    fg="#ff6b6b", bg="#16213e", font=("Arial", 12, "bold"))
        self.health_label.pack(side=tk.LEFT, padx=15)
        
        self.wind_label = tk.Label(self.info_frame, text="Vent: -> 0.0", 
                                  fg="#87ceeb", bg="#16213e", font=("Arial", 12, "bold"))
        self.wind_label.pack(side=tk.LEFT, padx=15)
        
        self.status_label = tk.Label(self.info_frame, text="", 
                                    fg="#a855f7", bg="#16213e", font=("Arial", 10))
        self.status_label.pack(side=tk.RIGHT, padx=15)
    
    def spawn_worms(self):
        """Spawn player and enemy worms"""
        self.worms.clear()
        
        spawn_positions = []
        for x in range(100, WIDTH - 100, 200):
            y = self.terrain[x] - WORM_RADIUS - 5
            spawn_positions.append((x, y))
        
        random.shuffle(spawn_positions)
        
        # Player worm
        px, py = spawn_positions[0]
        self.worms.append(Worm(px, py, PLAYER_COLOR, "Joueur", is_player=True))
        
        # Enemy worms
        enemy_names = ["Bot Alpha", "Bot Beta", "Bot Gamma"]
        for i, name in enumerate(enemy_names):
            if i + 1 < len(spawn_positions):
                ex, ey = spawn_positions[i + 1]
                self.worms.append(Worm(ex, ey, ENEMY_COLOR, name, is_player=False))
    
    def spawn_powerups(self):
        """Spawn power-ups on the map"""
        self.powerups.clear()
        power_types = ["health", "shield", "double_damage", "jetpack"]
        
        for _ in range(4):
            x = random.randint(100, WIDTH - 100)
            y = self.terrain[x] - 30
            power_type = random.choice(power_types)
            self.powerups.append(PowerUp(x, y, power_type))
    
    def select_weapon(self, weapon: str):
        worm = self.get_current_worm()
        if worm and worm.is_player:
            if weapon == "teleport":
                self.teleport_mode = True
                self.status_label.config(text="Cliquez pour teleporter!")
            else:
                self.teleport_mode = False
                self.status_label.config(text="")
            worm.selected_weapon = weapon
    
    def on_click(self, event):
        """Handle mouse clicks for teleportation"""
        if self.teleport_mode and self.game_state == "playing":
            worm = self.get_current_worm()
            if worm and worm.is_player and worm.weapons["teleport"]["count"] > 0:
                # Teleport to clicked position
                target_x = event.x
                if 0 <= target_x < len(self.terrain):
                    target_y = self.terrain[target_x] - WORM_RADIUS - 5
                    worm.pos.x = target_x
                    worm.pos.y = target_y
                    worm.vel = Vector2(0, 0)
                    worm.weapons["teleport"]["count"] -= 1
                    self.teleport_mode = False
                    self.status_label.config(text="")
                    self.next_turn()
    
    def get_current_worm(self) -> Optional[Worm]:
        alive_worms = [w for w in self.worms if w.alive]
        if not alive_worms:
            return None
        return alive_worms[self.current_turn % len(alive_worms)]
    
    def on_key_press(self, event):
        self.keys_pressed.add(event.keysym)
    
    def on_key_release(self, event):
        self.keys_pressed.discard(event.keysym)
    
    def fire(self, event=None):
        if self.game_state != "playing" or self.teleport_mode:
            return
        
        worm = self.get_current_worm()
        if not worm or not worm.alive:
            return
        
        weapon = worm.selected_weapon
        
        if weapon == "airstrike" and worm.weapons["airstrike"]["count"] > 0:
            # Launch multiple projectiles from the sky
            worm.weapons["airstrike"]["count"] -= 1
            angle_rad = math.radians(worm.aim_angle)
            target_x = worm.pos.x + math.cos(angle_rad) * 200
            
            for i in range(-2, 3):
                proj = Projectile(
                    target_x + i * 30, -50,
                    0, 8,
                    "airstrike",
                    is_airstrike=True
                )
                self.projectiles.append(proj)
            self.game_state = "projectile"
        elif weapon == "teleport":
            self.teleport_mode = True
            self.status_label.config(text="Cliquez pour teleporter!")
        else:
            # Normal projectile
            angle_rad = math.radians(worm.aim_angle)
            speed = worm.power / 5
            damage_mult = 2 if worm.double_damage else 1
            vx = math.cos(angle_rad) * speed
            vy = math.sin(angle_rad) * speed
            
            proj = Projectile(
                worm.pos.x + math.cos(angle_rad) * 20,
                worm.pos.y + math.sin(angle_rad) * 20,
                vx, vy,
                weapon
            )
            self.projectiles.append(proj)
            self.game_state = "projectile"
    
    def end_turn(self, event=None):
        if self.game_state == "playing":
            self.next_turn()
    
    def next_turn(self):
        self.teleport_mode = False
        self.status_label.config(text="")
        
        alive_worms = [w for w in self.worms if w.alive]
        if len(alive_worms) <= 1:
            self.game_state = "game_over"
            return
        
        self.current_turn = (self.current_turn + 1) % len(alive_worms)
        self.time_left = self.turn_time
        self.wind = random.uniform(-2, 2)
        self.game_state = "playing"
        
        # Occasionally spawn new powerup
        if random.random() < 0.3:
            x = random.randint(100, WIDTH - 100)
            y = self.terrain[x] - 30
            power_type = random.choice(["health", "shield", "double_damage", "jetpack"])
            self.powerups.append(PowerUp(x, y, power_type))
        
        # AI turn
        current = self.get_current_worm()
        if current and not current.is_player:
            self.root.after(500, self.ai_turn)
    
    def ai_turn(self):
        """Simple AI behavior"""
        worm = self.get_current_worm()
        if not worm or worm.is_player or not worm.alive:
            return
        
        player = next((w for w in self.worms if w.is_player and w.alive), None)
        if not player:
            self.next_turn()
            return
        
        dx = player.pos.x - worm.pos.x
        dy = player.pos.y - worm.pos.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        base_angle = math.degrees(math.atan2(dy - distance * 0.3, dx))
        worm.aim_angle = base_angle + random.uniform(-15, 15)
        worm.power = min(80, max(30, distance / 5 + random.uniform(-10, 10)))
        
        self.root.after(1000, lambda: self.ai_fire(worm))
    
    def ai_fire(self, worm: Worm):
        if worm.alive and self.game_state == "playing":
            angle_rad = math.radians(worm.aim_angle)
            speed = worm.power / 5
            vx = math.cos(angle_rad) * speed
            vy = math.sin(angle_rad) * speed
            
            proj = Projectile(
                worm.pos.x + math.cos(angle_rad) * 20,
                worm.pos.y + math.sin(angle_rad) * 20,
                vx, vy,
                random.choice(["bazooka", "grenade"])
            )
            self.projectiles.append(proj)
            self.game_state = "projectile"
    
    def create_explosion(self, x: float, y: float, weapon_type: str):
        """Create explosion and damage terrain/worms"""
        worm = self.get_current_worm()
        damage_mult = 2 if (worm and worm.double_damage) else 1
        
        weapon_data = {
            "bazooka": {"damage": 35, "radius": 40},
            "grenade": {"damage": 45, "radius": 50},
            "airstrike": {"damage": 30, "radius": 35},
        }
        
        data = weapon_data.get(weapon_type, weapon_data["bazooka"])
        radius = data["radius"]
        damage = data["damage"] * damage_mult
        
        self.explosions.append(Explosion(x, y, radius, damage))
        
        # Damage terrain
        for tx in range(int(x - radius), int(x + radius)):
            if 0 <= tx < len(self.terrain):
                dist_x = abs(tx - x)
                crater_depth = math.sqrt(max(0, radius*radius - dist_x*dist_x))
                self.terrain[tx] = min(HEIGHT - 50, int(self.terrain[tx] + crater_depth))
        
        # Damage worms
        for w in self.worms:
            if not w.alive:
                continue
            dist = math.sqrt((w.pos.x - x)**2 + (w.pos.y - y)**2)
            if dist < radius:
                dmg = int(damage * (1 - dist / radius))
                w.take_damage(dmg)
                if dist > 0:
                    knock = (radius - dist) / 5
                    w.vel.x += (w.pos.x - x) / dist * knock
                    w.vel.y += (w.pos.y - y) / dist * knock - 3
    
    def check_powerup_collision(self):
        """Check if current worm collects a powerup"""
        worm = self.get_current_worm()
        if not worm or not worm.alive:
            return
        
        for powerup in self.powerups[:]:
            if not powerup.active:
                continue
            
            dist = math.sqrt((worm.pos.x - powerup.pos.x)**2 + (worm.pos.y - powerup.pos.y)**2)
            if dist < 25:
                # Apply powerup effect
                if powerup.power_type == "health":
                    worm.health = min(worm.max_health, worm.health + 30)
                    self.status_label.config(text="+30 Vie!")
                elif powerup.power_type == "shield":
                    worm.shield_active = True
                    worm.shield_turns = 3
                    self.status_label.config(text="Bouclier active!")
                elif powerup.power_type == "double_damage":
                    worm.double_damage = True
                    worm.double_damage_turns = 2
                    self.status_label.config(text="Double degats!")
                elif powerup.power_type == "jetpack":
                    worm.jetpack_fuel = 100
                    self.status_label.config(text="Jetpack!")
                
                powerup.active = False
                self.powerups.remove(powerup)
    
    def restart_game(self, event=None):
        self.terrain = generate_terrain(WIDTH, HEIGHT)
        self.projectiles.clear()
        self.explosions.clear()
        self.powerups.clear()
        self.spawn_worms()
        self.spawn_powerups()
        self.current_turn = 0
        self.time_left = self.turn_time
        self.game_state = "playing"
        self.wind = random.uniform(-2, 2)
        self.teleport_mode = False
        self.status_label.config(text="")
    
    def update(self):
        """Main game loop"""
        self.frame_count += 1
        
        # Handle input
        worm = self.get_current_worm()
        if worm and worm.is_player and self.game_state == "playing":
            if "Left" in self.keys_pressed:
                worm.move(-1, self.terrain)
            if "Right" in self.keys_pressed:
                worm.move(1, self.terrain)
            if "Up" in self.keys_pressed:
                worm.aim_angle = max(-170, worm.aim_angle - 2)
            if "Down" in self.keys_pressed:
                worm.aim_angle = min(-10, worm.aim_angle + 2)
            if "plus" in self.keys_pressed or "equal" in self.keys_pressed:
                worm.power = min(100, worm.power + 1)
            if "minus" in self.keys_pressed:
                worm.power = max(10, worm.power - 1)
            if "w" in self.keys_pressed:
                if worm.jetpack_fuel > 0:
                    worm.use_jetpack()
                else:
                    worm.jump()
        
        # Update worms
        for w in self.worms:
            w.update(self.terrain)
        
        # Check powerup collisions
        self.check_powerup_collision()
        
        # Update powerups
        for p in self.powerups:
            p.update(self.frame_count)
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj.vel.x += self.wind * 0.01
            result = proj.update(self.terrain)
            if result:
                self.create_explosion(result[0], result[1], proj.weapon_type)
            if not proj.active:
                self.projectiles.remove(proj)
        
        # Update explosions
        for exp in self.explosions[:]:
            exp.update()
            if not exp.active:
                self.explosions.remove(exp)
        
        # Check if projectiles done
        if self.game_state == "projectile" and not self.projectiles and not self.explosions:
            self.root.after(500, self.next_turn)
            self.game_state = "waiting"
        
        # Update timer
        if self.game_state == "playing":
            self.time_left -= 1
            if self.time_left <= 0:
                self.next_turn()
        
        # Check win condition
        alive_players = [w for w in self.worms if w.alive and w.is_player]
        alive_enemies = [w for w in self.worms if w.alive and not w.is_player]
        
        if not alive_players or not alive_enemies:
            self.game_state = "game_over"
        
        # Update UI
        self.update_ui()
        
        # Draw
        self.draw()
        
        # Schedule next frame
        self.root.after(16, self.update)
    
    def update_ui(self):
        worm = self.get_current_worm()
        if worm:
            self.turn_label.config(text=f"Tour: {worm.name}")
            self.health_label.config(text=f"{worm.health} HP")
            
            weapon_names = {"bazooka": "Bazooka", "grenade": "Grenade", "airstrike": "Frappe", "teleport": "Teleport"}
            name = weapon_names.get(worm.selected_weapon, "Bazooka")
            self.weapon_label.config(text=f"{name} | {int(worm.power)}%")
            
            # Show active effects
            effects = []
            if worm.shield_active:
                effects.append("[Bouclier]")
            if worm.double_damage:
                effects.append("[x2 Degats]")
            if worm.jetpack_fuel > 0:
                effects.append(f"[Jetpack:{worm.jetpack_fuel}]")
            if effects and not self.status_label.cget("text"):
                self.status_label.config(text=" ".join(effects))
        
        self.time_label.config(text=f"{self.time_left // 60}s")
        
        wind_arrow = "->" if self.wind > 0 else "<-"
        self.wind_label.config(text=f"Vent: {wind_arrow} {abs(self.wind):.1f}")
    
    def draw(self):
        self.canvas.delete("all")
        
        # Draw sky gradient
        for i in range(0, HEIGHT, 30):
            color = self.blend_color("#87CEEB", "#4169E1", i / HEIGHT)
            self.canvas.create_rectangle(0, i, WIDTH, i + 30, fill=color, outline="")
        
        # Draw clouds
        for i in range(5):
            cx = (i * 250 + self.frame_count * 0.2) % (WIDTH + 100) - 50
            cy = 50 + i * 30
            for j in range(3):
                self.canvas.create_oval(cx + j*25, cy, cx + j*25 + 50, cy + 30, 
                                       fill="white", outline="")
        
        # Draw terrain
        points = [(0, HEIGHT)]
        for x in range(0, len(self.terrain), 2):
            points.append((x, self.terrain[x]))
        points.append((WIDTH, HEIGHT))
        
        self.canvas.create_polygon(points, fill=TERRAIN_COLOR, outline="")
        
        # Draw grass on top
        for x in range(0, WIDTH, 4):
            if x < len(self.terrain):
                y = self.terrain[x]
                self.canvas.create_line(x, y, x, y - 6, fill=TERRAIN_GRASS, width=3)
        
        # Draw water
        water_y = HEIGHT - 30
        for i in range(3):
            wave_offset = math.sin(self.frame_count * 0.05 + i) * 3
            self.canvas.create_rectangle(0, water_y + i*10 + wave_offset, WIDTH, HEIGHT, 
                                        fill=self.blend_color(WATER_COLOR, "#000080", i/3), outline="")
        
        # Draw powerups
        for powerup in self.powerups:
            if not powerup.active:
                continue
            x, y = powerup.pos.x, powerup.pos.y + powerup.bob_offset
            color = powerup.colors[powerup.power_type]
            
            # Glow effect
            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="", outline=color, width=2)
            self.canvas.create_oval(x - 12, y - 12, x + 12, y + 12, fill=color, outline="white", width=2)
            
            # Symbol
            symbols = {"health": "+", "shield": "S", "double_damage": "x2", "jetpack": "J"}
            self.canvas.create_text(x, y, text=symbols[powerup.power_type], 
                                   fill="white", font=("Arial", 10, "bold"))
        
        # Draw explosions
        for exp in self.explosions:
            progress = exp.frame / exp.max_frames
            radius = exp.radius * (0.5 + progress * 0.5)
            colors = ["#FF4500", "#FF6347", "#FF7F50", "#FFD700"]
            for i, color in enumerate(colors):
                r = radius * (1 - i * 0.2)
                if r > 0:
                    self.canvas.create_oval(exp.x - r, exp.y - r, exp.x + r, exp.y + r,
                                           fill=color, outline="")
        
        # Draw projectiles
        for proj in self.projectiles:
            for i, (tx, ty) in enumerate(proj.trail):
                alpha = i / len(proj.trail)
                size = 2 + alpha * 3
                self.canvas.create_oval(tx - size, ty - size, tx + size, ty + size,
                                       fill="#FFA500", outline="")
            
            self.canvas.create_oval(proj.pos.x - PROJECTILE_RADIUS, proj.pos.y - PROJECTILE_RADIUS,
                                   proj.pos.x + PROJECTILE_RADIUS, proj.pos.y + PROJECTILE_RADIUS,
                                   fill=PROJECTILE_COLOR, outline="black")
        
        # Draw worms
        current_worm = self.get_current_worm()
        for worm in self.worms:
            if not worm.alive:
                continue
            
            x, y = worm.pos.x, worm.pos.y
            
            # Shield effect
            if worm.shield_active:
                self.canvas.create_oval(x - WORM_RADIUS - 8, y - WORM_RADIUS - 8,
                                       x + WORM_RADIUS + 8, y + WORM_RADIUS + 8,
                                       outline="#00BFFF", width=3)
            
            # Double damage effect
            if worm.double_damage:
                self.canvas.create_oval(x - WORM_RADIUS - 5, y - WORM_RADIUS - 5,
                                       x + WORM_RADIUS + 5, y + WORM_RADIUS + 5,
                                       outline="#FF4500", width=2)
            
            # Body
            self.canvas.create_oval(x - WORM_RADIUS, y - WORM_RADIUS,
                                   x + WORM_RADIUS, y + WORM_RADIUS,
                                   fill=worm.color, outline="black", width=2)
            
            # Eyes
            self.canvas.create_oval(x - 6, y - 6, x - 2, y - 2, fill="white", outline="black")
            self.canvas.create_oval(x + 2, y - 6, x + 6, y - 2, fill="white", outline="black")
            self.canvas.create_oval(x - 5, y - 5, x - 3, y - 3, fill="black")
            self.canvas.create_oval(x + 3, y - 5, x + 5, y - 3, fill="black")
            
            # Health bar
            bar_width = 30
            bar_height = 4
            health_pct = worm.health / worm.max_health
            self.canvas.create_rectangle(x - bar_width/2, y - WORM_RADIUS - 15,
                                        x + bar_width/2, y - WORM_RADIUS - 15 + bar_height,
                                        fill="#333", outline="black")
            self.canvas.create_rectangle(x - bar_width/2, y - WORM_RADIUS - 15,
                                        x - bar_width/2 + bar_width * health_pct, 
                                        y - WORM_RADIUS - 15 + bar_height,
                                        fill="#00ff00" if health_pct > 0.5 else "#ff0000", outline="")
            
            # Name
            self.canvas.create_text(x, y - WORM_RADIUS - 22, text=worm.name,
                                   fill="white", font=("Arial", 8, "bold"))
            
            # Aim indicator for current worm
            if worm == current_worm:
                angle_rad = math.radians(worm.aim_angle)
                aim_length = 30 + worm.power / 3
                aim_x = x + math.cos(angle_rad) * aim_length
                aim_y = y + math.sin(angle_rad) * aim_length
                
                self.canvas.create_line(x, y, aim_x, aim_y, fill="red", width=2, arrow=tk.LAST)
                
                # Selection indicator
                self.canvas.create_oval(x - WORM_RADIUS - 5, y - WORM_RADIUS - 5,
                                       x + WORM_RADIUS + 5, y + WORM_RADIUS + 5,
                                       outline="yellow", width=2)
                
                # Jetpack indicator
                if worm.jetpack_fuel > 0:
                    self.canvas.create_text(x, y + WORM_RADIUS + 15, 
                                           text=f"Jetpack: {worm.jetpack_fuel}", fill="purple",
                                           font=("Arial", 8, "bold"))
        
        # Teleport mode indicator
        if self.teleport_mode:
            self.canvas.create_text(WIDTH // 2, 100, text="CLIQUEZ POUR TELEPORTER",
                                   fill="#a855f7", font=("Arial", 16, "bold"))
        
        # Draw game over screen
        if self.game_state == "game_over":
            self.canvas.create_rectangle(WIDTH/2 - 180, HEIGHT/2 - 70,
                                        WIDTH/2 + 180, HEIGHT/2 + 70,
                                        fill="#1a1a2e", outline="#00d4ff", width=4)
            
            alive_players = [w for w in self.worms if w.alive and w.is_player]
            if alive_players:
                text = "VICTOIRE!"
                color = "#00ff00"
            else:
                text = "DEFAITE!"
                color = "#ff0000"
            
            self.canvas.create_text(WIDTH/2, HEIGHT/2 - 20, text=text,
                                   fill=color, font=("Arial", 28, "bold"))
            self.canvas.create_text(WIDTH/2, HEIGHT/2 + 30, text="Appuyez sur R pour recommencer",
                                   fill="white", font=("Arial", 14))
    
    def blend_color(self, color1: str, color2: str, t: float) -> str:
        """Blend two hex colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"


def main():
    root = tk.Tk()
    root.resizable(False, False)
    game = Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()

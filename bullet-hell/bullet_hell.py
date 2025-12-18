"""
Bullet Hell Game avec Tkinter et Object Pooling
"""
import tkinter as tk
import math
import random
from dataclasses import dataclass
from typing import List, Optional

# Configuration du jeu
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_SIZE = 15
PLAYER_SPEED = 5
BULLET_RADIUS = 4
ENEMY_BULLET_RADIUS = 6
POOL_SIZE = 500

@dataclass
class Vector2:
    x: float
    y: float

# ==================== OBJECT POOLING ====================

class Bullet:
    """Classe représentant un projectile (joueur ou ennemi)"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.radius = BULLET_RADIUS
        self.active = False
        self.canvas_id = None
        self.color = "yellow"
        self.is_player_bullet = True
    
    def reset(self, x: float, y: float, vx: float, vy: float, 
              radius: float, color: str, is_player: bool):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.is_player_bullet = is_player
        self.active = True
    
    def update(self):
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        
        # Désactiver si hors écran
        if (self.x < -50 or self.x > WINDOW_WIDTH + 50 or 
            self.y < -50 or self.y > WINDOW_HEIGHT + 50):
            self.active = False


class BulletPool:
    """Pool d'objets pour les projectiles - évite les allocations mémoire"""
    def __init__(self, size: int):
        self.pool: List[Bullet] = [Bullet() for _ in range(size)]
        self.active_bullets: List[Bullet] = []
    
    def get(self, x: float, y: float, vx: float, vy: float,
            radius: float = BULLET_RADIUS, color: str = "yellow", 
            is_player: bool = True) -> Optional[Bullet]:
        """Récupère un projectile inactif du pool"""
        for bullet in self.pool:
            if not bullet.active:
                bullet.reset(x, y, vx, vy, radius, color, is_player)
                if bullet not in self.active_bullets:
                    self.active_bullets.append(bullet)
                return bullet
        return None  # Pool épuisé
    
    def update_all(self):
        """Met à jour tous les projectiles actifs"""
        for bullet in self.active_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.active_bullets.remove(bullet)
    
    def get_active(self) -> List[Bullet]:
        return [b for b in self.active_bullets if b.active]
    
    def clear_all(self):
        """Désactive tous les projectiles"""
        for bullet in self.pool:
            bullet.active = False
        self.active_bullets.clear()


class Enemy:
    """Classe représentant un ennemi"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.health = 1
        self.active = False
        self.canvas_id = None
        self.shoot_timer = 0
        self.shoot_delay = 60
        self.pattern = 0
        self.angle = 0
        self.radius = 20
    
    def reset(self, x: float, y: float, health: int = 3, pattern: int = 0):
        self.x = x
        self.y = y
        self.health = health
        self.active = True
        self.shoot_timer = random.randint(0, 30)
        self.pattern = pattern
        self.angle = 0
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(0.5, 1.5)
    
    def update(self):
        if not self.active:
            return
        
        self.x += self.vx
        self.y += self.vy
        self.angle += 0.05
        
        # Rebond sur les côtés
        if self.x < 30 or self.x > WINDOW_WIDTH - 30:
            self.vx *= -1
        
        # Désactiver si trop bas
        if self.y > WINDOW_HEIGHT + 50:
            self.active = False


class EnemyPool:
    """Pool d'objets pour les ennemis"""
    def __init__(self, size: int):
        self.pool: List[Enemy] = [Enemy() for _ in range(size)]
        self.active_enemies: List[Enemy] = []
    
    def get(self, x: float, y: float, health: int = 3, pattern: int = 0) -> Optional[Enemy]:
        for enemy in self.pool:
            if not enemy.active:
                enemy.reset(x, y, health, pattern)
                if enemy not in self.active_enemies:
                    self.active_enemies.append(enemy)
                return enemy
        return None
    
    def update_all(self):
        for enemy in self.active_enemies[:]:
            enemy.update()
            if not enemy.active:
                self.active_enemies.remove(enemy)
    
    def get_active(self) -> List[Enemy]:
        return [e for e in self.active_enemies if e.active]
    
    def clear_all(self):
        for enemy in self.pool:
            enemy.active = False
        self.active_enemies.clear()


# ==================== PATTERNS DE TIR ====================

class BulletPatterns:
    """Générateur de patterns de tir pour les ennemis"""
    
    @staticmethod
    def circular(pool: BulletPool, x: float, y: float, num_bullets: int = 12, speed: float = 3):
        """Tir circulaire"""
        for i in range(num_bullets):
            angle = (2 * math.pi * i) / num_bullets
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            pool.get(x, y, vx, vy, ENEMY_BULLET_RADIUS, "#ff4444", False)
    
    @staticmethod
    def spiral(pool: BulletPool, x: float, y: float, base_angle: float, speed: float = 4):
        """Tir en spirale"""
        for i in range(3):
            angle = base_angle + (2 * math.pi * i) / 3
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            pool.get(x, y, vx, vy, ENEMY_BULLET_RADIUS, "#ff66ff", False)
    
    @staticmethod
    def aimed(pool: BulletPool, x: float, y: float, target_x: float, target_y: float, 
              spread: int = 3, speed: float = 5):
        """Tir visé vers le joueur"""
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            return
        
        base_angle = math.atan2(dy, dx)
        for i in range(spread):
            angle = base_angle + (i - spread//2) * 0.15
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            pool.get(x, y, vx, vy, ENEMY_BULLET_RADIUS, "#44ff44", False)
    
    @staticmethod
    def wave(pool: BulletPool, x: float, y: float, time: float, speed: float = 3):
        """Tir en vague"""
        for i in range(5):
            offset = math.sin(time + i * 0.5) * 2
            pool.get(x + i * 15 - 30, y, offset, speed, ENEMY_BULLET_RADIUS, "#44ffff", False)


# ==================== JEU PRINCIPAL ====================

class BulletHellGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 Bullet Hell - Object Pooling Demo 🔥")
        self.root.resizable(False, False)
        
        # Canvas principal
        self.canvas = tk.Canvas(
            self.root, 
            width=WINDOW_WIDTH, 
            height=WINDOW_HEIGHT, 
            bg="#1a1a2e",
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Pools d'objets
        self.bullet_pool = BulletPool(POOL_SIZE)
        self.enemy_pool = EnemyPool(50)
        
        # Joueur
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT - 80
        self.player_id = None
        self.player_hitbox_id = None
        
        # État du jeu
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.frame_count = 0
        self.invincible = 0
        
        # Contrôles
        self.keys = set()
        self.shoot_cooldown = 0
        
        # UI
        self.score_text = None
        self.lives_text = None
        self.pool_text = None
        
        # Bindings
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", lambda e: self.restart() if self.game_over else None)
        
        self.setup_ui()
        self.spawn_initial_enemies()
        self.game_loop()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.score_text = self.canvas.create_text(
            10, 10, anchor="nw", fill="white", 
            font=("Arial", 16, "bold"), text="Score: 0"
        )
        self.lives_text = self.canvas.create_text(
            10, 35, anchor="nw", fill="#ff6666", 
            font=("Arial", 16, "bold"), text="Vies: ❤❤❤"
        )
        self.pool_text = self.canvas.create_text(
            WINDOW_WIDTH - 10, 10, anchor="ne", fill="#888888", 
            font=("Arial", 12), text="Bullets: 0"
        )
        
        # Instructions
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20, 
            fill="#666666", font=("Arial", 10),
            text="ZQSD/Flèches: Déplacer | SHIFT: Tir concentré | ESPACE: Restart"
        )
    
    def spawn_initial_enemies(self):
        """Fait apparaître les premiers ennemis"""
        for i in range(5):
            x = 100 + i * 150
            self.enemy_pool.get(x, -50 - i * 30, health=5, pattern=i % 4)
    
    def key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        # Normaliser les touches shift
        if key.startswith("shift"):
            self.keys.add("shift")
    
    def key_release(self, event):
        key = event.keysym.lower()
        self.keys.discard(key)
        # Normaliser les touches shift
        if key.startswith("shift"):
            self.keys.discard("shift")
    
    def restart(self):
        """Redémarre le jeu"""
        self.bullet_pool.clear_all()
        self.enemy_pool.clear_all()
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT - 80
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.invincible = 60
        self.frame_count = 0
        self.spawn_initial_enemies()
    
    def update_player(self):
        """Met à jour la position et les actions du joueur"""
        if self.game_over:
            return
        
        # Vitesse (shift = plus lent pour esquiver)
        speed = PLAYER_SPEED * 0.4 if "shift" in self.keys else PLAYER_SPEED
        
        # Déplacement
        if "z" in self.keys or "up" in self.keys:
            self.player_y = max(PLAYER_SIZE, self.player_y - speed)
        if "s" in self.keys or "down" in self.keys:
            self.player_y = min(WINDOW_HEIGHT - PLAYER_SIZE, self.player_y + speed)
        if "q" in self.keys or "left" in self.keys:
            self.player_x = max(PLAYER_SIZE, self.player_x - speed)
        if "d" in self.keys or "right" in self.keys:
            self.player_x = min(WINDOW_WIDTH - PLAYER_SIZE, self.player_x + speed)
        
        # Tir automatique
        if self.shoot_cooldown <= 0:
            self.player_shoot()
            self.shoot_cooldown = 5
        else:
            self.shoot_cooldown -= 1
        
        # Invincibilité
        if self.invincible > 0:
            self.invincible -= 1
    
    def player_shoot(self):
        """Le joueur tire"""
        # Tir principal
        self.bullet_pool.get(self.player_x, self.player_y - 20, 0, -12, 5, "#00ffff", True)
        
        # Tirs latéraux
        self.bullet_pool.get(self.player_x - 10, self.player_y - 15, -1, -11, 4, "#00cccc", True)
        self.bullet_pool.get(self.player_x + 10, self.player_y - 15, 1, -11, 4, "#00cccc", True)
    
    def update_enemies(self):
        """Met à jour les ennemis et leurs tirs"""
        self.enemy_pool.update_all()
        
        for enemy in self.enemy_pool.get_active():
            enemy.shoot_timer -= 1
            
            if enemy.shoot_timer <= 0:
                # Différents patterns selon l'ennemi
                if enemy.pattern == 0:
                    BulletPatterns.circular(self.bullet_pool, enemy.x, enemy.y, 8, 2.5)
                    enemy.shoot_delay = 90
                elif enemy.pattern == 1:
                    BulletPatterns.spiral(self.bullet_pool, enemy.x, enemy.y, enemy.angle, 3)
                    enemy.shoot_delay = 15
                elif enemy.pattern == 2:
                    BulletPatterns.aimed(self.bullet_pool, enemy.x, enemy.y, 
                                        self.player_x, self.player_y, 5, 4)
                    enemy.shoot_delay = 45
                else:
                    BulletPatterns.wave(self.bullet_pool, enemy.x, enemy.y, 
                                       self.frame_count * 0.1, 3)
                    enemy.shoot_delay = 30
                
                enemy.shoot_timer = enemy.shoot_delay
        
        # Spawn de nouveaux ennemis
        if self.frame_count % 180 == 0 and len(self.enemy_pool.get_active()) < 8:
            x = random.randint(100, WINDOW_WIDTH - 100)
            pattern = random.randint(0, 3)
            health = 3 + self.score // 500
            self.enemy_pool.get(x, -30, health, pattern)
    
    def check_collisions(self):
        """Vérifie les collisions"""
        if self.game_over:
            return
        
        # Bullets du joueur vs ennemis
        for bullet in self.bullet_pool.get_active():
            if bullet.is_player_bullet:
                for enemy in self.enemy_pool.get_active():
                    dx = bullet.x - enemy.x
                    dy = bullet.y - enemy.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < enemy.radius + bullet.radius:
                        bullet.active = False
                        enemy.health -= 1
                        self.score += 10
                        
                        if enemy.health <= 0:
                            enemy.active = False
                            self.score += 100
                        break
            
            # Bullets ennemis vs joueur
            elif self.invincible <= 0:
                dx = bullet.x - self.player_x
                dy = bullet.y - self.player_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Hitbox très petite (style bullet hell)
                if dist < 5:
                    bullet.active = False
                    self.lives -= 1
                    self.invincible = 120
                    
                    if self.lives <= 0:
                        self.game_over = True
        
        # Collision joueur vs ennemis
        if self.invincible <= 0:
            for enemy in self.enemy_pool.get_active():
                dx = enemy.x - self.player_x
                dy = enemy.y - self.player_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < enemy.radius + 5:
                    self.lives -= 1
                    self.invincible = 120
                    if self.lives <= 0:
                        self.game_over = True
    
    def render(self):
        """Affiche le jeu"""
        # Effacer les anciens éléments (sauf UI)
        self.canvas.delete("game")
        
        # Dessiner les projectiles
        for bullet in self.bullet_pool.get_active():
            color = bullet.color
            if bullet.is_player_bullet:
                # Effet de traînée pour les tirs du joueur
                self.canvas.create_oval(
                    bullet.x - bullet.radius - 2, bullet.y - bullet.radius + 5,
                    bullet.x + bullet.radius + 2, bullet.y + bullet.radius + 15,
                    fill="#004444", outline="", tags="game"
                )
            self.canvas.create_oval(
                bullet.x - bullet.radius, bullet.y - bullet.radius,
                bullet.x + bullet.radius, bullet.y + bullet.radius,
                fill=color, outline="white" if not bullet.is_player_bullet else "",
                tags="game"
            )
        
        # Dessiner les ennemis
        for enemy in self.enemy_pool.get_active():
            # Corps
            self.canvas.create_polygon(
                enemy.x, enemy.y - enemy.radius,
                enemy.x - enemy.radius, enemy.y + enemy.radius,
                enemy.x + enemy.radius, enemy.y + enemy.radius,
                fill="#8844aa", outline="#cc66ff", width=2, tags="game"
            )
            # Barre de vie
            health_width = (enemy.health / 5) * 30
            self.canvas.create_rectangle(
                enemy.x - 15, enemy.y - enemy.radius - 8,
                enemy.x - 15 + health_width, enemy.y - enemy.radius - 4,
                fill="#44ff44", outline="", tags="game"
            )
        
        # Dessiner le joueur
        if not self.game_over:
            # Effet de clignotement si invincible
            if self.invincible <= 0 or self.frame_count % 6 < 3:
                # Vaisseau
                self.canvas.create_polygon(
                    self.player_x, self.player_y - PLAYER_SIZE,
                    self.player_x - PLAYER_SIZE, self.player_y + PLAYER_SIZE,
                    self.player_x, self.player_y + 5,
                    self.player_x + PLAYER_SIZE, self.player_y + PLAYER_SIZE,
                    fill="#00aaff", outline="#00ffff", width=2, tags="game"
                )
                # Hitbox visible (petit point)
                self.canvas.create_oval(
                    self.player_x - 3, self.player_y - 3,
                    self.player_x + 3, self.player_y + 3,
                    fill="white", outline="", tags="game"
                )
                # Flamme du réacteur
                flame_offset = math.sin(self.frame_count * 0.5) * 3
                self.canvas.create_polygon(
                    self.player_x - 5, self.player_y + PLAYER_SIZE,
                    self.player_x, self.player_y + PLAYER_SIZE + 10 + flame_offset,
                    self.player_x + 5, self.player_y + PLAYER_SIZE,
                    fill="#ff6600", outline="#ffcc00", tags="game"
                )
        
        # Mise à jour UI
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        hearts = "❤" * self.lives + "♡" * (3 - self.lives)
        self.canvas.itemconfig(self.lives_text, text=f"Vies: {hearts}")
        
        active_bullets = len(self.bullet_pool.get_active())
        self.canvas.itemconfig(self.pool_text, 
            text=f"Bullets actifs: {active_bullets}/{POOL_SIZE}")
        
        # Game Over
        if self.game_over:
            self.canvas.create_rectangle(
                WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 60,
                WINDOW_WIDTH//2 + 150, WINDOW_HEIGHT//2 + 60,
                fill="#1a1a2e", outline="#ff4444", width=3, tags="game"
            )
            self.canvas.create_text(
                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20,
                text="GAME OVER", fill="#ff4444",
                font=("Arial", 32, "bold"), tags="game"
            )
            self.canvas.create_text(
                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
                text=f"Score Final: {self.score}", fill="white",
                font=("Arial", 18), tags="game"
            )
            self.canvas.create_text(
                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 45,
                text="Appuyez sur ESPACE pour rejouer", fill="#888888",
                font=("Arial", 12), tags="game"
            )
    
    def game_loop(self):
        """Boucle principale du jeu"""
        if not self.paused:
            self.frame_count += 1
            
            # Mises à jour
            self.update_player()
            self.update_enemies()
            self.bullet_pool.update_all()
            self.check_collisions()
            
            # Rendu
            self.render()
        
        # ~60 FPS
        self.root.after(16, self.game_loop)
    
    def run(self):
        self.root.mainloop()


# ==================== LANCEMENT ====================

if __name__ == "__main__":
    game = BulletHellGame()
    game.run()

import tkinter as tk
from tkinter import messagebox
import math
import time

WIDTH = 800
HEIGHT = 600
PATH = [(50, 300), (200, 300), (200, 150), (400, 150), (400, 450), (600, 450), (600, 300), (750, 300)]

BLOON_TYPES = {
    'red': {'health': 1, 'speed': 1, 'color': 'red', 'value': 1},
    'blue': {'health': 1, 'speed': 1.5, 'color': 'blue', 'value': 2},
    'green': {'health': 2, 'speed': 2, 'color': 'green', 'value': 3},
}

TOWER_TYPES = {
    'dart': {'cost': 170, 'range': 50, 'damage': 1, 'color': 'gray', 'fire_rate': 1},
    'tack': {'cost': 280, 'range': 60, 'damage': 1, 'color': 'yellow', 'fire_rate': 0.5, 'projectiles': 8},
    'sniper': {'cost': 350, 'range': 200, 'damage': 2, 'color': 'black', 'fire_rate': 2},
}

class Bloon:
    def __init__(self, bloon_type, path):
        self.bloon_type = bloon_type
        self.health = BLOON_TYPES[bloon_type]['health']
        self.speed = BLOON_TYPES[bloon_type]['speed']
        self.color = BLOON_TYPES[bloon_type]['color']
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.alive = True
        self.popped = False

    def move(self):
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > self.speed:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            else:
                self.x = target_x
                self.y = target_y
                self.path_index += 1
        else:
            self.alive = False
            return True  # escaped
        return False

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.popped = True
            self.alive = False
            return True  # popped
        return False

class Tower:
    def __init__(self, tower_type, x, y):
        self.tower_type = tower_type
        self.x = x
        self.y = y
        self.range = TOWER_TYPES[tower_type]['range']
        self.damage = TOWER_TYPES[tower_type]['damage']
        self.color = TOWER_TYPES[tower_type]['color']
        self.fire_rate = TOWER_TYPES[tower_type]['fire_rate']
        self.last_fired = 0
        self.projectiles = TOWER_TYPES[tower_type].get('projectiles', 1)

    def can_fire(self, current_time):
        return current_time - self.last_fired >= 1 / self.fire_rate

    def fire(self, bloons):
        if not self.can_fire(time.time()):
            return []
        self.last_fired = time.time()
        closest = None
        min_dist = float('inf')
        for bloon in bloons:
            if not bloon.alive:
                continue
            dist = math.sqrt((bloon.x - self.x)**2 + (bloon.y - self.y)**2)
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                closest = bloon
        if closest:
            if self.tower_type == 'tack':
                projectiles = []
                for i in range(self.projectiles):
                    angle = (2 * math.pi / self.projectiles) * i
                    dx = math.cos(angle) * 10
                    dy = math.sin(angle) * 10
                    projectiles.append(Projectile(self.x, self.y, dx, dy, self.damage))
                return projectiles
            else:
                dx = closest.x - self.x
                dy = closest.y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                speed = 5
                dx = (dx / dist) * speed if dist > 0 else 0
                dy = (dy / dist) * speed if dist > 0 else 0
                return [Projectile(self.x, self.y, dx, dy, self.damage, closest)]
        return []

class Projectile:
    def __init__(self, x, y, dx, dy, damage, target=None):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.target = target
        self.alive = True

    def move(self):
        self.x += self.dx
        self.y += self.dy

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BTD6 Clone")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg='green')
        self.canvas.pack()
        self.path = PATH
        self.bloons = []
        self.towers = []
        self.projectiles = []
        self.money = 650
        self.health = 100
        self.wave = 1
        self.wave_bloons = []
        self.wave_timer = 0
        self.selected_tower = None
        self.ui_frame = tk.Frame(self.root)
        self.ui_frame.pack()
        self.money_label = tk.Label(self.ui_frame, text=f"Money: {self.money}")
        self.money_label.pack(side=tk.LEFT)
        self.health_label = tk.Label(self.ui_frame, text=f"Health: {self.health}")
        self.health_label.pack(side=tk.LEFT)
        self.wave_label = tk.Label(self.ui_frame, text=f"Wave: {self.wave}")
        self.wave_label.pack(side=tk.LEFT)
        self.tower_buttons = {}
        for tower_type in TOWER_TYPES:
            btn = tk.Button(self.ui_frame, text=f"{tower_type.capitalize()} (${TOWER_TYPES[tower_type]['cost']})", command=lambda t=tower_type: self.select_tower(t))
            btn.pack(side=tk.LEFT)
            self.tower_buttons[tower_type] = btn
        self.canvas.bind("<Button-1>", self.place_tower)
        self.draw_path()
        self.spawn_wave()
        self.root.after(100, self.game_loop)

    def draw_path(self):
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i+1]
            self.canvas.create_line(x1, y1, x2, y2, width=20, fill='brown')

    def select_tower(self, tower_type):
        self.selected_tower = tower_type

    def place_tower(self, event):
        if self.selected_tower and self.money >= TOWER_TYPES[self.selected_tower]['cost']:
            valid = True
            for tower in self.towers:
                dist = math.sqrt((event.x - tower.x)**2 + (event.y - tower.y)**2)
                if dist < 40:
                    valid = False
                    break
            for i in range(len(self.path) - 1):
                x1, y1 = self.path[i]
                x2, y2 = self.path[i+1]
                dist = self.distance_to_line(event.x, event.y, x1, y1, x2, y2)
                if dist < 20:
                    valid = False
                    break
            if valid:
                tower = Tower(self.selected_tower, event.x, event.y)
                self.towers.append(tower)
                self.money -= TOWER_TYPES[self.selected_tower]['cost']
                self.update_ui()
                self.selected_tower = None

    def distance_to_line(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        t = ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)
        t = max(0, min(1, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

    def spawn_wave(self):
        num_red = self.wave * 10
        num_blue = max(0, (self.wave - 2) * 5)
        num_green = max(0, (self.wave - 5) * 3)
        for _ in range(num_red):
            self.wave_bloons.append('red')
        for _ in range(num_blue):
            self.wave_bloons.append('blue')
        for _ in range(num_green):
            self.wave_bloons.append('green')

    def game_loop(self):
        current_time = time.time()
        if self.wave_bloons and current_time - self.wave_timer > 0.5:
            bloon_type = self.wave_bloons.pop(0)
            bloon = Bloon(bloon_type, self.path)
            self.bloons.append(bloon)
            self.wave_timer = current_time
        for bloon in self.bloons[:]:
            if bloon.popped:
                self.money += BLOON_TYPES[bloon.bloon_type]['value']
                self.update_ui()
                self.bloons.remove(bloon)
            elif bloon.move():
                self.health -= 1
                self.update_ui()
                if self.health <= 0:
                    messagebox.showinfo("Game Over", "You lost!")
                    self.root.quit()
                self.bloons.remove(bloon)
            elif not bloon.alive:
                self.bloons.remove(bloon)
        for tower in self.towers:
            projectiles = tower.fire(self.bloons)
            self.projectiles.extend(projectiles)
        for projectile in self.projectiles[:]:
            projectile.move()
            if projectile.target:
                if projectile.target.alive:
                    dist = math.sqrt((projectile.x - projectile.target.x)**2 + (projectile.y - projectile.target.y)**2)
                    if dist < 10:
                        projectile.target.take_damage(projectile.damage)
                        projectile.alive = False
            else:
                for bloon in self.bloons:
                    if bloon.alive:
                        dist = math.sqrt((projectile.x - bloon.x)**2 + (projectile.y - bloon.y)**2)
                        if dist < 10:
                            bloon.take_damage(projectile.damage)
                            projectile.alive = False
                            break
            if not projectile.alive:
                self.projectiles.remove(projectile)
        if not self.wave_bloons and not self.bloons:
            self.wave += 1
            self.spawn_wave()
            self.update_ui()
        self.canvas.delete("all")
        self.draw_path()
        for bloon in self.bloons:
            if bloon.alive:
                self.canvas.create_oval(bloon.x-10, bloon.y-10, bloon.x+10, bloon.y+10, fill=bloon.color)
        for tower in self.towers:
            self.canvas.create_rectangle(tower.x-15, tower.y-15, tower.x+15, tower.y+15, fill=tower.color)
        for projectile in self.projectiles:
            if projectile.alive:
                self.canvas.create_oval(projectile.x-3, projectile.y-3, projectile.x+3, projectile.y+3, fill='black')
        self.root.after(50, self.game_loop)

    def update_ui(self):
        self.money_label.config(text=f"Money: {self.money}")
        self.health_label.config(text=f"Health: {self.health}")
        self.wave_label.config(text=f"Wave: {self.wave}")

if __name__ == "__main__":
    game = Game()
    game.root.mainloop()
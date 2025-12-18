import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
WORLD_WIDTH = 25  # tiles
WORLD_HEIGHT = 18  # tiles

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zelda Clone")
        self.canvas = tk.Canvas(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='black')
        self.canvas.pack()

        # Game state
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.world = World()
        self.enemies = [Enemy(100, 100), Enemy(200, 200)]
        self.items = [Item(300, 300, 'sword'), Item(400, 400, 'key')]
        self.dungeons = []
        self.inventory = Inventory()

        # UI elements
        self.health_label = tk.Label(self.root, text=f"Health: {self.player.health}")
        self.health_label.pack()
        self.inventory_label = tk.Label(self.root, text=f"Inventory: {self.inventory.items}")
        self.inventory_label.pack()

        # Buttons
        save_button = tk.Button(self.root, text="Save Game", command=self.save_game)
        save_button.pack()
        load_button = tk.Button(self.root, text="Load Game", command=self.load_game)
        load_button.pack()

        # Bind keys
        self.root.bind('<KeyPress>', self.handle_key_press)
        self.root.bind('<KeyRelease>', self.handle_key_release)

        # Game loop
        self.running = True
        self.last_time = time.time()
        self.game_loop()

        self.root.mainloop()

    def game_loop(self):
        if not self.running:
            return

        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Update game state
        self.update(dt)
        self.render()

        # Schedule next frame
        self.root.after(16, self.game_loop)  # ~60 FPS

    def update(self, dt):
        self.player.update(dt, self.world)
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.world)

        # Check item collisions
        items_to_remove = []
        for item in self.items:
            if self.check_collision(self.player, item):
                self.inventory.add_item(item.type)
                items_to_remove.append(item)
        for item in items_to_remove:
            self.items.remove(item)

        # Check enemy collisions
        if self.player.attacking:
            for enemy in self.enemies:
                if self.check_collision(self.player, enemy):
                    enemy.health -= 10
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)

        # Enemy damage to player
        for enemy in self.enemies:
            if self.check_collision(self.player, enemy):
                self.player.health -= 5
                if self.player.health <= 0:
                    messagebox.showinfo("Game Over", "You died!")
                    self.running = False

        # Update UI
        self.health_label.config(text=f"Health: {self.player.health}")
        self.inventory_label.config(text=f"Inventory: {self.inventory.items}")

    def check_collision(self, obj1, obj2):
        return (obj1.x < obj2.x + TILE_SIZE and
                obj1.x + TILE_SIZE > obj2.x and
                obj1.y < obj2.y + TILE_SIZE and
                obj1.y + TILE_SIZE > obj2.y)

    def save_game(self):
        data = {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health
            },
            'inventory': self.inventory.items
        }
        with open('zelda-clone/save.json', 'w') as f:
            json.dump(data, f)
        messagebox.showinfo("Save", "Game saved!")

    def load_game(self):
        if os.path.exists('zelda-clone/save.json'):
            with open('zelda-clone/save.json', 'r') as f:
                data = json.load(f)
            self.player.x = data['player']['x']
            self.player.y = data['player']['y']
            self.player.health = data['player']['health']
            self.inventory.items = data['inventory']
            messagebox.showinfo("Load", "Game loaded!")
        else:
            messagebox.showerror("Load", "No save file found!")

    def render(self):
        self.canvas.delete('all')
        # Render world
        self.world.render(self.canvas)
        # Render player
        self.player.render(self.canvas)
        # Render enemies
        for enemy in self.enemies:
            enemy.render(self.canvas)
        # Render items
        for item in self.items:
            item.render(self.canvas)

    def handle_key_press(self, event):
        if event.keysym == 'w' or event.keysym == 'Up':
            self.player.move_up = True
        elif event.keysym == 's' or event.keysym == 'Down':
            self.player.move_down = True
        elif event.keysym == 'a' or event.keysym == 'Left':
            self.player.move_left = True
        elif event.keysym == 'd' or event.keysym == 'Right':
            self.player.move_right = True
        elif event.keysym == 'space':
            self.player.attack()

    def handle_key_release(self, event):
        if event.keysym == 'w' or event.keysym == 'Up':
            self.player.move_up = False
        elif event.keysym == 's' or event.keysym == 'Down':
            self.player.move_down = False
        elif event.keysym == 'a' or event.keysym == 'Left':
            self.player.move_left = False
        elif event.keysym == 'd' or event.keysym == 'Right':
            self.player.move_right = False

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 200  # pixels per second
        self.health = 100
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.attacking = False
        self.attack_timer = 0

    def update(self, dt, world):
        dx = dy = 0
        if self.move_up:
            dy -= self.speed * dt
        if self.move_down:
            dy += self.speed * dt
        if self.move_left:
            dx -= self.speed * dt
        if self.move_right:
            dx += self.speed * dt

        # Check wall collisions
        new_x = self.x + dx
        new_y = self.y + dy

        # Check corners for collision
        if not (world.is_wall(new_x, new_y) or
                world.is_wall(new_x + TILE_SIZE - 1, new_y) or
                world.is_wall(new_x, new_y + TILE_SIZE - 1) or
                world.is_wall(new_x + TILE_SIZE - 1, new_y + TILE_SIZE - 1)):
            self.x = new_x
            self.y = new_y

        # Keep in bounds
        self.x = max(0, min(SCREEN_WIDTH - TILE_SIZE, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - TILE_SIZE, self.y))

        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_timer = 0.5  # 0.5 seconds attack duration

    def render(self, canvas):
        color = 'red' if self.attacking else 'blue'
        canvas.create_rectangle(self.x, self.y, self.x + TILE_SIZE, self.y + TILE_SIZE, fill=color)

class World:
    def __init__(self):
        self.tiles = []
        # Initialize with grass tiles and some walls
        for y in range(WORLD_HEIGHT):
            row = []
            for x in range(WORLD_WIDTH):
                if x == 0 or x == WORLD_WIDTH - 1 or y == 0 or y == WORLD_HEIGHT - 1:
                    row.append('wall')
                elif (x == 5 and y > 5) or (y == 10 and x > 10):
                    row.append('wall')
                else:
                    row.append('grass')
            self.tiles.append(row)

    def is_wall(self, x, y):
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_x < WORLD_WIDTH and 0 <= tile_y < WORLD_HEIGHT:
            return self.tiles[tile_y][tile_x] == 'wall'
        return True  # Out of bounds is wall

    def render(self, canvas):
        for y in range(WORLD_HEIGHT):
            for x in range(WORLD_WIDTH):
                tile_x = x * TILE_SIZE
                tile_y = y * TILE_SIZE
                color = 'green' if self.tiles[y][x] == 'grass' else 'gray'
                canvas.create_rectangle(tile_x, tile_y, tile_x + TILE_SIZE, tile_y + TILE_SIZE, fill=color)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 100
        self.health = 50

    def update(self, dt, player, world):
        # Simple AI: move towards player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            move_x = (dx / dist) * self.speed * dt
            move_y = (dy / dist) * self.speed * dt
            new_x = self.x + move_x
            new_y = self.y + move_y
            # Check wall collision
            if not (world.is_wall(new_x, new_y) or
                    world.is_wall(new_x + TILE_SIZE - 1, new_y) or
                    world.is_wall(new_x, new_y + TILE_SIZE - 1) or
                    world.is_wall(new_x + TILE_SIZE - 1, new_y + TILE_SIZE - 1)):
                self.x = new_x
                self.y = new_y

    def render(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x + TILE_SIZE, self.y + TILE_SIZE, fill='red')

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type

    def render(self, canvas):
        color = 'yellow' if self.type == 'sword' else 'purple'
        canvas.create_rectangle(self.x, self.y, self.x + TILE_SIZE, self.y + TILE_SIZE, fill=color)

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

class Dungeon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rooms = []

if __name__ == "__main__":
    game = Game()
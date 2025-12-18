import tkinter as tk
import math

# Constants
WIDTH = 800
HEIGHT = 600
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2  # One ray per 2 pixels for performance
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
WALL_HEIGHT = HEIGHT // 2

class DoomClone:
    def __init__(self, root):
        self.root = root
        self.root.title("Doom Clone")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
        self.canvas.pack()

        # Player variables
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0

        # Map (simple 2D array: 0 = empty, 1 = wall)
        self.game_map = [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1]
        ]

        self.enemies = [[3.5, 3.5], [5.5, 2.5]]  # List of enemies: [x, y]
        self.bullets = []  # List of bullets: (x, y, angle)

        # Bind keys
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)

        self.keys = {'w': False, 's': False, 'a': False, 'd': False, 'Left': False, 'Right': False, 'space': False}

        self.game_loop()

    def on_key_press(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = True

    def on_key_release(self, event):
        key = event.keysym
        if key in self.keys:
            self.keys[key] = False

    def game_loop(self):
        self.update()
        self.render()
        self.root.after(16, self.game_loop)  # ~60 FPS

    def update(self):
        # Player movement
        if self.keys['w']:
            new_x = self.player_x + math.cos(self.player_angle) * 0.1
            new_y = self.player_y + math.sin(self.player_angle) * 0.1
            if not self.check_collision(new_x, new_y):
                self.player_x, self.player_y = new_x, new_y
        if self.keys['s']:
            new_x = self.player_x - math.cos(self.player_angle) * 0.1
            new_y = self.player_y - math.sin(self.player_angle) * 0.1
            if not self.check_collision(new_x, new_y):
                self.player_x, self.player_y = new_x, new_y
        if self.keys['a']:
            self.player_angle -= 0.1
        if self.keys['d']:
            self.player_angle += 0.1
        if self.keys['Left']:
            self.player_angle -= 0.05
        if self.keys['Right']:
            self.player_angle += 0.05

        # Shooting
        if self.keys['space']:
            self.shoot()
            self.keys['space'] = False  # Prevent continuous shooting

        # Update bullets
        for bullet in self.bullets[:]:
            bullet[0] += math.cos(bullet[2]) * 0.2
            bullet[1] += math.sin(bullet[2]) * 0.2
            if self.check_collision(bullet[0], bullet[1]):
                self.bullets.remove(bullet)
            # Check collision with enemies
            for enemy in self.enemies[:]:
                if math.hypot(bullet[0] - enemy[0], bullet[1] - enemy[1]) < 0.5:
                    self.enemies.remove(enemy)
                    self.root.bell()  # Sound effect for enemy hit
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        # Update enemies (simple AI: move towards player)
        for enemy in self.enemies:
            dx = self.player_x - enemy[0]
            dy = self.player_y - enemy[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                enemy[0] += (dx / dist) * 0.02
                enemy[1] += (dy / dist) * 0.02
            # Check if enemy touches player
            if dist < 0.5:
                self.game_over()

    def check_collision(self, x, y):
        map_x = int(x)
        map_y = int(y)
        if 0 <= map_x < len(self.game_map[0]) and 0 <= map_y < len(self.game_map):
            return self.game_map[map_y][map_x] == 1
        return True

    def shoot(self):
        self.bullets.append([self.player_x, self.player_y, self.player_angle])
        self.root.bell()  # Sound effect for shooting

    def render(self):
        self.canvas.delete('all')

        # Raycasting
        for ray in range(NUM_RAYS):
            angle = self.player_angle - HALF_FOV + ray * DELTA_ANGLE
            distance = self.cast_ray(angle)
            wall_height = WALL_HEIGHT / (distance + 0.0001)  # Avoid division by zero
            wall_top = HEIGHT // 2 - wall_height // 2
            wall_bottom = HEIGHT // 2 + wall_height // 2

            # Draw wall column
            color = 'gray' if distance < MAX_DEPTH else 'darkgray'
            self.canvas.create_line(ray * 2, wall_top, ray * 2, wall_bottom, fill=color, width=2)

        # Draw enemies (simple dots on minimap or in 3D space)
        for enemy in self.enemies:
            # Simple 2D representation for now
            screen_x = (enemy[0] - self.player_x) * 50 + WIDTH // 2
            screen_y = (enemy[1] - self.player_y) * 50 + HEIGHT // 2
            self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill='red')

        # Draw bullets
        for bullet in self.bullets:
            screen_x = (bullet[0] - self.player_x) * 50 + WIDTH // 2
            screen_y = (bullet[1] - self.player_y) * 50 + HEIGHT // 2
            self.canvas.create_oval(screen_x - 2, screen_y - 2, screen_x + 2, screen_y + 2, fill='yellow')

    def cast_ray(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        for depth in range(1, MAX_DEPTH):
            x = self.player_x + cos_a * depth
            y = self.player_y + sin_a * depth

            if self.check_collision(x, y):
                return depth
        return MAX_DEPTH

    def game_over(self):
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER", font=("Arial", 50), fill="red")
        self.root.after(2000, self.root.quit)

if __name__ == "__main__":
    root = tk.Tk()
    game = DoomClone(root)
    root.mainloop()
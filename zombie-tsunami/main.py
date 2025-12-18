import tkinter as tk
import random

class ZombieTsunami:
    def __init__(self, root):
        self.root = root
        self.root.title("Zombie Tsunami")
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.pack()

        # Player
        self.player = self.canvas.create_rectangle(50, 250, 70, 300, fill='blue')
        self.player_speed = 10
        self.player_x = 60

        # Game variables
        self.zombies = []
        self.bullets = []
        self.score = 0
        self.health = 100
        self.wave = 1
        self.zombie_speed = 2
        self.spawn_timer = 0
        self.spawn_rate = 60  # frames between spawns

        # UI
        self.score_text = self.canvas.create_text(700, 20, text=f"Score: {self.score}", fill='white', font=('Arial', 16))
        self.health_text = self.canvas.create_text(700, 50, text=f"Health: {self.health}", fill='white', font=('Arial', 16))
        self.wave_text = self.canvas.create_text(700, 80, text=f"Wave: {self.wave}", fill='white', font=('Arial', 16))

        # Bind keys
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<space>', self.shoot)

        # Game loop
        self.game_loop()

    def move_left(self, event):
        if self.player_x > 10:
            self.canvas.move(self.player, -self.player_speed, 0)
            self.player_x -= self.player_speed

    def move_right(self, event):
        if self.player_x < 780:
            self.canvas.move(self.player, self.player_speed, 0)
            self.player_x += self.player_speed

    def shoot(self, event):
        bullet = self.canvas.create_rectangle(self.player_x + 10, 275, self.player_x + 20, 285, fill='yellow')
        self.bullets.append(bullet)

    def spawn_zombie(self):
        y = random.randint(0, 550)
        zombie = self.canvas.create_rectangle(800, y, 820, y + 50, fill='green')
        self.zombies.append(zombie)

    def game_loop(self):
        # Move zombies
        to_remove_zombies = []
        for zombie in self.zombies:
            self.canvas.move(zombie, -self.zombie_speed, 0)
            coords = self.canvas.coords(zombie)
            if coords[0] < 0:
                to_remove_zombies.append(zombie)
                self.health -= 10
                self.canvas.itemconfig(self.health_text, text=f"Health: {self.health}")
                if self.health <= 0:
                    self.game_over()
                    return

        for zombie in to_remove_zombies:
            self.canvas.delete(zombie)
            self.zombies.remove(zombie)

        # Move bullets
        to_remove_bullets = []
        for bullet in self.bullets:
            self.canvas.move(bullet, 10, 0)
            coords = self.canvas.coords(bullet)
            if coords[0] > 800:
                to_remove_bullets.append(bullet)

        for bullet in to_remove_bullets:
            self.canvas.delete(bullet)
            self.bullets.remove(bullet)

        # Check collisions
        to_remove_zombies = []
        to_remove_bullets = []
        for zombie in self.zombies:
            z_coords = self.canvas.coords(zombie)
            for bullet in self.bullets:
                b_coords = self.canvas.coords(bullet)
                if (b_coords[0] < z_coords[2] and b_coords[2] > z_coords[0] and
                    b_coords[1] < z_coords[3] and b_coords[3] > z_coords[1]):
                    to_remove_zombies.append(zombie)
                    to_remove_bullets.append(bullet)
                    self.score += 1
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        for zombie in to_remove_zombies:
            if zombie in self.zombies:
                self.canvas.delete(zombie)
                self.zombies.remove(zombie)
        for bullet in to_remove_bullets:
            if bullet in self.bullets:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # Spawn zombies
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_zombie()
            self.spawn_timer = 0
            if self.score > 0 and self.score % 10 == 0:
                self.wave += 1
                self.zombie_speed += 0.5
                self.spawn_rate = max(20, self.spawn_rate - 5)
                self.canvas.itemconfig(self.wave_text, text=f"Wave: {self.wave}")

        self.root.after(16, self.game_loop)  # ~60 FPS

    def game_over(self):
        self.canvas.create_text(400, 300, text="GAME OVER", fill='red', font=('Arial', 48))
        self.canvas.create_text(400, 350, text=f"Final Score: {self.score}", fill='white', font=('Arial', 24))

if __name__ == "__main__":
    root = tk.Tk()
    game = ZombieTsunami(root)
    root.mainloop()
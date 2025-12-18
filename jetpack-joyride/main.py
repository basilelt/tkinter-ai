import tkinter as tk
import random
import time

class Player:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = 100
        self.y = 300
        self.velocity_y = 0
        self.jetpack_on = False
        self.size = 20
        # Draw player as character: head, body, arms, legs
        self.head = canvas.create_oval(self.x - 8, self.y - 35, self.x + 8, self.y - 19, fill='peachpuff')
        self.body = canvas.create_rectangle(self.x - 6, self.y - 19, self.x + 6, self.y + 5, fill='blue')
        self.left_arm = canvas.create_line(self.x - 6, self.y - 15, self.x - 12, self.y - 5, width=3, fill='peachpuff')
        self.right_arm = canvas.create_line(self.x + 6, self.y - 15, self.x + 12, self.y - 5, width=3, fill='peachpuff')
        self.left_leg = canvas.create_line(self.x - 3, self.y + 5, self.x - 6, self.y + 15, width=3, fill='blue')
        self.right_leg = canvas.create_line(self.x + 3, self.y + 5, self.x + 6, self.y + 15, width=3, fill='blue')
        self.jetpack = canvas.create_rectangle(self.x - 10, self.y - 10, self.x - 6, self.y + 10, fill='gray')
        self.flame = None

    def update(self):
        if self.jetpack_on:
            self.velocity_y -= 0.5  # upward acceleration
            if not self.flame:
                self.flame = self.canvas.create_polygon(self.x - 10, self.y + 10, self.x - 8, self.y + 20, self.x - 6, self.y + 10, fill='orange')
        else:
            self.velocity_y += 0.3  # gravity
            if self.flame:
                self.canvas.delete(self.flame)
                self.flame = None

        self.y += self.velocity_y

        # boundaries
        if self.y < 50:
            self.y = 50
            self.velocity_y = 0
        if self.y > 550:
            self.y = 550
            self.velocity_y = 0

        # Update positions
        dy = self.y - 300  # offset from initial
        self.canvas.coords(self.head, self.x - 8, self.y - 35, self.x + 8, self.y - 19)
        self.canvas.coords(self.body, self.x - 6, self.y - 19, self.x + 6, self.y + 5)
        self.canvas.coords(self.left_arm, self.x - 6, self.y - 15, self.x - 12, self.y - 5)
        self.canvas.coords(self.right_arm, self.x + 6, self.y - 15, self.x + 12, self.y - 5)
        self.canvas.coords(self.left_leg, self.x - 3, self.y + 5, self.x - 6, self.y + 15)
        self.canvas.coords(self.right_leg, self.x + 3, self.y + 5, self.x + 6, self.y + 15)
        self.canvas.coords(self.jetpack, self.x - 10, self.y - 10, self.x - 6, self.y + 10)
        if self.flame:
            self.canvas.coords(self.flame, self.x - 10, self.y + 10, self.x - 8, self.y + 20, self.x - 6, self.y + 10)

    def toggle_jetpack(self):
        self.jetpack_on = not self.jetpack_on

class Obstacle:
    def __init__(self, canvas, x, y, obstacle_type='block'):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.speed = 5
        if obstacle_type == 'laser':
            self.id = canvas.create_line(x, y, x + 800, y, width=5, fill='red')
            self.width = 800
            self.height = 5
        elif obstacle_type == 'missile':
            self.id = canvas.create_polygon(x, y, x + 20, y - 10, x + 40, y, x + 20, y + 10, fill='darkred')
            self.width = 40
            self.height = 20
        else:  # block
            self.width = random.randint(20, 50)
            self.height = random.randint(20, 100)
            self.id = canvas.create_rectangle(x, y, x + self.width, y + self.height, fill='red')

    def update(self):
        self.x -= self.speed
        if self.type == 'laser':
            self.canvas.coords(self.id, self.x, self.y, self.x + 800, self.y)
        elif self.type == 'missile':
            self.canvas.coords(self.id, self.x, self.y, self.x + 20, self.y - 10, self.x + 40, self.y, self.x + 20, self.y + 10)
        else:
            self.canvas.coords(self.id, self.x, self.y, self.x + self.width, self.y + self.height)

    def off_screen(self):
        return self.x + self.width < 0

class Coin:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = 10
        self.id = canvas.create_oval(x - self.size, y - self.size,
                                    x + self.size, y + self.size, fill='yellow')

    def update(self):
        self.x -= 5
        self.canvas.coords(self.id, self.x - self.size, self.y - self.size,
                          self.x + self.size, self.y + self.size)

    def off_screen(self):
        return self.x + self.size < 0

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='skyblue')
        self.canvas.pack()

        # Background elements
        self.clouds = []
        for i in range(5):
            x = random.randint(0, 800)
            y = random.randint(50, 200)
            cloud = self.canvas.create_oval(x, y, x + 60, y + 40, fill='white', outline='lightgray')
            self.clouds.append(cloud)

        self.ground_x = 0
        self.ground = self.canvas.create_rectangle(0, 550, 1600, 600, fill='green')

        self.player = Player(self.canvas)
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.score_text = self.canvas.create_text(700, 50, text=f'Score: {self.score}', font=('Arial', 20))

        self.game_over = False
        self.spawn_timer = 0

        self.root.bind('<space>', lambda e: self.player.toggle_jetpack())
        self.root.bind('<KeyPress>', self.key_press)

        self.animate()

    def key_press(self, event):
        if event.keysym == 'r' and self.game_over:
            self.restart()

    def spawn_obstacle(self):
        y = random.randint(100, 500)
        types = ['block', 'laser', 'missile']
        obstacle_type = random.choice(types)
        self.obstacles.append(Obstacle(self.canvas, 800, y, obstacle_type))

    def spawn_coin(self):
        y = random.randint(100, 500)
        self.coins.append(Coin(self.canvas, 800, y))

    def animate(self):
        if not self.game_over:
            self.player.update()

            # Scroll ground
            self.ground_x -= 5
            if self.ground_x <= -800:
                self.ground_x = 0
            self.canvas.coords(self.ground, self.ground_x, 550, self.ground_x + 1600, 600)

            # update obstacles
            for obs in self.obstacles[:]:
                obs.update()
                if obs.off_screen():
                    self.obstacles.remove(obs)
                    self.canvas.delete(obs.id)

            # update coins
            for coin in self.coins[:]:
                coin.update()
                if coin.off_screen():
                    self.coins.remove(coin)
                    self.canvas.delete(coin.id)

            # spawn new items
            self.spawn_timer += 1
            if self.spawn_timer % 60 == 0:  # every second approx
                self.spawn_obstacle()
                if random.random() < 0.5:
                    self.spawn_coin()

            # check collisions
            self.check_collisions()

            self.root.after(16, self.animate)  # ~60 FPS

    def check_collisions(self):
        player_coords = self.canvas.coords(self.player.body)  # Use body as main collision box

        # obstacles
        for obs in self.obstacles:
            obs_coords = self.canvas.coords(obs.id)
            if self.overlap(player_coords, obs_coords):
                self.game_over = True
                self.canvas.create_text(400, 300, text='Game Over! Press R to restart', font=('Arial', 30))

        # coins
        for coin in self.coins[:]:
            coin_coords = self.canvas.coords(coin.id)
            if self.overlap(player_coords, coin_coords):
                self.score += 10
                self.canvas.itemconfig(self.score_text, text=f'Score: {self.score}')
                self.coins.remove(coin)
                self.canvas.delete(coin.id)

    def overlap(self, rect1, rect2):
        return not (rect1[2] < rect2[0] or rect1[0] > rect2[2] or rect1[1] > rect2[3] or rect1[3] < rect2[1])

    def restart(self):
        self.canvas.delete('all')
        self.player = Player(self.canvas)
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.score_text = self.canvas.create_text(700, 50, text=f'Score: {self.score}', font=('Arial', 20))
        self.game_over = False
        self.spawn_timer = 0
        self.animate()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Jetpack Joyride')
    game = Game(root)
    root.mainloop()
import tkinter as tk
import random

# Constants
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
ZOMBIE_SIZE = 20
ZOMBIE_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -12
GROUND_Y = CANVAS_HEIGHT - 50
OBSTACLE_SPEED = 5
COLLECTIBLE_SPEED = 5
UPDATE_INTERVAL = 16  # ~60 FPS

class Zombie:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.size = ZOMBIE_SIZE
        # Simple zombie shape: head and body
        self.head = canvas.create_oval(self.x - 8, self.y - 25, self.x + 8, self.y - 9, fill='green')
        self.body = canvas.create_rectangle(self.x - 6, self.y - 9, self.x + 6, self.y + 5, fill='darkgreen')
        self.id = self.body  # Use body for collision

    def update(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        if self.y > GROUND_Y - 5:  # Adjust for body height
            self.y = GROUND_Y - 5
            self.velocity_y = 0
        # Update positions
        dy = self.y - (GROUND_Y - self.size//2)  # offset
        self.canvas.coords(self.head, self.x - 8, self.y - 25, self.x + 8, self.y - 9)
        self.canvas.coords(self.body, self.x - 6, self.y - 9, self.x + 6, self.y + 5)

    def jump(self):
        if self.y >= GROUND_Y - self.size//2:
            self.velocity_y = JUMP_STRENGTH

class Obstacle:
    def __init__(self, canvas, x, obstacle_type='building'):
        self.canvas = canvas
        self.x = x
        self.type = obstacle_type
        if obstacle_type == 'building':
            self.width = random.randint(20, 50)
            self.height = random.randint(50, 100)
            self.y = GROUND_Y - self.height
            self.id = canvas.create_rectangle(self.x, self.y, self.x + self.width, GROUND_Y, fill='gray')
        elif obstacle_type == 'car':
            self.width = random.randint(30, 60)
            self.height = 20
            self.y = GROUND_Y - self.height
            self.id = canvas.create_rectangle(self.x, self.y, self.x + self.width, GROUND_Y, fill='red')

    def update(self):
        self.x -= OBSTACLE_SPEED
        if self.type == 'building':
            self.canvas.coords(self.id, self.x, self.y, self.x + self.width, GROUND_Y)
        else:
            self.canvas.coords(self.id, self.x, self.y, self.x + self.width, GROUND_Y)

    def off_screen(self):
        return self.x + self.width < 0

class Collectible:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = 15
        self.id = canvas.create_oval(self.x - self.size, self.y - self.size,
                                     self.x + self.size, self.y + self.size, fill='blue')

    def update(self):
        self.x -= COLLECTIBLE_SPEED
        self.canvas.coords(self.id, self.x - self.size, self.y - self.size,
                           self.x + self.size, self.y + self.size)

    def off_screen(self):
        return self.x + self.size < 0

class ZombieTsunami:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zombie Tsunami Clone")
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='lightblue')
        self.canvas.pack()

        # Ground
        self.ground = self.canvas.create_rectangle(0, GROUND_Y, CANVAS_WIDTH, CANVAS_HEIGHT, fill='green')

        # Zombies
        self.zombies = [Zombie(self.canvas, 100, GROUND_Y - ZOMBIE_SIZE//2)]
        self.horde_size = 1

        # Obstacles and collectibles
        self.obstacles = []
        self.collectibles = []

        # Score
        self.distance = 0
        self.score_text = self.canvas.create_text(700, 30, text=f'Horde: {self.horde_size}  Distance: {self.distance}', font=('Arial', 16))

        self.game_over = False
        self.spawn_timer = 0

        # Bind events
        self.canvas.bind('<Button-1>', lambda e: self.jump_horde())
        self.root.bind('<space>', lambda e: self.jump_horde())
        self.root.bind('<r>', lambda e: self.restart() if self.game_over else None)

        self.update()
        self.root.mainloop()

    def jump_horde(self):
        if not self.game_over:
            for zombie in self.zombies:
                zombie.jump()

    def find_safe_x(self, preferred_x):
        # Try to place at preferred_x, but avoid obstacles
        for obs in self.obstacles:
            obs_left = obs.x
            obs_right = obs.x + obs.width
            if preferred_x >= obs_left and preferred_x <= obs_right:
                # Shift left or right
                if preferred_x - 30 < 0:
                    return preferred_x + 30
                else:
                    return preferred_x - 30
        return preferred_x

    def spawn_obstacle(self):
        types = ['building', 'car']
        obstacle_type = random.choice(types)
        self.obstacles.append(Obstacle(self.canvas, CANVAS_WIDTH, obstacle_type))

    def spawn_collectible(self):
        y = random.randint(GROUND_Y - 100, GROUND_Y - 20)
        self.collectibles.append(Collectible(self.canvas, CANVAS_WIDTH, y))

    def update(self):
        if not self.game_over:
            # Update zombies
            for zombie in self.zombies:
                zombie.update()

            # Scroll if lead zombie is too far right
            if self.zombies and self.zombies[0].x > 400:
                scroll_amount = ZOMBIE_SPEED
                for zombie in self.zombies:
                    zombie.x -= scroll_amount
                for obs in self.obstacles:
                    obs.x -= scroll_amount
                for coll in self.collectibles:
                    coll.x -= scroll_amount

            # Update obstacles
            for obs in self.obstacles[:]:
                obs.update()
                if obs.off_screen():
                    self.obstacles.remove(obs)
                    self.canvas.delete(obs.id)

            # Update collectibles
            for coll in self.collectibles[:]:
                coll.update()
                if coll.off_screen():
                    self.collectibles.remove(coll)
                    self.canvas.delete(coll.id)

            # Spawn new items
            self.spawn_timer += 1
            if self.spawn_timer % 120 == 0:  # every 2 seconds
                self.spawn_obstacle()
                if random.random() < 0.6:
                    self.spawn_collectible()

            # Check collisions
            self.check_collisions()

            # Update score
            self.distance += ZOMBIE_SPEED
            self.canvas.itemconfig(self.score_text, text=f'Horde: {self.horde_size}  Distance: {self.distance}')

        self.root.after(UPDATE_INTERVAL, self.update)

    def check_collisions(self):
        zombies_to_remove = []
        for zombie in self.zombies:
            zombie_coords = self.canvas.coords(zombie.id)

            # Obstacles
            for obs in self.obstacles:
                obs_coords = self.canvas.coords(obs.id)
                if self.overlap(zombie_coords, obs_coords):
                    zombies_to_remove.append(zombie)
                    break

            # Collectibles
            for coll in self.collectibles[:]:
                coll_coords = self.canvas.coords(coll.id)
                if self.overlap(zombie_coords, coll_coords):
                    self.horde_size += 1
                    # Add new zombie at safe position
                    safe_x = self.find_safe_x(zombie.x - 30)
                    new_zombie = Zombie(self.canvas, safe_x, zombie.y)
                    self.zombies.append(new_zombie)
                    self.collectibles.remove(coll)
                    self.canvas.delete(coll.id)
                    break

        # Remove collided zombies
        for zombie in zombies_to_remove:
            self.zombies.remove(zombie)
            self.canvas.delete(zombie.head)
            self.canvas.delete(zombie.body)
            self.horde_size -= 1

        # Check if no zombies left
        if not self.zombies:
            self.game_over = True
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                    text='Game Over!\nPress R to restart', font=('Arial', 30))

    def overlap(self, rect1, rect2):
        return not (rect1[2] < rect2[0] or rect1[0] > rect2[2] or rect1[1] > rect2[3] or rect1[3] < rect2[1])

    def restart(self):
        if self.game_over:
            self.canvas.delete('all')
            # Recreate ground and score
            self.ground = self.canvas.create_rectangle(0, GROUND_Y, CANVAS_WIDTH, CANVAS_HEIGHT, fill='green')
            self.zombies = [Zombie(self.canvas, 100, GROUND_Y - ZOMBIE_SIZE//2)]
            self.horde_size = 1
            self.obstacles = []
            self.collectibles = []
            self.distance = 0
            self.score_text = self.canvas.create_text(700, 30, text=f'Horde: {self.horde_size}  Distance: {self.distance}', font=('Arial', 16))
            self.game_over = False
            self.spawn_timer = 0

if __name__ == '__main__':
    ZombieTsunami()
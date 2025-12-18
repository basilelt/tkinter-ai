import tkinter as tk
import random
import math

class FruitNinja:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.pack()
        self.fruits = []
        self.bombs = []
        self.score = 0
        self.game_over = False
        self.mouse_path = []
        self.canvas.bind('<B1-Motion>', self.slice)
        self.canvas.bind('<ButtonRelease-1>', self.end_slice)
        self.root.bind('<Key-r>', self.restart)
        self.spawn_timer = 0
        self.update()

    def spawn_fruit(self):
        x = random.randint(50, 750)
        y = 600
        vx = random.randint(-5, 5)
        vy = random.randint(-15, -10)
        emoji = random.choice(['🍎', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🥝'])
        fruit = {'x': x, 'y': y, 'vx': vx, 'vy': vy, 'emoji': emoji, 'sliced': False}
        self.fruits.append(fruit)

    def spawn_bomb(self):
        x = random.randint(50, 750)
        y = 600
        vx = random.randint(-3, 3)
        vy = random.randint(-12, -8)
        bomb = {'x': x, 'y': y, 'vx': vx, 'vy': vy, 'emoji': '💣', 'sliced': False}
        self.bombs.append(bomb)

    def update(self):
        if not self.game_over:
            self.spawn_timer += 1
            if self.spawn_timer % 30 == 0:
                self.spawn_fruit()
            if self.spawn_timer % 200 == 0:
                self.spawn_bomb()
            # update fruits
            for fruit in self.fruits[:]:
                fruit['x'] += fruit['vx']
                fruit['y'] += fruit['vy']
                fruit['vy'] += 0.5  # gravity
                if fruit['y'] > 650 or fruit['sliced']:
                    self.fruits.remove(fruit)
            for bomb in self.bombs[:]:
                bomb['x'] += bomb['vx']
                bomb['y'] += bomb['vy']
                bomb['vy'] += 0.5
                if bomb['y'] > 650 or bomb['sliced']:
                    self.bombs.remove(bomb)
            # check slicing
            for fruit in self.fruits[:]:
                if not fruit['sliced'] and self.check_slice(fruit):
                    fruit['sliced'] = True
                    self.score += 1
            for bomb in self.bombs[:]:
                if not bomb['sliced'] and self.check_slice(bomb):
                    bomb['sliced'] = True
                    self.game_over = True
        self.draw()
        self.root.after(16, self.update)  # ~60fps

    def check_slice(self, obj):
        # simple: if mouse path intersects obj
        for p1, p2 in zip(self.mouse_path[:-1], self.mouse_path[1:]):
            dist = math.hypot(obj['x'] - p1[0], obj['y'] - p1[1])
            if dist < 30:
                return True
        return False

    def slice(self, event):
        self.mouse_path.append((event.x, event.y))

    def end_slice(self, event):
        self.mouse_path = []

    def restart(self, event):
        self.fruits = []
        self.bombs = []
        self.score = 0
        self.game_over = False
        self.mouse_path = []
        self.spawn_timer = 0

    def draw(self):
        self.canvas.delete('all')
        for fruit in self.fruits:
            if not fruit['sliced']:
                self.canvas.create_text(fruit['x'], fruit['y'], text=fruit['emoji'], font=('Arial', 40))
        for bomb in self.bombs:
            if not bomb['sliced']:
                self.canvas.create_text(bomb['x'], bomb['y'], text=bomb['emoji'], font=('Arial', 40))
        self.canvas.create_text(400, 50, text=f'Score: {self.score}', fill='white', font=('Arial', 24))
        if self.game_over:
            self.canvas.create_text(400, 300, text='GAME OVER', fill='white', font=('Arial', 48))
            self.canvas.create_text(400, 350, text='Press R to restart', fill='white', font=('Arial', 24))

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Fruit Ninja')
    game = FruitNinja(root)
    root.mainloop()
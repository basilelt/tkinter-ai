import tkinter as tk
import random

# Constants
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 500
BIRD_SIZE = 20
PIPE_WIDTH = 50
PIPE_GAP = 150
GRAVITY = 1
FLAP_STRENGTH = -10
PIPE_SPEED = 5
GROUND_Y = CANVAS_HEIGHT - 10
CEILING_Y = 10
BIRD_START_X = 100
BIRD_START_Y = CANVAS_HEIGHT // 2
PIPE_START_X = CANVAS_WIDTH
PIPE_MIN_HEIGHT = 50
PIPE_MAX_HEIGHT = CANVAS_HEIGHT - PIPE_GAP - PIPE_MIN_HEIGHT
UPDATE_INTERVAL = 50

class Bird:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.velocity = 0
        self.id = canvas.create_oval(self.x - BIRD_SIZE//2, self.y - BIRD_SIZE//2,
                                     self.x + BIRD_SIZE//2, self.y + BIRD_SIZE//2, fill='yellow')

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.canvas.coords(self.id, self.x - BIRD_SIZE//2, self.y - BIRD_SIZE//2,
                           self.x + BIRD_SIZE//2, self.y + BIRD_SIZE//2)

class Pipe:
    def __init__(self, canvas, x, height):
        self.canvas = canvas
        self.x = x
        self.height = height
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.passed = False
        self.top_id = canvas.create_rectangle(self.x, 0, self.x + self.width, self.height, fill='green')
        self.bottom_id = canvas.create_rectangle(self.x, self.height + self.gap,
                                                 self.x + self.width, CANVAS_HEIGHT, fill='green')

    def update(self):
        self.x -= PIPE_SPEED
        self.canvas.coords(self.top_id, self.x, 0, self.x + self.width, self.height)
        self.canvas.coords(self.bottom_id, self.x, self.height + self.gap,
                           self.x + self.width, CANVAS_HEIGHT)

class FlappyBird:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flappy Bird")
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='skyblue')
        self.canvas.pack()
        self.bird = Bird(self.canvas)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.canvas.bind('<Button-1>', lambda e: self.flap())
        self.root.bind('<space>', lambda e: self.flap())
        self.create_pipe()
        self.update()
        self.root.mainloop()

    def flap(self):
        if not self.game_over:
            self.bird.flap()

    def create_pipe(self):
        height = random.randint(PIPE_MIN_HEIGHT, PIPE_MAX_HEIGHT)
        self.pipes.append(Pipe(self.canvas, PIPE_START_X, height))

    def update(self):
        if not self.game_over:
            self.bird.update()
            # Update pipes and check for scoring
            for pipe in self.pipes:
                pipe.update()
                if not pipe.passed and self.bird.x > pipe.x + pipe.width:
                    pipe.passed = True
                    self.score += 1
            # Remove off-screen pipes
            self.pipes = [p for p in self.pipes if p.x + p.width >= 0]
            # Create new pipe if needed
            if len(self.pipes) == 0 or self.pipes[-1].x < CANVAS_WIDTH - 200:
                self.create_pipe()
            self.check_collision()
        self.canvas.delete('score')
        self.canvas.create_text(CANVAS_WIDTH // 2, 20, text=f'Score: {self.score}', tag='score')
        self.root.after(UPDATE_INTERVAL, self.update)

    def check_collision(self):
        # Bird with ground/ceiling
        if self.bird.y > GROUND_Y or self.bird.y < CEILING_Y:
            self.game_over = True
        # Bird with pipes
        for pipe in self.pipes:
            if (self.bird.x + BIRD_SIZE//2 > pipe.x and
                self.bird.x - BIRD_SIZE//2 < pipe.x + pipe.width):
                if (self.bird.y - BIRD_SIZE//2 < pipe.height or
                    self.bird.y + BIRD_SIZE//2 > pipe.height + pipe.gap):
                    self.game_over = True
        if self.game_over:
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                    text='Game Over\nClick to restart', font=('Arial', 20), tag='game_over')
            self.canvas.bind('<Button-1>', lambda e: self.restart())

    def restart(self):
        self.canvas.delete('all')
        self.bird = Bird(self.canvas)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.create_pipe()
        self.canvas.bind('<Button-1>', lambda e: self.flap())

if __name__ == '__main__':
    FlappyBird()
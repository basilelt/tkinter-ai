import math
import time
import json
import random

WIDTH = 800
HEIGHT = 600

def generate_random_path():
    path = [(50, random.randint(200, 400))]
    num_points = random.randint(5, 8)
    for i in range(1, num_points):
        x = 50 + (WIDTH - 100) * i // num_points
        y = random.randint(100, HEIGHT - 100)
        path.append((x, y))
    path.append((WIDTH - 50, random.randint(200, 400)))
    return path

PATH = generate_random_path()

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
    def __init__(self, bloon_type, path, id):
        self.id = id
        self.bloon_type = bloon_type
        self.health = BLOON_TYPES[bloon_type]['health']
        self.speed = BLOON_TYPES[bloon_type]['speed']
        self.color = BLOON_TYPES[bloon_type]['color']
        self.path = path
        self.path_index = 0
        self.x, self.y = self.path[0]
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

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.bloon_type,
            'health': self.health,
            'x': self.x,
            'y': self.y,
            'alive': self.alive,
            'popped': self.popped
        }

class Tower:
    def __init__(self, tower_type, x, y, id):
        self.id = id
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

    def fire(self, current_time):
        self.last_fired = current_time
        # Return projectile info
        return {'x': self.x, 'y': self.y, 'damage': self.damage, 'projectiles': self.projectiles}

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.tower_type,
            'x': self.x,
            'y': self.y
        }

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, damage, speed=5):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.speed = speed
        self.alive = True

    def move(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.alive = False

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'alive': self.alive
        }

class GameState:
    def __init__(self):
        self.path = generate_random_path()
        self.bloons = {}
        self.towers = {}
        self.projectiles = {}
        self.health = 100
        self.money = 650
        self.wave = 1
        self.wave_in_progress = False
        self.bloon_id_counter = 0
        self.tower_id_counter = 0
        self.projectile_id_counter = 0
        self.last_update = time.time()

    def add_bloon(self, bloon_type):
        self.bloon_id_counter += 1
        bloon = Bloon(bloon_type, self.path, self.bloon_id_counter)
        self.bloons[self.bloon_id_counter] = bloon
        return bloon

    def add_tower(self, tower_type, x, y):
        cost = TOWER_TYPES[tower_type]['cost']
        if self.money >= cost:
            self.money -= cost
            self.tower_id_counter += 1
            tower = Tower(tower_type, x, y, self.tower_id_counter)
            self.towers[self.tower_id_counter] = tower
            return tower
        return None

    def update(self):
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Move bloons
        escaped = []
        for bloon in list(self.bloons.values()):
            if bloon.move():
                escaped.append(bloon.id)
                self.health -= 1

        for id in escaped:
            del self.bloons[id]

        # Towers fire
        for tower in self.towers.values():
            if tower.can_fire(current_time):
                # Find target
                target = None
                min_dist = float('inf')
                for bloon in self.bloons.values():
                    dist = math.sqrt((tower.x - bloon.x)**2 + (tower.y - bloon.y)**2)
                    if dist <= tower.range and dist < min_dist:
                        min_dist = dist
                        target = bloon
                if target:
                    proj_info = tower.fire(current_time)
                    # Create projectiles
                    if tower.projectiles == 1:
                        self.projectile_id_counter += 1
                        proj = Projectile(tower.x, tower.y, target.x, target.y, proj_info['damage'])
                        self.projectiles[self.projectile_id_counter] = proj
                    else:
                        # For tack shooter, multiple projectiles in circle
                        for i in range(tower.projectiles):
                            angle = 2 * math.pi * i / tower.projectiles
                            tx = target.x + 20 * math.cos(angle)
                            ty = target.y + 20 * math.sin(angle)
                            self.projectile_id_counter += 1
                            proj = Projectile(tower.x, tower.y, tx, ty, proj_info['damage'])
                            self.projectiles[self.projectile_id_counter] = proj

        # Move projectiles and check collisions
        to_remove_proj = []
        for proj_id, proj in list(self.projectiles.items()):
            proj.move()
            if not proj.alive:
                to_remove_proj.append(proj_id)
                continue
            # Check collision with bloons
            for bloon in list(self.bloons.values()):
                dist = math.sqrt((proj.x - bloon.x)**2 + (proj.y - bloon.y)**2)
                if dist < 10:  # hit radius
                    bloon.health -= proj.damage
                    if bloon.health <= 0:
                        bloon.popped = True
                        self.money += BLOON_TYPES[bloon.bloon_type]['value']
                        del self.bloons[bloon.id]
                    to_remove_proj.append(proj_id)
                    break

        for id in to_remove_proj:
            if id in self.projectiles:
                del self.projectiles[id]

    def to_dict(self):
        return {
            'path': self.path,
            'bloons': {id: b.to_dict() for id, b in self.bloons.items()},
            'towers': {id: t.to_dict() for id, t in self.towers.items()},
            'projectiles': {id: p.to_dict() for id, p in self.projectiles.items()},
            'health': self.health,
            'money': self.money,
            'wave': self.wave,
            'wave_in_progress': self.wave_in_progress
        }

    def from_dict(self, data):
        self.path = data['path']
        self.bloons = {int(id): Bloon(b['type'], self.path, int(id)) for id, b in data['bloons'].items()}
        for id, b in self.bloons.items():
            b_data = data['bloons'][str(id)]
            b.health = b_data['health']
            b.x = b_data['x']
            b.y = b_data['y']
            b.alive = b_data['alive']
            b.popped = b_data['popped']
        self.towers = {int(id): Tower(t['type'], t['x'], t['y'], int(id)) for id, t in data['towers'].items()}
        self.projectiles = {}
        for id, p in data['projectiles'].items():
            # Note: projectiles don't have full state, recreate simply
            proj = Projectile(p['x'], p['y'], p['x'], p['y'], 1)  # dummy
            proj.alive = p['alive']
            self.projectiles[int(id)] = proj
        self.health = data['health']
        self.money = data['money']
        self.wave = data['wave']
        self.wave_in_progress = data['wave_in_progress']
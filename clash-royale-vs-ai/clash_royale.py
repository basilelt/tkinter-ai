"""
Clash Royale Clone avec Tkinter
Un jeu de stratégie en temps réel simplifié
"""

import tkinter as tk
from tkinter import font
import random
import math

# Constantes du jeu
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 600
CARD_WIDTH = 80
CARD_HEIGHT = 100
ELIXIR_MAX = 10
ELIXIR_RATE = 0.03  # Élixir par frame

# Couleurs
COLORS = {
    'grass': '#4a7c23',
    'river': '#3498db',
    'bridge': '#8b4513',
    'tower_ally': '#3498db',
    'tower_enemy': '#e74c3c',
    'elixir': '#9b59b6',
    'gold': '#f1c40f',
}

# Types de troupes
TROOPS = {
    'knight': {
        'name': 'Chevalier',
        'hp': 150,
        'damage': 20,
        'speed': 1.5,
        'range': 30,
        'cost': 3,
        'color': '#3498db',
        'size': 15,
        'attack_speed': 1.0,
        'type': 'ground'
    },
    'archer': {
        'name': 'Archère',
        'hp': 60,
        'damage': 15,
        'speed': 2,
        'range': 120,
        'cost': 3,
        'color': '#e91e63',
        'size': 12,
        'attack_speed': 1.2,
        'type': 'ground'
    },
    'giant': {
        'name': 'Géant',
        'hp': 300,
        'damage': 35,
        'speed': 0.8,
        'range': 30,
        'cost': 5,
        'color': '#ff9800',
        'size': 22,
        'attack_speed': 1.5,
        'target': 'buildings',
        'type': 'ground'
    },
    'goblin': {
        'name': 'Gobelin',
        'hp': 40,
        'damage': 12,
        'speed': 3,
        'range': 25,
        'cost': 2,
        'color': '#4caf50',
        'size': 10,
        'attack_speed': 0.8,
        'type': 'ground'
    },
    'musketeer': {
        'name': 'Mousquetaire',
        'hp': 80,
        'damage': 25,
        'speed': 1.5,
        'range': 150,
        'cost': 4,
        'color': '#9c27b0',
        'size': 14,
        'attack_speed': 1.5,
        'type': 'ground'
    },
    'minion': {
        'name': 'Gargouille',
        'hp': 45,
        'damage': 18,
        'speed': 2.5,
        'range': 40,
        'cost': 3,
        'color': '#00bcd4',
        'size': 12,
        'attack_speed': 1.0,
        'type': 'air'
    },
    'fireball': {
        'name': 'Boule de Feu',
        'damage': 100,
        'radius': 50,
        'cost': 4,
        'color': '#ff5722',
        'type': 'spell'
    },
    'arrows': {
        'name': 'Flèches',
        'damage': 50,
        'radius': 80,
        'cost': 3,
        'color': '#795548',
        'type': 'spell'
    }
}


class Tower:
    def __init__(self, x, y, team, is_king=False):
        self.x = x
        self.y = y
        self.team = team  # 'ally' ou 'enemy'
        self.is_king = is_king
        self.max_hp = 400 if is_king else 250
        self.hp = self.max_hp
        self.damage = 15 if is_king else 10
        self.range = 120
        self.attack_speed = 1.0
        self.attack_cooldown = 0
        self.size = 35 if is_king else 28
        self.alive = True
        self.target = None

    def draw(self, canvas):
        if not self.alive:
            return
        
        color = COLORS['tower_ally'] if self.team == 'ally' else COLORS['tower_enemy']
        
        # Tour principale
        canvas.create_rectangle(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=color, outline='#2c3e50', width=3
        )
        
        # Couronne pour la tour du roi
        if self.is_king:
            canvas.create_polygon(
                self.x - 20, self.y - self.size - 5,
                self.x - 10, self.y - self.size - 15,
                self.x, self.y - self.size - 5,
                self.x + 10, self.y - self.size - 15,
                self.x + 20, self.y - self.size - 5,
                fill='#f1c40f', outline='#d4ac0d'
            )
        
        # Barre de vie
        hp_ratio = self.hp / self.max_hp
        bar_width = self.size * 2
        canvas.create_rectangle(
            self.x - self.size, self.y - self.size - 12,
            self.x + self.size, self.y - self.size - 5,
            fill='#7f8c8d', outline=''
        )
        canvas.create_rectangle(
            self.x - self.size, self.y - self.size - 12,
            self.x - self.size + bar_width * hp_ratio, self.y - self.size - 5,
            fill='#2ecc71' if hp_ratio > 0.3 else '#e74c3c', outline=''
        )
        
        # HP text
        canvas.create_text(
            self.x, self.y,
            text=str(int(self.hp)),
            fill='white',
            font=('Arial', 8, 'bold')
        )

    def update(self, troops, projectiles):
        if not self.alive:
            return
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1/60
        
        # Trouver une cible
        self.target = None
        min_dist = self.range
        
        for troop in troops:
            if troop.team != self.team and troop.alive:
                dist = math.sqrt((troop.x - self.x)**2 + (troop.y - self.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    self.target = troop
        
        # Attaquer
        if self.target and self.attack_cooldown <= 0:
            projectiles.append(Projectile(
                self.x, self.y,
                self.target,
                self.damage,
                '#f1c40f',
                speed=8
            ))
            self.attack_cooldown = self.attack_speed

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False


class Troop:
    def __init__(self, x, y, troop_type, team):
        self.x = x
        self.y = y
        self.troop_type = troop_type
        self.team = team
        
        stats = TROOPS[troop_type]
        self.name = stats['name']
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.range = stats['range']
        self.cost = stats['cost']
        self.color = stats['color']
        self.size = stats['size']
        self.attack_speed = stats['attack_speed']
        self.troop_class = stats['type']
        self.target_buildings = stats.get('target') == 'buildings'
        
        self.attack_cooldown = 0
        self.target = None
        self.alive = True

    def draw(self, canvas):
        if not self.alive:
            return
        
        # Corps de la troupe
        if self.troop_class == 'air':
            # Les troupes aériennes ont des ailes
            canvas.create_oval(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                fill=self.color, outline='#2c3e50', width=2
            )
            # Ailes
            canvas.create_polygon(
                self.x - self.size - 5, self.y,
                self.x - self.size, self.y - 8,
                self.x - self.size, self.y + 8,
                fill=self.color
            )
            canvas.create_polygon(
                self.x + self.size + 5, self.y,
                self.x + self.size, self.y - 8,
                self.x + self.size, self.y + 8,
                fill=self.color
            )
        else:
            canvas.create_oval(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                fill=self.color, outline='#2c3e50', width=2
            )
        
        # Indicateur d'équipe
        team_color = '#3498db' if self.team == 'ally' else '#e74c3c'
        canvas.create_oval(
            self.x - 5, self.y - 5,
            self.x + 5, self.y + 5,
            fill=team_color, outline=''
        )
        
        # Barre de vie
        hp_ratio = self.hp / self.max_hp
        bar_width = self.size * 2
        canvas.create_rectangle(
            self.x - self.size, self.y - self.size - 8,
            self.x + self.size, self.y - self.size - 3,
            fill='#7f8c8d', outline=''
        )
        canvas.create_rectangle(
            self.x - self.size, self.y - self.size - 8,
            self.x - self.size + bar_width * hp_ratio, self.y - self.size - 3,
            fill='#2ecc71' if hp_ratio > 0.3 else '#e74c3c', outline=''
        )

    def update(self, troops, towers, projectiles):
        if not self.alive:
            return
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1/60
        
        # Trouver une cible
        self.target = None
        min_dist = float('inf')
        
        # Cibler les tours si c'est un géant ou pas d'autres cibles
        if self.target_buildings:
            for tower in towers:
                if tower.team != self.team and tower.alive:
                    dist = math.sqrt((tower.x - self.x)**2 + (tower.y - self.y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        self.target = tower
        else:
            # Cibler les troupes ennemies
            for troop in troops:
                if troop.team != self.team and troop.alive:
                    dist = math.sqrt((troop.x - self.x)**2 + (troop.y - self.y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        self.target = troop
            
            # Si pas de troupe, cibler les tours
            if not self.target:
                for tower in towers:
                    if tower.team != self.team and tower.alive:
                        dist = math.sqrt((tower.x - self.x)**2 + (tower.y - self.y)**2)
                        if dist < min_dist:
                            min_dist = dist
                            self.target = tower
        
        if self.target:
            dist = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
            
            if dist <= self.range:
                # Attaquer
                if self.attack_cooldown <= 0:
                    if self.range > 50:  # Attaque à distance
                        projectiles.append(Projectile(
                            self.x, self.y,
                            self.target,
                            self.damage,
                            self.color
                        ))
                    else:  # Attaque au corps à corps
                        self.target.take_damage(self.damage)
                    self.attack_cooldown = self.attack_speed
            else:
                # Se déplacer vers la cible
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False


class Projectile:
    def __init__(self, x, y, target, damage, color, speed=6):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.speed = speed
        self.alive = True

    def draw(self, canvas):
        if not self.alive:
            return
        canvas.create_oval(
            self.x - 4, self.y - 4,
            self.x + 4, self.y + 4,
            fill=self.color, outline='#2c3e50'
        )

    def update(self):
        if not self.alive or not self.target.alive:
            self.alive = False
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < 10:
            self.target.take_damage(self.damage)
            self.alive = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed


class SpellEffect:
    def __init__(self, x, y, spell_type):
        self.x = x
        self.y = y
        self.spell_type = spell_type
        self.stats = TROOPS[spell_type]
        self.radius = self.stats['radius']
        self.damage = self.stats['damage']
        self.color = self.stats['color']
        self.lifetime = 30  # frames
        self.alive = True

    def draw(self, canvas):
        if not self.alive:
            return
        
        alpha = self.lifetime / 30
        canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill='', outline=self.color, width=3
        )
        
        inner_radius = self.radius * (1 - alpha)
        canvas.create_oval(
            self.x - inner_radius, self.y - inner_radius,
            self.x + inner_radius, self.y + inner_radius,
            fill=self.color, outline='', stipple='gray50'
        )

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False


class Card:
    def __init__(self, troop_type, x, y):
        self.troop_type = troop_type
        self.x = x
        self.y = y
        self.stats = TROOPS[troop_type]
        self.selected = False

    def draw(self, canvas, elixir):
        can_afford = elixir >= self.stats['cost']
        
        # Fond de la carte
        bg_color = '#2c3e50' if can_afford else '#7f8c8d'
        canvas.create_rectangle(
            self.x, self.y,
            self.x + CARD_WIDTH, self.y + CARD_HEIGHT,
            fill=bg_color, outline='#f1c40f' if self.selected else '#1a252f', width=3
        )
        
        # Image de la troupe (cercle coloré)
        canvas.create_oval(
            self.x + 15, self.y + 15,
            self.x + CARD_WIDTH - 15, self.y + 55,
            fill=self.stats['color'], outline='white', width=2
        )
        
        # Nom
        canvas.create_text(
            self.x + CARD_WIDTH // 2, self.y + 70,
            text=self.stats['name'],
            fill='white',
            font=('Arial', 8, 'bold')
        )
        
        # Coût en élixir
        canvas.create_oval(
            self.x + 5, self.y + CARD_HEIGHT - 25,
            self.x + 25, self.y + CARD_HEIGHT - 5,
            fill=COLORS['elixir'], outline='white'
        )
        canvas.create_text(
            self.x + 15, self.y + CARD_HEIGHT - 15,
            text=str(self.stats['cost']),
            fill='white',
            font=('Arial', 10, 'bold')
        )

    def contains(self, x, y):
        return (self.x <= x <= self.x + CARD_WIDTH and 
                self.y <= y <= self.y + CARD_HEIGHT)


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Clash Royale - Python Edition")
        self.root.resizable(False, False)
        
        # Canvas principal
        self.canvas = tk.Canvas(
            root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT + 150,
            bg=COLORS['grass']
        )
        self.canvas.pack()
        
        # État du jeu
        self.elixir = 5
        self.enemy_elixir = 5
        self.troops = []
        self.projectiles = []
        self.spell_effects = []
        self.game_time = 180  # 3 minutes
        self.game_over = False
        self.winner = None
        
        # Tours
        self.towers = [
            # Tours alliées
            Tower(100, CANVAS_HEIGHT - 80, 'ally'),
            Tower(300, CANVAS_HEIGHT - 80, 'ally'),
            Tower(200, CANVAS_HEIGHT - 40, 'ally', is_king=True),
            # Tours ennemies
            Tower(100, 80, 'enemy'),
            Tower(300, 80, 'enemy'),
            Tower(200, 40, 'enemy', is_king=True),
        ]
        
        # Deck de cartes
        self.deck = ['knight', 'archer', 'giant', 'goblin', 'musketeer', 'minion', 'fireball', 'arrows']
        random.shuffle(self.deck)
        self.hand = self.deck[:4]
        self.next_card = self.deck[4] if len(self.deck) > 4 else self.deck[0]
        self.deck_index = 5
        
        self.cards = []
        self.update_cards()
        
        self.selected_card = None
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        
        # Bindings
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # Lancer le jeu
        self.update()

    def update_cards(self):
        self.cards = []
        start_x = (CANVAS_WIDTH - (4 * CARD_WIDTH + 3 * 10)) // 2
        for i, troop_type in enumerate(self.hand):
            self.cards.append(Card(
                troop_type,
                start_x + i * (CARD_WIDTH + 10),
                CANVAS_HEIGHT + 30
            ))

    def on_click(self, event):
        if self.game_over:
            self.restart_game()
            return
        
        # Vérifier si on clique sur une carte
        for card in self.cards:
            if card.contains(event.x, event.y):
                if self.elixir >= card.stats['cost']:
                    self.selected_card = card
                    card.selected = True
                    self.dragging = True
                    self.drag_x = event.x
                    self.drag_y = event.y
                return
        
        # Déselectionner
        if self.selected_card:
            self.selected_card.selected = False
            self.selected_card = None

    def on_drag(self, event):
        if self.dragging and self.selected_card:
            self.drag_x = event.x
            self.drag_y = event.y

    def on_release(self, event):
        if self.dragging and self.selected_card:
            # Vérifier si on place dans la zone alliée
            if event.y > CANVAS_HEIGHT // 2 and event.y < CANVAS_HEIGHT:
                self.place_troop(event.x, event.y, self.selected_card.troop_type, 'ally')
                self.elixir -= self.selected_card.stats['cost']
                
                # Remplacer la carte
                idx = self.hand.index(self.selected_card.troop_type)
                self.hand[idx] = self.next_card
                self.next_card = self.deck[self.deck_index % len(self.deck)]
                self.deck_index += 1
                self.update_cards()
            
            self.selected_card.selected = False
            self.selected_card = None
            self.dragging = False

    def place_troop(self, x, y, troop_type, team):
        stats = TROOPS[troop_type]
        
        if stats['type'] == 'spell':
            # Effet de sort
            self.spell_effects.append(SpellEffect(x, y, troop_type))
            # Appliquer les dégâts
            for troop in self.troops:
                if troop.team != team:
                    dist = math.sqrt((troop.x - x)**2 + (troop.y - y)**2)
                    if dist <= stats['radius']:
                        troop.take_damage(stats['damage'])
            for tower in self.towers:
                if tower.team != team:
                    dist = math.sqrt((tower.x - x)**2 + (tower.y - y)**2)
                    if dist <= stats['radius']:
                        tower.take_damage(stats['damage'])
        else:
            # Créer la troupe
            self.troops.append(Troop(x, y, troop_type, team))

    def enemy_ai(self):
        """IA simple pour l'ennemi"""
        if self.enemy_elixir >= 4:
            # Choisir une carte aléatoire
            available = [t for t, s in TROOPS.items() if s.get('type') != 'spell' and s['cost'] <= self.enemy_elixir]
            if available:
                troop_type = random.choice(available)
                x = random.randint(100, 300)
                y = random.randint(50, 150)
                self.place_troop(x, y, troop_type, 'enemy')
                self.enemy_elixir -= TROOPS[troop_type]['cost']

    def check_game_over(self):
        ally_king = self.towers[2]
        enemy_king = self.towers[5]
        
        if not ally_king.alive:
            self.game_over = True
            self.winner = 'enemy'
        elif not enemy_king.alive:
            self.game_over = True
            self.winner = 'ally'
        elif self.game_time <= 0:
            # Comparer les tours détruites
            ally_destroyed = sum(1 for t in self.towers[:3] if not t.alive)
            enemy_destroyed = sum(1 for t in self.towers[3:] if not t.alive)
            
            if enemy_destroyed > ally_destroyed:
                self.winner = 'ally'
            elif ally_destroyed > enemy_destroyed:
                self.winner = 'enemy'
            else:
                # Comparer les HP
                ally_hp = sum(t.hp for t in self.towers[:3])
                enemy_hp = sum(t.hp for t in self.towers[3:])
                self.winner = 'ally' if ally_hp > enemy_hp else 'enemy'
            
            self.game_over = True

    def restart_game(self):
        self.elixir = 5
        self.enemy_elixir = 5
        self.troops = []
        self.projectiles = []
        self.spell_effects = []
        self.game_time = 180
        self.game_over = False
        self.winner = None
        
        self.towers = [
            Tower(100, CANVAS_HEIGHT - 80, 'ally'),
            Tower(300, CANVAS_HEIGHT - 80, 'ally'),
            Tower(200, CANVAS_HEIGHT - 40, 'ally', is_king=True),
            Tower(100, 80, 'enemy'),
            Tower(300, 80, 'enemy'),
            Tower(200, 40, 'enemy', is_king=True),
        ]
        
        random.shuffle(self.deck)
        self.hand = self.deck[:4]
        self.next_card = self.deck[4]
        self.deck_index = 5
        self.update_cards()

    def draw(self):
        self.canvas.delete('all')
        
        # Fond du terrain
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=COLORS['grass'])
        
        # Rivière
        self.canvas.create_rectangle(
            0, CANVAS_HEIGHT // 2 - 20,
            CANVAS_WIDTH, CANVAS_HEIGHT // 2 + 20,
            fill=COLORS['river'], outline=''
        )
        
        # Ponts
        for x in [100, 300]:
            self.canvas.create_rectangle(
                x - 30, CANVAS_HEIGHT // 2 - 25,
                x + 30, CANVAS_HEIGHT // 2 + 25,
                fill=COLORS['bridge'], outline='#5d3a1a', width=2
            )
        
        # Ligne médiane
        self.canvas.create_line(
            0, CANVAS_HEIGHT // 2,
            CANVAS_WIDTH, CANVAS_HEIGHT // 2,
            fill='#ffffff', dash=(5, 5), width=2
        )
        
        # Tours
        for tower in self.towers:
            tower.draw(self.canvas)
        
        # Troupes
        for troop in self.troops:
            troop.draw(self.canvas)
        
        # Projectiles
        for proj in self.projectiles:
            proj.draw(self.canvas)
        
        # Effets de sorts
        for effect in self.spell_effects:
            effect.draw(self.canvas)
        
        # Zone de prévisualisation lors du drag
        if self.dragging and self.selected_card:
            stats = self.selected_card.stats
            if stats['type'] == 'spell':
                self.canvas.create_oval(
                    self.drag_x - stats['radius'], self.drag_y - stats['radius'],
                    self.drag_x + stats['radius'], self.drag_y + stats['radius'],
                    fill='', outline=stats['color'], width=2, dash=(5, 5)
                )
            else:
                self.canvas.create_oval(
                    self.drag_x - 20, self.drag_y - 20,
                    self.drag_x + 20, self.drag_y + 20,
                    fill=stats['color'], outline='white', width=2, stipple='gray50'
                )
        
        # Interface
        self.draw_ui()
        
        # Écran de fin
        if self.game_over:
            self.draw_game_over()

    def draw_ui(self):
        # Fond de l'interface
        self.canvas.create_rectangle(
            0, CANVAS_HEIGHT,
            CANVAS_WIDTH, CANVAS_HEIGHT + 150,
            fill='#1a252f', outline=''
        )
        
        # Timer
        minutes = int(self.game_time) // 60
        seconds = int(self.game_time) % 60
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT + 15,
            text=f"{minutes}:{seconds:02d}",
            fill='white',
            font=('Arial', 14, 'bold')
        )
        
        # Barre d'élixir
        elixir_bar_width = CANVAS_WIDTH - 40
        self.canvas.create_rectangle(
            20, CANVAS_HEIGHT + 130,
            CANVAS_WIDTH - 20, CANVAS_HEIGHT + 145,
            fill='#2c3e50', outline='white'
        )
        self.canvas.create_rectangle(
            20, CANVAS_HEIGHT + 130,
            20 + (elixir_bar_width * self.elixir / ELIXIR_MAX), CANVAS_HEIGHT + 145,
            fill=COLORS['elixir'], outline=''
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT + 137,
            text=f"{int(self.elixir)}/{ELIXIR_MAX}",
            fill='white',
            font=('Arial', 10, 'bold')
        )
        
        # Cartes
        for card in self.cards:
            card.draw(self.canvas, self.elixir)
        
        # Prochaine carte
        self.canvas.create_text(
            CANVAS_WIDTH - 45, CANVAS_HEIGHT + 60,
            text="Next:",
            fill='white',
            font=('Arial', 8)
        )
        self.canvas.create_oval(
            CANVAS_WIDTH - 60, CANVAS_HEIGHT + 70,
            CANVAS_WIDTH - 30, CANVAS_HEIGHT + 100,
            fill=TROOPS[self.next_card]['color'],
            outline='white'
        )

    def draw_game_over(self):
        # Overlay sombre
        self.canvas.create_rectangle(
            0, 0, CANVAS_WIDTH, CANVAS_HEIGHT + 150,
            fill='black', stipple='gray50'
        )
        
        # Message
        if self.winner == 'ally':
            text = "VICTOIRE!"
            color = '#2ecc71'
        else:
            text = "DÉFAITE!"
            color = '#e74c3c'
        
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 20,
            text=text,
            fill=color,
            font=('Arial', 36, 'bold')
        )
        
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 30,
            text="Cliquez pour rejouer",
            fill='white',
            font=('Arial', 14)
        )

    def update(self):
        if not self.game_over:
            # Mettre à jour le timer
            self.game_time -= 1/60
            
            # Régénérer l'élixir
            self.elixir = min(ELIXIR_MAX, self.elixir + ELIXIR_RATE)
            self.enemy_elixir = min(ELIXIR_MAX, self.enemy_elixir + ELIXIR_RATE)
            
            # IA ennemie
            if random.random() < 0.02:  # ~2% de chance par frame
                self.enemy_ai()
            
            # Mettre à jour les tours
            for tower in self.towers:
                tower.update(self.troops, self.projectiles)
            
            # Mettre à jour les troupes
            for troop in self.troops:
                troop.update(self.troops, self.towers, self.projectiles)
            
            # Mettre à jour les projectiles
            for proj in self.projectiles:
                proj.update()
            
            # Mettre à jour les effets
            for effect in self.spell_effects:
                effect.update()
            
            # Nettoyer les objets morts
            self.troops = [t for t in self.troops if t.alive]
            self.projectiles = [p for p in self.projectiles if p.alive]
            self.spell_effects = [e for e in self.spell_effects if e.alive]
            
            # Vérifier la fin du jeu
            self.check_game_over()
        
        # Dessiner
        self.draw()
        
        # Boucle de jeu
        self.root.after(16, self.update)  # ~60 FPS


def main():
    root = tk.Tk()
    game = Game(root)
    root.mainloop()


if __name__ == '__main__':
    main()

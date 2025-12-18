import tkinter as tk
from tkinter import messagebox
import random
import time
import copy

# Configuration des unités par âge
AGES = {
    1: {
        'name': 'Stone Age',
        'units': [
            {'name': 'Clubman', 'cost': 15, 'hp': 50, 'damage': 10, 'range': 1, 'speed': 2},
            {'name': 'Slinger', 'cost': 30, 'hp': 40, 'damage': 8, 'range': 4, 'speed': 1.5},
            {'name': 'Dino Rider', 'cost': 100, 'hp': 200, 'damage': 30, 'range': 1, 'speed': 1}
        ],
        'cost': 0,
        'turret_hp': 200,
        'turret_damage': 5
    },
    2: {
        'name': 'Castle Age',
        'units': [
            {'name': 'Swordsman', 'cost': 25, 'hp': 80, 'damage': 15, 'range': 1, 'speed': 2},
            {'name': 'Archer', 'cost': 40, 'hp': 60, 'damage': 12, 'range': 5, 'speed': 1.5},
            {'name': 'Knight', 'cost': 150, 'hp': 300, 'damage': 40, 'range': 1, 'speed': 1}
        ],
        'cost': 500,
        'turret_hp': 350,
        'turret_damage': 8
    },
    3: {
        'name': 'Renaissance',
        'units': [
            {'name': 'Pikeman', 'cost': 35, 'hp': 100, 'damage': 20, 'range': 2, 'speed': 2},
            {'name': 'Musketeer', 'cost': 50, 'hp': 80, 'damage': 18, 'range': 6, 'speed': 1.5},
            {'name': 'Cannon', 'cost': 200, 'hp': 400, 'damage': 50, 'range': 7, 'speed': 0.8}
        ],
        'cost': 1500,
        'turret_hp': 500,
        'turret_damage': 12
    },
    4: {
        'name': 'Modern Age',
        'units': [
            {'name': 'Soldier', 'cost': 50, 'hp': 120, 'damage': 25, 'range': 1, 'speed': 2.5},
            {'name': 'Sniper', 'cost': 70, 'hp': 100, 'damage': 30, 'range': 8, 'speed': 1.5},
            {'name': 'Tank', 'cost': 300, 'hp': 600, 'damage': 70, 'range': 6, 'speed': 1}
        ],
        'cost': 3000,
        'turret_hp': 700,
        'turret_damage': 15
    },
    5: {
        'name': 'Future Age',
        'units': [
            {'name': 'Mech', 'cost': 80, 'hp': 150, 'damage': 35, 'range': 2, 'speed': 2.5},
            {'name': 'Laser', 'cost': 100, 'hp': 120, 'damage': 40, 'range': 9, 'speed': 1.5},
            {'name': 'Robot', 'cost': 500, 'hp': 1000, 'damage': 100, 'range': 5, 'speed': 1.2}
        ],
        'cost': 5000,
        'turret_hp': 1000,
        'turret_damage': 20
    }
}

class Unit:
    """Classe représentant une unité"""
    def __init__(self, unit_data, player, x, y):
        self.name = unit_data['name']
        self.max_hp = unit_data['hp']
        self.hp = unit_data['hp']
        self.damage = unit_data['damage']
        self.range = unit_data['range']
        self.speed = unit_data['speed']
        self.player = player  # 1 ou 2
        self.x = x
        self.y = y
        self.target = None
        self.attack_cooldown = 0
        self.alive = True
        
    def move(self, game_width):
        """Déplacer l'unité vers l'ennemi"""
        if self.player == 1:
            self.x += self.speed
            if self.x > game_width:
                self.alive = False
        else:
            self.x -= self.speed
            if self.x < 0:
                self.alive = False
    
    def can_attack(self, target):
        """Vérifier si l'unité peut attaquer la cible"""
        distance = abs(self.x - target.x)
        return distance <= self.range * 20  # 20 pixels = 1 unité de portée
    
    def attack(self, target):
        """Attaquer une cible"""
        if self.attack_cooldown <= 0:
            target.hp -= self.damage
            self.attack_cooldown = 30  # 30 frames entre chaque attaque
            if target.hp <= 0:
                target.alive = False
            return True
        return False
    
    def update(self):
        """Mettre à jour l'unité"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

class Turret:
    """Classe représentant une tourelle (base)"""
    def __init__(self, player, x, y, hp, damage):
        self.player = player
        self.x = x
        self.y = y
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.range = 150
        self.attack_cooldown = 0
        self.alive = True
    
    def can_attack(self, target):
        """Vérifier si la tourelle peut attaquer"""
        distance = abs(self.x - target.x)
        return distance <= self.range
    
    def attack(self, target):
        """Attaquer une cible"""
        if self.attack_cooldown <= 0:
            target.hp -= self.damage
            self.attack_cooldown = 20
            if target.hp <= 0:
                target.alive = False
            return True
        return False
    
    def update(self):
        """Mettre à jour la tourelle"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

class GameState:
    """Classe représentant l'état du jeu pour l'IA"""
    def __init__(self):
        self.player1_gold = 100
        self.player2_gold = 100
        self.player1_xp = 0
        self.player2_xp = 0
        self.player1_age = 1
        self.player2_age = 1
        self.player1_units = []
        self.player2_units = []
        self.player1_turret = None
        self.player2_turret = None
        
    def copy(self):
        """Créer une copie de l'état"""
        new_state = GameState()
        new_state.player1_gold = self.player1_gold
        new_state.player2_gold = self.player2_gold
        new_state.player1_xp = self.player1_xp
        new_state.player2_xp = self.player2_xp
        new_state.player1_age = self.player1_age
        new_state.player2_age = self.player2_age
        new_state.player1_turret = copy.deepcopy(self.player1_turret)
        new_state.player2_turret = copy.deepcopy(self.player2_turret)
        new_state.player1_units = [copy.deepcopy(u) for u in self.player1_units]
        new_state.player2_units = [copy.deepcopy(u) for u in self.player2_units]
        return new_state
    
    def evaluate(self):
        """Évaluer l'état du jeu pour l'IA (du point de vue du joueur 2)"""
        score = 0
        
        # Évaluation des tourelles
        if self.player2_turret and self.player2_turret.alive:
            score += self.player2_turret.hp * 2
        if self.player1_turret and self.player1_turret.alive:
            score -= self.player1_turret.hp * 2
        
        # Évaluation des unités
        for unit in self.player2_units:
            if unit.alive:
                score += unit.hp + unit.damage * 2
        
        for unit in self.player1_units:
            if unit.alive:
                score -= unit.hp + unit.damage * 2
        
        # Évaluation de l'or et de l'âge
        score += self.player2_gold * 0.5
        score -= self.player1_gold * 0.5
        score += (self.player2_age - self.player1_age) * 200
        
        # Position des unités (bonus si près de la base ennemie)
        for unit in self.player2_units:
            if unit.alive:
                score += (800 - unit.x) * 0.1  # Plus près de la base ennemie = mieux
        
        for unit in self.player1_units:
            if unit.alive:
                score -= unit.x * 0.1
        
        return score

class AgeOfWarAI:
    """IA avec élagage Alpha-Beta"""
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
    
    def get_possible_actions(self, state, player):
        """Obtenir toutes les actions possibles pour un joueur"""
        actions = []
        
        gold = state.player2_gold if player == 2 else state.player1_gold
        age = state.player2_age if player == 2 else state.player1_age
        
        # Actions: acheter des unités
        for i, unit_data in enumerate(AGES[age]['units']):
            if gold >= unit_data['cost']:
                actions.append(('buy_unit', i))
        
        # Action: évoluer vers l'âge suivant
        if age < 5 and gold >= AGES[age + 1]['cost']:
            actions.append(('upgrade_age', None))
        
        # Action: ne rien faire (attendre)
        actions.append(('wait', None))
        
        return actions
    
    def apply_action(self, state, action, player):
        """Appliquer une action à l'état (simulation)"""
        new_state = state.copy()
        action_type, action_param = action
        
        if player == 2:
            if action_type == 'buy_unit':
                unit_data = AGES[new_state.player2_age]['units'][action_param]
                new_state.player2_gold -= unit_data['cost']
                # Simuler l'ajout d'une unité
                new_unit = Unit(unit_data, 2, 750, 250)
                new_state.player2_units.append(new_unit)
            elif action_type == 'upgrade_age':
                new_state.player2_gold -= AGES[new_state.player2_age + 1]['cost']
                new_state.player2_age += 1
                # Améliorer la tourelle
                new_state.player2_turret.max_hp = AGES[new_state.player2_age]['turret_hp']
                new_state.player2_turret.hp = AGES[new_state.player2_age]['turret_hp']
                new_state.player2_turret.damage = AGES[new_state.player2_age]['turret_damage']
        else:
            if action_type == 'buy_unit':
                unit_data = AGES[new_state.player1_age]['units'][action_param]
                new_state.player1_gold -= unit_data['cost']
                new_unit = Unit(unit_data, 1, 50, 250)
                new_state.player1_units.append(new_unit)
            elif action_type == 'upgrade_age':
                new_state.player1_gold -= AGES[new_state.player1_age + 1]['cost']
                new_state.player1_age += 1
                new_state.player1_turret.max_hp = AGES[new_state.player1_age]['turret_hp']
                new_state.player1_turret.hp = AGES[new_state.player1_age]['turret_hp']
                new_state.player1_turret.damage = AGES[new_state.player1_age]['turret_damage']
        
        return new_state
    
    def alpha_beta(self, state, depth, alpha, beta, maximizing_player):
        """Algorithme Alpha-Beta"""
        self.nodes_evaluated += 1
        
        # Conditions de terminaison
        if depth == 0 or not state.player1_turret.alive or not state.player2_turret.alive:
            return state.evaluate(), None
        
        player = 2 if maximizing_player else 1
        actions = self.get_possible_actions(state, player)
        
        if maximizing_player:
            max_eval = float('-inf')
            best_action = None
            
            for action in actions:
                new_state = self.apply_action(state, action, player)
                eval_score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = action
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Élagage Beta
            
            return max_eval, best_action
        else:
            min_eval = float('inf')
            best_action = None
            
            for action in actions:
                new_state = self.apply_action(state, action, player)
                eval_score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_action = action
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Élagage Alpha
            
            return min_eval, best_action
    
    def get_best_action(self, state):
        """Obtenir la meilleure action"""
        self.nodes_evaluated = 0
        _, best_action = self.alpha_beta(state, self.max_depth, float('-inf'), float('inf'), True)
        return best_action

class AgeOfWar:
    def __init__(self, root):
        self.root = root
        self.root.title("Age of War")
        self.root.resizable(False, False)
        
        # Dimensions du jeu
        self.width = 800
        self.height = 500
        
        # Canvas principal
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#87CEEB")
        self.canvas.pack()
        
        # Frame pour les contrôles
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()
        
        # Variables du jeu
        self.game_started = False
        self.game_over = False
        self.player1_gold = 100
        self.player2_gold = 100
        self.player1_xp = 0
        self.player2_xp = 0
        self.player1_age = 1
        self.player2_age = 1
        self.gold_per_second = 2
        self.gold_timer = 0
        
        # Unités
        self.player1_units = []
        self.player2_units = []
        
        # Tourelles
        self.player1_turret = Turret(1, 50, 250, AGES[1]['turret_hp'], AGES[1]['turret_damage'])
        self.player2_turret = Turret(2, 750, 250, AGES[1]['turret_hp'], AGES[1]['turret_damage'])
        
        # IA
        self.ai = AgeOfWarAI(max_depth=3)
        self.ai_timer = 0
        self.ai_delay = 60  # L'IA agit toutes les 60 frames
        
        # Interface
        self.create_ui()
        self.draw_game()
        
        # Démarrer le jeu
        self.game_started = True
        self.update()
    
    def create_ui(self):
        """Créer l'interface utilisateur"""
        # Informations joueur 1
        self.p1_info_frame = tk.Frame(self.control_frame)
        self.p1_info_frame.grid(row=0, column=0, padx=10)
        
        self.p1_gold_label = tk.Label(self.p1_info_frame, text=f"Or: {self.player1_gold}", 
                                      font=("Arial", 12, "bold"), fg="gold")
        self.p1_gold_label.pack()
        
        self.p1_age_label = tk.Label(self.p1_info_frame, 
                                     text=f"Âge: {AGES[self.player1_age]['name']}", 
                                     font=("Arial", 10))
        self.p1_age_label.pack()
        
        self.p1_turret_label = tk.Label(self.p1_info_frame, 
                                        text=f"Base: {self.player1_turret.hp}/{self.player1_turret.max_hp}", 
                                        font=("Arial", 10))
        self.p1_turret_label.pack()
        
        # Boutons d'unités pour le joueur 1
        self.unit_buttons = []
        for i, unit_data in enumerate(AGES[self.player1_age]['units']):
            btn = tk.Button(self.p1_info_frame, 
                           text=f"{unit_data['name']}\n{unit_data['cost']} or",
                           command=lambda idx=i: self.buy_unit(1, idx),
                           width=12, height=2)
            btn.pack(side=tk.LEFT, padx=2)
            self.unit_buttons.append(btn)
        
        # Bouton d'évolution d'âge
        self.upgrade_button = tk.Button(self.p1_info_frame, 
                                       text="Évoluer\n(500 or)",
                                       command=self.upgrade_age_player1,
                                       width=12, height=2, bg="lightblue")
        self.upgrade_button.pack(side=tk.LEFT, padx=2)
        
        # Informations IA (joueur 2)
        self.p2_info_frame = tk.Frame(self.control_frame)
        self.p2_info_frame.grid(row=0, column=1, padx=10)
        
        self.p2_gold_label = tk.Label(self.p2_info_frame, text=f"Or IA: {self.player2_gold}", 
                                      font=("Arial", 12, "bold"), fg="red")
        self.p2_gold_label.pack()
        
        self.p2_age_label = tk.Label(self.p2_info_frame, 
                                     text=f"Âge IA: {AGES[self.player2_age]['name']}", 
                                     font=("Arial", 10))
        self.p2_age_label.pack()
        
        self.p2_turret_label = tk.Label(self.p2_info_frame, 
                                        text=f"Base IA: {self.player2_turret.hp}/{self.player2_turret.max_hp}", 
                                        font=("Arial", 10))
        self.p2_turret_label.pack()
        
        self.ai_info_label = tk.Label(self.p2_info_frame, 
                                      text="IA: Alpha-Beta (prof. 3)", 
                                      font=("Arial", 9), fg="blue")
        self.ai_info_label.pack()
    
    def draw_game(self):
        """Dessiner le terrain de jeu"""
        # Dessiner le sol
        self.canvas.create_rectangle(0, 300, self.width, self.height, fill="#8B4513", outline="")
        
        # Dessiner les bases
        self.draw_turret(self.player1_turret, "blue")
        self.draw_turret(self.player2_turret, "red")
    
    def draw_turret(self, turret, color):
        """Dessiner une tourelle"""
        # Base
        self.canvas.create_rectangle(
            turret.x - 30, turret.y - 50,
            turret.x + 30, turret.y + 50,
            fill=color, outline="black", width=2
        )
        # Canon
        if turret.player == 1:
            self.canvas.create_rectangle(
                turret.x + 20, turret.y - 10,
                turret.x + 50, turret.y + 10,
                fill=color, outline="black", width=2
            )
        else:
            self.canvas.create_rectangle(
                turret.x - 50, turret.y - 10,
                turret.x - 20, turret.y + 10,
                fill=color, outline="black", width=2
            )
        
        # Barre de vie
        hp_percent = turret.hp / turret.max_hp
        self.canvas.create_rectangle(
            turret.x - 30, turret.y - 60,
            turret.x + 30, turret.y - 55,
            fill="red", outline="black"
        )
        self.canvas.create_rectangle(
            turret.x - 30, turret.y - 60,
            turret.x - 30 + (60 * hp_percent), turret.y - 55,
            fill="green", outline=""
        )
    
    def draw_unit(self, unit):
        """Dessiner une unité"""
        color = "blue" if unit.player == 1 else "red"
        size = 15
        
        # Corps de l'unité
        self.canvas.create_rectangle(
            unit.x - size, unit.y - size,
            unit.x + size, unit.y + size,
            fill=color, outline="black", width=2
        )
        
        # Barre de vie
        hp_percent = unit.hp / unit.max_hp
        bar_width = 30
        self.canvas.create_rectangle(
            unit.x - bar_width//2, unit.y - size - 8,
            unit.x + bar_width//2, unit.y - size - 3,
            fill="red", outline="black"
        )
        self.canvas.create_rectangle(
            unit.x - bar_width//2, unit.y - size - 8,
            unit.x - bar_width//2 + (bar_width * hp_percent), unit.y - size - 3,
            fill="green", outline=""
        )
    
    def buy_unit(self, player, unit_index):
        """Acheter une unité"""
        if player == 1:
            age = self.player1_age
            unit_data = AGES[age]['units'][unit_index]
            
            if self.player1_gold >= unit_data['cost']:
                self.player1_gold -= unit_data['cost']
                unit = Unit(unit_data, 1, 80, 250)
                self.player1_units.append(unit)
                self.update_ui()
        else:
            age = self.player2_age
            unit_data = AGES[age]['units'][unit_index]
            
            if self.player2_gold >= unit_data['cost']:
                self.player2_gold -= unit_data['cost']
                unit = Unit(unit_data, 2, 720, 250)
                self.player2_units.append(unit)
                self.update_ui()
    
    def upgrade_age_player1(self):
        """Améliorer l'âge du joueur 1"""
        if self.player1_age < 5:
            cost = AGES[self.player1_age + 1]['cost']
            if self.player1_gold >= cost:
                self.player1_gold -= cost
                self.player1_age += 1
                
                # Améliorer la tourelle
                self.player1_turret.max_hp = AGES[self.player1_age]['turret_hp']
                self.player1_turret.hp = AGES[self.player1_age]['turret_hp']
                self.player1_turret.damage = AGES[self.player1_age]['turret_damage']
                
                # Mettre à jour l'interface
                self.update_unit_buttons()
                self.update_ui()
    
    def upgrade_age_player2(self):
        """Améliorer l'âge du joueur 2 (IA)"""
        if self.player2_age < 5:
            cost = AGES[self.player2_age + 1]['cost']
            if self.player2_gold >= cost:
                self.player2_gold -= cost
                self.player2_age += 1
                
                # Améliorer la tourelle
                self.player2_turret.max_hp = AGES[self.player2_age]['turret_hp']
                self.player2_turret.hp = AGES[self.player2_age]['turret_hp']
                self.player2_turret.damage = AGES[self.player2_age]['turret_damage']
                
                self.update_ui()
    
    def update_unit_buttons(self):
        """Mettre à jour les boutons d'unités"""
        for btn in self.unit_buttons:
            btn.destroy()
        
        self.unit_buttons = []
        for i, unit_data in enumerate(AGES[self.player1_age]['units']):
            btn = tk.Button(self.p1_info_frame, 
                           text=f"{unit_data['name']}\n{unit_data['cost']} or",
                           command=lambda idx=i: self.buy_unit(1, idx),
                           width=12, height=2)
            btn.pack(side=tk.LEFT, padx=2)
            self.unit_buttons.append(btn)
        
        # Mettre à jour le bouton d'évolution
        if self.player1_age < 5:
            cost = AGES[self.player1_age + 1]['cost']
            self.upgrade_button.config(text=f"Évoluer\n({cost} or)")
        else:
            self.upgrade_button.config(text="Max Âge", state=tk.DISABLED)
    
    def update_ui(self):
        """Mettre à jour l'interface"""
        self.p1_gold_label.config(text=f"Or: {self.player1_gold}")
        self.p1_age_label.config(text=f"Âge: {AGES[self.player1_age]['name']}")
        self.p1_turret_label.config(text=f"Base: {self.player1_turret.hp}/{self.player1_turret.max_hp}")
        
        self.p2_gold_label.config(text=f"Or IA: {self.player2_gold}")
        self.p2_age_label.config(text=f"Âge IA: {AGES[self.player2_age]['name']}")
        self.p2_turret_label.config(text=f"Base IA: {self.player2_turret.hp}/{self.player2_turret.max_hp}")
    
    def ai_make_decision(self):
        """L'IA prend une décision avec Alpha-Beta"""
        # Créer l'état actuel du jeu
        state = GameState()
        state.player1_gold = self.player1_gold
        state.player2_gold = self.player2_gold
        state.player1_xp = self.player1_xp
        state.player2_xp = self.player2_xp
        state.player1_age = self.player1_age
        state.player2_age = self.player2_age
        state.player1_units = self.player1_units
        state.player2_units = self.player2_units
        state.player1_turret = self.player1_turret
        state.player2_turret = self.player2_turret
        
        # Obtenir la meilleure action
        best_action = self.ai.get_best_action(state)
        
        if best_action:
            action_type, action_param = best_action
            
            if action_type == 'buy_unit':
                self.buy_unit(2, action_param)
            elif action_type == 'upgrade_age':
                self.upgrade_age_player2()
    
    def update(self):
        """Mettre à jour le jeu"""
        if self.game_started and not self.game_over:
            # Générer de l'or
            self.gold_timer += 1
            if self.gold_timer >= 30:  # Toutes les 0.6 secondes
                self.player1_gold += self.gold_per_second
                self.player2_gold += self.gold_per_second
                self.gold_timer = 0
                self.update_ui()
            
            # IA prend une décision
            self.ai_timer += 1
            if self.ai_timer >= self.ai_delay:
                self.ai_make_decision()
                self.ai_timer = 0
            
            # Mettre à jour les unités du joueur 1
            for unit in self.player1_units[:]:
                if not unit.alive:
                    self.player1_units.remove(unit)
                    self.player2_xp += 10
                    continue
                
                unit.update()
                
                # Chercher une cible
                target_found = False
                
                # Attaquer les unités ennemies
                for enemy in self.player2_units:
                    if enemy.alive and unit.can_attack(enemy):
                        unit.attack(enemy)
                        target_found = True
                        break
                
                # Attaquer la tourelle ennemie
                if not target_found and unit.can_attack(self.player2_turret):
                    unit.attack(self.player2_turret)
                    target_found = True
                
                # Se déplacer si pas de cible
                if not target_found:
                    unit.move(self.width)
            
            # Mettre à jour les unités du joueur 2
            for unit in self.player2_units[:]:
                if not unit.alive:
                    self.player2_units.remove(unit)
                    self.player1_xp += 10
                    continue
                
                unit.update()
                
                # Chercher une cible
                target_found = False
                
                # Attaquer les unités ennemies
                for enemy in self.player1_units:
                    if enemy.alive and unit.can_attack(enemy):
                        unit.attack(enemy)
                        target_found = True
                        break
                
                # Attaquer la tourelle ennemie
                if not target_found and unit.can_attack(self.player1_turret):
                    unit.attack(self.player1_turret)
                    target_found = True
                
                # Se déplacer si pas de cible
                if not target_found:
                    unit.move(self.width)
            
            # Les tourelles attaquent
            self.player1_turret.update()
            for enemy in self.player2_units:
                if enemy.alive and self.player1_turret.can_attack(enemy):
                    self.player1_turret.attack(enemy)
                    break
            
            self.player2_turret.update()
            for enemy in self.player1_units:
                if enemy.alive and self.player2_turret.can_attack(enemy):
                    self.player2_turret.attack(enemy)
                    break
            
            # Vérifier les conditions de victoire
            if not self.player1_turret.alive:
                self.game_over = True
                messagebox.showinfo("Game Over", "L'IA a gagné!")
            elif not self.player2_turret.alive:
                self.game_over = True
                messagebox.showinfo("Victoire", "Vous avez gagné!")
            
            # Redessiner le jeu
            self.canvas.delete("all")
            self.draw_game()
            
            # Dessiner toutes les unités
            for unit in self.player1_units + self.player2_units:
                if unit.alive:
                    self.draw_unit(unit)
        
        # Continuer la boucle
        if not self.game_over:
            self.root.after(20, self.update)

def main():
    root = tk.Tk()
    game = AgeOfWar(root)
    root.mainloop()

if __name__ == "__main__":
    main()

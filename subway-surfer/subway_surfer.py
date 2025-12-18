import tkinter as tk
import random

class SubwaySurfers:
    def __init__(self, root):
        self.root = root
        self.root.title("Subway Surfers")
        self.root.resizable(False, False)
        
        # Dimensions du jeu
        self.width = 400
        self.height = 600
        
        # Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#2C2C2C")
        self.canvas.pack()
        
        # Variables du joueur
        self.player_width = 40
        self.player_height = 60
        self.lanes = [self.width // 4, self.width // 2, 3 * self.width // 4]
        self.current_lane = 1  # 0, 1, ou 2
        self.player_x = self.lanes[self.current_lane] - self.player_width // 2
        self.player_y = self.height - 150
        
        # Variables de saut
        self.is_jumping = False
        self.is_sliding = False
        self.jump_velocity = 0
        self.gravity = 1.2
        self.jump_strength = -18
        self.original_player_y = self.player_y
        
        # Variables du jeu
        self.game_speed = 8
        self.speed_increment = 0.0005
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.game_started = False
        
        # Obstacles
        self.obstacles = []
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_delay = 80  # frames
        
        # Pièces
        self.coins = []
        self.coin_spawn_timer = 0
        self.coin_spawn_delay = 40
        
        # Dessiner les voies (lignes de train)
        self.draw_lanes()
        
        # Créer le joueur
        self.player = self.canvas.create_rectangle(
            self.player_x, self.player_y,
            self.player_x + self.player_width,
            self.player_y + self.player_height,
            fill="#FFD700", outline="#FFA500", width=3
        )
        
        # Ajouter un visage simple au joueur
        self.player_face = self.canvas.create_oval(
            self.player_x + 10, self.player_y + 10,
            self.player_x + 30, self.player_y + 30,
            fill="#FF6347", outline="#FF4500", width=2
        )
        
        # Texte du score
        self.score_text = self.canvas.create_text(
            50, 30, text=f"Score: {self.score}", 
            font=("Arial", 16, "bold"), fill="white"
        )
        
        # Texte du high score
        self.high_score_text = self.canvas.create_text(
            self.width - 80, 30, text=f"Best: {self.high_score}",
            font=("Arial", 16, "bold"), fill="white"
        )
        
        # Texte d'instructions
        self.start_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="← → pour changer de voie\n↑ pour sauter\n↓ pour glisser\n\nESPACE pour commencer",
            font=("Arial", 14, "bold"), fill="white", justify="center"
        )
        
        # Bindings
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.jump)
        self.root.bind("<Down>", self.slide)
        self.root.bind("<space>", self.start_game)
        
        # Lancer la boucle de jeu
        self.update()
    
    def draw_lanes(self):
        """Dessiner les lignes des voies"""
        # Ligne gauche
        self.canvas.create_line(
            self.width // 4 - 40, 0, self.width // 4 - 40, self.height,
            fill="#FFD700", width=2, dash=(10, 10)
        )
        # Ligne droite
        self.canvas.create_line(
            3 * self.width // 4 + 40, 0, 3 * self.width // 4 + 40, self.height,
            fill="#FFD700", width=2, dash=(10, 10)
        )
    
    def start_game(self, event):
        """Démarrer le jeu"""
        if not self.game_started:
            self.game_started = True
            self.canvas.delete(self.start_text)
        elif self.game_over:
            self.reset_game()
    
    def reset_game(self):
        """Réinitialiser le jeu"""
        self.game_over = False
        self.game_started = True
        self.score = 0
        self.game_speed = 8
        self.current_lane = 1
        self.player_x = self.lanes[self.current_lane] - self.player_width // 2
        self.player_y = self.height - 150
        self.original_player_y = self.player_y
        self.is_jumping = False
        self.is_sliding = False
        self.jump_velocity = 0
        
        # Supprimer tous les obstacles et pièces
        for obstacle in self.obstacles:
            self.canvas.delete(obstacle['id'])
        self.obstacles.clear()
        
        for coin in self.coins:
            self.canvas.delete(coin['id'])
        self.coins.clear()
        
        # Supprimer le texte game over
        self.canvas.delete("game_over")
        
        # Mettre à jour le score
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        
        # Réinitialiser les timers
        self.obstacle_spawn_timer = 0
        self.coin_spawn_timer = 0
    
    def move_left(self, event):
        """Déplacer le joueur vers la voie de gauche"""
        if self.game_started and not self.game_over and self.current_lane > 0:
            self.current_lane -= 1
            self.player_x = self.lanes[self.current_lane] - self.player_width // 2
    
    def move_right(self, event):
        """Déplacer le joueur vers la voie de droite"""
        if self.game_started and not self.game_over and self.current_lane < 2:
            self.current_lane += 1
            self.player_x = self.lanes[self.current_lane] - self.player_width // 2
    
    def jump(self, event):
        """Faire sauter le joueur"""
        if self.game_started and not self.game_over and not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.jump_velocity = self.jump_strength
    
    def slide(self, event):
        """Faire glisser le joueur"""
        if self.game_started and not self.game_over and not self.is_sliding and not self.is_jumping:
            self.is_sliding = True
            self.slide_timer = 20  # Durée du slide en frames
    
    def spawn_obstacle(self):
        """Créer un obstacle aléatoire"""
        lane = random.randint(0, 2)
        x = self.lanes[lane] - 20
        y = -60
        
        # Types d'obstacles: 0 = haut (barrière), 1 = bas (obstacle)
        obstacle_type = random.choice([0, 1])
        
        if obstacle_type == 0:
            # Obstacle haut (à éviter en glissant)
            obstacle_id = self.canvas.create_rectangle(
                x, y, x + 40, y + 40,
                fill="#FF4500", outline="#DC143C", width=2
            )
            height = 40
            needs_slide = False
        else:
            # Obstacle bas (à éviter en sautant)
            obstacle_id = self.canvas.create_rectangle(
                x, y, x + 40, y + 60,
                fill="#8B0000", outline="#DC143C", width=2
            )
            height = 60
            needs_slide = True
        
        self.obstacles.append({
            'id': obstacle_id,
            'x': x,
            'y': y,
            'lane': lane,
            'width': 40,
            'height': height,
            'needs_slide': needs_slide
        })
    
    def spawn_coin(self):
        """Créer une pièce aléatoire"""
        lane = random.randint(0, 2)
        x = self.lanes[lane] - 10
        y = -30
        height_offset = random.choice([0, -80, -160])  # Sol, mi-hauteur, haut
        y += height_offset
        
        coin_id = self.canvas.create_oval(
            x, y, x + 20, y + 20,
            fill="#FFD700", outline="#FFA500", width=3
        )
        
        self.coins.append({
            'id': coin_id,
            'x': x,
            'y': y,
            'lane': lane,
            'size': 20
        })
    
    def check_collision(self):
        """Vérifier les collisions avec les obstacles"""
        player_left = self.player_x
        player_right = self.player_x + self.player_width
        player_top = self.player_y
        player_bottom = self.player_y + (self.player_height // 2 if self.is_sliding else self.player_height)
        
        for obstacle in self.obstacles:
            obs_left = obstacle['x']
            obs_right = obstacle['x'] + obstacle['width']
            obs_top = obstacle['y']
            obs_bottom = obstacle['y'] + obstacle['height']
            
            # Vérifier si le joueur est dans la même voie
            if obstacle['lane'] == self.current_lane:
                # Vérifier la collision rectangulaire
                if (player_left < obs_right and player_right > obs_left and
                    player_top < obs_bottom and player_bottom > obs_top):
                    
                    # Si l'obstacle est bas et que le joueur saute, pas de collision
                    if obstacle['needs_slide'] and self.is_jumping and player_bottom < obs_top + 20:
                        continue
                    
                    # Si l'obstacle est haut et que le joueur glisse, pas de collision
                    if not obstacle['needs_slide'] and self.is_sliding:
                        continue
                    
                    return True
        return False
    
    def check_coin_collection(self):
        """Vérifier la collecte des pièces"""
        player_center_x = self.player_x + self.player_width // 2
        player_center_y = self.player_y + self.player_height // 2
        
        coins_to_remove = []
        for coin in self.coins:
            coin_center_x = coin['x'] + coin['size'] // 2
            coin_center_y = coin['y'] + coin['size'] // 2
            
            # Vérifier si le joueur est dans la même voie et proche de la pièce
            if coin['lane'] == self.current_lane:
                distance = ((player_center_x - coin_center_x) ** 2 + 
                           (player_center_y - coin_center_y) ** 2) ** 0.5
                
                if distance < 40:  # Rayon de collecte
                    self.score += 10
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    coins_to_remove.append(coin)
        
        # Supprimer les pièces collectées
        for coin in coins_to_remove:
            self.canvas.delete(coin['id'])
            self.coins.remove(coin)
    
    def update(self):
        """Mettre à jour le jeu"""
        if self.game_started and not self.game_over:
            # Augmenter progressivement la vitesse
            self.game_speed += self.speed_increment
            
            # Gérer le saut
            if self.is_jumping:
                self.jump_velocity += self.gravity
                self.player_y += self.jump_velocity
                
                # Vérifier si le joueur a atterri
                if self.player_y >= self.original_player_y:
                    self.player_y = self.original_player_y
                    self.is_jumping = False
                    self.jump_velocity = 0
            
            # Gérer le slide
            if self.is_sliding:
                self.slide_timer -= 1
                if self.slide_timer <= 0:
                    self.is_sliding = False
            
            # Spawner des obstacles
            self.obstacle_spawn_timer += 1
            if self.obstacle_spawn_timer >= self.obstacle_spawn_delay:
                self.spawn_obstacle()
                self.obstacle_spawn_timer = 0
                # Réduire progressivement le délai (augmenter la difficulté)
                self.obstacle_spawn_delay = max(40, self.obstacle_spawn_delay - 0.1)
            
            # Spawner des pièces
            self.coin_spawn_timer += 1
            if self.coin_spawn_timer >= self.coin_spawn_delay:
                self.spawn_coin()
                self.coin_spawn_timer = 0
            
            # Déplacer les obstacles
            obstacles_to_remove = []
            for obstacle in self.obstacles:
                obstacle['y'] += self.game_speed
                self.canvas.coords(
                    obstacle['id'],
                    obstacle['x'], obstacle['y'],
                    obstacle['x'] + obstacle['width'],
                    obstacle['y'] + obstacle['height']
                )
                
                # Supprimer les obstacles hors écran
                if obstacle['y'] > self.height:
                    obstacles_to_remove.append(obstacle)
                    self.score += 1
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
            
            for obstacle in obstacles_to_remove:
                self.canvas.delete(obstacle['id'])
                self.obstacles.remove(obstacle)
            
            # Déplacer les pièces
            coins_to_remove = []
            for coin in self.coins:
                coin['y'] += self.game_speed
                self.canvas.coords(
                    coin['id'],
                    coin['x'], coin['y'],
                    coin['x'] + coin['size'],
                    coin['y'] + coin['size']
                )
                
                # Supprimer les pièces hors écran
                if coin['y'] > self.height:
                    coins_to_remove.append(coin)
            
            for coin in coins_to_remove:
                self.canvas.delete(coin['id'])
                self.coins.remove(coin)
            
            # Vérifier la collecte des pièces
            self.check_coin_collection()
            
            # Vérifier les collisions
            if self.check_collision():
                self.game_over = True
                
                # Mettre à jour le high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.canvas.itemconfig(self.high_score_text, text=f"Best: {self.high_score}")
                
                self.canvas.create_text(
                    self.width // 2, self.height // 2,
                    text=f"GAME OVER\nScore: {self.score}\n\nESPACE pour rejouer",
                    font=("Arial", 18, "bold"), fill="red", justify="center",
                    tags="game_over"
                )
            
            # Mettre à jour la position du joueur
            player_height = self.player_height // 2 if self.is_sliding else self.player_height
            player_y_offset = self.player_height // 2 if self.is_sliding else 0
            
            self.canvas.coords(
                self.player,
                self.player_x, self.player_y + player_y_offset,
                self.player_x + self.player_width,
                self.player_y + player_y_offset + player_height
            )
            
            self.canvas.coords(
                self.player_face,
                self.player_x + 10, self.player_y + 10 + player_y_offset,
                self.player_x + 30, self.player_y + 30 + player_y_offset
            )
        
        # Continuer la boucle
        self.root.after(20, self.update)

def main():
    root = tk.Tk()
    game = SubwaySurfers(root)
    root.mainloop()

if __name__ == "__main__":
    main()

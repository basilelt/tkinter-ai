import tkinter as tk
import random
import math

class DoodleJump:
    def __init__(self, root):
        self.root = root
        self.root.title("Doodle Jump")
        self.root.resizable(False, False)
        
        # Dimensions du jeu
        self.width = 400
        self.height = 600
        
        # Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#87CEEB")
        self.canvas.pack()
        
        # Variables du joueur
        self.player_width = 40
        self.player_height = 40
        self.player_x = self.width // 2 - self.player_width // 2
        self.player_y = self.height - 150
        self.player_velocity_y = 0
        self.player_velocity_x = 0
        
        # Variables du jeu
        self.gravity = 0.5
        self.jump_strength = -15
        self.move_speed = 5
        self.platform_width = 70
        self.platform_height = 15
        self.platforms = []
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.game_started = False
        
        # Créer le joueur
        self.player = self.canvas.create_oval(
            self.player_x, self.player_y,
            self.player_x + self.player_width,
            self.player_y + self.player_height,
            fill="#228B22", outline="#006400", width=2
        )
        
        # Créer les plateformes initiales
        self.create_initial_platforms()
        
        # Texte du score
        self.score_text = self.canvas.create_text(
            50, 30, text=f"Score: {self.score}", 
            font=("Arial", 16, "bold"), fill="white"
        )
        
        # Texte du high score
        self.high_score_text = self.canvas.create_text(
            self.width - 70, 30, text=f"Best: {self.high_score}",
            font=("Arial", 16, "bold"), fill="white"
        )
        
        # Texte d'instructions
        self.start_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text="Utilisez les flèches ← → pour bouger\nAppuyez sur ESPACE pour commencer",
            font=("Arial", 14, "bold"), fill="white", justify="center"
        )
        
        # Bindings
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<space>", self.start_game)
        self.root.bind("<KeyRelease-Left>", self.stop_move)
        self.root.bind("<KeyRelease-Right>", self.stop_move)
        
        # Lancer la boucle de jeu
        self.update()
    
    def create_initial_platforms(self):
        """Créer les plateformes initiales"""
        # Plateforme de départ
        platform = {
            'x': self.width // 2 - self.platform_width // 2,
            'y': self.height - 100,
            'id': None
        }
        platform['id'] = self.canvas.create_rectangle(
            platform['x'], platform['y'],
            platform['x'] + self.platform_width,
            platform['y'] + self.platform_height,
            fill="#8B4513", outline="#654321", width=2
        )
        self.platforms.append(platform)
        
        # Créer des plateformes supplémentaires
        y = self.height - 100
        while y > -100:
            y -= random.randint(60, 100)
            x = random.randint(0, self.width - self.platform_width)
            platform = {
                'x': x,
                'y': y,
                'id': None
            }
            platform['id'] = self.canvas.create_rectangle(
                x, y, x + self.platform_width, y + self.platform_height,
                fill="#8B4513", outline="#654321", width=2
            )
            self.platforms.append(platform)
    
    def start_game(self, event):
        """Démarrer le jeu"""
        if not self.game_started:
            self.game_started = True
            self.canvas.delete(self.start_text)
            self.player_velocity_y = self.jump_strength
        elif self.game_over:
            self.reset_game()
    
    def reset_game(self):
        """Réinitialiser le jeu"""
        self.game_over = False
        self.game_started = True
        self.score = 0
        self.player_x = self.width // 2 - self.player_width // 2
        self.player_y = self.height - 150
        self.player_velocity_y = self.jump_strength
        self.player_velocity_x = 0
        
        # Supprimer les anciennes plateformes
        for platform in self.platforms:
            self.canvas.delete(platform['id'])
        self.platforms.clear()
        
        # Recréer les plateformes
        self.create_initial_platforms()
        
        # Supprimer le texte game over
        self.canvas.delete("game_over")
        
        # Mettre à jour le score
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
    
    def move_left(self, event):
        """Déplacer le joueur vers la gauche"""
        if self.game_started and not self.game_over:
            self.player_velocity_x = -self.move_speed
    
    def move_right(self, event):
        """Déplacer le joueur vers la droite"""
        if self.game_started and not self.game_over:
            self.player_velocity_x = self.move_speed
    
    def stop_move(self, event):
        """Arrêter le mouvement horizontal"""
        self.player_velocity_x = 0
    
    def check_platform_collision(self):
        """Vérifier la collision avec les plateformes"""
        if self.player_velocity_y > 0:  # Le joueur tombe
            player_bottom = self.player_y + self.player_height
            player_center_x = self.player_x + self.player_width // 2
            
            for platform in self.platforms:
                # Vérifier si le joueur est au-dessus de la plateforme
                if (platform['y'] <= player_bottom <= platform['y'] + self.platform_height + 10 and
                    platform['x'] <= player_center_x <= platform['x'] + self.platform_width):
                    # Collision détectée
                    self.player_velocity_y = self.jump_strength
                    return True
        return False
    
    def update(self):
        """Mettre à jour le jeu"""
        if self.game_started and not self.game_over:
            # Appliquer la gravité
            self.player_velocity_y += self.gravity
            
            # Mettre à jour la position du joueur
            self.player_y += self.player_velocity_y
            self.player_x += self.player_velocity_x
            
            # Limites horizontales (passage de l'autre côté)
            if self.player_x < -self.player_width:
                self.player_x = self.width
            elif self.player_x > self.width:
                self.player_x = -self.player_width
            
            # Vérifier les collisions avec les plateformes
            self.check_platform_collision()
            
            # Scroll de la caméra quand le joueur monte
            if self.player_y < self.height // 3:
                scroll_amount = self.height // 3 - self.player_y
                self.player_y = self.height // 3
                
                # Déplacer les plateformes vers le bas
                for platform in self.platforms:
                    platform['y'] += scroll_amount
                    self.canvas.coords(
                        platform['id'],
                        platform['x'], platform['y'],
                        platform['x'] + self.platform_width,
                        platform['y'] + self.platform_height
                    )
                
                # Augmenter le score
                self.score += int(scroll_amount)
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                
                # Mettre à jour le high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.canvas.itemconfig(self.high_score_text, text=f"Best: {self.high_score}")
                
                # Supprimer les plateformes hors écran et en créer de nouvelles
                self.platforms = [p for p in self.platforms if p['y'] < self.height + 50]
                for p in [plat for plat in self.platforms if plat['y'] >= self.height + 50]:
                    self.canvas.delete(p['id'])
                
                # Créer de nouvelles plateformes en haut
                while len(self.platforms) < 10:
                    y = self.platforms[0]['y'] - random.randint(60, 100)
                    x = random.randint(0, self.width - self.platform_width)
                    platform = {
                        'x': x,
                        'y': y,
                        'id': None
                    }
                    platform['id'] = self.canvas.create_rectangle(
                        x, y, x + self.platform_width, y + self.platform_height,
                        fill="#8B4513", outline="#654321", width=2
                    )
                    self.platforms.insert(0, platform)
            
            # Vérifier si le joueur est tombé
            if self.player_y > self.height:
                self.game_over = True
                self.canvas.create_text(
                    self.width // 2, self.height // 2,
                    text=f"GAME OVER\nScore: {self.score}\n\nAppuyez sur ESPACE pour rejouer",
                    font=("Arial", 18, "bold"), fill="red", justify="center",
                    tags="game_over"
                )
            
            # Mettre à jour la position du joueur sur le canvas
            self.canvas.coords(
                self.player,
                self.player_x, self.player_y,
                self.player_x + self.player_width,
                self.player_y + self.player_height
            )
        
        # Continuer la boucle
        self.root.after(20, self.update)

def main():
    root = tk.Tk()
    game = DoodleJump(root)
    root.mainloop()

if __name__ == "__main__":
    main()

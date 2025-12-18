"""
Simulateur de course de billes 2D avec Tkinter
Les billes roulent sur une piste comme des vraies billes
"""

import tkinter as tk
import random
import math

# Configuration
LARGEUR = 1200
HAUTEUR = 700
NB_BILLES = 5
GRAVITE = 0.7
FRICTION_SOL = 0.992
RAYON_BILLE = 10

# Couleurs des billes
COULEURS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
NOMS_BILLES = ['Rouge', 'Cyan', 'Bleu', 'Vert', 'Jaune']


class Piste:
    """La piste est une série de segments sur lesquels les billes roulent"""
    def __init__(self):
        self.segments = []  # Liste de (x1, y1, x2, y2)
    
    def generer(self):
        """Génère une piste aléatoire de gauche à droite avec des pentes prononcées"""
        self.segments = []
        
        # Point de départ EN HAUT à gauche
        x = 50
        y = random.randint(60, 120)  # Commence plus haut
        
        # Générer des segments
        while x < LARGEUR - 100:
            # Longueur du segment
            longueur = random.randint(100, 180)
            
            # Angle du segment - pentes plus prononcées, surtout descendantes
            # Plus de chances de descendre que de monter
            if random.random() < 0.75:  # 75% de chances de descendre
                angle = random.uniform(0.2, 0.6)  # Descente prononcée
            else:
                angle = random.uniform(-0.2, 0.1)  # Légère montée ou plat
            
            # Nouveau point
            new_x = x + longueur * math.cos(angle)
            new_y = y + longueur * math.sin(angle)
            
            # Rester dans les limites (mais permettre d'aller plus bas)
            new_y = max(80, min(HAUTEUR - 80, new_y))
            new_x = min(LARGEUR - 50, new_x)
            
            self.segments.append((x, y, new_x, new_y))
            
            x = new_x
            y = new_y
        
        # Dernier segment - descente finale vers l'arrivée
        self.segments.append((x, y, LARGEUR - 50, min(HAUTEUR - 60, y + 50)))
    
    def dessiner(self, canvas):
        """Dessine la piste"""
        for (x1, y1, x2, y2) in self.segments:
            # Ligne principale (sol)
            canvas.create_line(x1, y1, x2, y2, fill='#8B4513', width=8, capstyle='round')
            # Ligne de dessus (effet 3D)
            canvas.create_line(x1, y1-2, x2, y2-2, fill='#A0522D', width=4, capstyle='round')
    
    def trouver_segment(self, x):
        """Trouve le segment sur lequel se trouve la position x"""
        for i, (x1, y1, x2, y2) in enumerate(self.segments):
            if x1 <= x <= x2 or x2 <= x <= x1:
                return i
        # Si pas trouvé, retourner le plus proche
        if x < self.segments[0][0]:
            return 0
        return len(self.segments) - 1
    
    def get_y_sol(self, x):
        """Retourne la hauteur du sol à la position x"""
        idx = self.trouver_segment(x)
        x1, y1, x2, y2 = self.segments[idx]
        
        if x2 == x1:
            return y1
        
        # Interpolation linéaire
        t = (x - x1) / (x2 - x1)
        t = max(0, min(1, t))
        return y1 + t * (y2 - y1)
    
    def get_angle(self, x):
        """Retourne l'angle du sol à la position x"""
        idx = self.trouver_segment(x)
        x1, y1, x2, y2 = self.segments[idx]
        return math.atan2(y2 - y1, x2 - x1)


class Bille:
    def __init__(self, canvas, x, y, couleur, numero, nom):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.rayon = RAYON_BILLE
        self.couleur = couleur
        self.numero = numero
        self.nom = nom
        self.arrivee = False
        self.au_sol = False
        
        # Créer la bille
        self.id = canvas.create_oval(
            x - self.rayon, y - self.rayon,
            x + self.rayon, y + self.rayon,
            fill=couleur, outline='white', width=2
        )
        self.texte_id = canvas.create_text(
            x, y, text=str(numero), fill='white', font=('Arial', 8, 'bold')
        )
    
    def update(self, piste, zone_arrivee):
        if self.arrivee:
            return
        
        # Gravité
        self.vy += GRAVITE
        
        # Position temporaire
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # Collision avec le sol de la piste
        y_sol = piste.get_y_sol(new_x)
        
        if new_y + self.rayon >= y_sol:
            # On touche le sol
            new_y = y_sol - self.rayon
            self.au_sol = True
            
            # Angle du sol
            angle = piste.get_angle(new_x)
            
            # Décomposer la vitesse en composantes tangentielle et normale
            # Tangente au sol
            tx = math.cos(angle)
            ty = math.sin(angle)
            # Normale au sol (vers le haut)
            nx = -ty
            ny = tx
            
            # Vitesse normale (vers le sol)
            v_normal = self.vx * nx + self.vy * ny
            
            # Si on va vers le sol, rebondir légèrement
            if v_normal < 0:
                # Annuler la composante normale (avec petit rebond)
                self.vx -= v_normal * nx * 1.1
                self.vy -= v_normal * ny * 1.1
            
            # Accélération due à la pente (gravité projetée sur la tangente)
            g_tangent = GRAVITE * ty  # ty = sin(angle)
            self.vx += g_tangent * tx
            self.vy += g_tangent * ty
            
            # Friction au sol
            self.vx *= FRICTION_SOL
            self.vy *= FRICTION_SOL
        else:
            self.au_sol = False
        
        # Limites horizontales
        new_x = max(self.rayon, min(LARGEUR - self.rayon, new_x))
        
        # Mettre à jour la position
        self.x = new_x
        self.y = new_y
        
        # Mettre à jour l'affichage
        self.canvas.coords(
            self.id,
            self.x - self.rayon, self.y - self.rayon,
            self.x + self.rayon, self.y + self.rayon
        )
        self.canvas.coords(self.texte_id, self.x, self.y)
        
        # Vérifier arrivée
        if zone_arrivee:
            zx, zy, zw, zh = zone_arrivee
            if zx < self.x < zx + zw and zy < self.y < zy + zh:
                self.arrivee = True


def collision_billes(b1, b2):
    """Gère la collision entre deux billes"""
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.sqrt(dx * dx + dy * dy)
    
    min_dist = b1.rayon + b2.rayon
    
    if dist < min_dist and dist > 0:
        # Normaliser
        nx = dx / dist
        ny = dy / dist
        
        # Séparer les billes
        overlap = min_dist - dist
        b1.x -= nx * overlap * 0.5
        b1.y -= ny * overlap * 0.5
        b2.x += nx * overlap * 0.5
        b2.y += ny * overlap * 0.5
        
        # Vitesses relatives
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        
        # Vitesse relative dans la direction de collision
        dvn = dvx * nx + dvy * ny
        
        # Ne rien faire si les billes s'éloignent déjà
        if dvn > 0:
            return
        
        # Impulsion (coefficient de restitution = 0.8)
        j = -1.8 * dvn / 2
        
        b1.vx += j * nx
        b1.vy += j * ny
        b2.vx -= j * nx
        b2.vy -= j * ny


class CoursesBilles:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏁 Course de Billes 🏁")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c3e50')
        
        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=LARGEUR,
            height=HAUTEUR,
            bg='#87CEEB',  # Ciel bleu
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Info
        self.info_frame = tk.Frame(self.root, bg='#2c3e50')
        self.info_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_course = tk.Label(
            self.info_frame,
            text="Course #1",
            font=('Arial', 14, 'bold'),
            fg='#f1c40f', bg='#2c3e50'
        )
        self.label_course.pack(side='left', padx=10)
        
        self.label_classement = tk.Label(
            self.info_frame,
            text="",
            font=('Arial', 11),
            fg='white', bg='#2c3e50'
        )
        self.label_classement.pack(side='left', padx=20, expand=True)
        
        self.btn_nouvelle = tk.Button(
            self.info_frame,
            text="🔄 Nouvelle Course",
            font=('Arial', 10, 'bold'),
            bg='#27ae60', fg='white',
            command=self.nouvelle_course
        )
        self.btn_nouvelle.pack(side='right', padx=10)
        
        # Variables
        self.piste = Piste()
        self.billes = []
        self.zone_arrivee = None
        self.num_course = 1
        self.classement = []
        self.running = True
        
        self.nouvelle_course()
        self.update()
        
        self.root.mainloop()
    
    def nouvelle_course(self):
        self.canvas.delete('all')
        
        # Dessiner le fond (herbe en bas)
        self.canvas.create_rectangle(0, HAUTEUR - 50, LARGEUR, HAUTEUR, fill='#228B22', outline='')
        
        # Nuages
        for _ in range(5):
            x = random.randint(50, LARGEUR - 50)
            y = random.randint(30, 100)
            for dx in range(-20, 30, 15):
                self.canvas.create_oval(x + dx, y, x + dx + 40, y + 25, fill='white', outline='')
        
        # Générer la piste
        self.piste.generer()
        self.piste.dessiner(self.canvas)
        
        # Zone d'arrivée
        dernier_seg = self.piste.segments[-1]
        fin_x, fin_y = dernier_seg[2], dernier_seg[3]
        self.zone_arrivee = (fin_x - 40, fin_y - 60, 80, 80)
        
        # Dessiner l'arrivée
        zx, zy, zw, zh = self.zone_arrivee
        self.canvas.create_rectangle(zx, zy, zx + zw, zy + zh, fill='', outline='#f1c40f', width=3)
        self.canvas.create_text(zx + zw//2, zy - 10, text="🏁", font=('Arial', 16))
        
        # Créer les billes
        self.billes = []
        self.classement = []
        
        premier_seg = self.piste.segments[0]
        depart_x, depart_y = premier_seg[0], premier_seg[1]
        
        for i in range(NB_BILLES):
            x = depart_x + i * 5  # Légèrement décalées
            y = depart_y - RAYON_BILLE - 5 - i * 3  # Empilées au-dessus du sol
            
            bille = Bille(
                self.canvas, x, y,
                COULEURS[i], i + 1, NOMS_BILLES[i]
            )
            bille.vx = random.uniform(0.5, 2)  # Impulsion initiale
            self.billes.append(bille)
        
        # Dessiner le départ
        self.canvas.create_text(depart_x, depart_y - 50, text="🚀 GO!", font=('Arial', 14, 'bold'), fill='#e74c3c')
        
        self.label_course.config(text=f"Course #{self.num_course}")
        self.label_classement.config(text="En course...")
        self.running = True
    
    def update(self):
        if self.running:
            # Mettre à jour les billes
            for bille in self.billes:
                bille.update(self.piste, self.zone_arrivee)
                
                if bille.arrivee and bille not in self.classement:
                    self.classement.append(bille)
            
            # Collisions entre billes
            for i in range(len(self.billes)):
                for j in range(i + 1, len(self.billes)):
                    b1, b2 = self.billes[i], self.billes[j]
                    if not b1.arrivee and not b2.arrivee:
                        collision_billes(b1, b2)
            
            # Afficher classement
            if self.classement:
                medailles = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
                txt = "  ".join([f"{medailles[i]} {b.nom}" for i, b in enumerate(self.classement)])
                self.label_classement.config(text=txt)
            
            # Fin de course
            if all(b.arrivee for b in self.billes):
                self.running = False
                self.afficher_resultats()
                self.root.after(4000, self.prochaine_course)
        
        self.root.after(16, self.update)
    
    def afficher_resultats(self):
        cx, cy = LARGEUR // 2, HAUTEUR // 2
        
        self.canvas.create_rectangle(cx - 150, cy - 100, cx + 150, cy + 100,
                                    fill='#2c3e50', outline='#f1c40f', width=3)
        self.canvas.create_text(cx, cy - 70, text="🏆 RÉSULTATS 🏆",
                               fill='#f1c40f', font=('Arial', 16, 'bold'))
        
        medailles = ['🥇', '🥈', '🥉']
        for i, bille in enumerate(self.classement[:3]):
            self.canvas.create_text(cx, cy - 20 + i * 35,
                                   text=f"{medailles[i]} {bille.nom}",
                                   fill=bille.couleur, font=('Arial', 14, 'bold'))
    
    def prochaine_course(self):
        self.num_course += 1
        self.nouvelle_course()


if __name__ == "__main__":
    CoursesBilles()

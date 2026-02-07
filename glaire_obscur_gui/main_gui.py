#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Le Glaire Obscur – RPG Graphique avec Tkinter
Point d'entrée principal.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
import os
from datetime import datetime
from typing import Dict, List

# Import des modules du jeu (ils sont dans le même dossier)
from world import CARTE_DU_GLAIRE, Zone, obtenir_lieu
from characters import TOUS_LES_PERSONNAGES, Personnage, trouver_personnage
from combat import creer_joueur, creer_xi, creer_spam_fromager, tour_combat


class GlaireObscurGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Le Glaire Obscur – RPG Graphique")
        self.root.geometry("1024x768")
        self.root.configure(bg="#2c2c2c")

        # État du jeu
        self.joueur = creer_joueur("Agent Gestapesto")
        self.zone_actuelle = Zone.QG_GESTAPESTO
        self.tour = 1
        self.ressources = {
            "fromage_de_femme": 0,
            "poussiere_loli": 0,
            "jus_ecorce": 0,
            "n2o": 0,
            "stick_sali": 0,
            "kebab_explosif": 0,
            "chiasse": 0,
        }
        self.relations = {
            "Miss Pinelli": 100,
            "Gérard le Mouleur": 50,
            "Xi": -100,
            "Thomas Mauvais": 0,
            "Dorian P": 80,
        }
        self.combat_en_cours = False
        self.ennemi_actuel = None
        self.logs = []

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 10), padding=6)
        style.configure("TLabel", font=("Helvetica", 11), background="#2c2c2c", foreground="white")
        style.configure("TFrame", background="#2c2c2c")

        self.setup_ui()
        self.refresh_affichage()

    def setup_ui(self):
        # === Menu ===
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouvelle partie", command=self.nouvelle_partie)
        file_menu.add_command(label="Sauvegarder", command=self.sauvegarder)
        file_menu.add_command(label="Charger", command=self.charger)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        self.root.config(menu=menubar)

        # === Layout principal ===
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Colonne gauche : infos joueur
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="👤 Agent Gestapesto", font=("Helvetica", 14, "bold")).pack(pady=10)
        self.lbl_stats = ttk.Label(left_frame, text=self.stats_text(), font=("Courier", 10))
        self.lbl_stats.pack(pady=10, anchor="w")

        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        ttk.Label(left_frame, text="🎒 Ressources", font=("Helvetica", 12, "bold")).pack(pady=5)
        self.lbl_ressources = ttk.Label(left_frame, text=self.ressources_text(), font=("Courier", 9))
        self.lbl_ressources.pack(pady=5, anchor="w")

        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        ttk.Label(left_frame, text="🤝 Relations", font=("Helvetica", 12, "bold")).pack(pady=5)
        self.lbl_relations = ttk.Label(left_frame, text=self.relations_text(), font=("Courier", 9))
        self.lbl_relations.pack(pady=5, anchor="w")

        # Colonne droite : zone de jeu
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Panneau supérieur : description de la zone
        zone_frame = ttk.LabelFrame(right_frame, text="📍 Lieu actuel", padding=10)
        zone_frame.pack(fill=tk.X, pady=(0,10))
        self.lbl_zone_nom = ttk.Label(zone_frame, text=self.zone_nom(), font=("Helvetica", 14, "bold"))
        self.lbl_zone_nom.pack(anchor="w")
        self.lbl_zone_desc = ttk.Label(zone_frame, text=self.zone_desc(), wraplength=700)
        self.lbl_zone_desc.pack(anchor="w", pady=5)

        # Zone de logs (événements)
        log_frame = ttk.LabelFrame(right_frame, text="📜 Journal", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=12, bg="#1e1e1e", fg="lightgreen", font=("Courier", 9), state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Boutons d'action
        actions_frame = ttk.Frame(right_frame)
        actions_frame.pack(fill=tk.X)

        btn_explorer = ttk.Button(actions_frame, text="🔍 Explorer", command=self.action_explorer)
        btn_explorer.pack(side=tk.LEFT, padx=5)

        btn_parler = ttk.Button(actions_frame, text="💬 Parler à...", command=self.popup_parler)
        btn_parler.pack(side=tk.LEFT, padx=5)

        btn_inventory = ttk.Button(actions_frame, text="🎒 Inventaire", command=self.popup_inventory)
        btn_inventory.pack(side=tk.LEFT, padx=5)

        btn_deplacer = ttk.Button(actions_frame, text="🚶 Se déplacer", command=self.popup_deplacement)
        btn_deplacer.pack(side=tk.LEFT, padx=5)

        btn_quitter = ttk.Button(actions_frame, text="🚪 Quitter", command=self.root.quit)
        btn_quitter.pack(side=tk.RIGHT, padx=5)

    def stats_text(self):
        j = self.joueur
        return (
            f"Niveau : {j.niveau}\n"
            f"PV : {j.pv}/{j.pv_max}\n"
            f"Attaque : {j.attaque}\n"
            f"Défense : {j.defense}\n"
            f"Vitesse : {j.vitesse}\n"
            f"XP : {j.experience}/{j.experience_next}"
        )

    def ressources_text(self):
        lines = []
        for res, qty in self.ressources.items():
            if qty > 0:
                lines.append(f"{res}: {qty}")
        return "\n".join(lines) if lines else "Aucune ressource"

    def relations_text(self):
        lines = []
        for pers, val in self.relations.items():
            barre = "█" * (val // 10) if val >= 0 else "▒" * (abs(val) // 10)
            lines.append(f"{pers} : {val}% {barre}")
        return "\n".join(lines)

    def zone_nom(self):
        lieu = obtenir_lieu(self.zone_actuelle)
        return lieu.nom

    def zone_desc(self):
        lieu = obtenir_lieu(self.zone_actuelle)
        return f"{lieu.description}\nDanger : {'★' * lieu.危険_level} / 5"

    def refresh_affichage(self):
        self.lbl_stats.config(text=self.stats_text())
        self.lbl_ressources.config(text=self.ressources_text())
        self.lbl_relations.config(text=self.relations_text())
        self.lbl_zone_nom.config(text=self.zone_nom())
        self.lbl_zone_desc.config(text=self.zone_desc())

    def log(self, message):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, f"[Tour {self.tour}] {message}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    # === Actions ===
    def action_explorer(self):
        if self.combat_en_cours:
            self.log("Vous êtes déjà en combat !")
            return
        self.log(f"Vous explorez {self.zone_nom()}...")
        lieu = obtenir_lieu(self.zone_actuelle)
        evenement = random.choice(lieu.evenements_possibles)
        self.log(evenement)
        # Ressources
        if random.random() < 0.5:
            res = random.choice(list(lieu.ressources.keys()))
            qty = lieu.ressources.get(res, 1)
            self.ressources[res] = self.ressources.get(res, 0) + qty
            self.log(f"🎒 Vous trouvez {qty} x {res} !")
        # Rencontre
        if random.random() < 0.3:
            ennemi = self.generer_ennemi(lieu.危険_level)
            self.ennemi_actuel = ennemi
            self.combat_en_cours = True
            self.log(f"\n⚠️  ENNEMI : {ennemi.nom} apparaît ! (PV: {ennemi.pv})")
            self.log("Combat automatisé en cours...")
            self.root.after(1000, self.tour_combat_auto)
        else:
            self.log("Aucun ennemi en vue.")
        self.tour += 1
        self.refresh_affichage()

    def generer_ennemi(self, danger):
        if danger <= 1:
            return creer_spam_fromager() if random.random() < 0.6 else creer_xi()
        elif danger == 2:
            return creer_thomas_mauvais() if random.random() < 0.5 else creer_spam_fromager()
        else:
            return creer_xi() if random.random() < 0.7 else creer_thomas_mauvais()

    def tour_combat_auto(self):
        if not self.combat_en_cours or not self.ennemi_actuel:
            return
        # Tour joueur
        att_index = random.randint(0, len(self.joueur.attaques) - 1)
        res_j = self.joueur.attaquer(self.ennemi_actuel, att_index)
        self.log(f"{res_j['attaquant']} utilise {res_j['attaque']} ! {res_j['message']}")
        if not self.ennemi_actuel.est_vivant():
            self.log(f"☠️  {self.ennemi_actuel.nom} vaincu ! +{self.ennemi_actuel.experience} XP")
            self.joueur.experience += self.ennemi_actuel.experience
            for res, qty in self.ennemi_actuel.loot.items():
                self.ressources[res] = self.ressources.get(res, 0) + qty
            self.combat_en_cours = False
            self.ennemi_actuel = None
            self.verifier_niveau()
            self.refresh_affichage()
            return
        # Tour ennemi
        res_e = self.ennemi_actuel.attaquer(self.joueur, 0)
        self.log(f"{res_e['attaquant']} utilise {res_e['attaque']} ! {res_e['message']}")
        if not self.joueur.est_vivant():
            self.log("💀 Vous êtes mort ! La Gestapesto vous ressuscite au QG.")
            self.joueur.pv = self.joueur.pv_max // 2
            self.zone_actuelle = Zone.QG_GESTAPESTO
            self.combat_en_cours = False
            self.ennemi_actuel = None
            self.refresh_affichage()
            return
        # Tour suivant
        self.root.after(1200, self.tour_combat_auto)

    def verifier_niveau(self):
        while self.joueur.experience >= self.joueur.experience_next:
            self.joueur.experience -= self.joueur.experience_next
            self.joueur.niveau += 1
            self.joueur.pv_max += 10
            self.joueur.pv = self.joueur.pv_max
            self.joueur.attaque += 2
            self.joueur.defense += 1
            self.joueur.vitesse += 1
            self.joueur.experience_next = int(self.joueur.experience_next * 1.2)
            self.log(f"🎉 Niveau {self.joueur.niveau} ! Stats augmentées.")

    def popup_parler(self):
        win = tk.Toplevel(self.root)
        win.title("Parler à un PNJ")
        win.geometry("400x300")
        ttk.Label(win, text="Choisissez un personnage :").pack(pady=10)
        lb = tk.Listbox(win, height=10)
        for p in TOUS_LES_PERSONNAGES:
            lb.insert(tk.END, p.nom)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        def parler():
            sel = lb.curselection()
            if not sel:
                return
            nom = lb.get(sel[0])
            pers = trouver_personnage(nom)
            if pers:
                messagebox.showinfo(f"Conversation avec {pers.nom}", pers.presentation() + "\n\n" + f"{pers.nom} : \"Nyaa~ 🐾\"")
            win.destroy()
        ttk.Button(win, text="Parler", command=parler).pack(pady=10)

    def popup_inventory(self):
        win = tk.Toplevel(self.root)
        win.title("Inventaire")
        win.geometry("300x400")
        txt = scrolledtext.ScrolledText(win, font=("Courier", 10))
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, "=== RESSOURCES ===\n")
        for res, qty in self.ressources.items():
            if qty > 0:
                txt.insert(tk.END, f"{res}: {qty}\n")
        txt.insert(tk.END, "\n=== STATS ===\n")
        j = self.joueur
        txt.insert(tk.END, f"Niv.{j.niveau} PV:{j.pv}/{j.pv_max} Att:{j.attaque} Def:{j.defense} Vit:{j.vitesse}\n")
        txt.config(state=tk.DISABLED)

    def popup_deplacement(self):
        win = tk.Toplevel(self.root)
        win.title("Se déplacer")
        win.geometry("350x300")
        ttk.Label(win, text="Zones disponibles :").pack(pady=10)
        lb = tk.Listbox(win, height=12)
        zones = list(Zone)
        for z in zones:
            lb.insert(tk.END, z.name)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        def deplacer():
            sel = lb.curselection()
            if not sel:
                return
            zone_name = lb.get(sel[0])
            try:
                zone = Zone[zone_name]
                self.zone_actuelle = zone
                self.log(f"🚶 Vous vous déplacez vers : {self.zone_nom()}")
                self.refresh_affichage()
                win.destroy()
            except KeyError:
                pass
        ttk.Button(win, text="Aller", command=deplacer).pack(pady=10)

    def nouvelle_partie(self):
        if messagebox.askyesno("Nouvelle partie", "Voulez-vous recommencer ?"):
            self.joueur = creer_joueur("Agent Gestapesto")
            self.zone_actuelle = Zone.QG_GESTAPESTO
            self.tour = 1
            self.ressources = {k:0 for k in self.ressources}
            self.combat_en_cours = False
            self.ennemi_actuel = None
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.delete(1.0, tk.END)
            self.txt_log.config(state=tk.DISABLED)
            self.refresh_affichage()
            self.log("Nouvelle partie commencée ! Bienvenue dans le glaire obscur.")

    def sauvegarder(self):
        data = {
            "nom": self.joueur.nom,
            "pv": self.joueur.pv,
            "pv_max": self.joueur.pv_max,
            "niveau": self.joueur.niveau,
            "experience": self.joueur.experience,
            "attaque": self.joueur.attaque,
            "defense": self.joueur.defense,
            "vitesse": self.joueur.vitesse,
            "zone": self.zone_actuelle.name,
            "tour": self.tour,
            "ressources": self.ressources,
            "relations": self.relations,
        }
        filename = f"glaire_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Sauvegarde", f"Partie sauvegardée dans : {filename}")

    def charger(self):
        # Simplifié : charge le dernier fichier de sauvegarde
        files = [f for f in os.listdir(".") if f.startswith("glaire_save_") and f.endswith(".json")]
        if not files:
            messagebox.showwarning("Charger", "Aucune sauvegarde trouvée.")
            return
        latest = max(files, key=os.path.getctime)
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.joueur.nom = data["nom"]
        self.joueur.pv = data["pv"]
        self.joueur.pv_max = data["pv_max"]
        self.joueur.niveau = data["niveau"]
        self.joueur.experience = data["experience"]
        self.joueur.attaque = data["attaque"]
        self.joueur.defense = data["defense"]
        self.joueur.vitesse = data["vitesse"]
        self.zone_actuelle = Zone[data["zone"]]
        self.tour = data["tour"]
        self.ressources = data["ressources"]
        self.relations = data["relations"]
        self.refresh_affichage()
        messagebox.showinfo("Charger", f"Partie chargée : {latest}")


def main():
    root = tk.Tk()
    app = GlaireObscurGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
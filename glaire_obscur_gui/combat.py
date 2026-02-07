#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de combat du RPG Le Glaire Obscur.
"""

import random
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from enum import Enum, auto


class TypeAttaque(Enum):
    PHYSIQUE = auto()
    FROMAGERE = auto()
    ALCHIMIQUE = auto()
    MIAOU = auto()  # magique
    KEBAB_EXPLOSIF = auto()
    STICK_SALI = auto()


@dataclass
class Attaque:
    nom: str
    type_attaque: TypeAttaque
    degats_min: int
    degats_max: int
    chance_critique: float = 0.15
    description: str = ""
    effet_special: Optional[Callable] = None

    def lancer(self, attaquant: "EntiteCombat", cible: "EntiteCombat") -> Dict:
        """Lance l'attaque et retourne un dict avec les résultats."""
        degats_base = random.randint(self.degats_min, self.degats_max)
        critique = random.random() < self.chance_critique
        if critique:
            degats_base = int(degats_base * 1.5)
            resultat = f"CRITIQUE! {self.nom} frappe fort!"
        else:
            resultat = f"{self.nom} touche."
        # Calcule les dégâts réels en fonction de la défense
        defense_cible = cible.defense
        if self.type_attaque == TypeAttaque.MIAOU:
            # Les attaques miaou ignorent une partie de la défense (magie pure)
            defense_cible = int(defense_cible * 0.5)
        degats_finaux = max(1, degats_base - defense_cible // 2)
        cible.pv -= degats_finaux
        return {
            "attaquant": attaquant.nom,
            "cible": cible.nom,
            "attaque": self.nom,
            "degats": degats_finaux,
            "critique": critique,
            "message": resultat,
            "cible_pv_restant": max(0, cible.pv),
        }


@dataclass
class EntiteCombat:
    nom: str
    pv_max: int
    pv: int
    attaque: int
    defense: int
    vitesse: int
    niveau: int = 1
    experience: int = 0
    experience_next: int = 100
    attaques: List[Attaque] = field(default_factory=list)
    est_joueur: bool = False
    loot: Dict[str, int] = field(default_factory=dict)  # ressources tuées

    def est_vivant(self) -> bool:
        return self.pv > 0

    def subir_degats(self, degats: int) -> None:
        self.pv = max(0, self.pv - degats)

    def attaquer(self, cible: "EntiteCombat", attaque_index: int = 0) -> Dict:
        if not self.attaques:
            # Attaque de base si aucune attaque définie
            degats = random.randint(self.attaque // 2, self.attaque)
            cible.subir_degats(degats)
            return {
                "attaquant": self.nom,
                "cible": cible.nom,
                "attaque": "Attaque basique",
                "degats": degats,
                "critique": False,
                "message": f"{self.nom} attaque {cible.nom} et inflige {degats} dégâts.",
                "cible_pv_restant": cible.pv,
            }
        if attaque_index < 0 or attaque_index >= len(self.attaques):
            attaque_index = 0
        return self.attaques[attaque_index].lancer(self, cible)

    def gagner_experience(self, montant: int) -> List[str]:
        """Accorde de l'expérience et monte de niveau si nécessaire. Retourne les messages de progression."""
        msgs = []
        self.experience += montant
        while self.experience >= self.experience_next:
            self.experience -= self.experience_next
            self.niveau += 1
            self.pv_max += 10
            self.pv = self.pv_max  # heal complet
            self.attaque += 2
            self.defense += 1
            self.vitesse += 1
            self.experience_next = int(self.experience_next * 1.2)
            msgs.append(f"🎉 {self.nom} monte au niveau {self.niveau} ! PV max +10, attaque +2, défense +1, vitesse +1.")
        return msgs


# === Attagues prédéfinies ===

# Joueur / Gestapesto
ATTAQUE_MIAOU = Attaque(
    nom="Miaou! (Attaque 6-7)",
    type_attaque=TypeAttaque.MIAOU,
    degats_min=8,
    degats_max=14,
    chance_critique=0.2,
    description="Miaulement sacré qui transperce les défenses."
)

ATTAQUE_STICK_SALI = Attaque(
    nom="Bâton sali",
    type_attaque=TypeAttaque.PHYSIQUE,
    degats_min=6,
    degats_max=12,
    chance_critique=0.1,
    description="Coup de bâton imprégné de fromage pourri."
)

ATTAQUE_KEBAB_EXPLOSIF = Attaque(
    nom="Kebab explosif",
    type_attaque=TypeAttaque.KEBAB_EXPLOSIF,
    degats_min=10,
    degats_max=18,
    chance_critique=0.15,
    description="Kebab intergalactique qui explose au contact."
)

ATTAQUE_JUS_ECORCE = Attaque(
    nom="Jet de jus d'écorce",
    type_attaque=TypeAttaque.ALCHIMIQUE,
    degats_min=5,
    degats_max=10,
    chance_critique=0.12,
    description="Liquide alchimique corrosif."
)

ATTAQUE_POUSSIERE_LOLI = Attaque(
    nom="Poussière de Loli",
    type_attaque=TypeAttaque.ALCHIMIQUE,
    degats_min=4,
    degats_max=9,
    chance_critique=0.25,
    description="Poudre phosphorescente qui rend les ennemis confus."
)

# Ennemis
ATTAQUE_SPAM = Attaque(
    nom="Spam fromager infect",
    type_attaque=TypeAttaque.PHYSIQUE,
    degats_min=3,
    degats_max=7,
    chance_critique=0.05,
    description="Le spam attaque en groupe."
)

ATTAQUE_VOL_CHIASSE = Attaque(
    nom="Vol de chiasse",
    type_attaque=TypeAttaque.MIAOU,
    degats_min=6,
    degats_max=12,
    chance_critique=0.2,
    description="Xi tente de dérober votre chiasse."
)

ATTAQUE_CHIMIQUE = Attaque(
    nom="Vapeur chimique d'Alsachimie",
    type_attaque=TypeAttaque.ALCHIMIQUE,
    degats_min=5,
    degats_max=11,
    chance_critique=0.1,
    description="Produits toxiques des usines."
)

ATTAQUE_FUTANARI = Attaque(
    nom="Transformation futa",
    type_attaque=TypeAttaque.PHYSIQUE,
    degats_min=7,
    degats_max=13,
    chance_critique=0.15,
    description="Thomas Mauvais utilise ses pouvoirs d'alchimie pervertie."
)


# === Fabrique d'ennemis ===
def creer_spam_fromager() -> EntiteCombat:
    return EntiteCombat(
        nom="Spam Fromager Infect",
        pv_max=30,
        pv=30,
        attaque=4,
        defense=1,
        vitesse=2,
        niveau=1,
        experience=25,
        experience_next=100,
        attaques=[ATTAQUE_SPAM],
        loot={"fromage_avarie": random.randint(1, 2), "poussiere_loli": 0},
    )


def creer_xi() -> EntiteCombat:
    return EntiteCombat(
        nom="Xi (Voleur de chiasse)",
        pv_max=70,
        pv=70,
        attaque=9,
        defense=3,
        vitesse=5,
        niveau=3,
        experience=100,
        experience_next=300,
        attaques=[ATTAQUE_VOL_CHIASSE, ATTAQUE_CHIMIQUE],
        loot={"chiasse_retrouvee": 1, "kebab_explosif": random.randint(0, 1)},
    )


def creer_thomas_mauvais() -> EntiteCombat:
    return EntiteCombat(
        nom="Thomas Mauvais (technicien Alsachimie)",
        pv_max=50,
        pv=50,
        attaque=7,
        defense=4,
        vitesse=3,
        niveau=2,
        experience=60,
        experience_next=200,
        attaques=[ATTAQUE_CHIMIQUE, ATTAQUE_FUTANARI],
        loot={"preuves_alsachimie": 1, "n2o": random.randint(0, 2)},
    )


def creer_kebab_explosif() -> EntiteCombat:
    return EntiteCombat(
        nom="Kebab explosif",
        pv_max=20,
        pv=20,
        attaque=10,
        defense=0,
        vitesse=1,
        niveau=1,
        experience=15,
        experience_next=100,
        attaques=[Attaque(
            nom="Explosion",
            type_attaque=TypeAttaque.KEBAB_EXPLOSIF,
            degats_min=8,
            degats_max=15,
            chance_critique=0.3,
            description="Explosion massive au moment de la mort."
        )],
        loot={"embryon_kebab": 1},
    )


def creer_joueur(nom: str = "Agent de la Gestapesto") -> EntiteCombat:
    return EntiteCombat(
        nom=nom,
        pv_max=100,
        pv=100,
        attaque=8,
        defense=3,
        vitesse=4,
        niveau=1,
        experience=0,
        experience_next=100,
        attaques=[ATTAQUE_MIAOU, ATTAQUE_STICK_SALI, ATTAQUE_KEBAB_EXPLOSIF, ATTAQUE_JUS_ECORCE, ATTAQUE_POUSSIERE_LOLI],
        est_joueur=True,
        loot={},
    )


# === Système de tour par tour ===
def tour_combat(joueur: EntiteCombat, ennemi: EntiteCombat) -> Tuple[Dict, bool]:
    """Exécute un tour de combat complet (joueur puis ennemi). Retourne (log_combat, fini)."""
    log = []
    # --- Tour du joueur ---
    # Le joueur choisit une attaque (aléatoirement ici, en version simple)
    attaque_index = random.randint(0, len(joueur.attaques) - 1)
    resultat_joueur = joueur.attaquer(ennemi, attaque_index)
    log.append(f"{resultat_joueur['attaquant']} utilise {resultat_joueur['attaque']} !")
    log.append(resultat_joueur["message"])
    if not ennemi.est_vivant():
        log.append(f"☠️  {ennemi.nom} est vaincu !")
        return log, True
    # --- Tour de l'ennemi ---
    resultat_ennemi = ennemi.attaquer(joueur, 0)
    log.append(f"{resultat_ennemi['attaquant']} utilise {resultat_ennemi['attaque']} !")
    log.append(resultat_ennemi["message"])
    if not joueur.est_vivant():
        log.append(f"💀 {joueur.nom} est mort ! (Mais la Gestapesto vous ramènera...)")
        return log, True
    return log, False


if __name__ == "__main__":
    # Démo rapide
    j = creer_joueur("Agent X")
    e = creer_spam_fromager()
    print(f"Combat : {j.nom} (PV: {j.pv}) vs {e.nom} (PV: {e.pv})")
    tour = 1
    while j.est_vivant() and e.est_vivant():
        print(f"\n--- Tour {tour} ---")
        log, fini = tour_combat(j, e)
        for ligne in log:
            print(ligne)
        if fini:
            break
        tour += 1
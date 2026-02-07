#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monde du Glaire Obscur : lieux, événements, états.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional, Tuple
from enum import Enum, auto


class Zone(Enum):
    GLAIRE_OBSCUR = auto()
    CHATEAU_PINELLI = auto()
    LABORATOIRE_ALCHIMIQUE = auto()
    USINE_ALSACHIMIE = auto()
    SALLE_SECRETE = auto()
    DECISION_TREES = auto()
    KEBAB_INTERGALACTIQUE = auto()
    RESIDENCE_DORIAN_P = auto()
    QG_GESTAPESTO = auto()


@dataclass
class Lieu:
    nom: str
    zone: Zone
    description: str
    evenements_possibles: List[str]
    危険_level: int = 1  # 1-5
    ressources: Dict[str, int] = field(default_factory=dict)  # ex: {"fromage_de_femme": 2, "poussiere_loli": 1}
    personnages_presents: List[str] = field(default_factory=list)  # noms de personnages

    def explorer(self) -> Dict:
        """Retourne un événement aléatoire d'exploration."""
        if self.evenements_possibles:
            evenement = random.choice(self.evenements_possibles)
        else:
            evenement = "Rien de spécial ne se passe..."
        return {
            "lieu": self.nom,
            "evenement": evenement,
            "danger": self.危険_level,
            "ressources_trouvees": {k: v for k, v in self.ressources.items() if random.random() < 0.5}
        }


# === Définition des lieux ===

# 1. Glaire Obscur (zone principale, mouvante)
GLAIRE = Lieu(
    nom="Le Glaire Obscur",
    zone=Zone.GLAIRE_OBSCUR,
    description="Un espace visqueux et changeant, rempli de lumière lactée et de décision trees qui miaulent. Le cœur du fromage intergalactique.",
    evenements_possibles=[
        "Vous entendez un miaulement lointain...",
        "Un spam fromager surgit d'un coin sombre!",
        "Le sol tremble, un kebab explosif apparaît!",
        "Une lueur 6-7 vous guide vers un objet brillant.",
        "Vous croisez une silhouette phosphorescente (agent secret).",
        "Le jus d'écorce suinte des parois...",
        "Vous sentez l'odeur du fromage de femme frais.",
        "Des Loli dansent en ronde dans le brouillard.",
    ],
    危険_level=3,
    ressources={"poussiere_loli": random.randint(0, 2), "jus_ecorce": random.randint(1, 3)},
    personnages_presents=["agent_secret"]
)

# 2. Château de Miss Pinelli
CHATEAU = Lieu(
    nom="Château de Miss Pinelli",
    zone=Zone.CHATEAU_PINELLI,
    description="Résidence officielle de la Présidente. Des lunettes carrées traînent sur des parapets de fromage. L'ambiance est solennelle.",
    evenements_possibles=[
        "Miss Pinelli vous convoque pour un briefing.",
        "Vous trouvez une formule alchimique écrite dans le fromage.",
        "Une cérémonie d'initiation est en cours.",
        "Le conseil strategique discute du plan Quoicumbeh.",
        "Rien, juste le silence respectueux.",
    ],
    危険_level=1,
    ressources={"formule_fromagere": 1},
    personnages_presents=["Miss Pinelli", "Tonton MaziniiX_"]
)

# 3. Laboratoire alchimique
LABORATOIRE = Lieu(
    nom="Laboratoire Alchimique Secret",
    zone=Zone.LABORATOIRE_ALCHIMIQUE,
    description="Pièce où Gérard le Mouleur fabrique le fromage de femme. Des fioles de N2O grésillent.",
    evenements_possibles=[
        "Gérard vous apprend une étape de la recette 6.7.",
        "Un explodeur de N2O surchauffe! Danger!",
        "Vous découvrez un échantillon de fromage de femme en cours d'affinage.",
        "Le chronomètre en os de licorne sonne la fin du pétrissage.",
        "Des bulles de N2O envahissent la pièce.",
    ],
    危険_level=2,
    ressources={"fromage_femme_partiel": random.randint(0, 1), "n2o": random.randint(1, 2)},
    personnages_presents=["Gérard le Mouleur"]
)

# 4. Usine Alsachimie
ALSACHIMIE = Lieu(
    nom="Usine Alsachimie (filiale BASF)",
    zone=Zone.USINE_ALSACHIMIE,
    description="Complexe industriel chimique. Des cuves de polyamide et des odeurs suspectes. Thomas Mauvais pourrait être là.",
    evenements_possibles=[
        "Vous surprenez Thomas Mauvais en train de fabriquer du fromage de femme clandestinement!",
        "Des vapeurs chimiques transforment les travailleurs en futanari-alchimiques.",
        "Vous trouvez des documents compromettants sur la chiasse volée.",
        "Xi est en train de superviser une livraison de kebab explosif.",
        "L'alarme retentit : intrusion dans le glaire obscur!",
    ],
    危険_level=4,
    ressources={"preuves_alsachimie": 1, "kebab_explosif": random.randint(0, 2)},
    personnages_presents=["Thomas Mauvais", "Xi", "travailleurs_contamines"]
)

# 5. Salle secrète
SALLE_SECRETE = Lieu(
    nom="Salle Secrète sous le château",
    zone=Zone.SALLE_SECRETE,
    description="Pièce cachée remplie de bougies en écorce de decision tree. Lieu des initiations et des rituels.",
    evenements_possibles=[
        "Une nouvelle recrue est en train d'être initiée!",
        "Vous trouvez un pinceau sali sacré.",
        "Des larmes phosphorescentes de Pierre Pierre Chartier tracent des symboles.",
        "Le miaulement rituel résonne : 'QUOICUMBEH!'",
        "Le sol est couvert de fromage de femme frais.",
    ],
    危険_level=1,
    ressources={"pinceau_sali": 1, "fromage_femme_frais": random.randint(0, 1)},
    personnages_presents=["Pierre Pierre Chartier", "Lilian"]
)

# 6. Decision Trees
DECISION_TREES = Lieu(
    nom="Forêt des Decision Trees",
    zone=Zone.DECISION_TREES,
    description="Arbres qui prennent des décisions et miaulent. L'endroit idéal pour l'épluchage stratégique.",
    evenements_possibles=[
        "Un arbre miaule faux : il faut l'élaguer!",
        "Le gradient de la chiasse coule dans les branches.",
        "Tonton MaziniiX_ vous apprend l'art du pruning.",
        "Un arbre infecté par le spam fromager attaque!",
        "Vous obtenez un fruit de décision rare (6-7).",
    ],
    危険_level=2,
    ressources={"fruit_decision": random.randint(0, 2), "jus_ecorce": 1},
    personnages_presents=["Tonton MaziniiX_"]
)

# 7. Kebab intergalactique
KEBAB = Lieu(
    nom="Kebab Intergalactique",
    zone=Zone.KEBAB_INTERGALACTIQUE,
    description="Comptoir cosmique où le kebab est servi avec des sauces fromagères rares. Lieu de rencontres interdimensionnelles.",
    evenements_possibles=[
        "Un kebab explosif à moitié caché attire votre attention.",
        "Vous croisez un voyageur du futur (Pierre Pierre Chartier).",
        "Le patron demande de l'aide contre un envahisseur Xi.",
        "Vous achetez un kebab intergalactique (soigne 10 PV).",
        "Des extra-terrestres fromagers sont à la table d'à côté.",
    ],
    危険_level=1,
    ressources={"kebab_normal": random.randint(1, 3), "sauce_fromagere": random.randint(0, 2)},
    personnages_presents=["Pierre Pierre Chartier"]
)

# 8. Résidence de Dorian P
RESIDENCE_DORIAN_P = Lieu(
    nom="Résidence de Dorian P",
    zone=Zone.RESIDENCE_DORIAN_P,
    description="Lieu de vie discret de Dorian P. La chiasse volée était cachée ici avant le vol.",
    evenements_possibles=[
        "Des traces de lutte et du jus d'écorce partout.",
        "Un message codé de Xi laisse des indices.",
        "Dorian P vous supplie de récupérer sa chiasse.",
        "Un stick sali abandonné gît sur le sol.",
        "Une odeur de N2O persiste : l'endroit a été piégé.",
    ],
    危険_level=2,
    ressources={"indices_chiasse": 1, "stick_sali": random.randint(0, 1)},
    personnages_presents=["Dorian P"]
)

# 9. QG Gestapesto
QG = Lieu(
    nom="QG de la Gestapesto",
    zone=Zone.QG_GESTAPESTO,
    description="Quartier général secret. Table de stratège, cartes du glaire obscur, et stock de fromage et munitions.",
    evenements_possibles=[
        "Briefing général : l'activation 6-7 est imminente.",
        "Vous recevez une mission : nettoyer le spam, récupérer la chiasse, etc.",
        "Tonton MaziniiX_ présente son plan Quoicumbeh.",
        "Le moral des troupes est bon : tout le monde miaule.",
        "Des rapports font état d'une invasion d'Xi au sud.",
    ],
    危険_level=0,
    ressources={"mission_urgence": 1, "rations_fromagères": 2},
    personnages_presents=["Miss Pinelli", "Tonton MaziniiX_", "Gérard le Mouleur", "Papa Basil"]
)

# === Carte dynamique ===
CARTE_DU_GLAIRE: Dict[Zone, Lieu] = {
    Zone.GLAIRE_OBSCUR: GLAIRE,
    Zone.CHATEAU_PINELLI: CHATEAU,
    Zone.LABORATOIRE_ALCHIMIQUE: LABORATOIRE,
    Zone.USINE_ALSACHIMIE: ALSACHIMIE,
    Zone.SALLE_SECRETE: SALLE_SECRETE,
    Zone.DECISION_TREES: DECISION_TREES,
    Zone.KEBAB_INTERGALACTIQUE: KEBAB,
    Zone.RESIDENCE_DORIAN_P: RESIDENCE_DORIAN_P,
    Zone.QG_GESTAPESTO: QG,
}


def obtenir_lieu(zone: Zone) -> Lieu:
    return CARTE_DU_GLAIRE.get(zone, GLAIRE)


def deplacement_aleatoire(zone_actuelle: Zone) -> Zone:
    """Retourne une zone voisine (aléatoire)."""
    zones = list(Zone)
    # Exclure la zone actuelle
    zones_possibles = [z for z in zones if z != zone_actuelle]
    return random.choice(zones_possibles)


# Test
if __name__ == "__main__":
    print("=== Carte du Glaire Obscur ===")
    for zone, lieu in CARTE_DU_GLAIRE.items():
        print(f"- {lieu.nom} (danger {lieu.危険_level}/5)")
        print(f"  Description : {lieu.description[:80]}...")
        print(f"  Evenements : {len(lieu.evenements_possibles)} types")
        print()
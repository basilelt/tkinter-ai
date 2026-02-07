#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personnages de l'univers du Glaire Obscur et de la Gestapesto.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto


class Archetype(Enum):
    COMMANDANT = auto()
    EXPERT = auto()
    AGENT = auto()
    STRATEGE = auto()
    DESTRUCTEUR = auto()
    MYTHIQUE = auto()
    ENVAHISSEUR = auto()


@dataclass
class Personnage:
    nom: str
    archetype: Archetype
    titre: str
    description: str
    traits: List[str] = field(default_factory=list)
    lieux_affiliation: List[str] = field(default_factory=list)
    quest_liees: List[str] = field(default_factory=list)

    def presentation(self) -> str:
        return f"{self.titre} {self.nom} : {self.description}"


# === Commandants ===
MISS_PINELLI = Personnage(
    nom="Miss Pinelli",
    archetype=Archetype.COMMANDANT,
    titre="Présidente / Commandante en chef",
    description="Chef de la Gestapesto, lunettes carrées, écrit des formules dans le fromage. Elle guide les opérations dans le glaire obscur.",
    traits=["autoritaire", "visionnaire", "maternelle (maman)"],
    lieux_affiliation=["glaire obscur", "château de Miss Pinelli"],
    quest_liees=["initiation", "defense_glaire", "recuperer_chiasse"]
)

LILIAN = MISS_PINELLI  # alias
PRESIDENTE_LILIAN = MISS_PINELLI

# === Experts ===
GERARD_LE_MOULEUR = Personnage(
    nom="Gérard le Mouleur",
    archetype=Archetype.EXPERT,
    titre="Expert foutreanari 24/7, certification 6.7",
    description="Maître de l'alchimie fromagère. Il connaît tous les secrets du fromage de femme et du N2O.",
    traits=["perfectionniste", "exigeant", "un peu crade"],
    lieux_affiliation=["laboratoire alchimique", "glaire obscur"],
    quest_liees=["creer_fromage", "purifier_glaire"]
)

# === Agents ===
PIERRE_PIERRE_CHARTIER = Personnage(
    nom="Pierre Pierre Chartier X2007",
    archetype=Archetype.AGENT,
    titre="Agent temporel aux larmes phosphorescentes",
    description="Agent spécial capable de pleurer des larmes qui brillent. Il opère à travers le temps.",
    traits=["mélancolique", "fiable", "traumatisé par le fromage"],
    lieux_affiliation=["salles secrètes", "glaire obscur"],
    quest_liees=["mission_temps", "recup_chiasse"]
)

PAPA_BASIL = Personnage(
    nom="Papa Basil",
    archetype=Archetype.AGENT,
    titre="Force de frappe kebab-grenade",
    description="Combatif armé de kebabs explosifs. Il nettoie le spam fromager sans ménagement.",
    traits=["agressif", "loyal", "amateur de kebab"],
    lieux_affiliation=["zones de combat", "glaire obscur"],
    quest_liees=["nettoyer_spam", "assaut_alsachimie"]
)

# === Stratèges ===
TONTON_MAZINIIX_ = Personnage(
    nom="Tonton MaziniiX_",
    archetype=Archetype.STRATEGE,
    titre="Conseiller stratégique, inventeur du quoicoufoutre",
    description="Pense les décisions stratégiques, maîtrise l'épluchage des decision trees. Son mot d'ordre : \"QUOICUMBEH!\"",
    traits=["mystérieux", "ingénieux", "un peu taré"],
    lieux_affiliation=["salle de strategy", "glaire obscur"],
    quest_liees=["decision_trees", "contre_attaque"]
)

# === Destructeurs ===
LOLI_YASSINE = Personnage(
    nom="Loli Yassine",
    archetype=Archetype.DESTRUCTEUR,
    titre="Destructeur des mondes",
    description="Entité crainte, allégeance au sperme, jus, cum. Il peut anéantir les dimensions fromagères.",
    traits=["dévastateur", "incontrôlable", "respecté"],
    lieux_affiliation=["les ombres du glaire", "intergalactique"],
    quest_liees=["apocalypse_fromagere", "detruire_xi"]
)

# === Mythique ===
ENSICUCK = Personnage(
    nom="Ensicuck",
    archetype=Archetype.MYTHIQUE,
    titre="Le plus bel homme du glaire obscur",
    description="Figure légendaire, objet de tous les hommages. On murmure son nom dans les rituels.",
    traits=["mystique", "vénéré", "insaisissable"],
    lieux_affiliation=["mythes du fromage", "glaire obscur"],
    quest_liees=["recherche_ensicuck", "rituel"]
)

# === Envahisseurs / Antagonistes ===
XI = Personnage(
    nom="Xi",
    archetype=Archetype.ENVAHISSEUR,
    titre="Voleur de chiasse intergalactique",
    description="Adversaire principal, a dérobé la chiasse de Dorian P. Il veut corrompre le fromage de femme.",
    traits=["rusé", "sournois", "ennemi juré de la Gestapesto"],
    lieux_affiliation=["usines Alsachimie", "kebab intergalactique"],
    quest_liees=["recuperer_chiasse", "detruire_xi"]
)

SPAM_FROMAGER = Personnage(
    nom="Spam Fromager Attaquant",
    archetype=Archetype.ENVAHISSEUR,
    titre="Élementaire du fromage avarié",
    description="Créature parasite qui infeste le glaire obscur, génère du spam et de la pourriture lactique.",
    traits=["infect", "répugnant", "en meute"],
    lieux_affiliation=["zones polluées", "glaire obscur"],
    quest_liees=["nettoyer_spam"]
)

THOMAS_MAUVAIS = Personnage(
    nom="Thomas Mauvais",
    archetype=Archetype.ENVAHISSEUR,
    titre="Technicien suspect d'Alsachimie",
    description="Employé d'Alsachimie, peut-être impliqué dans la fabrication clandestine de fromage de femme. Son nom est ironique... ou pas.",
    traits=["ambigu", "travailleur", "potentiellement futanari-alchimique"],
    lieux_affiliation=["Alsachimie", "usines polyamide"],
    quest_liees=["enquete_alsachimie", "infiltrer_usine"]
)

# === Figures accessoires ===
CHRIST_SYLVAIN_PIERRE_DURIF = Personnage(
    nom="Christ Sylvain Pierre Durif",
    archetype=Archetype.ENVAHISSEUR,
    titre="Cible de la lettre de mise en demeure",
    description="Individu ayant volé la chiasse de Dorian P et déréglé le jus d'écorce.",
    traits=["filou", "introuvable", "cité dans les textes légaux du fromage"],
    lieux_affiliation=["inconnu"],
    quest_liees=["lettre_mise_demeure"]
)

DORIAN_P = Personnage(
    nom="Dorian P",
    archetype=Archetype.AGENT,
    titre="Victime de la chiasse volée",
    description="Membre de la Gestapesto dont la chiasse a été dérobée. Il attend son retour.",
    traits="victime déterminé",
    lieux_affiliation=["glaire obscur"],
    quest_liees=["recuperer_chiasse"]
)

# === Rassemblement ===
TOUS_LES_PERSONNAGES = [
    MISS_PINELLI, LILIAN, PRESIDENTE_LILIAN,
    GERARD_LE_MOULEUR,
    PIERRE_PIERRE_CHARTIER,
    PAPA_BASIL,
    TONTON_MAZINIIX_,
    LOLI_YASSINE,
    ENSICUCK,
    XI,
    SPAM_FROMAGER,
    THOMAS_MAUVAIS,
    CHRIST_SYLVAIN_PIERRE_DURIF,
    DORIAN_P,
]

# Index par nom (minuscules, sans accents simples)
INDEX_NOMS: Dict[str, Personnage] = {
    p.nom.lower().replace(" ", "").replace("é", "e").replace("è", "e").replace("à", "a"): p
    for p in TOUS_LES_PERSONNAGES
}


def trouver_personnage(terme: str) -> Optional[Personnage]:
    """
    Recherche un personnage par un terme (nom partiel, insensible à la casse).
    """
    terme_clean = terme.lower().strip()
    for key, p in INDEX_NOMS.items():
        if terme_clean in key or key in terme_clean:
            return p
    return None


def liste_personnages_par_archetype(archetype: Archetype) -> List[Personnage]:
    return [p for p in TOUS_LES_PERSONNAGES if p.archetype == archetype]


if __name__ == "__main__":
    print("=== Personnages de la Gestapesto ===")
    for p in TOUS_LES_PERSONNAGES:
        print(f"- {p.titre} : {p.nom}")
    print(f"\nTotal : {len(TOUS_LES_PERSONNAGES)} personnages.")
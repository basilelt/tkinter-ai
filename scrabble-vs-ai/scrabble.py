"""
Scrabble avec interface Tkinter et IA Minimax
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from collections import Counter
import copy

# ==================== CONSTANTES ====================

# Valeurs des lettres en français
LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3, 'Q': 8, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10, '*': 0
}

# Distribution des lettres (version française simplifiée)
LETTER_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 3, 'E': 15, 'F': 2, 'G': 2, 'H': 2, 'I': 8,
    'J': 1, 'K': 1, 'L': 5, 'M': 3, 'N': 6, 'O': 6, 'P': 2, 'Q': 1, 'R': 6,
    'S': 6, 'T': 6, 'U': 6, 'V': 2, 'W': 1, 'X': 1, 'Y': 1, 'Z': 1, '*': 2
}

# Cases spéciales du plateau (positions du Scrabble standard)
# MT = Mot Triple, MD = Mot Double, LT = Lettre Triple, LD = Lettre Double
BOARD_SIZE = 15
CENTER = 7

TRIPLE_WORD = [(0,0), (0,7), (0,14), (7,0), (7,14), (14,0), (14,7), (14,14)]
DOUBLE_WORD = [(1,1), (2,2), (3,3), (4,4), (1,13), (2,12), (3,11), (4,10),
               (13,1), (12,2), (11,3), (10,4), (13,13), (12,12), (11,11), (10,10),
               (7,7)]  # Centre
TRIPLE_LETTER = [(1,5), (1,9), (5,1), (5,5), (5,9), (5,13),
                 (9,1), (9,5), (9,9), (9,13), (13,5), (13,9)]
DOUBLE_LETTER = [(0,3), (0,11), (2,6), (2,8), (3,0), (3,7), (3,14),
                 (6,2), (6,6), (6,8), (6,12), (7,3), (7,11),
                 (8,2), (8,6), (8,8), (8,12), (11,0), (11,7), (11,14),
                 (12,6), (12,8), (14,3), (14,11)]

# Couleurs
COLORS = {
    'board': '#C4A484',
    'triple_word': '#FF6B6B',
    'double_word': '#FFB6C1',
    'triple_letter': '#4ECDC4',
    'double_letter': '#87CEEB',
    'center': '#FFD700',
    'tile': '#F5DEB3',
    'selected': '#90EE90',
    'placed': '#DDA0DD'
}

# Dictionnaire français simplifié (mots courants de 2-7 lettres)
DICTIONARY = {
    'AA', 'AH', 'AI', 'AN', 'AS', 'AU', 'AY', 'BA', 'BE', 'BI', 'BU', 'CA', 'CE',
    'CI', 'DA', 'DE', 'DO', 'DU', 'EH', 'EN', 'ES', 'ET', 'EU', 'EX', 'FA', 'FI',
    'GO', 'HA', 'HE', 'HI', 'HO', 'IF', 'IL', 'IN', 'JE', 'KA', 'LA', 'LE', 'LI',
    'LU', 'MA', 'ME', 'MI', 'MU', 'NA', 'NE', 'NI', 'NO', 'NU', 'OC', 'OH', 'ON',
    'OR', 'OS', 'OU', 'PI', 'PU', 'QI', 'RA', 'RE', 'RI', 'RU', 'SA', 'SE', 'SI',
    'SU', 'TA', 'TE', 'TU', 'UN', 'US', 'UT', 'VA', 'VU', 'WU', 'XI',
    # Mots de 3 lettres
    'AIE', 'AIL', 'AIR', 'AME', 'AMI', 'ANE', 'ANS', 'ARC', 'ARE', 'ART', 'BAL',
    'BAS', 'BAT', 'BEC', 'BEL', 'BEN', 'BIS', 'BLE', 'BOA', 'BOL', 'BON', 'BUS',
    'BUT', 'CAP', 'CAR', 'CAS', 'CEP', 'CES', 'CLE', 'COL', 'COQ', 'COR', 'COU',
    'CRI', 'CRU', 'CUL', 'DES', 'DIX', 'DON', 'DOS', 'DUC', 'DUR', 'EAU', 'ECU',
    'ELU', 'ERE', 'EST', 'ETE', 'EUX', 'FAN', 'FAR', 'FAX', 'FEE', 'FER', 'FEU',
    'FIL', 'FIN', 'FIS', 'FIT', 'FOI', 'FOU', 'FUR', 'GAI', 'GAL', 'GAZ', 'GEL',
    'GIT', 'GUI', 'ICI', 'ILE', 'JET', 'JEU', 'JUS', 'KIT', 'LAC', 'LAS', 'LAV',
    'LES', 'LIT', 'LOI', 'LOU', 'LUI', 'LUX', 'MAI', 'MAL', 'MAS', 'MAT', 'MAX',
    'MER', 'MES', 'MET', 'MIE', 'MIS', 'MOI', 'MOT', 'MOU', 'MUR', 'MUS', 'NET',
    'NEZ', 'NID', 'NON', 'NOS', 'NUE', 'NUI', 'NUL', 'NUS', 'OIE', 'OUI', 'OUR',
    'PAN', 'PAR', 'PAS', 'PAT', 'PAU', 'PEU', 'PIE', 'PIN', 'PLI', 'POT', 'PRE',
    'PRI', 'PUA', 'PUB', 'PUR', 'QUE', 'QUI', 'RAI', 'RAS', 'RAT', 'RAZ', 'RIS',
    'RIT', 'RIZ', 'ROC', 'ROI', 'RUE', 'RUS', 'RUT', 'SAC', 'SEC', 'SEL', 'SES',
    'SKI', 'SOI', 'SOL', 'SON', 'SOU', 'SUA', 'SUD', 'SUR', 'SUS', 'TAC', 'TAS',
    'TEL', 'TES', 'THE', 'TIC', 'TIR', 'TOI', 'TON', 'TOP', 'TOT', 'TRI', 'TUE',
    'UNE', 'UNI', 'UNS', 'URE', 'USA', 'VAN', 'VAS', 'VAU', 'VER', 'VIA', 'VIE',
    'VIF', 'VIN', 'VIS', 'VIT', 'VOL', 'VOS', 'VUE', 'VUS', 'ZEN', 'ZOO',
    # Mots de 4-7 lettres courants
    'AIDE', 'AILE', 'AINE', 'AIRE', 'AISE', 'AMER', 'AMIE', 'ANGE', 'ANIS',
    'ARME', 'AUBE', 'AVEC', 'AVIS', 'BAIN', 'BEAU', 'BIEN', 'BLEU', 'BOIS',
    'BOUT', 'BRAS', 'CAFE', 'CAGE', 'CALME', 'CAMP', 'CANE', 'CAPE', 'CASE',
    'CAVE', 'CECI', 'CELA', 'CENT', 'CEUX', 'CHAT', 'CHER', 'CHEZ', 'CIEL',
    'CINQ', 'CITE', 'CLEF', 'COIN', 'COLE', 'COMA', 'CONE', 'COTE', 'COUP',
    'COUR', 'DAME', 'DANS', 'DATE', 'DEJA', 'DEUX', 'DIEU', 'DIRE', 'DOIT',
    'DONC', 'DONT', 'DOUX', 'DRAP', 'DURE', 'EAUX', 'ELLE', 'ELLES', 'ENCORE',
    'ENTRE', 'ETAIT', 'ETAT', 'ETRE', 'FACE', 'FAIT', 'FAIM', 'FAIS', 'FAUT',
    'FAUX', 'FETE', 'FILE', 'FILS', 'FINE', 'FOIS', 'FOND', 'FONT', 'FORT',
    'FOUT', 'GARE', 'GARS', 'GENS', 'GOUT', 'GRIS', 'GROS', 'HAUT', 'HERBE',
    'HEURE', 'HIER', 'HOMME', 'IDEE', 'ILES', 'IMAGE', 'JAMBE', 'JEAN', 'JEUX',
    'JOIE', 'JOUE', 'JOUR', 'JUGE', 'JUPE', 'JURE', 'JUSTE', 'KILO', 'LAIT',
    'LAME', 'LARD', 'LAVE', 'LEUR', 'LIEU', 'LIGNE', 'LIRE', 'LISTE', 'LIVRE',
    'LOIN', 'LONG', 'LORS', 'LOUP', 'LUNE', 'LUXE', 'MAGE', 'MAIN', 'MAIS',
    'MALE', 'MARE', 'MARS', 'MAUX', 'MERE', 'MIDI', 'MIEN', 'MIEUX', 'MISE',
    'MODE', 'MOIS', 'MONDE', 'MONT', 'MORT', 'MOTS', 'MULE', 'MURS', 'NAGE',
    'NERF', 'NEUF', 'NOEL', 'NOIR', 'NOMS', 'NORD', 'NOTE', 'NOUS', 'NUIT',
    'ONDE', 'PAGE', 'PAIE', 'PAIN', 'PAIX', 'PAPA', 'PARC', 'PART', 'PAYS',
    'PEAU', 'PERE', 'PEUT', 'PEUR', 'PIED', 'PILE', 'PIPE', 'PIRE', 'PLAN',
    'PLUS', 'PNEU', 'POIL', 'POIS', 'PONT', 'PORC', 'PORT', 'POSE', 'POUR',
    'PRES', 'PRET', 'PRIX', 'QUAI', 'QUEL', 'QUOI', 'RACE', 'RAGE', 'RAID',
    'RANG', 'RARE', 'RAVE', 'RAVI', 'RAYON', 'REEL', 'REIN', 'REND', 'RESTE',
    'REVE', 'RIEN', 'RIRE', 'RIVE', 'ROBE', 'ROLE', 'ROND', 'ROSE', 'ROUE',
    'RUDE', 'SAGE', 'SAIN', 'SALE', 'SANG', 'SANS', 'SAUF', 'SAUT', 'SEIN',
    'SENS', 'SEPT', 'SEUL', 'SIEN', 'SITE', 'SOIE', 'SOIR', 'SOLE', 'SOMME',
    'SONT', 'SORT', 'SOUS', 'STOP', 'SUIS', 'SUJET', 'SURE', 'TACT', 'TANT',
    'TARD', 'TAUX', 'TAXE', 'TELS', 'TEMPS', 'TENIR', 'TENU', 'TERRE', 'TETE',
    'TIEN', 'TIENT', 'TIGE', 'TIRE', 'TOIT', 'TOUS', 'TOUT', 'TRAM', 'TRES',
    'TROP', 'TROU', 'TRUE', 'TUBE', 'TYPE', 'UNIT', 'VAIN', 'VEAU', 'VENT',
    'VERS', 'VIDE', 'VIEUX', 'VILE', 'VILLE', 'VITE', 'VOIE', 'VOIR', 'VOIX',
    'VOTE', 'VOUS', 'VRAI', 'YEUX', 'ZERO', 'ZONE'
}


# ==================== CLASSES ====================

class Bag:
    """Sac de lettres"""
    def __init__(self):
        self.letters = []
        for letter, count in LETTER_DISTRIBUTION.items():
            self.letters.extend([letter] * count)
        random.shuffle(self.letters)
    
    def draw(self, count):
        """Piocher des lettres"""
        drawn = []
        for _ in range(min(count, len(self.letters))):
            drawn.append(self.letters.pop())
        return drawn
    
    def remaining(self):
        return len(self.letters)
    
    def is_empty(self):
        return len(self.letters) == 0


class Player:
    """Joueur (humain ou IA)"""
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.rack = []
        self.score = 0
    
    def add_letters(self, letters):
        self.rack.extend(letters)
    
    def remove_letters(self, letters):
        for letter in letters:
            if letter in self.rack:
                self.rack.remove(letter)
    
    def rack_string(self):
        return ''.join(sorted(self.rack))


class Board:
    """Plateau de jeu"""
    def __init__(self):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.first_move = True
    
    def get_cell(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.grid[row][col]
        return None
    
    def set_cell(self, row, col, letter):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            self.grid[row][col] = letter
    
    def is_empty(self, row, col):
        return self.get_cell(row, col) is None
    
    def get_multiplier(self, row, col):
        """Retourne le multiplicateur de la case"""
        if (row, col) in TRIPLE_WORD:
            return ('word', 3)
        elif (row, col) in DOUBLE_WORD:
            return ('word', 2)
        elif (row, col) in TRIPLE_LETTER:
            return ('letter', 3)
        elif (row, col) in DOUBLE_LETTER:
            return ('letter', 2)
        return ('none', 1)
    
    def copy(self):
        """Copie profonde du plateau"""
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        new_board.first_move = self.first_move
        return new_board


class Move:
    """Représente un coup"""
    def __init__(self, word, row, col, horizontal, letters_used):
        self.word = word
        self.row = row
        self.col = col
        self.horizontal = horizontal
        self.letters_used = letters_used  # Lettres du chevalet utilisées
        self.score = 0


class ScrabbleGame:
    """Logique du jeu"""
    def __init__(self):
        self.board = Board()
        self.bag = Bag()
        self.players = []
        self.current_player_idx = 0
        self.consecutive_passes = 0
        self.game_over = False
    
    def add_player(self, name, is_ai=False):
        player = Player(name, is_ai)
        player.add_letters(self.bag.draw(7))
        self.players.append(player)
    
    def current_player(self):
        return self.players[self.current_player_idx]
    
    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
    
    def calculate_word_score(self, word, start_row, start_col, horizontal, new_tiles_positions):
        """Calcule le score d'un mot"""
        score = 0
        word_multiplier = 1
        
        for i, letter in enumerate(word):
            if horizontal:
                row, col = start_row, start_col + i
            else:
                row, col = start_row + i, start_col
            
            letter_score = LETTER_VALUES.get(letter.upper(), 0)
            
            # Appliquer les bonus seulement pour les nouvelles tuiles
            if (row, col) in new_tiles_positions:
                mult_type, mult_value = self.board.get_multiplier(row, col)
                if mult_type == 'letter':
                    letter_score *= mult_value
                elif mult_type == 'word':
                    word_multiplier *= mult_value
            
            score += letter_score
        
        return score * word_multiplier
    
    def get_cross_words(self, row, col, letter, horizontal):
        """Trouve les mots croisés formés"""
        words = []
        
        # Direction perpendiculaire
        if horizontal:
            # Chercher verticalement
            start_row = row
            while start_row > 0 and self.board.get_cell(start_row - 1, col) is not None:
                start_row -= 1
            
            word = ""
            r = start_row
            while r < BOARD_SIZE:
                cell = self.board.get_cell(r, col)
                if cell is not None:
                    word += cell
                elif r == row:
                    word += letter
                else:
                    break
                r += 1
            
            if len(word) > 1:
                words.append((word, start_row, col, False))
        else:
            # Chercher horizontalement
            start_col = col
            while start_col > 0 and self.board.get_cell(row, start_col - 1) is not None:
                start_col -= 1
            
            word = ""
            c = start_col
            while c < BOARD_SIZE:
                cell = self.board.get_cell(row, c)
                if cell is not None:
                    word += cell
                elif c == col:
                    word += letter
                else:
                    break
                c += 1
            
            if len(word) > 1:
                words.append((word, row, start_col, True))
        
        return words
    
    def validate_placement(self, tiles_placed):
        """Valide le placement des tuiles"""
        if not tiles_placed:
            return False, "Aucune tuile placée"
        
        # Vérifier alignement
        rows = [t[0] for t in tiles_placed]
        cols = [t[1] for t in tiles_placed]
        
        horizontal = len(set(rows)) == 1
        vertical = len(set(cols)) == 1
        
        if not horizontal and not vertical:
            return False, "Les tuiles doivent être alignées"
        
        # Premier coup doit passer par le centre
        if self.board.first_move:
            if not any(r == CENTER and c == CENTER for r, c, _ in tiles_placed):
                center_covered = False
                if horizontal:
                    row = rows[0]
                    min_col, max_col = min(cols), max(cols)
                    if row == CENTER and min_col <= CENTER <= max_col:
                        center_covered = True
                else:
                    col = cols[0]
                    min_row, max_row = min(rows), max(rows)
                    if col == CENTER and min_row <= CENTER <= max_row:
                        center_covered = True
                
                if not center_covered:
                    return False, "Le premier mot doit passer par le centre"
        
        # Vérifier connexion avec le plateau (sauf premier coup)
        if not self.board.first_move:
            connected = False
            for row, col, _ in tiles_placed:
                # Vérifier les cases adjacentes
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        if self.board.get_cell(nr, nc) is not None:
                            connected = True
                            break
                if connected:
                    break
            
            if not connected:
                return False, "Le mot doit être connecté au plateau"
        
        return True, "OK"
    
    def get_formed_words(self, tiles_placed):
        """Récupère tous les mots formés par un placement"""
        if not tiles_placed:
            return []
        
        words = []
        rows = [t[0] for t in tiles_placed]
        cols = [t[1] for t in tiles_placed]
        
        horizontal = len(set(rows)) == 1
        
        # Créer une copie temporaire du plateau
        temp_board = self.board.copy()
        for row, col, letter in tiles_placed:
            temp_board.set_cell(row, col, letter)
        
        # Mot principal
        if horizontal:
            row = rows[0]
            # Trouver le début du mot
            start_col = min(cols)
            while start_col > 0 and temp_board.get_cell(row, start_col - 1) is not None:
                start_col -= 1
            
            # Construire le mot
            word = ""
            col = start_col
            while col < BOARD_SIZE and temp_board.get_cell(row, col) is not None:
                word += temp_board.get_cell(row, col)
                col += 1
            
            if len(word) > 1:
                words.append((word, row, start_col, True))
        else:
            col = cols[0]
            start_row = min(rows)
            while start_row > 0 and temp_board.get_cell(start_row - 1, col) is not None:
                start_row -= 1
            
            word = ""
            row = start_row
            while row < BOARD_SIZE and temp_board.get_cell(row, col) is not None:
                word += temp_board.get_cell(row, col)
                row += 1
            
            if len(word) > 1:
                words.append((word, start_row, col, False))
        
        # Mots croisés
        for row, col, letter in tiles_placed:
            if horizontal:
                # Chercher mot vertical
                start_row = row
                while start_row > 0 and temp_board.get_cell(start_row - 1, col) is not None:
                    start_row -= 1
                
                word = ""
                r = start_row
                while r < BOARD_SIZE and temp_board.get_cell(r, col) is not None:
                    word += temp_board.get_cell(r, col)
                    r += 1
                
                if len(word) > 1:
                    words.append((word, start_row, col, False))
            else:
                # Chercher mot horizontal
                start_col = col
                while start_col > 0 and temp_board.get_cell(row, start_col - 1) is not None:
                    start_col -= 1
                
                word = ""
                c = start_col
                while c < BOARD_SIZE and temp_board.get_cell(row, c) is not None:
                    word += temp_board.get_cell(row, c)
                    c += 1
                
                if len(word) > 1:
                    words.append((word, row, start_col, True))
        
        return words
    
    def validate_words(self, words):
        """Vérifie que tous les mots sont dans le dictionnaire"""
        invalid = []
        for word, _, _, _ in words:
            if word.upper() not in DICTIONARY:
                invalid.append(word)
        return invalid
    
    def calculate_move_score(self, tiles_placed):
        """Calcule le score total d'un coup"""
        words = self.get_formed_words(tiles_placed)
        new_positions = set((r, c) for r, c, _ in tiles_placed)
        
        total_score = 0
        for word, row, col, horizontal in words:
            total_score += self.calculate_word_score(word, row, col, horizontal, new_positions)
        
        # Bonus de 50 points pour utiliser les 7 lettres
        if len(tiles_placed) == 7:
            total_score += 50
        
        return total_score
    
    def play_move(self, tiles_placed):
        """Joue un coup"""
        # Valider le placement
        valid, msg = self.validate_placement(tiles_placed)
        if not valid:
            return False, msg, 0
        
        # Vérifier les mots formés
        words = self.get_formed_words(tiles_placed)
        if not words:
            return False, "Aucun mot valide formé", 0
        
        invalid_words = self.validate_words(words)
        if invalid_words:
            return False, f"Mots invalides: {', '.join(invalid_words)}", 0
        
        # Calculer le score
        score = self.calculate_move_score(tiles_placed)
        
        # Appliquer le coup
        for row, col, letter in tiles_placed:
            self.board.set_cell(row, col, letter)
        
        self.board.first_move = False
        self.current_player().score += score
        
        # Retirer les lettres du chevalet
        letters_used = [letter for _, _, letter in tiles_placed]
        self.current_player().remove_letters(letters_used)
        
        # Piocher de nouvelles lettres
        new_letters = self.bag.draw(len(letters_used))
        self.current_player().add_letters(new_letters)
        
        self.consecutive_passes = 0
        
        # Vérifier fin de partie
        if len(self.current_player().rack) == 0 and self.bag.is_empty():
            self.game_over = True
        
        return True, f"Mots formés: {', '.join(w[0] for w in words)}", score
    
    def pass_turn(self):
        """Passer son tour"""
        self.consecutive_passes += 1
        if self.consecutive_passes >= 4:  # 2 passes consécutives par joueur
            self.game_over = True
        self.next_turn()
    
    def exchange_letters(self, letters):
        """Échanger des lettres"""
        if self.bag.remaining() < len(letters):
            return False, "Pas assez de lettres dans le sac"
        
        player = self.current_player()
        for letter in letters:
            if letter not in player.rack:
                return False, f"Lettre {letter} non disponible"
        
        # Retirer les lettres
        player.remove_letters(letters)
        
        # Piocher de nouvelles lettres
        new_letters = self.bag.draw(len(letters))
        player.add_letters(new_letters)
        
        # Remettre les lettres dans le sac
        self.bag.letters.extend(letters)
        random.shuffle(self.bag.letters)
        
        self.consecutive_passes = 0
        self.next_turn()
        
        return True, "Lettres échangées"


# ==================== IA MINIMAX ====================

class ScrabbleAI:
    """IA utilisant Minimax pour jouer au Scrabble"""
    
    def __init__(self, game, max_depth=2):
        self.game = game
        self.max_depth = max_depth
    
    def find_all_moves(self, board, rack):
        """Trouve tous les coups possibles"""
        moves = []
        rack_letters = list(rack)
        
        if board.first_move:
            # Premier coup: doit passer par le centre
            moves.extend(self._find_moves_at_position(board, rack_letters, CENTER, CENTER, True))
            moves.extend(self._find_moves_at_position(board, rack_letters, CENTER, CENTER, False))
        else:
            # Trouver toutes les positions d'ancrage
            anchors = self._find_anchors(board)
            for row, col in anchors:
                moves.extend(self._find_moves_at_anchor(board, rack_letters, row, col))
        
        return moves
    
    def _find_anchors(self, board):
        """Trouve les cases d'ancrage (adjacentes à des lettres existantes)"""
        anchors = set()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board.is_empty(row, col):
                    # Vérifier si adjacent à une lettre
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            if not board.is_empty(nr, nc):
                                anchors.add((row, col))
                                break
        return anchors
    
    def _find_moves_at_position(self, board, rack, row, col, horizontal):
        """Trouve les mots possibles passant par une position"""
        moves = []
        
        # Essayer différentes combinaisons de lettres
        for length in range(2, min(8, len(rack) + 1)):
            for word in DICTIONARY:
                if len(word) <= length:
                    # Vérifier si on peut former ce mot
                    letters_needed = list(word.upper())
                    rack_copy = rack[:]
                    can_form = True
                    letters_used = []
                    
                    for letter in letters_needed:
                        if letter in rack_copy:
                            rack_copy.remove(letter)
                            letters_used.append(letter)
                        elif '*' in rack_copy:  # Joker
                            rack_copy.remove('*')
                            letters_used.append('*')
                        else:
                            can_form = False
                            break
                    
                    if can_form:
                        # Essayer de placer le mot
                        for start_offset in range(len(word)):
                            if horizontal:
                                start_col = col - start_offset
                                if start_col >= 0 and start_col + len(word) <= BOARD_SIZE:
                                    tiles = [(row, start_col + i, word[i]) for i in range(len(word))]
                                    move = Move(word, row, start_col, True, letters_used)
                                    moves.append((move, tiles))
                            else:
                                start_row = row - start_offset
                                if start_row >= 0 and start_row + len(word) <= BOARD_SIZE:
                                    tiles = [(start_row + i, col, word[i]) for i in range(len(word))]
                                    move = Move(word, start_row, col, False, letters_used)
                                    moves.append((move, tiles))
        
        return moves
    
    def _find_moves_at_anchor(self, board, rack, anchor_row, anchor_col):
        """Trouve les coups possibles à une position d'ancrage"""
        moves = []
        
        for horizontal in [True, False]:
            # Trouver le préfixe existant
            if horizontal:
                prefix = ""
                col = anchor_col - 1
                while col >= 0 and not board.is_empty(anchor_row, col):
                    prefix = board.get_cell(anchor_row, col) + prefix
                    col -= 1
                start_col = col + 1
            else:
                prefix = ""
                row = anchor_row - 1
                while row >= 0 and not board.is_empty(row, anchor_col):
                    prefix = board.get_cell(row, anchor_col) + prefix
                    row -= 1
                start_row = row + 1
            
            # Essayer d'étendre avec des mots du dictionnaire
            for word in DICTIONARY:
                word_upper = word.upper()
                if prefix and not word_upper.startswith(prefix.upper()):
                    continue
                
                # Calculer les lettres nécessaires
                suffix = word_upper[len(prefix):]
                if not suffix:
                    continue
                
                rack_copy = rack[:]
                letters_used = []
                can_form = True
                
                for letter in suffix:
                    if letter in rack_copy:
                        rack_copy.remove(letter)
                        letters_used.append(letter)
                    elif '*' in rack_copy:
                        rack_copy.remove('*')
                        letters_used.append('*')
                    else:
                        can_form = False
                        break
                
                if can_form:
                    if horizontal:
                        if start_col + len(word_upper) <= BOARD_SIZE:
                            tiles = []
                            for i, letter in enumerate(word_upper):
                                c = start_col + i
                                if board.is_empty(anchor_row, c):
                                    tiles.append((anchor_row, c, letter))
                            if tiles:
                                move = Move(word_upper, anchor_row, start_col, True, letters_used)
                                moves.append((move, tiles))
                    else:
                        if start_row + len(word_upper) <= BOARD_SIZE:
                            tiles = []
                            for i, letter in enumerate(word_upper):
                                r = start_row + i
                                if board.is_empty(r, anchor_col):
                                    tiles.append((r, anchor_col, letter))
                            if tiles:
                                move = Move(word_upper, start_row, anchor_col, False, letters_used)
                                moves.append((move, tiles))
        
        return moves
    
    def evaluate_move(self, move, tiles):
        """Évalue un coup (heuristique)"""
        score = self.game.calculate_move_score(tiles)
        
        # Bonus pour utiliser des lettres difficiles
        for letter in move.letters_used:
            if letter in 'JKQWXYZ':
                score += 5
        
        # Bonus pour utiliser plus de lettres
        score += len(tiles) * 2
        
        return score
    
    def minimax(self, board, rack, depth, is_maximizing, alpha, beta):
        """Algorithme Minimax avec élagage alpha-beta"""
        if depth == 0:
            return 0, None
        
        moves = self.find_all_moves(board, rack)
        
        if not moves:
            return 0, None
        
        if is_maximizing:
            max_eval = float('-inf')
            best_move = None
            
            for move, tiles in moves[:20]:  # Limiter pour la performance
                # Simuler le coup
                eval_score = self.evaluate_move(move, tiles)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (move, tiles)
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            
            for move, tiles in moves[:20]:
                eval_score = self.evaluate_move(move, tiles)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (move, tiles)
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def find_best_move(self):
        """Trouve le meilleur coup pour l'IA"""
        player = self.game.current_player()
        rack = player.rack[:]
        
        # Trouver tous les coups possibles
        moves = self.find_all_moves(self.game.board, rack)
        
        if not moves:
            return None
        
        # Évaluer chaque coup
        best_score = float('-inf')
        best_move = None
        
        for move, tiles in moves:
            # Valider le coup
            valid, _ = self.game.validate_placement(tiles)
            if not valid:
                continue
            
            words = self.game.get_formed_words(tiles)
            invalid = self.game.validate_words(words)
            if invalid:
                continue
            
            score = self.evaluate_move(move, tiles)
            
            if score > best_score:
                best_score = score
                best_move = tiles
        
        return best_move


# ==================== INTERFACE TKINTER ====================

class ScrabbleGUI:
    """Interface graphique du Scrabble"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scrabble - Joueur vs IA Minimax")
        self.root.configure(bg='#2C3E50')
        
        # Initialiser le jeu
        self.game = ScrabbleGame()
        self.game.add_player("Joueur", is_ai=False)
        self.game.add_player("IA Minimax", is_ai=True)
        
        self.ai = ScrabbleAI(self.game)
        
        # Variables d'interface
        self.selected_letter = None
        self.selected_rack_idx = None
        self.tiles_placed = []  # [(row, col, letter), ...]
        self.cell_buttons = {}
        self.rack_buttons = []
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(padx=20, pady=20)
        
        # Frame gauche (plateau)
        left_frame = tk.Frame(main_frame, bg='#2C3E50')
        left_frame.pack(side=tk.LEFT, padx=10)
        
        # Titre
        title = tk.Label(left_frame, text="SCRABBLE", font=('Arial', 24, 'bold'),
                        bg='#2C3E50', fg='white')
        title.pack(pady=10)
        
        # Plateau
        board_frame = tk.Frame(left_frame, bg='#8B4513', padx=5, pady=5)
        board_frame.pack()
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Déterminer la couleur de la case
                color = COLORS['board']
                text = ""
                
                if (row, col) in TRIPLE_WORD:
                    color = COLORS['triple_word']
                    text = "MT"
                elif (row, col) in DOUBLE_WORD:
                    color = COLORS['double_word']
                    text = "MD"
                elif (row, col) in TRIPLE_LETTER:
                    color = COLORS['triple_letter']
                    text = "LT"
                elif (row, col) in DOUBLE_LETTER:
                    color = COLORS['double_letter']
                    text = "LD"
                
                if row == CENTER and col == CENTER:
                    color = COLORS['center']
                    text = "★"
                
                btn = tk.Button(board_frame, text=text, width=3, height=1,
                               font=('Arial', 10, 'bold'), bg=color,
                               relief=tk.RAISED, borderwidth=2,
                               command=lambda r=row, c=col: self._on_cell_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                self.cell_buttons[(row, col)] = btn
        
        # Frame droite (infos et contrôles)
        right_frame = tk.Frame(main_frame, bg='#2C3E50')
        right_frame.pack(side=tk.RIGHT, padx=20, fill=tk.Y)
        
        # Tableau des scores
        scores_frame = tk.LabelFrame(right_frame, text="Scores", font=('Arial', 14, 'bold'),
                                     bg='#34495E', fg='white', padx=10, pady=10)
        scores_frame.pack(fill=tk.X, pady=10)
        
        self.score_labels = {}
        for player in self.game.players:
            frame = tk.Frame(scores_frame, bg='#34495E')
            frame.pack(fill=tk.X, pady=5)
            
            name_label = tk.Label(frame, text=player.name + ":", font=('Arial', 12),
                                 bg='#34495E', fg='white', anchor='w')
            name_label.pack(side=tk.LEFT)
            
            score_label = tk.Label(frame, text="0", font=('Arial', 12, 'bold'),
                                  bg='#34495E', fg='#2ECC71')
            score_label.pack(side=tk.RIGHT)
            self.score_labels[player.name] = score_label
        
        # Tour actuel
        self.turn_label = tk.Label(right_frame, text="Tour: Joueur", font=('Arial', 14),
                                   bg='#2C3E50', fg='#F1C40F')
        self.turn_label.pack(pady=10)
        
        # Lettres restantes dans le sac
        self.bag_label = tk.Label(right_frame, text="Sac: 86 lettres", font=('Arial', 12),
                                  bg='#2C3E50', fg='white')
        self.bag_label.pack(pady=5)
        
        # Valeur des lettres
        values_frame = tk.LabelFrame(right_frame, text="Valeur des lettres", font=('Arial', 12, 'bold'),
                                     bg='#34495E', fg='white', padx=10, pady=10)
        values_frame.pack(fill=tk.X, pady=10)
        
        values_text = ""
        for i, (letter, value) in enumerate(sorted(LETTER_VALUES.items())):
            values_text += f"{letter}={value} "
            if (i + 1) % 9 == 0:
                values_text += "\n"
        
        values_label = tk.Label(values_frame, text=values_text, font=('Courier', 9),
                               bg='#34495E', fg='white', justify=tk.LEFT)
        values_label.pack()
        
        # Chevalet du joueur
        rack_frame = tk.LabelFrame(right_frame, text="Votre chevalet", font=('Arial', 14, 'bold'),
                                   bg='#34495E', fg='white', padx=10, pady=10)
        rack_frame.pack(fill=tk.X, pady=10)
        
        self.rack_container = tk.Frame(rack_frame, bg='#34495E')
        self.rack_container.pack()
        
        # Boutons de contrôle
        control_frame = tk.Frame(right_frame, bg='#2C3E50')
        control_frame.pack(pady=20)
        
        self.play_btn = tk.Button(control_frame, text="Jouer", font=('Arial', 12, 'bold'),
                                  bg='#27AE60', fg='white', width=10,
                                  command=self._play_move)
        self.play_btn.pack(pady=5)
        
        self.cancel_btn = tk.Button(control_frame, text="Annuler", font=('Arial', 12, 'bold'),
                                    bg='#E74C3C', fg='white', width=10,
                                    command=self._cancel_placement)
        self.cancel_btn.pack(pady=5)
        
        self.pass_btn = tk.Button(control_frame, text="Passer", font=('Arial', 12, 'bold'),
                                  bg='#95A5A6', fg='white', width=10,
                                  command=self._pass_turn)
        self.pass_btn.pack(pady=5)
        
        self.exchange_btn = tk.Button(control_frame, text="Échanger", font=('Arial', 12, 'bold'),
                                      bg='#3498DB', fg='white', width=10,
                                      command=self._exchange_letters)
        self.exchange_btn.pack(pady=5)
        
        # Message
        self.message_label = tk.Label(right_frame, text="", font=('Arial', 11),
                                      bg='#2C3E50', fg='#F39C12', wraplength=200)
        self.message_label.pack(pady=10)
    
    def _update_display(self):
        """Met à jour l'affichage"""
        # Mettre à jour les scores
        for player in self.game.players:
            self.score_labels[player.name].config(text=str(player.score))
        
        # Mettre à jour le tour
        current = self.game.current_player()
        self.turn_label.config(text=f"Tour: {current.name}")
        
        # Mettre à jour le sac
        self.bag_label.config(text=f"Sac: {self.game.bag.remaining()} lettres")
        
        # Mettre à jour le plateau
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                letter = self.game.board.get_cell(row, col)
                btn = self.cell_buttons[(row, col)]
                
                if letter:
                    btn.config(text=letter, bg=COLORS['tile'], font=('Arial', 12, 'bold'))
                else:
                    # Restaurer la couleur originale
                    color = COLORS['board']
                    text = ""
                    
                    if (row, col) in TRIPLE_WORD:
                        color = COLORS['triple_word']
                        text = "MT"
                    elif (row, col) in DOUBLE_WORD:
                        color = COLORS['double_word']
                        text = "MD"
                    elif (row, col) in TRIPLE_LETTER:
                        color = COLORS['triple_letter']
                        text = "LT"
                    elif (row, col) in DOUBLE_LETTER:
                        color = COLORS['double_letter']
                        text = "LD"
                    
                    if row == CENTER and col == CENTER:
                        color = COLORS['center']
                        text = "★"
                    
                    # Vérifier si une tuile a été placée temporairement
                    placed = False
                    for pr, pc, pl in self.tiles_placed:
                        if pr == row and pc == col:
                            btn.config(text=pl, bg=COLORS['placed'], font=('Arial', 12, 'bold'))
                            placed = True
                            break
                    
                    if not placed:
                        btn.config(text=text, bg=color, font=('Arial', 10, 'bold'))
        
        # Mettre à jour le chevalet
        self._update_rack()
        
        # Activer/désactiver les boutons selon le joueur
        is_human_turn = not self.game.current_player().is_ai
        self.play_btn.config(state=tk.NORMAL if is_human_turn else tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL if is_human_turn else tk.DISABLED)
        self.pass_btn.config(state=tk.NORMAL if is_human_turn else tk.DISABLED)
        self.exchange_btn.config(state=tk.NORMAL if is_human_turn else tk.DISABLED)
    
    def _update_rack(self):
        """Met à jour l'affichage du chevalet"""
        # Supprimer les anciens boutons
        for btn in self.rack_buttons:
            btn.destroy()
        self.rack_buttons = []
        
        # Afficher le chevalet du joueur humain
        human_player = self.game.players[0]
        
        for idx, letter in enumerate(human_player.rack):
            # Vérifier si la lettre a été placée
            placed = False
            for _, _, pl in self.tiles_placed:
                if pl == letter and not placed:
                    temp_rack = human_player.rack[:]
                    for _, _, placed_letter in self.tiles_placed:
                        if placed_letter in temp_rack:
                            temp_rack.remove(placed_letter)
                    if letter not in temp_rack[:idx+1]:
                        placed = True
            
            color = COLORS['selected'] if idx == self.selected_rack_idx else COLORS['tile']
            
            btn = tk.Button(self.rack_container, text=letter, width=3, height=2,
                           font=('Arial', 14, 'bold'), bg=color,
                           command=lambda i=idx: self._on_rack_click(i))
            btn.pack(side=tk.LEFT, padx=2)
            
            # Afficher la valeur
            value_label = tk.Label(self.rack_container, text=str(LETTER_VALUES.get(letter, 0)),
                                  font=('Arial', 8), bg='#34495E', fg='white')
            value_label.place(in_=btn, relx=0.8, rely=0.8)
            
            self.rack_buttons.append(btn)
    
    def _on_rack_click(self, idx):
        """Gère le clic sur une lettre du chevalet"""
        if self.game.current_player().is_ai:
            return
        
        if self.selected_rack_idx == idx:
            self.selected_rack_idx = None
            self.selected_letter = None
        else:
            self.selected_rack_idx = idx
            self.selected_letter = self.game.players[0].rack[idx]
        
        self._update_rack()
    
    def _on_cell_click(self, row, col):
        """Gère le clic sur une case du plateau"""
        if self.game.current_player().is_ai:
            return
        
        # Si une lettre est sélectionnée et la case est vide
        if self.selected_letter and self.game.board.is_empty(row, col):
            # Vérifier qu'il n'y a pas déjà une tuile placée
            for pr, pc, _ in self.tiles_placed:
                if pr == row and pc == col:
                    return
            
            # Placer la tuile temporairement
            self.tiles_placed.append((row, col, self.selected_letter))
            
            # Retirer du chevalet virtuel
            self.selected_letter = None
            self.selected_rack_idx = None
            
            self._update_display()
        
        # Si on clique sur une tuile placée, la retirer
        else:
            for i, (pr, pc, pl) in enumerate(self.tiles_placed):
                if pr == row and pc == col:
                    self.tiles_placed.pop(i)
                    self._update_display()
                    return
    
    def _play_move(self):
        """Joue le coup actuel"""
        if not self.tiles_placed:
            self.message_label.config(text="Placez des lettres sur le plateau!")
            return
        
        success, message, score = self.game.play_move(self.tiles_placed)
        
        if success:
            self.tiles_placed = []
            self.message_label.config(text=f"{message}\n+{score} points!")
            self._update_display()
            
            # Vérifier fin de partie
            if self.game.game_over:
                self._show_game_over()
                return
            
            # Tour suivant
            self.game.next_turn()
            self._update_display()
            
            # Si c'est le tour de l'IA
            if self.game.current_player().is_ai:
                self.root.after(1000, self._ai_play)
        else:
            self.message_label.config(text=message)
    
    def _cancel_placement(self):
        """Annule le placement actuel"""
        self.tiles_placed = []
        self.selected_letter = None
        self.selected_rack_idx = None
        self._update_display()
        self.message_label.config(text="Placement annulé")
    
    def _pass_turn(self):
        """Passe le tour"""
        self.tiles_placed = []
        self.game.pass_turn()
        self._update_display()
        self.message_label.config(text="Tour passé")
        
        if self.game.game_over:
            self._show_game_over()
            return
        
        # Si c'est le tour de l'IA
        if self.game.current_player().is_ai:
            self.root.after(1000, self._ai_play)
    
    def _exchange_letters(self):
        """Échange des lettres"""
        if not self.selected_rack_idx is not None:
            self.message_label.config(text="Sélectionnez des lettres à échanger")
            return
        
        letter = self.game.players[0].rack[self.selected_rack_idx]
        success, message = self.game.exchange_letters([letter])
        
        if success:
            self.selected_letter = None
            self.selected_rack_idx = None
            self._update_display()
            self.message_label.config(text=message)
            
            # Si c'est le tour de l'IA
            if self.game.current_player().is_ai:
                self.root.after(1000, self._ai_play)
        else:
            self.message_label.config(text=message)
    
    def _ai_play(self):
        """Fait jouer l'IA"""
        self.message_label.config(text="L'IA réfléchit...")
        self.root.update()
        
        # Trouver le meilleur coup
        best_move = self.ai.find_best_move()
        
        if best_move:
            success, message, score = self.game.play_move(best_move)
            
            if success:
                self.message_label.config(text=f"IA: {message}\n+{score} points!")
                self._update_display()
                
                if self.game.game_over:
                    self._show_game_over()
                    return
                
                self.game.next_turn()
                self._update_display()
            else:
                # L'IA passe si elle ne peut pas jouer
                self.game.pass_turn()
                self.message_label.config(text="L'IA passe son tour")
                self._update_display()
                
                if self.game.game_over:
                    self._show_game_over()
        else:
            # Pas de coup possible, passer
            self.game.pass_turn()
            self.message_label.config(text="L'IA passe son tour")
            self._update_display()
            
            if self.game.game_over:
                self._show_game_over()
    
    def _show_game_over(self):
        """Affiche la fin de partie"""
        winner = max(self.game.players, key=lambda p: p.score)
        message = f"Partie terminée!\n\nGagnant: {winner.name}\n\n"
        
        for player in self.game.players:
            message += f"{player.name}: {player.score} points\n"
        
        messagebox.showinfo("Fin de partie", message)
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


# ==================== MAIN ====================

if __name__ == "__main__":
    app = ScrabbleGUI()
    app.run()

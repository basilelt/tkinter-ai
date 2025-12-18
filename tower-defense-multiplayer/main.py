import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import json
import time
from game import WIDTH, HEIGHT, PATH, TOWER_TYPES, GameState

class Menu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tower Defense Multiplayer - Menu")
        self.root.geometry("300x200")

        tk.Label(self.root, text="Choisissez une option:").pack(pady=20)

        tk.Button(self.root, text="Héberger une partie", command=self.host_game).pack(pady=10)
        tk.Button(self.root, text="Rejoindre une partie", command=self.join_game).pack(pady=10)

        self.root.mainloop()

    def host_game(self):
        self.root.destroy()
        # Start server in thread
        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)  # Wait for server to start
        Client(is_host=True)

    def join_game(self):
        host = simpledialog.askstring("Rejoindre", "Adresse IP du serveur:")
        if host:
            self.root.destroy()
            Client(host=host, is_host=False)
        else:
            messagebox.showerror("Erreur", "Adresse requise")

    def run_server(self):
        from server import Server
        server = Server()
        server.run()

class Client:
    def __init__(self, host='127.0.0.1', port=65432, is_host=False):
        self.host = host
        self.port = port
        self.is_host = is_host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
        except:
            messagebox.showerror("Erreur de connexion", "Impossible de se connecter au serveur")
            return

        self.game_state = None
        self.root = tk.Tk()
        self.root.title("Tower Defense Multiplayer")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg='green')
        self.canvas.pack()

        # UI elements
        self.info_label = tk.Label(self.root, text="Health: 100 | Money: 650 | Wave: 1")
        self.info_label.pack()

        self.start_wave_button = tk.Button(self.root, text="Start Wave", command=self.start_wave)
        self.start_wave_button.pack()

        # Tower buttons
        self.tower_buttons = {}
        for tower_type, info in TOWER_TYPES.items():
            btn = tk.Button(self.root, text=f"{tower_type.capitalize()} (${info['cost']})", command=lambda t=tower_type: self.select_tower(t))
            btn.pack(side=tk.LEFT)
            self.tower_buttons[tower_type] = btn

        self.selected_tower = None
        self.canvas.bind("<Button-1>", self.place_tower)

        # Start threads
        self.receive_thread = threading.Thread(target=self.receive_updates)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.root.mainloop()

    def select_tower(self, tower_type):
        self.selected_tower = tower_type

    def place_tower(self, event):
        if self.selected_tower and self.game_state:
            message = {
                'action': 'place_tower',
                'tower_type': self.selected_tower,
                'x': event.x,
                'y': event.y
            }
            try:
                self.socket.sendall(json.dumps(message).encode())
                self.selected_tower = None
            except:
                pass

    def start_wave(self):
        message = {'action': 'start_wave'}
        try:
            self.socket.sendall(json.dumps(message).encode())
        except:
            pass

    def receive_updates(self):
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                state = json.loads(data.decode())
                self.game_state = state
                self.root.after(0, self.update_display)
            except:
                break

    def update_display(self):
        if not self.game_state:
            return
        self.canvas.delete("all")

        # Draw path
        path = self.game_state.get('path', PATH)
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, width=30, fill='gray', capstyle=tk.ROUND)

        # Draw bloons
        for bloon_data in self.game_state['bloons'].values():
            x, y = bloon_data['x'], bloon_data['y']
            color = bloon_data['type']
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color)

        # Draw towers
        for tower_data in self.game_state['towers'].values():
            x, y = tower_data['x'], tower_data['y']
            color = TOWER_TYPES[tower_data['type']]['color']
            self.canvas.create_rectangle(x-15, y-15, x+15, y+15, fill=color)

        # Draw projectiles
        for proj_data in self.game_state['projectiles'].values():
            x, y = proj_data['x'], proj_data['y']
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='black')

        # Update info
        self.info_label.config(text=f"Health: {self.game_state['health']} | Money: {self.game_state['money']} | Wave: {self.game_state['wave']}")

if __name__ == "__main__":
    Menu()
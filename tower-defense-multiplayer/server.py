import socket
import threading
import json
import time
from game import GameState

HOST = '127.0.0.1'
PORT = 65432

class Server:
    def __init__(self):
        self.game_state = GameState()
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")
        self.running = True
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.start()
        # Start first wave
        self.start_wave()

    def game_loop(self):
        while self.running:
            self.game_state.update()
            # Send game state to all clients
            state_data = json.dumps(self.game_state.to_dict())
            for client in self.clients[:]:
                try:
                    client.sendall(state_data.encode())
                except:
                    self.clients.remove(client)
            time.sleep(0.05)  # ~20 FPS

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.process_message(message)
            except:
                break
        client_socket.close()
        if client_socket in self.clients:
            self.clients.remove(client_socket)

    def process_message(self, message):
        action = message.get('action')
        if action == 'place_tower':
            tower_type = message['tower_type']
            x = message['x']
            y = message['y']
            self.game_state.add_tower(tower_type, x, y)
        elif action == 'start_wave':
            if not self.game_state.wave_in_progress:
                self.start_wave()

    def start_wave(self):
        self.game_state.wave_in_progress = True
        # Simple wave: spawn some bloons
        for _ in range(self.game_state.wave * 5):
            self.game_state.add_bloon('red')
        # After some time, end wave (simplified)
        threading.Timer(10, self.end_wave).start()

    def end_wave(self):
        self.game_state.wave_in_progress = False
        self.game_state.wave += 1

    def run(self):
        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    server = Server()
    server.run()
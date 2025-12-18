# Tower Defense Multiplayer

A multiplayer Tower Defense game built with Tkinter and Python sockets.

## Features

- Cooperative gameplay: All players defend the same path together
- Shared health and money
- Multiple tower types: Dart, Tack, Sniper
- Real-time synchronization between players
- Wave-based enemy spawning

## How to Run

Run the main application:
```
python main.py
```

Choose "Héberger une partie" to host a game (starts server and client), or "Rejoindre une partie" to join by entering the host IP.

## Gameplay

- Click on tower buttons to select a tower type
- Click on the map to place the selected tower (if you have enough money)
- Click "Start Wave" to begin the next wave of enemies
- Towers automatically fire at enemies in range
- Game ends when health reaches 0

## Architecture

- **Server**: Manages game state, runs game loop, handles client connections
- **Client**: Displays game state, sends player actions to server
- **Game**: Shared game logic (Bloons, Towers, Projectiles)
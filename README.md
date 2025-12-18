# AI Games

## Prerequisites

- Python 3.14.0 (see `.python-version` file)
- pip (Python package installer)

## Installation

1. **Clone or download the project** to your local machine.

2. **Navigate to the project directory**:
   ```bash
   cd projet-ia
   ```

3. **Install the required dependencies**:
   ```bash
   brew install pyenv  # For macOS users
   brew install tcl-tk   # For macOS users to ensure Tkinter works properly
   
   env LDFLAGS="-L$(brew --prefix openssl@1.1)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix sqlite3)/lib -L$(brew --prefix xz)/lib -L$(brew --prefix zlib)/lib -L$(brew --prefix tcl-tk)/lib" \
   CPPFLAGS="-I$(brew --prefix openssl@1.1)/include -I$(brew --prefix readline)/include -I$(brew --prefix sqlite3)/include -I$(brew --prefix xz)/include -I$(brew --prefix zlib)/include -I$(brew --prefix tcl-tk)/include" \
   PKG_CONFIG_PATH="$(brew --prefix openssl@1.1)/lib/pkgconfig:$(brew --prefix readline)/lib/pkgconfig:$(brew --prefix sqlite3)/lib/pkgconfig:$(brew --prefix xz)/lib/pkgconfig:$(brew --prefix zlib)/lib/pkgconfig:$(brew --prefix tcl-tk)/lib/pkgconfig" \
   pyenv install 3.14.0 # For macOS users

   zsh # Reload shell to use pyenv

   python -m venv .venv

   pip install -r requirements.txt
   ```
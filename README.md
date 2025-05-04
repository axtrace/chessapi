# Chess API

API for working with the [Stockfish](https://github.com/official-stockfish/Stockfish) chess engine, built on FastAPI.

## Environment Setup

```bash
# Update packages and install Stockfish
sudo apt update
sudo apt install stockfish

# Clone the repository
git clone https://github.com/axtrace/chessapi/
cd chessapi/

# Create and activate virtual environment
sudo apt install python3.12-venv
python3 -m venv chessapi
source /home/{user}/chessapi/bin/activate

# Install dependencies
pip install fastapi uvicorn python-chess
```

## Running the Application

### First Run
```bash
python -m uvicorn chessapi:app --host 0.0.0.0 --port 8000
```

### Setting up systemd for Automatic Startup

1. Create a file `/etc/systemd/system/chessapi.service` with the following content:
```ini
[Unit]
Description=Chess API Service
After=network.target

[Service]
User={user}
WorkingDirectory=/home/{user}/chessapi
Environment="PATH=/home/{user}/chessapi/bin"
ExecStart=/home/{user}/chessapi/bin/python -m uvicorn chessapi:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Start and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chessapi
sudo systemctl start chessapi
```

### Service Management

- Check status:
```bash
sudo systemctl status chessapi
```

- View logs:
```bash
journalctl -u chessapi -f
```

- Restart service:
```bash
sudo systemctl restart chessapi
```

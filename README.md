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
pip install fastapi uvicorn python-chess pydantic-settings
```

## API Key Setup

1. Generate a secure API key:
```bash
openssl rand -base64 32
```

2. Create a `.env` file in the project root:
```bash
nano .env
```

3. Add the API key to the `.env` file:
```
API_KEY=your-generated-key-here
```

4. Set proper permissions:
```bash
chmod 600 .env
```

Note: Keep your API key secret and never commit the `.env` file to version control.

## SSL Certificate Setup

1. Install certbot:
```bash
sudo apt install certbot
```

2. Stop the service to free port 80:
```bash
sudo systemctl stop chessapi
```

3. Obtain SSL certificate:
```bash
sudo certbot certonly --standalone -d alice-chess.ru --email your-email@example.com --agree-tos --non-interactive
```

4. Set proper permissions for certificates:
```bash
sudo chown -R {user}:{user} /etc/letsencrypt/
sudo chmod -R 755 /etc/letsencrypt/
```

## Running the Application

### Setting up systemd for Automatic Startup

1. Create a file `/etc/systemd/system/chessapi.service` with the following content:
```ini
[Unit]
Description=Chess API FastAPI Service
After=network.target

[Service]
User={user}
Group={user}
WorkingDirectory=/home/{user}/chessapi
Environment="PATH=/home/{user}/chessapi/bin"
ExecStart=/home/{user}/chessapi/bin/python -m uvicorn chessapi:app --host 0.0.0.0 --port 8000 --ssl-keyfile /etc/letsencrypt/live/alice-chess.ru/privkey.pem --ssl-certfile /etc/letsencrypt/live/alice-chess.ru/fullchain.pem
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

## API Usage

All API endpoints require authentication using an API key. Include the API key in the `X-API-Key` header:

```bash
curl -X POST "https://alice-chess.ru:8000/bestmove/" \
     -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "depth": 10}'
```

Note: Replace `your-secret-api-key-here` with your actual API key.

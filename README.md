# Chess API

API для работы с шахматными движками, построенное на FastAPI.

## Подготовка окружения

```bash
# Обновление пакетов и установка Stockfish
sudo apt update
sudo apt install stockfish

# Клонирование репозитория
git clone https://github.com/axtrace/chessapi/
cd chessapi/

# Создание и активация виртуального окружения
sudo apt install python3.12-venv
python3 -m venv chessapi
source /home/{user}/chessapi/bin/activate

# Установка зависимостей
pip install fastapi uvicorn python-chess
```

## Запуск приложения

### Первый запуск
```bash
python -m uvicorn chessapi:app --host 0.0.0.0 --port 8000
```

### Настройка systemd для автоматического запуска

1. Создайте файл `/etc/systemd/system/chessapi.service` со следующим содержимым:
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

2. Запустите и включите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chessapi
sudo systemctl start chessapi
```

### Управление сервисом

- Проверка статуса:
```bash
sudo systemctl status chessapi
```

- Просмотр логов:
```bash
journalctl -u chessapi -f
```

- Перезапуск сервиса:
```bash
sudo systemctl restart chessapi
``` 


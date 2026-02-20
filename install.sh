#!/bin/bash
# Joy Vision Calculator - Ubuntu Installer
# Автоматический установщик для Ubuntu 20.04/22.04/24.04

set -e  # Остановка при ошибке

echo "===================================="
echo "Joy Vision Calculator"
echo "Установщик для Ubuntu"
echo "===================================="
echo ""

# Проверка root прав
if [[ $EUID -ne 0 ]]; then
   echo "ОШИБКА: Этот скрипт должен быть запущен с правами root (sudo)"
   exit 1
fi

# Получить имя пользователя, который запустил sudo
REAL_USER=${SUDO_USER:-$USER}
INSTALL_DIR="/home/$REAL_USER/joy-vision-calculator"

echo "Установка для пользователя: $REAL_USER"
echo "Директория установки: $INSTALL_DIR"
echo ""

# Шаг 1: Обновление системы
echo "[1/10] Обновление системы..."
apt update -qq
echo "OK"
echo ""

# Шаг 2: Установка системных пакетов
echo "[2/10] Установка системных пакетов..."
apt install -y -qq python3 python3-pip python3-venv git curl wget nginx > /dev/null 2>&1
echo "OK"
echo ""

# Шаг 3: Проверка Python
echo "[3/10] Проверка Python..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python версия: $PYTHON_VERSION"
echo "OK"
echo ""

# Шаг 4: Создание виртуального окружения
echo "[4/10] Создание виртуального окружения..."
if [ -d "$INSTALL_DIR/venv" ]; then
    echo "Виртуальное окружение уже существует, пропуск..."
else
    sudo -u $REAL_USER python3 -m venv $INSTALL_DIR/venv
    echo "OK"
fi
echo ""

# Шаг 5: Установка зависимостей
echo "[5/10] Установка Python зависимостей..."
sudo -u $REAL_USER $INSTALL_DIR/venv/bin/pip install --upgrade pip > /dev/null 2>&1
sudo -u $REAL_USER $INSTALL_DIR/venv/bin/pip install -r $INSTALL_DIR/requirements.txt
echo "OK"
echo ""

# Шаг 6: Создание директорий
echo "[6/10] Создание необходимых директорий..."
sudo -u $REAL_USER mkdir -p $INSTALL_DIR/data/exports
sudo -u $REAL_USER mkdir -p $INSTALL_DIR/static/fonts
sudo -u $REAL_USER mkdir -p $INSTALL_DIR/logs
echo "OK"
echo ""

# Шаг 7: Настройка .env
echo "[7/10] Настройка конфигурации..."
if [ -f "$INSTALL_DIR/.env" ]; then
    echo "Файл .env уже существует, пропуск..."
else
    sudo -u $REAL_USER cp $INSTALL_DIR/.env.example $INSTALL_DIR/.env
    # Генерация SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sudo -u $REAL_USER sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" $INSTALL_DIR/.env
    echo "Файл .env создан с автоматически сгенерированным SECRET_KEY"
fi
echo "OK"
echo ""

# Шаг 8: Настройка прав доступа
echo "[8/10] Настройка прав доступа..."
chown -R $REAL_USER:$REAL_USER $INSTALL_DIR
chmod -R 755 $INSTALL_DIR
chmod 600 $INSTALL_DIR/.env
echo "OK"
echo ""

# Шаг 9: Создание systemd service
echo "[9/10] Создание systemd service..."
cat > /etc/systemd/system/joyvision.service << EOF
[Unit]
Description=Joy Vision Calculator
After=network.target

[Service]
Type=notify
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 120 \\
    --access-logfile $INSTALL_DIR/logs/access.log \\
    --error-logfile $INSTALL_DIR/logs/error.log \\
    'app:create_app()'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable joyvision
echo "OK"
echo ""

# Шаг 10: Проверка установки
echo "[10/10] Проверка установки..."
cd $INSTALL_DIR
sudo -u $REAL_USER $INSTALL_DIR/venv/bin/python -c "from app import create_app; app = create_app(); print('Приложение импортировано успешно')"
echo "OK"
echo ""

# Финальные инструкции
echo "===================================="
echo "Установка завершена успешно!"
echo "===================================="
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Отредактируйте файл .env:"
echo "   sudo nano $INSTALL_DIR/.env"
echo ""
echo "   Обязательно настройте:"
echo "   - BITRIX24_WEBHOOK_URL"
echo "   - BITRIX24_FOLDER_ID"
echo ""
echo "2. Запустите сервис:"
echo "   sudo systemctl start joyvision"
echo ""
echo "3. Проверьте статус:"
echo "   sudo systemctl status joyvision"
echo ""
echo "4. Просмотр логов:"
echo "   sudo journalctl -u joyvision -f"
echo ""
echo "5. Настройте Nginx (см. INSTALL_UBUNTU.md шаг 10)"
echo ""
echo "Полная документация: INSTALL_UBUNTU.md"
echo ""

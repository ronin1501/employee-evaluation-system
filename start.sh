#!/bin/bash
# Переходим в директорию скрипта
cd "$(dirname "$0")"

# Активация виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Ошибка: Виртуальное окружение venv не найдено."
    echo "Попробуйте запустить: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Запуск приложения
echo "[*] Запуск сервера Flask..."
python3 app.py

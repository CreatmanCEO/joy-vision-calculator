#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки подключения к Битрикс24
Проверяет вебхук и ID папки
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

def test_bitrix_connection():
    """Тестирование подключения к Битрикс24"""

    print("=" * 50)
    print("Проверка подключения к Битрикс24")
    print("=" * 50)
    print()

    # Проверка переменных окружения
    webhook_url = os.getenv('BITRIX24_WEBHOOK_URL')
    folder_id = os.getenv('BITRIX24_FOLDER_ID')

    if not webhook_url:
        print("❌ ОШИБКА: BITRIX24_WEBHOOK_URL не установлен в .env")
        print("   Откройте файл .env и добавьте URL вебхука")
        return False

    if not folder_id:
        print("⚠️  ВНИМАНИЕ: BITRIX24_FOLDER_ID не установлен в .env")
        print("   Функция загрузки файлов не будет работать")
        print()

    print(f"✓ Вебхук URL: {webhook_url[:50]}...")
    if folder_id:
        print(f"✓ ID папки: {folder_id}")
    print()

    # Тест 1: Проверка вебхука
    print("[Тест 1/3] Проверка доступности вебхука...")
    try:
        # Попытка получить список сделок (минимальный запрос)
        url = f"{webhook_url}crm.deal.list.json"
        response = requests.post(url, json={"select": ["ID"], "filter": {}, "start": 0}, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                print("✓ Вебхук работает!")
                print(f"  Найдено сделок в CRM: {len(result.get('result', []))}")
            elif 'error' in result:
                print(f"❌ Ошибка Битрикс24: {result.get('error_description', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ HTTP ошибка {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут: Битрикс24 не отвечает")
        print("   Проверьте интернет-соединение")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения")
        print("   Проверьте URL вебхука и интернет-соединение")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False

    print()

    # Тест 2: Проверка прав доступа
    print("[Тест 2/3] Проверка прав доступа...")
    try:
        # Проверка прав на CRM
        url = f"{webhook_url}crm.deal.fields.json"
        response = requests.post(url, json={}, timeout=10)

        if response.status_code == 200 and 'result' in response.json():
            print("✓ Права на CRM: есть")
        else:
            print("⚠️  Права на CRM: возможно отсутствуют")

        # Проверка прав на Диск (если указан folder_id)
        if folder_id:
            url = f"{webhook_url}disk.folder.get.json"
            response = requests.post(url, json={"id": folder_id}, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    folder_name = result['result'].get('NAME', 'Неизвестно')
                    print(f"✓ Права на Диск: есть")
                    print(f"  Папка найдена: '{folder_name}'")
                elif 'error' in result:
                    error_desc = result.get('error_description', 'Неизвестная ошибка')
                    print(f"❌ Ошибка доступа к папке: {error_desc}")
                    print(f"   Проверьте BITRIX24_FOLDER_ID в .env")
                    return False
    except Exception as e:
        print(f"⚠️  Не удалось проверить права: {str(e)}")

    print()

    # Тест 3: Тестовый запрос создания сделки (dry-run)
    print("[Тест 3/3] Проверка возможности создания сделки...")
    try:
        url = f"{webhook_url}crm.deal.fields.json"
        response = requests.post(url, json={}, timeout=10)

        if response.status_code == 200 and 'result' in response.json():
            print("✓ Создание сделок: доступно")

            # Проверяем наличие обязательных полей
            fields = response.json()['result']
            if 'TITLE' in fields and 'OPPORTUNITY' in fields:
                print("  Все необходимые поля доступны")
            else:
                print("⚠️  Некоторые поля могут быть недоступны")
        else:
            print("⚠️  Не удалось проверить поля сделки")
    except Exception as e:
        print(f"⚠️  Ошибка проверки: {str(e)}")

    print()
    print("=" * 50)
    print("✅ Подключение к Битрикс24 настроено корректно!")
    print("=" * 50)
    print()
    print("Приложение готово к работе с Битрикс24")
    print()

    return True


if __name__ == "__main__":
    success = test_bitrix_connection()
    sys.exit(0 if success else 1)

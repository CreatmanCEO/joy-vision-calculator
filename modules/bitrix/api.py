# modules/bitrix/api.py
"""
API для работы с Битрикс24
Адаптировано из C:/Hans/old/core/bitrix_api.py
"""

import requests
import json
import base64
import os
import datetime


def get_webhook_url():
    """Получить URL вебхука из переменных окружения"""
    url = os.getenv('BITRIX24_WEBHOOK_URL')
    if not url:
        raise Exception("BITRIX24_WEBHOOK_URL не установлен в .env")
    return url


def create_deal(company_name, total_price, address=""):
    """
    Создаёт новую сделку в Битрикс24
    
    Args:
        company_name: название компании
        total_price: сумма сделки
        address: адрес (опционально)
    
    Returns:
        ID созданной сделки или None
    """
    url = f"{get_webhook_url()}crm.deal.add.json"
    data = {
        "fields": {
            "TITLE": f"Заказ - {company_name}",
            "ADDRESS": address,
            "CATEGORY_ID": 0,
            "STAGE_ID": "C0:NEW",
            "OPPORTUNITY": total_price,
            "CURRENCY_ID": "RUB"
        }
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("result"):
            return result["result"]
        else:
            error_msg = result.get("error_description", "Неизвестная ошибка")
            raise Exception(f"Ошибка создания сделки: {error_msg}")
    
    except Exception as e:
        raise Exception(f"Не удалось создать сделку: {str(e)}")


def update_deal(deal_id, total_price):
    """
    Обновляет сумму сделки
    
    Args:
        deal_id: ID сделки
        total_price: новая сумма
    
    Returns:
        True если успешно, иначе Exception
    """
    url = f"{get_webhook_url()}crm.deal.update.json"
    payload = {
        "id": deal_id,
        "fields": {
            "OPPORTUNITY": total_price
        }
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get("result"):
            return True
        else:
            error_msg = result.get("error_description", "Неизвестная ошибка")
            raise Exception(f"Ошибка обновления сделки: {error_msg}")
    
    except Exception as e:
        raise Exception(f"Не удалось обновить сделку: {str(e)}")


def get_deal_by_id(deal_id):
    """
    Получает сделку по ID
    
    Args:
        deal_id: ID сделки
    
    Returns:
        dict с данными сделки или None
    """
    url = f"{get_webhook_url()}crm.deal.get.json"
    data = {"id": deal_id}

    try:
        response = requests.post(url, json=data)
        result = response.json()
        return result.get("result")
    except Exception as e:
        raise Exception(f"Ошибка получения сделки: {str(e)}")


def upload_file_to_bitrix(file_path, folder_id=None):
    """
    Загружает файл в папку диска Битрикс24
    
    Args:
        file_path: путь к файлу
        folder_id: ID папки в Битрикс24 (из .env)
    
    Returns:
        ID загруженного файла или None
    """
    if not os.path.isfile(file_path):
        raise Exception(f"Файл не найден: {file_path}")

    if folder_id is None:
        folder_id = int(os.getenv('BITRIX24_FOLDER_ID', '0'))
        if folder_id == 0:
            raise Exception("BITRIX24_FOLDER_ID не установлен в .env")

    # Уникальное имя файла
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    unique_name = f"{base_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"

    with open(file_path, "rb") as f:
        content = f.read()

    encoded_content = base64.b64encode(content).decode("utf-8")

    url = f"{get_webhook_url()}disk.folder.uploadfile"
    payload = {
        "id": folder_id,
        "name": unique_name,
        "content": encoded_content
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()

        if not result.get("result", {}).get("uploadUrl"):
            error_msg = result.get("error_description", "Неизвестная ошибка")
            raise Exception(f"Ошибка получения uploadUrl: {error_msg}")

        upload_url = result["result"]["uploadUrl"]

        # Загружаем файл на полученный URL
        files = {"file": (unique_name, open(file_path, "rb"), "application/pdf")}
        data = {"id": folder_id}

        final_response = requests.post(upload_url, files=files, data=data)

        if final_response.status_code == 200:
            final_result = final_response.json()
            if final_result.get("result", {}).get("ID"):
                return final_result["result"]["ID"]
            else:
                error_msg = final_result.get("error_description", "Неизвестная ошибка")
                raise Exception(f"Ошибка загрузки файла: {error_msg}")
        else:
            raise Exception(f"HTTP ошибка {final_response.status_code} при загрузке файла")

    except Exception as e:
        raise Exception(f"Не удалось загрузить файл в Битрикс: {str(e)}")

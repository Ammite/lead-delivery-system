from datetime import datetime
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import uuid
import logging
import config
from email.mime.text import MIMEText
import smtplib
import requests  # для Telegram

app = FastAPI(title="Lead Delivery System", description="Система для обработки лидов", version="1.0.0")


logging.basicConfig(
    level=logging.DEBUG,  # минимальный уровень логирования
    format="%(asctime)s [%(levelname)s] %(message)s",  # формат лога
    handlers=[
        logging.StreamHandler()  # вывод в консоль
    ]
)
log = logging.getLogger("LDS")
log.setLevel(logging.DEBUG)

class Lead(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    text: Optional[str] = None
    source: str = None
    campaign: Optional[str] = None
    is_telegram: bool = False
    is_mail: bool = False
    is_form: bool = True
    api_key: str = None

@app.post("/leads")
async def create_lead(lead_data: Dict[str, Any]):
    """
    Принимает запрос с данными лида и собирает их в словарь
    """
    # Добавление id к лиду
    lead_data['id'] = str(uuid.uuid4())
    lead_id = lead_data.get("id", "|No uuid|")
    
    log.debug(f"Lead #{lead_id}. Got. Data: \n{json.dumps(lead_data, indent=4)}")

    # Обработка данных
    log.debug(f"Lead #{lead_id}. Process Data. Start")
    processed_lead = process_lead_data(lead_data)
    log.debug(f"Lead #{lead_id}. Process Data. End")
    if processed_lead is None:
        log.info(f"Lead #{lead_id} handling ended")
        return {
            "status": "error",
            "message": "Lead received and processed, but wasnt sent. Check logs for further information.",
            "lead_id": lead_data.get("id"),
            "data": processed_lead
        }
    
    log.debug(f"Lead #{lead_id}. Sending Data. Start.")

    if processed_lead.get("is_telegram", False):
        log.debug(f"Lead #{lead_id}. Sending Data. Start. Telegram.")
        if lead_data.get("is_form", True):
            log.debug(f"Lead #{lead_id}. Sending Data. Start. Telegram. Form.")
            send_form_to_telegram(lead_data)
        else:
            log.debug(f"Lead #{lead_id}. Sending Data. Start. Telegram. Chat.")
            send_lead_to_telegram(lead_data)
        log.debug(f"Lead #{lead_id}. Sending Data. End. Telegram.")

    if processed_lead.get("is_mail", False):
        log.debug(f"Lead #{lead_id}. Sending Data. Start. Email.")
        if lead_data.get("is_form", True):
            log.debug(f"Lead #{lead_id}. Sending Data. Start. Email. Form.")
            send_form_to_mail(lead_data)
        else:
            log.debug(f"Lead #{lead_id}. Sending Data. Start. Email. Chat.")
            send_lead_to_mail(lead_data)
        log.debug(f"Lead #{lead_id}. Sending Data. End. Email.")

    log.debug(f"Lead #{lead_id}. Sending Data. End.")
    
    log.info(f"Lead #{lead_id} handling ended")
    return {
        "status": "success",
        "message": "Lead received and processed",
        "lead_id": lead_data.get("id"),
        "data": processed_lead
    }

def send_lead_to_telegram(lead_data: Dict[str, Any]):
    lead_id = lead_data.get("id", "")
    lead_source = lead_data.get("source", "")
    lead_text = lead_data.get("text", "")
    tg_message = (
        f"🔔 <b>Новый лид</b>\n\n"
        f"🌐 <b>Чат:</b> {lead_source}\n"
        f"🕐 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"🆔 <b>ID:</b> {lead_id}\n"
        f"{lead_text}"
    )
    try:
        token = config.TELEGRAM_BOT_TOKEN
        chat_ids = config.source_data.get("source", {}).get("telegram_ids", [])
        chat_ids.extend(config.default_telegram_ids)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        responses = []
        log.debug(f"Lead #{lead_id}. Sending to chats: {str(chat_ids)}")
        for chat_id in chat_ids:
            payload = {"chat_id": chat_id, "text": tg_message, "parse_mode": "HTML"}
            r = requests.post(url, data=payload, timeout=10)
            responses.append((payload, r.content))
        return responses
    except Exception as e:
        log.error(f"Ошибка Telegram: {e}")
        return None

def send_form_to_telegram(lead_data: Dict[str, Any]):
    lead_name = lead_data.get("name", "")
    lead_phone = lead_data.get("phone", "")
    lead_email = lead_data.get("email", "")
    lead_id = lead_data.get("id", "")
    lead_source = lead_data.get("source", "")
    lead_campaign = lead_data.get("campaign", "")
    lead_text = lead_data.get("text", "")
    tg_message = (
        f"🔔 <b>Новая заявка</b>\n\n"
        f"🌐 <b>Сайт:</b> {lead_source}\n"
        f"📝 <b>Форма:</b> {lead_campaign}\n"
        f"👤 <b>Имя:</b> {lead_name}\n"
        f"📞 <b>Телефон:</b> {lead_phone}\n"
        f"📧 <b>Email:</b> {lead_email}\n"
        f"🕐 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"🆔 <b>ID:</b> {lead_id}\n"
        f"{lead_text}"
    )
    try:
        token = config.TELEGRAM_BOT_TOKEN
        chat_ids = config.source_data.get("source", {}).get("telegram_ids", [])
        chat_ids.extend(config.default_telegram_ids)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        responses = []
        log.debug(f"Lead #{lead_id}. Sending to chats: {str(chat_ids)}")
        for chat_id in chat_ids:
            payload = {"chat_id": chat_id, "text": tg_message, "parse_mode": "HTML"}
            r = requests.post(url, data=payload, timeout=10)
            responses.append((payload, r.content))
        return responses
    except Exception as e:
        log.error(f"Ошибка Telegram: {e}")
        return None
    
def send_lead_to_mail(lead_data: Dict[str, Any]) -> bool:
    lead_id = lead_data.get("id", "")
    lead_source = lead_data.get("source", "")
    lead_text = lead_data.get("text", "")
    subject = f"Новый лид с чата {lead_source}"
    body = (
        f"Чат: {lead_source}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"ID заявки: {lead_id}\n"
        f"{lead_text}"
    )
    try:
        recievers = config.source_data.get("source", {}).get("emails", [])
        recievers.extend(config.default_emails)
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = config.SMTP_from

        log.debug(f"Lead #{lead_id}. Sending to emails: {str(recievers)}")
        for to in recievers:
            msg["To"] = to
            with smtplib.SMTP(config.SMTP_host, config.SMTP_port) as server:
                server.starttls()
                server.login(config.SMPT_login, config.SMPT_pass)
                server.send_message(msg)

        return True
    except Exception as e:
        log.error(f"Ошибка SMTP: {e}")
        return False

def send_form_to_mail(lead_data: Dict[str, Any]):
    lead_name = lead_data.get("name", "")
    lead_phone = lead_data.get("phone", "")
    lead_email = lead_data.get("email", "")
    lead_id = lead_data.get("id", "")
    lead_source = lead_data.get("source", "")
    lead_campaign = lead_data.get("campaign", "")
    lead_text = lead_data.get("text", "")
    subject = f"Новая заявка с сайта {lead_source}"
    body = (
        f"Сайт: {lead_source}\n"
        f"Форма: {lead_campaign}\n"
        f"Имя: {lead_name}\n"
        f"Телефон: {lead_phone}\n"
        f"Email: {lead_email}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"ID заявки: {lead_id}\n"
        f"{lead_text}"
    )
    try:
        recievers = config.source_data.get("source", {}).get("emails", [])
        recievers.extend(config.default_emails)
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = config.SMTP_from

        log.debug(f"Lead #{lead_id}. Sending to emails: {str(recievers)}")
        for to in recievers:
            msg["To"] = to
            with smtplib.SMTP(config.SMTP_host, config.SMTP_port) as server:
                server.starttls()
                server.login(config.SMPT_login, config.SMPT_pass)
                server.send_message(msg)

        return True
    except Exception as e:
        log.error(f"Ошибка SMTP: {e}")
        return False

def process_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обрабатывает входящие данные лида
    """
    lead_id = lead_data.get("id", "|No uuid|")
    # Валидация данных
    log.debug(f"Lead #{lead_id}. Validate Data. Start")
    is_valid = validate_lead_data(lead_data)
    log.debug(f"Lead #{lead_id}. Validate Data. End")
    if not is_valid:
        return None
    # Фильтрация данных
    log.debug(f"Lead #{lead_id}. Filter Data. Start")
    is_spam = filter_lead_data(lead_data)
    log.debug(f"Lead #{lead_id}. Filter Data. End")
    if is_spam:
        return None
    return lead_data

def is_phone_valid(phone: str, lead_id: str) -> bool:
    """
    Проверка российского телефона:
    - Пустой телефон допустим (True)
    - Оставляем только цифры
    - Допускаем:
        * 6 или 7 цифр (городской номер)
        * 10 цифр, если начинается с 9 (мобильный без кода страны)
        * 11 цифр, если начинается с 7 или 8
        * 12 цифр, если начинается с 7 (аналог "+7", только без плюса)
    """
    if not phone:
        return True  # пустой телефон допустим

    # оставляем только цифры
    clean_phone = re.sub(r"[^0-9]", "", phone)

    if not clean_phone.isdigit():
        log.info(f"Lead #{lead_id} is not valid. Reason: phone number contains not digits")
        return False

    length = len(clean_phone)

    if length == 6:  # городской короткий
        return True

    if length == 7:  # городской
        return True

    if length == 10 and clean_phone.startswith("9"):  # мобильный без кода страны
        return True

    if length == 11 and clean_phone[0] in ("7", "8"):  # полный российский номер
        return True

    if length == 12 and clean_phone.startswith("7"):  # "+7" без плюса
        return True

    log.info(f"Lead #{lead_id} is not valid. Reason: didnt pass Russian phone numbers checks")
    return False

def is_email_valid(email: str, lead_id: str) -> bool:
    """
    Проверка email по логике:
    - Пустой email допустим (True)
    - Проверка синтаксиса
    - Блокировка временных/подозрительных доменов
    """

    if not email:
        return True  # пустой email допустим

    # базовая проверка
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        log.info(f"Lead #{lead_id} is not valid. Reason: email re.match error")
        return False

    # подозрительные домены
    suspicious_domains = [
        "tempmail.", "temp-mail.", "10minutemail.", "guerrillamail.",
        "mailinator.", "throwaway.", "spambox.", "trashmail."
    ]

    email_lower = email.lower()
    for domain in suspicious_domains:
        if domain in email_lower:
            log.info(f"Lead #{lead_id} is not valid. Reason: email is temporary ({domain})")
            return False

    # Email is valid
    return True

def validate_lead_data(lead_data: Dict[str, Any]) -> bool:
    """
    Валидирует данные лида
    """
    lead_id = lead_data.get("id", "|No uuid|")
    lead_source = lead_data.get("source", None)
    lead_api_key = lead_data.get("api_key", None)
    lead_phone = lead_data.get("phone", "")
    lead_email = lead_data.get("email", "")

    # Проверка наличия source
    if not lead_source:
        log.info(f"Lead #{lead_id} rejected. Reason: missing source")
        return False

    # Проверка наличия api_key
    if not lead_api_key:
        log.info(f"Lead #{lead_id} rejected. Reason: missing api_key")
        return False
    
    # Проверка что source есть в source_data
    if lead_source not in config.source_data:
        log.info(f"Lead #{lead_id} rejected. Reason: source '{lead_source}' not in source_data")
        return False

    # Проверка API ключа для данного источника
    expected_api_key = config.source_data.get(lead_source, {}).get("api_key", "")
    if expected_api_key != lead_api_key:
        log.info(f"Lead #{lead_id} rejected. Reason: invalid api_key for source '{lead_source}'")
        return False
    
    is_email_valid_check = is_email_valid(lead_email, lead_id)
    if not is_email_valid_check:
        return False

    is_phone_valid_check = is_phone_valid(lead_phone, lead_id)
    if not is_phone_valid_check:
        return False

    return True

def filter_lead_data(lead_data: Dict[str, Any]) -> bool:
    """
    Фильрует данные лида 
    Возвращает True если спам
    """
    lead_id = lead_data.get("id", "|No uuid|")
    lead_text = lead_data.get("text", "")
    lead_name = lead_data.get("name", "")
    text = lead_name + "\n" + lead_text

    text_lower = text.lower()
    for word in config.spam_words:
        if word.lower() in text_lower:
            log.info(f"Lead #{lead_id} is spam. Reason: contains banned word: {word}")
            return True
        
    # Не нашли причин, что это спам
    log.info(f"Lead #{lead_id} is NOT spam. Reason: did not found any spam flags")
    return False

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




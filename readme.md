# Lead Delivery System

Система для приёма, обработки, валидации и отправки лидов через Telegram и Email. Поддерживает лиды из чатов и веб-форм с автоматической фильтрацией спама.

## Возможности

- ✅ **REST API** для приёма лидов
- ✅ **Валидация данных** (телефоны, email)
- ✅ **Спам-фильтрация** по ключевым словам
- ✅ **Отправка в Telegram** с форматированием HTML
- ✅ **Отправка на Email** через SMTP
- ✅ **Поддержка двух типов лидов**: чаты и формы
- ✅ **Логирование** всех операций
- ✅ **UUID** для отслеживания каждого лида

## Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository_url>
cd lead-delivery-system
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**
```bash
cp config.example.py config.py
```

4. **Заполните настройки** в `config.py` (см. [Конфигурация](#конфигурация))

5. **Запустите сервер:**
```bash
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

## API

### POST /leads

Принимает данные лида и обрабатывает их согласно настройкам.

**Структура запроса:**
```json
{
    "name": "Иван Иванов",          // опционально
    "email": "ivan@example.com",     // опционально  
    "phone": "+79991234567",         // опционально
    "text": "Дополнительный текст",   // опционально
    "source": "website_name",        // ОБЯЗАТЕЛЬНО (из sources)
    "api_key": "your_secret_key",    // ОБЯЗАТЕЛЬНО (из source_data)
    "campaign": "contact_form",      // опционально
    "is_telegram": false,            // опционально (по умолчанию false)
    "is_mail": false,               // опционально (по умолчанию false)
    "is_form": true                 // опционально (по умолчанию true)
}
```

**Ответ при успехе:**
```json
{
    "status": "success",
    "message": "Lead received and processed",
    "lead_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": { ... }
}
```

**Ответ при ошибке:**
```json
{
    "status": "error", 
    "message": "Lead received and processed, but wasnt sent. Check logs for further information.",
    "lead_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": null
}
```

## Конфигурация

### Основные настройки в `config.py`

```python
# Разрешённые источники лидов
sources = (
    "website_name",
    "chat_source", 
    "landing_page"
)

# Стоп-слова для фильтрации спама  
spam_words = (
    'спам',
    'реклама',
    'продажа'
)

# Telegram чаты по умолчанию
default_telegram_ids = [-1001234567890]

# Email получатели по умолчанию
default_emails = ["manager@company.com"]
```

### SMTP настройки
```python
SMTP_host = "smtp.gmail.com"
SMTP_port = 587
SMPT_login = "your_email@gmail.com" 
SMPT_pass = "your_app_password"
SMTP_from = "noreply@company.com"
```

### Telegram настройки
```python
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
```

### ⚠️ Важная настройка: `source_data`

Это **ключевая конфигурация** системы, которая определяет куда отправлять лиды от каждого источника:

```python
source_data = {
    "website_name": {
        "api_key": "secret_key_for_website_name",
        "telegram_ids": [-1001111111111, -1002222222222], 
        "emails": ["sales@company.com", "manager@company.com"]
    },
    "chat_source": {
        "api_key": "secret_key_for_chat_source",
        "telegram_ids": [-1003333333333],
        "emails": ["support@company.com"]
    }
}
```

**🔐 КРИТИЧЕСКИ ВАЖНО - БЕЗОПАСНОСТЬ:**
- Каждый `source` из запроса должен присутствовать в `sources` **И** в `source_data`
- `api_key` в запросе **ОБЯЗАТЕЛЕН** и должен точно совпадать с ключом в `source_data[source]["api_key"]`
- Если источника нет в `source_data`, лид **НЕ БУДЕТ ОТПРАВЛЕН**
- Если `api_key` неверный или отсутствует, лид **БУДЕТ ОТКЛОНЕН**
- Telegram ID чаты должны быть **отрицательными числами** (групповые чаты)
- Email адреса будут объединены с `default_emails`
- Telegram ID будут объединены с `default_telegram_ids`
- **Храните API ключи в секрете!** Не публикуйте их в открытых репозиториях

## Типы лидов

### 1. Лиды из форм (`is_form: true`)
Приходят с сайтов через контактные формы. Содержат структурированные данные.

**Формат Telegram сообщения:**
```
🔔 Новая заявка

🌐 Сайт: website_name
📝 Форма: contact_form  
👤 Имя: Иван Иванов
📞 Телефон: +79991234567
📧 Email: ivan@example.com
🕐 Время: 25.08.2025 14:30:00
🆔 ID: 550e8400-e29b-41d4-a716-446655440000
Дополнительный текст
```

### 2. Лиды из чатов (`is_form: false`)
Приходят из мессенджеров, чат-ботов, социальных сетей.

**Формат Telegram сообщения:**
```
🔔 Новый лид

🌐 Чат: telegram_bot
🕐 Время: 25.08.2025 14:30:00  
🆔 ID: 550e8400-e29b-41d4-a716-446655440000
Текст сообщения от пользователя
```

## Валидация данных

### Телефонные номера
Поддерживаются российские номера:
- ✅ Пустой номер (допустимо)
- ✅ 6-7 цифр (городской)  
- ✅ 10 цифр начиная с "9" (мобильный без кода)
- ✅ 11 цифр начиная с "7" или "8"
- ✅ 12 цифр начиная с "7" (международный формат)

### Email адреса
- ✅ Пустой email (допустимо)
- ✅ Стандартная проверка регулярным выражением
- ❌ Блокировка временных email сервисов (`tempmail`, `10minutemail` и др.)

### Источники и API ключи
- ✅ Источник должен быть в списке `sources`
- ✅ Источник должен присутствовать в `source_data`
- ✅ API ключ обязателен в каждом запросе
- ✅ API ключ должен точно совпадать с настройкой в конфигурации
- ❌ Неизвестные источники отклоняются
- ❌ Запросы без API ключа отклоняются
- ❌ Неверные API ключи отклоняются

## Спам-фильтрация

Система проверяет поля `name` и `text` на наличие слов из `spam_words`:
- Проверка регистронезависимая
- При обнаружении спама лид отклоняется
- Все проверки логируются

## Логирование

Подробное логирование всех операций:

```
2025-08-25 14:30:00 [DEBUG] Lead #550e8400. Got. Data: {...}
2025-08-25 14:30:01 [DEBUG] Lead #550e8400. Process Data. Start
2025-08-25 14:30:01 [DEBUG] Lead #550e8400. Validate Data. Start  
2025-08-25 14:30:01 [DEBUG] Lead #550e8400. Validate Data. End
2025-08-25 14:30:01 [INFO] Lead #550e8400 is NOT spam. Reason: did not found any spam flags
2025-08-25 14:30:01 [DEBUG] Lead #550e8400. Sending Data. Start. Telegram.
2025-08-25 14:30:02 [INFO] Lead #550e8400 handling ended
```

## Примеры использования

### Отправка лида с формы
```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Петр Петров",
    "email": "petr@example.com", 
    "phone": "89991234567",
    "source": "website_name",
    "api_key": "secret_key_for_website_name",
    "campaign": "contact_form",
    "text": "Интересует ваша услуга",
    "is_form": true
  }'
```

### Отправка лида из чата
```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "source": "telegram_bot",
    "api_key": "secret_key_for_telegram_bot",
    "text": "Пользователь написал в боте: Привет! Как заказать?",
    "is_form": false
  }'
```

## Требования

- Python 3.7+
- FastAPI 0.116.1+
- Pydantic 2.11.7+
- Requests 2.32.5+ 
- Uvicorn 0.35.0+

## Файловая структура

```
lead-delivery-system/
├── main.py              # Основной код приложения
├── config.py            # Настройки (создать из config.example.py)  
├── config.example.py    # Пример настроек
├── requirements.txt     # Зависимости Python
├── README.md           # Документация
└── test.py             # Тесты (если есть)
```

## Безопасность

- **API ключи**: Обязательная проверка API ключей для каждого запроса
- **Валидация источников**: Двойная проверка source в `sources` и `source_data`
- **Валидация данных**: Все входящие данные валидируются
- **Спам-фильтрация**: По настраиваемым правилам в `spam_words`
- **Аудит**: Подробное логирование всех операций и причин отклонения
- **Email защита**: Блокировка временных email сервисов
- **Отклонение подозрительных запросов**: Автоматическое отклонение лидов без source или api_key

## Мониторинг

Для мониторинга работы системы:
1. Проверяйте логи на наличие ошибок
2. Отслеживайте статусы ответов API
3. Контролируйте доставку в Telegram и Email
4. Анализируйте количество отклонённых лидов

---

**Автор:** Ammiteus/Ammite  
**Версия:** 1.0.0
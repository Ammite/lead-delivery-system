# Lead Delivery System

Система для приёма, обработки, валидации и отправки лидов через Telegram и Email. Поддерживает лиды из чатов и веб-форм с автоматической фильтрацией спама.

## Возможности

- ✅ **REST API** для приёма лидов
- ✅ **Валидация данных** (телефоны, email)
- ✅ **Спам-фильтрация** по ключевым словам
- ✅ **Асинхронная отправка в Telegram** с форматированием HTML
- ✅ **Асинхронная отправка на Email** через SMTP
- ✅ **Параллельная обработка** всех отправок
- ✅ **Поддержка двух типов лидов**: чаты и формы
- ✅ **Логирование** всех операций
- ✅ **UUID** для отслеживания каждого лида
- ✅ **Высокая производительность** благодаря async/await

## Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/Ammite/lead-delivery-system
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

## Развертывание в Ubuntu (Production)

### Автоматическая установка

1. **Клонируйте репозиторий на сервер:**
```bash
git clone https://github.com/Ammite/lead-delivery-system
cd lead-delivery-system
```

2. **Запустите скрипт установки:**
```bash
chmod +x install.sh
sudo ./install.sh
```

Скрипт автоматически:
- Установит зависимости системы
- Создаст пользователя сервиса
- Настроит Python окружение
- Создаст systemd сервис
- Настроит Nginx reverse proxy
- Настроит firewall

3. **Настройте конфигурацию:**
```bash
sudo nano /opt/lead-delivery-system/config.py
sudo nano /opt/lead-delivery-system/.env
```

4. **Перезапустите сервис:**
```bash
sudo systemctl restart lead-delivery-system
```

### Управление сервисом

Используйте скрипт `manage.sh` для управления:

```bash
# Сделать исполняемым
chmod +x manage.sh

# Основные команды
./manage.sh start      # Запустить сервис
./manage.sh stop       # Остановить сервис  
./manage.sh restart    # Перезапустить сервис
./manage.sh status     # Показать статус
./manage.sh logs       # Показать логи в реальном времени
./manage.sh test       # Запустить нагрузочные тесты
./manage.sh backup     # Создать backup конфигурации
./manage.sh restore    # Восстановить из backup
./manage.sh update     # Обновить код из git
```

### Ручная установка

<details>
<summary>Для расширенной настройки (нажмите для раскрытия)</summary>

1. **Установите зависимости:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx systemd
```

2. **Создайте директорию и пользователя:**
```bash
sudo useradd --system --home-dir /opt/lead-delivery-system --shell /bin/false www-data
sudo mkdir -p /opt/lead-delivery-system
sudo chown www-data:www-data /opt/lead-delivery-system
```

3. **Скопируйте файлы:**
```bash
sudo cp -r . /opt/lead-delivery-system/
sudo chown -R www-data:www-data /opt/lead-delivery-system
```

4. **Настройте Python окружение:**
```bash
cd /opt/lead-delivery-system
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt
```

5. **Установите systemd сервис:**
```bash
sudo cp lead-delivery-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lead-delivery-system
sudo systemctl start lead-delivery-system
```

6. **Настройте Nginx (опционально):**
```bash
# Скопируйте конфигурацию из install.sh
sudo systemctl restart nginx
```

</details>

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
- aiohttp 3.12.15+ (для асинхронных HTTP запросов)
- aiosmtplib 4.0.2+ (для асинхронного SMTP)
- Requests 2.32.5+ 
- Uvicorn 0.35.0+

## Файловая структура

```
lead-delivery-system/
├── main.py                      # Основной код приложения (FastAPI + async)
├── config.py                    # Настройки (создать из config.example.py)  
├── config.example.py            # Пример настроек
├── requirements.txt             # Зависимости Python
├── test.py                     # Юнит-тесты
├── simple_load_test.py         # Нагрузочные тесты
├── load_test.py                # Продвинутые нагрузочные тесты
├── lead-delivery-system.service # Systemd сервис файл
├── install.sh                  # Скрипт автоматической установки Ubuntu
├── manage.sh                   # Скрипт управления сервисом
└── README.md                   # Документация
```

## Производительность

**Асинхронная архитектура:**
- ⚡ **Параллельные HTTP запросы** к Telegram API через aiohttp
- ⚡ **Параллельная отправка email** через aiosmtplib
- ⚡ **Одновременная обработка** Telegram и Email отправок
- ⚡ **Отсутствие блокировок** при отправке в несколько чатов/адресов

**Улучшения производительности:**
- 🚀 Время обработки сокращено с ~2 секунд до миллисекунд
- 🚀 RPS увеличен с ~10 до 100+ запросов в секунду
- 🚀 Масштабируемость при росте числа получателей
- 🚀 Эффективное использование ресурсов сервера

**Нагрузочное тестирование:**
```bash
# Простой нагрузочный тест
python simple_load_test.py

# Расширенный тест с выбором сценариев
python load_test.py
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
1. **Производительность**: Используйте нагрузочные тесты для контроля RPS
2. **Логи**: Проверяйте логи на наличие ошибок отправки
3. **API статусы**: Отслеживайте статусы ответов API
4. **Доставляемость**: Контролируйте успешность доставки в Telegram и Email
5. **Отклонения**: Анализируйте количество отклонённых лидов по причинам
6. **Асинхронные задачи**: Мониторьте время выполнения параллельных задач

---

**Автор:** Ammiteus/Ammite  
**Версия:** 1.0.0
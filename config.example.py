sources = (
    "tuple of source list",
)

spam_words = (
    'tuple of spam words', 
    'tuple of spam words', 
)
'''
Telegram id table:
'''
default_telegram_ids = []
'''
Emails table:

'''
default_emails = []


source_data = {
    "source_name_1": {
        "api_key": "",
        "telegram_ids": [],
        "emails": []
    },
    "source_name_2": {
        "api_key": "",
        "telegram_ids": [],
        "emails": []
    }
}


# SMTP
SMTP_host = ""
SMTP_port = ""
SMPT_login = ""
SMPT_pass = ""
SMTP_from = ""


# Telegram
TELEGRAM_BOT_TOKEN = "your_token"
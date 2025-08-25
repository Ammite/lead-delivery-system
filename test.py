import pytest
import requests
import json
import uuid
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestLeadDeliverySystem:
    
    def test_valid_form_lead(self):
        """Тест валидной заявки с формы"""
        lead_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com", 
            "phone": "79161234567",
            "text": "Хочу заказать услугу",
            "source": "rde.tomsk.ru",
            "api_key": "51b1f7314d70c6d6bf70e72ec8817ec4",
            "campaign": "contact_form",
            "is_form": True,
            "is_telegram": False,
            "is_mail": False
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "lead_id" in data
        
    def test_valid_chat_lead(self):
        """Тест валидного лида из чата"""
        lead_data = {
            "text": "Пользователь написал сообщение",
            "source": "smedia",
            "api_key": "6b037468ae0488072b31b198fab8f3e7",
            "is_form": False,
            "is_telegram": False,
            "is_mail": False
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
    def test_minimal_lead(self):
        """Тест минимального лида с обязательными полями"""
        lead_data = {
            "source": "radio",
            "api_key": "907a76f5718e3124f0762442fadfc67a"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
    def test_invalid_source(self):
        """Тест с невалидным источником"""
        lead_data = {
            "name": "Тест",
            "source": "invalid_source",
            "api_key": "some_key",
            "phone": "79161234567"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_spam_text(self):
        """Тест спам-фильтра по тексту"""
        lead_data = {
            "name": "Спаммер",
            "text": "Лучшее casino в интернете!",
            "source": "baget",
            "api_key": "dc8b5c0d189b75fdea5b14e2843e1430",
            "phone": "79161234567"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_spam_name(self):
        """Тест спам-фильтра по имени"""
        lead_data = {
            "name": "porn site promotion",
            "text": "Обычный текст",
            "source": "flagi",
            "api_key": "84d82ab836d4e4e07d8855a59d244482",
            "email": "test@example.com"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_invalid_phone_formats(self):
        """Тест различных невалидных форматов телефонов"""
        invalid_phones = [
            "123",           # слишком короткий (3 цифры)
            "12345",         # слишком короткий (5 цифр)  
            "12345678901234567890", # слишком длинный
            "abc123def",     # содержит буквы после очистки станет 123
            "1234567890",    # 10 цифр но не начинается с 9
            "21234567890",   # 11 цифр но не начинается с 7 или 8
            "612345678901",  # 12 цифр но не начинается с 7
            "8",             # 1 цифра
            "12",            # 2 цифры
            "1234",          # 4 цифры
            "12345678",      # 8 цифр
            "123456789"      # 9 цифр
        ]
        
        for phone in invalid_phones:
            lead_data = {
                "name": "Тест",
                "phone": phone,
                "source": "loshadka",
                "api_key": "82175fd27093d1b58b5f8544e6c2999a"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "error", f"Phone {phone} should be invalid"
            
    def test_valid_phone_formats(self):
        """Тест валидных форматов российских телефонов"""
        valid_phones = [
            "",              # пустой телефон
            "123456",        # городской 6 цифр
            "1234567",       # городской 7 цифр  
            "9161234567",    # мобильный без кода
            "79161234567",   # полный с 7
            "89161234567",   # полный с 8
            "779161234567"   # +7 без плюса
        ]
        
        for phone in valid_phones:
            lead_data = {
                "name": "Тест",
                "phone": phone,
                "source": "fortis",
                "api_key": "405d5b75a5e87cd04a5791c103d52cc2"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success", f"Phone {phone} should be valid"
            
    def test_invalid_email_formats(self):
        """Тест невалидных email адресов"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@tempmail.com",
            "test@10minutemail.com",
            "spam@guerrillamail.net",
            "fake@mailinator.org"
        ]
        
        for email in invalid_emails:
            lead_data = {
                "name": "Тест",
                "email": email,
                "source": "dorogoe",
                "api_key": "b36145ddb5361643de60cc67e188e22a"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "error", f"Email {email} should be invalid"
            
    def test_valid_email_formats(self):
        """Тест валидных email адресов"""
        valid_emails = [
            "",                    # пустой email
            "user@example.com",
            "test.email@domain.ru",
            "user+tag@site.co.uk",
            "admin@subdomain.example.org"
        ]
        
        for email in valid_emails:
            lead_data = {
                "name": "Тест",
                "email": email,
                "source": "themost",
                "api_key": "0497acbf69965dfd2724c54bd59590ed"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success", f"Email {email} should be valid"
            
    def test_all_spam_words(self):
        """Тест всех спам-слов из config"""
        spam_words = [
            'casino', 'porn', 'viagra', 'loan', 'credit', 
            'seo продвижение', 'раскрутка сайта', 'backlinks', 
            'бонус', 'крипто'
        ]
        
        for word in spam_words:
            lead_data = {
                "name": f"Пользователь {word}",
                "source": "rde.ru",
                "api_key": "548af577ef1b89c1a8744445359ce07f"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "error", f"Word '{word}' should trigger spam filter"
            
    def test_complete_form_lead(self):
        """Тест полной заявки с формы со всеми полями"""
        lead_data = {
            "name": "Анна Смирнова",
            "email": "anna@company.ru",
            "phone": "74951234567",
            "text": "Интересует разработка сайта для малого бизнеса",
            "source": "rde.tomsk.ru",
            "api_key": "51b1f7314d70c6d6bf70e72ec8817ec4",
            "campaign": "landing_form",
            "is_form": True,
            "is_telegram": False,
            "is_mail": False
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "lead_id" in data
        
    def test_case_insensitive_spam_filter(self):
        """Тест регистронезависимости спам-фильтра"""
        lead_data = {
            "name": "CASINO BEST",
            "text": "КРИПТО валюты",
            "source": "smedia",
            "api_key": "6b037468ae0488072b31b198fab8f3e7"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_multiple_sources(self):
        """Тест всех доступных источников"""
        sources_with_keys = {
            "rde.tomsk.ru": "51b1f7314d70c6d6bf70e72ec8817ec4",
            "smedia": "6b037468ae0488072b31b198fab8f3e7",
            "radio": "907a76f5718e3124f0762442fadfc67a",
            "baget": "dc8b5c0d189b75fdea5b14e2843e1430",
            "flagi": "84d82ab836d4e4e07d8855a59d244482",
            "loshadka": "82175fd27093d1b58b5f8544e6c2999a",
            "fortis": "405d5b75a5e87cd04a5791c103d52cc2",
            "dorogoe": "b36145ddb5361643de60cc67e188e22a",
            "themost": "0497acbf69965dfd2724c54bd59590ed",
            "rde.ru": "548af577ef1b89c1a8744445359ce07f"
        }
        
        for source, api_key in sources_with_keys.items():
            lead_data = {
                "name": "Тестовый пользователь",
                "source": source,
                "api_key": api_key
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success", f"Source {source} should be valid"
            
    def test_missing_data_fields(self):
        """Тест обработки пустых данных"""
        lead_data = {
            "source": "radio",
            "api_key": "907a76f5718e3124f0762442fadfc67a"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
    def test_boolean_flags(self):
        """Тест обработки всех boolean флагов"""
        # Тест с включенным telegram
        lead_data = {
            "name": "Тест",
            "source": "baget",
            "api_key": "dc8b5c0d189b75fdea5b14e2843e1430",
            "is_form": True,
            "is_telegram": True,
            "is_mail": False
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        # Тест с включенным email
        lead_data_mail = {
            "name": "Тест",
            "source": "baget",
            "api_key": "dc8b5c0d189b75fdea5b14e2843e1430",
            "is_form": True,
            "is_telegram": False,
            "is_mail": True
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data_mail)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
    def test_phone_with_special_chars(self):
        """Тест телефонов со специальными символами"""
        phones_with_chars = [
            "+7 (916) 123-45-67",  # очистится до 79161234567 (11 цифр, начинается с 7)
            "8-916-123-45-67",     # очистится до 89161234567 (11 цифр, начинается с 8) 
            "+7 916 123 45 67",    # очистится до 79161234567 (11 цифр, начинается с 7)
            "(495) 123-4567",      # очистится до 4951234567 (10 цифр, НЕ начинается с 9) - НЕВАЛИДЕН!
            "+7(916)123-45-67"     # очистится до 79161234567 (11 цифр, начинается с 7)
        ]
        
        for phone in phones_with_chars:
            lead_data = {
                "name": "Тест",
                "phone": phone,
                "source": "flagi",
                "api_key": "84d82ab836d4e4e07d8855a59d244482"
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            # (495) 123-4567 после очистки станет 4951234567 - 10 цифр, но не начинается с 9, поэтому невалиден
            if phone == "(495) 123-4567":
                assert data["status"] == "error", f"Phone {phone} should be invalid after cleaning (10 digits not starting with 9)"
            else:
                assert data["status"] == "success", f"Phone {phone} should be valid after cleaning"
            
    def test_chat_vs_form_flag(self):
        """Тест различий между чатом и формой"""
        # Тест чата
        chat_data = {
            "text": "Сообщение из чата",
            "source": "smedia",
            "api_key": "6b037468ae0488072b31b198fab8f3e7",
            "is_form": False
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=chat_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Тест формы  
        form_data = {
            "name": "Пользователь",
            "email": "user@test.com",
            "phone": "79161234567",
            "source": "smedia",
            "api_key": "6b037468ae0488072b31b198fab8f3e7", 
            "campaign": "main_form",
            "is_form": True
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=form_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
    def test_missing_api_key(self):
        """Тест отсутствующего API ключа"""
        lead_data = {
            "name": "Тест без ключа",
            "source": "rde.tomsk.ru"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_missing_source(self):
        """Тест отсутствующего source"""
        lead_data = {
            "name": "Тест без source",
            "api_key": "51b1f7314d70c6d6bf70e72ec8817ec4"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_wrong_api_key(self):
        """Тест неверного API ключа"""
        lead_data = {
            "name": "Тест с неверным ключом",
            "source": "rde.tomsk.ru",
            "api_key": "wrong_key_123456789"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_api_key_source_mismatch(self):
        """Тест несоответствия API ключа и источника"""
        lead_data = {
            "name": "Тест несоответствия",
            "source": "rde.tomsk.ru",
            "api_key": "6b037468ae0488072b31b198fab8f3e7"  # это ключ для smedia, а не rde.tomsk.ru
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_source_not_in_source_data(self):
        """Тест источника отсутствующего в source_data (но может быть в sources)"""
        lead_data = {
            "name": "Тест источника вне source_data",
            "source": "unknown_source",
            "api_key": "some_random_key"
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_all_sources_with_correct_keys(self):
        """Тест всех источников с правильными API ключами"""
        sources_with_keys = {
            "rde.tomsk.ru": "51b1f7314d70c6d6bf70e72ec8817ec4",
            "smedia": "6b037468ae0488072b31b198fab8f3e7",
            "radio": "907a76f5718e3124f0762442fadfc67a",
            "baget": "dc8b5c0d189b75fdea5b14e2843e1430",
            "flagi": "84d82ab836d4e4e07d8855a59d244482",
            "loshadka": "82175fd27093d1b58b5f8544e6c2999a",
            "fortis": "405d5b75a5e87cd04a5791c103d52cc2",
            "dorogoe": "b36145ddb5361643de60cc67e188e22a",
            "themost": "0497acbf69965dfd2724c54bd59590ed",
            "rde.ru": "548af577ef1b89c1a8744445359ce07f"
        }
        
        for source, api_key in sources_with_keys.items():
            lead_data = {
                "name": f"Тест для {source}",
                "source": source,
                "api_key": api_key
            }
            
            response = requests.post(f"{BASE_URL}/leads", json=lead_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success", f"Source {source} with correct API key should work"
            
    def test_empty_api_key(self):
        """Тест пустого API ключа"""
        lead_data = {
            "name": "Тест с пустым ключом",
            "source": "rde.tomsk.ru",
            "api_key": ""
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        
    def test_null_api_key(self):
        """Тест null API ключа"""
        lead_data = {
            "name": "Тест с null ключом", 
            "source": "rde.tomsk.ru",
            "api_key": None
        }
        
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"

if __name__ == "__main__":
    print("Запуск тестов Lead Delivery System...")
    print("Убедитесь что сервис запущен на http://localhost:8000")
    print()
    print("Для запуска тестов используйте:")
    print("pip install pytest requests")
    print("pytest test.py -v")
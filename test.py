import requests
from requests import get
import json
import base64
import random
from textwrap import fill

def print_banner():
    banner = """
     ██░ ██  █    ██  ███▄ ▄███▓ ▒█████   ██▒   █▓ ██▒   █▓
    ▓██░ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▒██▒  ██▒▓██░   █▒▓██░   █▒
    ▒██▀▀██░▓██  ▒██░▓██    ▓██░▒██░  ██▒ ▓██  █▒░ ▓██  █▒░
    ░▓█ ░██ ▓▓█  ░██░▒██    ▒██ ▒██   ██░  ▒██ █░░  ▒██ █░░
    ░▓█▒░██▓▒▒█████▓ ▒██▒   ░██▒░ ████▓▒░   ▒▀█░     ▒▀█░  
     ▒ ░░▒░▒░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░ ▒░▒░▒░    ░ ▐░     ░ ▐░  
     ▒ ░▒░ ░░░▒░ ░ ░ ░  ░      ░  ░ ▒ ▒░    ░ ░░     ░ ░░  
     ░  ░░ ░ ░░░ ░ ░ ░      ░   ░ ░ ░ ▒       ░░       ░░  
     ░  ░  ░   ░            ░       ░ ░        ░        ░  
                                              ░        ░   
    """
    print(banner)

def clean_data(data):
    """Очищает данные от ненужной технической информации и возвращает только полезные данные"""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Убираем технические поля
            if key.lower() in ['rows', 'count', 'status', 'error', 'success', 'message', 'score', '_id', 'index']:
                continue
            if isinstance(value, (dict, list)):
                cleaned_value = clean_data(value)
                if cleaned_value:  # Добавляем только если есть данные
                    cleaned[key] = cleaned_value
            elif value:  # Добавляем только непустые значения
                cleaned[key] = value
        return cleaned if cleaned else None
    
    elif isinstance(data, list):
        cleaned = []
        for item in data:
            cleaned_item = clean_data(item)
            if cleaned_item:  # Добавляем только если есть данные
                cleaned.append(cleaned_item)
        return cleaned if cleaned else None
    
    else:
        return data if data else None

def format_value(value, indent=0, max_width=80):
    """Форматирует значение для красивого вывода с переносами"""
    indent_str = " " * indent
    if isinstance(value, dict):
        result = ""
        for k, v in value.items():
            formatted = format_value(v, indent + 4, max_width - indent - 4)
            if formatted:
                result += f"\n{indent_str}{k}: {formatted}"
        return result if result else None
    elif isinstance(value, list):
        result = ""
        for i, item in enumerate(value, 1):
            formatted = format_value(item, indent + 4, max_width - indent - 4)
            if formatted:
                result += f"\n{indent_str}{i}. {formatted}"
        return result if result else None
    else:
        if value is None:
            return None
        # Форматируем текст с переносами
        text = str(value)
        if len(text) > max_width - indent:
            return fill(text, width=max_width - indent, subsequent_indent=' ' * (indent + 2))
        return text

def print_clean_data(data, source_name):
    """Выводит только чистые данные в красивом формате"""
    print(f"\n╔{'═' * 50}╗")
    print(f"║{f' РЕЗУЛЬТАТЫ ({source_name}) '.center(50)}║")
    print(f"╚{'═' * 50}╝")
    
    cleaned_data = clean_data(data)
    if not cleaned_data:
        print("│ Нет данных для отображения".ljust(51) + "│")
        print(f"╰{'─' * 50}╯")
        return
    
    formatted = format_value(cleaned_data)
    if formatted:
        # Разбиваем на строки и обрамляем
        lines = formatted.split('\n')
        print(f"╭{'─' * 50}╮")
        for line in lines:
            print(f"│ {line.ljust(48)} │")
        print(f"╰{'─' * 50}╯")
    else:
        print("│ Данные не содержат полезной информации".ljust(51) + "│")
        print(f"╰{'─' * 50}╯")

def check_credentials(login, password):
    try:
        # Получаем данные аутентификации с GitHub
        auth_url = "https://api.github.com/repos/mvd-cyber/login/contents/auth.json"
        response = requests.get(auth_url)
        if response.status_code != 200:
            print("Ошибка: Не удалось получить данные аутентификации")
            return False
            
        content = response.json()['content']
        decoded_content = base64.b64decode(content).decode('utf-8')
        auth_lines = decoded_content.split('\n')
        
        # Проверяем наличие комбинации логин:пароль
        credentials = f"{login}:{password}"
        for line in auth_lines:
            if line.strip() == credentials:
                return True
                
        return False
        
    except Exception as e:
        print(f"Ошибка при проверке аутентификации: {str(e)}")
        return False

def search_breachka(query, search_type, api_key):
    url = "https://breachka.com/api/v1/find/mass"
    
    payload = json.dumps({
        "requests": [query],
        "findType": search_type,
        "countryType": "RU"
    })
    
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if "bad request for url" in str(response.text).lower():
            return None
        return response.json()
    except Exception as e:
        if "bad request for url" in str(e).lower():
            return None
        return {"error": str(e)}

def search_usersbox(query, api_key):
    url = "https://api.usersbox.ru/v1/search"
    
    headers = {
        'Authorization': api_key
    }
    
    params = {
        'q': query
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if "bad request for url" in str(response.text).lower():
            return None
        return response.json()
    except Exception as e:
        if "bad request for url" in str(e).lower():
            return None
        return {"error": str(e)}

def search_leakosint(query, search_type):
    """Функция для поиска через LeakOsint API"""
    tokens = [
        "7791381618:Uvi9Sdaz",
    ]
    api_url = "https://leakosintapi.com/"
    
    token = random.choice(tokens)
    
    # Преобразуем тип поиска в формат LeakOsint
    if search_type == "VK":
        query_type = "vk"
    elif search_type == "FB":
        query_type = "facebook"
    elif search_type == "Summary" and "@" in query:
        query_type = "email"
    elif search_type == "Summary" and query.replace("+", "").isdigit():
        query_type = "phone"
    else:
        query_type = "general"
    
    data = {
        "token": token,
        "request": query,
        "limit": 100,
        "lang": "ru"
    }
    
    try:
        response = requests.post(api_url, json=data)
        if "bad request for url" in str(response.text).lower():
            return None
        response.raise_for_status()
        result = response.json()
        
        # Удаляем технические поля
        if "List" in result:
            cleaned_result = {"LeakOsint": []}
            for source, info in result["List"].items():
                if "Data" in info:
                    for entry in info["Data"]:
                        cleaned_entry = clean_data(entry)
                        if cleaned_entry:
                            cleaned_result["LeakOsint"].append({
                                "source": source,
                                "data": cleaned_entry
                            })
            return cleaned_result if cleaned_result["LeakOsint"] else {"message": "No data found"}
        return {"message": "No data found"}
    except Exception as e:
        if "bad request for url" in str(e).lower():
            return None
        return {"error": str(e)}

def universal_search(query, breachka_api_key, usersbox_api_key):
    """Универсальный поиск по доступным источникам"""
    results = {}
    
    # Определяем тип запроса
    if "@" in query:
        search_type = "Summary"  # Email
    elif query.replace("+", "").replace(" ", "").isdigit():
        search_type = "Summary"  # Телефон
    else:
        # Пробуем определить, это VK/FB или ФИО
        if "vk.com/" in query.lower() or "id" in query.lower():
            search_type = "VK"
        elif "facebook.com/" in query.lower():
            search_type = "FB"
        else:
            search_type = "Summary"  # ФИО или другое
    
    # Поиск через Breachka
    breachka_data = search_breachka(query, search_type, breachka_api_key)
    if breachka_data is not None and "error" not in breachka_data:
        results["Breachka"] = breachka_data
    
    # Поиск через UsersBox
    usersbox_data = search_usersbox(query, usersbox_api_key)
    if usersbox_data is not None and "error" not in usersbox_data:
        results["UsersBox"] = usersbox_data
    
    # Поиск через LeakOsint
    leakosint_data = search_leakosint(query, search_type)
    if leakosint_data is not None and "error" not in leakosint_data:
        results["LeakOsint"] = leakosint_data
    
    return results

def main_menu():
    """Главное меню программы"""
    print("\n╔════════════════════════════════════════════════╗")
    print("║               ГЛАВНОЕ МЕНЮ                   ║")
    print("╠════════════════════════════════════════════════╣")
    print("║ 1. Поиск по номеру телефона                  ║")
    print("║ 2. Поиск по email                            ║")
    print("║ 3. Поиск по ФИО и дате рождения              ║")
    print("║ 4. Поиск по VK username                      ║")
    print("║ 5. Поиск по VK ID                            ║")
    print("║ 6. Поиск по Facebook                         ║")
    print("║ 7. Универсальный поиск (автоопределение)     ║")
    print("║ 0. Выход                                     ║")
    print("╚════════════════════════════════════════════════╝")

def main():
    print_banner()
    
    # Запрашиваем логин и пароль
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    
    # Проверяем аутентификацию
    if not check_credentials(login, password):
        print("\n╔════════════════════════════════════════════════╗")
        print("║            ОШИБКА АВТОРИЗАЦИИ               ║")
        print("╠════════════════════════════════════════════════╣")
        print("║ Неверный логин или пароль                    ║")
        print("╚════════════════════════════════════════════════╝")
        input('\nНажмите Enter для выхода.')
        return
    
    print("\n╔════════════════════════════════════════════════╗")
    print("║          АВТОРИЗАЦИЯ УСПЕШНА                 ║")
    print("╚════════════════════════════════════════════════╝")
    
    # API ключи
    breachka_api_key = "04f377017f8d46f2be1ff59198bbb514"
    usersbox_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkX2F0IjoxNzUxOTg0NTY1LCJhcHBfaWQiOjE3NTEzMTM5MTN9.pVrdFBE0wrutI9hvlZj74Od5I_nsEpLsNsLGsqQBYEk"
    
    if not breachka_api_key:
        breachka_api_key = input("Введите API ключ для Breachka: ")
    if not usersbox_api_key:
        usersbox_api_key = input("Введите API ключ для UsersBox: ")
    
    while True:
        main_menu()
        choice = input("\nВведите номер варианта (0-7): ")
        
        if choice == "0":
            print("Выход из программы...")
            break
        
        query = ""
        search_type = ""
        
        if choice == "1":
            search_type = "Summary"
            query = input('Введите номер телефона: ')
        elif choice == "2":
            search_type = "Summary"
            query = input('Введите email: ')
        elif choice == "3":
            search_type = "Summary"
            fio = input('Введите ФИО: ')
            dob = input('Введите дату рождения (ДД.ММ.ГГГГ): ')
            query = f"{fio} {dob}"
        elif choice == "4":
            search_type = "VK"
            query = input('Введите VK username: ')
        elif choice == "5":
            search_type = "VK"
            query = input('Введите VK ID: ')
        elif choice == "6":
            search_type = "FB"
            query = input('Введите Facebook username или ID: ')
        elif choice == "7":
            query = input('Введите запрос для универсального поиска (телефон, email, ФИО, ссылка): ')
        else:
            print("Неверный выбор")
            continue
        
        print("\nВыполняем запросы...\n")
        
        if choice == "7":
            # Универсальный поиск
            results = universal_search(query, breachka_api_key, usersbox_api_key)
            for source, data in results.items():
                print_clean_data(data, source)
        else:
            # Поиск через Breachka
            breachka_data = search_breachka(query, search_type, breachka_api_key)
            if breachka_data is None:
                pass  # Не выводим ничего при bad request
            elif "error" in breachka_data:
                print("╔════════════════════════════════════════════════╗")
                print("║              ОШИБКА ПРИ ЗАПРОСЕ               ║")
                print("╠════════════════════════════════════════════════╣")
                print(f"║ Breachka: {breachka_data['error']}")
                print("╚════════════════════════════════════════════════╝")
            else:
                print_clean_data(breachka_data, "Breachka")
            
            # Поиск через UsersBox
            usersbox_data = search_usersbox(query, usersbox_api_key)
            if usersbox_data is None:
                pass  # Не выводим ничего при bad request
            elif "error" in usersbox_data:
                print("╔════════════════════════════════════════════════╗")
                print("║              ОШИБКА ПРИ ЗАПРОСЕ               ║")
                print("╠════════════════════════════════════════════════╣")
                print(f"║ UsersBox: {usersbox_data['error']}")
                print("╚════════════════════════════════════════════════╝")
            else:
                print_clean_data(usersbox_data, "UsersBox")
            
            # Поиск через LeakOsint
            leakosint_data = search_leakosint(query, search_type)
            if leakosint_data is None:
                pass  # Не выводим ничего при bad request
            elif "error" in leakosint_data:
                print("╔════════════════════════════════════════════════╗")
                print("║              ОШИБКА ПРИ ЗАПРОСЕ               ║")
                print("╠════════════════════════════════════════════════╣")
                print(f"║ LeakOsint: {leakosint_data['error']}")
                print("╚════════════════════════════════════════════════╝")
            else:
                print_clean_data(leakosint_data, "LeakOsint")
        
        input('\nНажмите Enter для продолжения...')

if __name__ == "__main__":
    main()

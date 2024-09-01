from playwright.sync_api import sync_playwright
import csv
import json

# Функция для получения общего количества объектов
def get_total_objects(page):
    # Формируем URL для запроса
    url = "https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/kn/object?offset=0&limit=20&sortField=obj_publ_dt&sortType=desc&place=0-44&objStatus=0"
    
    # Осуществляем переход на страницу с данным URL
    response = page.goto(url)
    
    # Получаем текстовый ответ страницы
    response_body = page.evaluate("document.body.innerText")
    
    try:
        # Пробуем преобразовать текстовый ответ в JSON
        data = json.loads(response_body)
        
        # Извлекаем общее количество объектов из данных
        total = data['data']['total']
        print(total)
        return total
    
    # Обработка ошибок, связанных с некорректным JSON
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    
    # Обработка любых других исключений
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    # Если произошла ошибка, возвращаем None
    return None

# Функция для получения списка идентификаторов объектов
def get_obj_ids(page, total):
    # Формируем URL с учетом общего количества объектов
    url = f"https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/kn/object?offset=0&limit={total-1}&sortField=obj_publ_dt&sortType=desc&place=0-44&objStatus=0"
    
    # Осуществляем переход на страницу с данным URL
    response = page.goto(url)
    
    # Получаем текстовый ответ страницы
    response_body = page.evaluate("document.body.innerText")
    
    try:
        # Пробуем преобразовать текстовый ответ в JSON
        data = json.loads(response_body)
        
        # Извлекаем список идентификаторов объектов
        obj_ids = [item['objId'] for item in data['data']['list']]
        return obj_ids
    
    # Обработка ошибок, связанных с некорректным JSON
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    
    # Обработка любых других исключений
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    # Если произошла ошибка, возвращаем пустой список
    return []

# Функция для получения детальной информации об объекте по его идентификатору
def get_object_details(page, obj_id):
    # Формируем URL для конкретного объекта по его идентификатору
    url = f"https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/object/{obj_id}"
    
    # Осуществляем переход на страницу с данным URL
    response = page.goto(url)
    
    # Получаем текстовый ответ страницы
    response_body = page.evaluate("document.body.innerText")
    
    try:
        # Пробуем преобразовать текстовый ответ в JSON
        data = json.loads(response_body)
        
        # Извлекаем данные об объекте
        obj = data['data']
        
        # Формируем словарь с нужными полями и возвращаем его
        return {
            "Название объекта": obj.get('nameObj', '-'),
            "Адрес": obj.get('address', '-'),
            "Идентификатор": obj.get('id', '-'),
            "Ввод в эксплуатацию": obj.get('objReady100PercDt', '-'),
            "Полное наименование застройщика": obj.get('developer', {}).get('devFullCleanNm', '-'),
            "Название группы застройщика": obj.get('developer', {}).get('developerGroupName', '-'),
            "Дата публикации": obj.get('objPublDt', '-'),
            "Выдача ключей": obj.get('objTransferPlanDt', '-'),
            "Средняя цена": obj.get('objPriceAvg', '-'),
            "Распроданность квартир %": obj.get('soldOutPerc', '-'),
            "Описание класса объекта": obj.get('objLkClassDesc', '-'),
            "Количество квартир": obj.get('objFlatCnt', '-'),
        }
    
    # Обработка ошибок, связанных с некорректным JSON
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    
    # Обработка любых других исключений
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    # Если произошла ошибка, возвращаем пустой словарь
    return {}

# Главная функция программы
def main():
    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Получаем общее количество объектов
        total = get_total_objects(page)
        if total is None:
            print("Не удалось получить общее количество объектов.")
            return
        
        # Получаем список идентификаторов объектов
        obj_ids = get_obj_ids(page, total)
        
        # Открываем файл для записи данных в формате CSV
        with open('objects_data.csv', 'w', newline='', encoding='utf-8') as file:
            # Создаем объект для записи данных в формате CSV
            writer = csv.DictWriter(file, fieldnames=[
                "Название объекта", "Адрес", "Идентификатор", "Ввод в эксплуатацию", 
                "Полное наименование застройщика", "Название группы застройщика", 
                "Дата публикации", "Выдача ключей", "Средняя цена", 
                "Распроданность квартир %", "Описание класса объекта", "Количество квартир"
            ])
            # Записываем заголовки в CSV
            writer.writeheader()
            
            # Проходимся по каждому идентификатору объекта и записываем его данные в CSV
            for obj_id in obj_ids:
                details = get_object_details(page, obj_id)
                if details:
                    writer.writerow(details)
                    print(f"Обработан объект с id {obj_id}")
        
        # Закрываем браузер
        browser.close()

# Запускаем главную функцию
if __name__ == "__main__":
    main()


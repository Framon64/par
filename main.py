from playwright.sync_api import sync_playwright
import csv
import json

def get_total_objects(page):
    url = "https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/kn/object?offset=0&limit=20&sortField=obj_publ_dt&sortType=desc&place=0-44&objStatus=0"
    response = page.goto(url)
    response_body = page.evaluate("document.body.innerText")
    try:
        data = json.loads(response_body)
        total = data['data']['total']
        print(total)
        return total
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    return None

def get_obj_ids(page, total):
    url = f"https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/kn/object?offset=0&limit={total-1}&sortField=obj_publ_dt&sortType=desc&place=0-44&objStatus=0"
    response = page.goto(url)
    response_body = page.evaluate("document.body.innerText")
    try:
        data = json.loads(response_body)
        obj_ids = [item['objId'] for item in data['data']['list']]
        return obj_ids
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    return []

def get_object_details(page, obj_id):
    url = f"https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/object/{obj_id}"
    response = page.goto(url)
    response_body = page.evaluate("document.body.innerText")
    try:
        data = json.loads(response_body)
        obj = data['data']
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
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера не является корректным JSON.")
        print("Ответ сервера:", response_body)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    return {}

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Открываем браузер в видимом режиме
        page = browser.new_page()
        
        total = get_total_objects(page)
        if total is None:
            print("Не удалось получить общее количество объектов.")
            return
        
        obj_ids = get_obj_ids(page, total)
        
        with open('objects_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                "Название объекта", "Адрес", "Идентификатор", "Ввод в эксплуатацию", 
                "Полное наименование застройщика", "Название группы застройщика", 
                "Дата публикации", "Выдача ключей", "Средняя цена", 
                "Распроданность квартир %", "Описание класса объекта", "Количество квартир"
            ])
            writer.writeheader()
            for obj_id in obj_ids:
                details = get_object_details(page, obj_id)
                if details:
                    writer.writerow(details)
                    print(f"Обработан объект с id {obj_id}")
        
        browser.close()

if __name__ == "__main__":
    main()

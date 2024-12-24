import time
import json
import requests
import tqdm
import bs4
import pandas as pd
from datetime import datetime

def get_vacancies(text="python",
                  experience="noExperience", employment=None, schedule=None):
    params = {
            "per_page": 100,
            "page": 0,
            "period": 30,
            "text": text,
            "experience": experience,
            "employment": employment,
            "schedule": schedule,
        }

    res = requests.get("https://api.hh.ru/vacancies", params=params)
    if not res.ok:
        print('Error:', res)
        return {}
    vacancies = res.json()["items"]
    pages = res.json()['pages']

    for page in tqdm.trange(1, pages):
        params['page'] = page
        res = requests.get("https://api.hh.ru/vacancies", params=params)
        if res.ok:
            response_json = res.json()
            vacancies.extend(response_json["items"])
        else:
            print(res)

    return vacancies


def get_full_descriptions(vacancies):
    vacancies_full = []
    for entry in tqdm.tqdm(vacancies):
        try:
            vacancy_id = entry['id']
            description = requests.get(f"https://api.hh.ru/vacancies/{vacancy_id}")
            description_dict = description.json() #словарь
            parsed_html = bs4.BeautifulSoup(str(description_dict['description']), 'html.parser')
            description_text = parsed_html.text
            description_dict['description'] = description_text  
            published_at_str = description_dict["published_at"]
            created_at_str = description_dict["created_at"]
            initial_created_at_str = description_dict["initial_created_at"]
            published_at_obj = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S%z")
            created_at_obj = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S%z")
            initial_created_at_obj = datetime.strptime(initial_created_at_str, "%Y-%m-%dT%H:%M:%S%z")
            vc_date1 = published_at_obj.strftime("%d-%m-%Y %H:%M:%S")
            vc_date2 = created_at_obj.strftime("%d-%m-%Y %H:%M:%S")
            vc_date3 = initial_created_at_obj.strftime("%d-%m-%Y %H:%M:%S")
            description_dict["published_at"] = vc_date1
            description_dict["created_at"] = vc_date2
            description_dict["initial_created_at"] = vc_date3

            time_str = description_dict['time']
            time_at_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S %p")
            vc_time = time_at_obj.strftime("%d-%m-%Y %H:%M:%S")
            
            vacancies_full.append(description_dict)
            #print(description_dict) #печать вакансий в консоль
            time.sleep(0.4)
        except KeyError:
            if 'description' not in description_dict:
                description_dict['description'] = 'Нет данных'
            if 'published_at' not in description_dict:
                description_dict['published_at'] = 'Нет данных'
            if 'created_at' not in description_dict:
                description_dict['created_at'] = 'Нет данных'
            if 'initial_created_at' not in description_dict:
                description_dict['initial_created_at'] = 'Нет данных'
            if 'time' not in description_dict:
                description_dict['time'] = 'Нет данных'
                return description_dict
            print('Ошибка KeyError')
            
    return vacancies_full

vacancies = get_vacancies(text="python",
                          experience="noExperience",
                          employment=None,
                          schedule=None)
print('Загружено', len(vacancies), 'вакансий')

vacancies_full = get_full_descriptions(vacancies)

pd.DataFrame(vacancies_full).to_excel('Вакансии.xlsx')

print('Файл загружен')
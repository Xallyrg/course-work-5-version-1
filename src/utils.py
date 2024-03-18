from typing import Any
import requests
import json
import psycopg2


def get_hh_data(list_of_companies: list[str]) -> list[dict[str, Any]]:
    '''
    Получает данные об интересующих компаниях с hh.ru с помощью requests и вакансии от них
    :param list_of_companies: список компаний
    :return: полученные данные в формате словаря с двумя свойствами --- именем компании и списком её вакансий
    '''
    # data это итоговый список
    data = []

    for company_name in list_of_companies:
        print(f'Получаю данные о {company_name}')
        # page это специальная переменная чтобы взять все результаты, data_for_company --- данные о конкретной компании
        page = 0
        data_for_company = []
        # получаю ответ, добавляю в дату и посылаю следующий запрос с увеличением номера страницы на 1, чтобы достать все данные
        while True:
            params = {
                "text": f"COMPANY_NAME:{company_name}",
                "page": f"{page}",
                "per_page": 100
            }
            response = requests.get(f"https://api.hh.ru/vacancies/", params=params)
            hh_data = json.loads(response.text)
            hh_vacancies = hh_data["items"]
            if len(hh_vacancies) > 0:
                data_for_company.extend(hh_vacancies)
                page +=1
                # print(f'Длина ответа 1 {len(hh_vacancies)}. Длина моих данных {len(data)}')
            else:
                break

        print(f'Получил данные о {company_name}, вакансий {len(data_for_company)}')
        data.append(
            {
                "employer": f"{company_name}",
                "vacancies": data_for_company,
                "number of vacancies": len(data_for_company)
            }
        )

    return data


def create_database(database_name: str, params: dict) -> None:
    """
    Создает базу данных и таблицы для созранения данных о компаниях и вакансий.
    :param db_names: Названия базы данных
    :param params: параметры для подключения
    :return:
    """
    return None


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """
    Записывает данные в базу данных
    :param data: какие данные надо записать
    :param database_name: название базы данных
    :param params: параметры для подключения
    :return:
    """
    return None


class DBManager():
    """
    Класс для получения и вывода данных из базы данных с вакансиями
    """
    def __init__(self, database_name: str):
        '''Создавая класс спрашиваем имя БД'''
        self.__database_name = database_name

    @property
    def database_name(self):
        '''Запрещаем менять имя БД'''
        return self.__database_name

    def __repr__(self):
        '''Магический метод репр'''
        return f'DBManager({self.__database_name})'

    def __str__(self):
        '''Магический метод стр'''
        return f'Класс для просмотра данных из базы данных {self.__database_name}'

    def get_companies_and_vacancies_count(self):
        '''
        :return: Возвращает список всех компаний и количество вакансий в каждой из них
        '''
        pass

    def get_all_vacancies(self):
        '''
        :return: Возвращает список всех вакансий, указывая
        компанию работодателя
        название вакансии
        зарплату
        ссылку на вакансию
        '''
        pass

    def get_avg_salary(self):
        '''
        :return: Возвращает среднюю зарплату по всем вакансиям
        '''
        pass

    def get_vacancies_with_higher_salary(self):
        '''
        :return: Возвращает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        '''
        pass

    def get_vacancies_with_keyword(self, keywords: list[str]):
        '''
        :return: Возвращает список всех вакансий, в названии которых содержатся переданные в метод слова, например python
        '''
        pass

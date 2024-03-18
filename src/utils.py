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

    # для каждой компании в списке
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
            # если от очередной страницы 0 ответов, то заканчиваю цикл, иначе сохраняю данные и page +=1
            if len(hh_vacancies) > 0:
                data_for_company.extend(hh_vacancies)
                page +=1
                # print(f'Длина ответа 1 {len(hh_vacancies)}. Длина моих данных {len(data)}')
            else:
                break

        # добавляю словарь компании и перехожу к следующей
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
    # подключаемся к постгресс чтобы создать нужную БД
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    with conn.cursor() as cur:
        # Удаляем на всякий случай БД и создаем её заново
        # (удаляем силовым методом, потому что pgAdmin так просто не закрывает соединение)
        try:
            cur.execute(f'DROP DATABASE {database_name} WITH (FORCE)')
        except:
            pass
        finally:
            cur.execute(f'CREATE DATABASE {database_name}')
    conn.close()

    # Теперь подключаемся к БД и создаем там две таблицы
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE employers (
                    employer_id serial PRIMARY KEY,
                    employer_name VARCHAR NOT NULL,
                    number_of_vacancies integer NOT NULL
                );
            """)

    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE public.vacancies(
                    vacancy_id SERIAL PRIMARY KEY,
                    employer_id integer NOT NULL,
                    vacancy_name VARCHAR NOT NULL,
                    salary_from integer,
                    salary_to integer,
                    salary_to_print VARCHAR NOT NULL,
                    url VARCHAR NOT NULL,
                    CONSTRAINT fk_vacancies_employers FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
                );
            """)

    conn.commit()
    conn.close()

    return None


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """
    Записывает данные в базу данных
    :param data: какие данные надо записать
    :param database_name: название базы данных
    :param params: параметры для подключения
    :return:
    """
    # подключаемся к БД
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        # Для каждой компании
        for company in data:
            # вытаскиваем данные
            employer_name = company['employer']
            employer_number_of_vacancies = company['number of vacancies']
            # записываем данные о работодателе в таблицу employers
            cur.execute(
                """
                INSERT INTO employers (employer_name, number_of_vacancies)
                VALUES (%s, %s)
                RETURNING employer_id
                """,
                (employer_name, employer_number_of_vacancies)
            )

            # Получаем номер, под которым записали работодателя и список его вакансий
            employer_id = cur.fetchone()[0]
            employer_vacancies = company['vacancies']
            # для каждой вакансии работодателя
            for vacancy in employer_vacancies:
                # получаем данные --- название, зарплату, ссылку
                vacansy_name = vacancy['name']

                try:
                    salary_from = int(vacancy["salary"]["from"])
                except TypeError:
                    salary_from = None
                try:
                    salary_to = int(vacancy["salary"]["to"])
                except TypeError:
                    salary_to = None
                if salary_from != None:
                    if salary_to != None:
                        salary_to_print = f'Зарплата от {salary_from} до {salary_to}'
                    else:
                        salary_to_print = f'Зарплата от {salary_from}'
                else:
                    if salary_to != None:
                        salary_to_print = f'Зарплата до {salary_to}'
                    else:
                        salary_to_print = f'Зарплата не указана'

                url = vacancy['alternate_url']

                # вставляем данные в БД
                cur.execute(
                    """
                    INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, salary_to_print, url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (employer_id, vacansy_name, salary_from, salary_to, salary_to_print, url)
                )

    conn.commit()
    conn.close()

    return None


class DBManager():
    """
    Класс для получения и вывода данных из базы данных с вакансиями
    """
    def __init__(self, database_name: str, params: dict):
        '''Создавая класс спрашиваем имя БД'''
        self.__database_name = database_name
        self.__params = params

    @property
    def database_name(self):
        '''Запрещаем менять имя БД'''
        return self.__database_name

    @property
    def params(self):
        '''Запрещаем менять параметры подключения'''
        return self.__params

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
        conn = psycopg2.connect(dbname = self.__database_name, **self.__params)
        list_of_companies = []

        with conn.cursor() as cur:
            # Достаем нужные данные из таблицы employers
                cur.execute(
                    """
                    SELECT * FROM employers
                    """
                )

                # Сохраняем данные в нормальном формате
                data = cur.fetchall()
                for row in data:
                    # print(f'Название компании: {row[1]}, количество вакансий {row[2]}')
                    list_of_companies.append({
                        'Название компании': row[1],
                        'Количество вакансий': row[2]
                    })

        conn.close()
        return list_of_companies

    def get_all_vacancies(self):
        '''
        :return: Возвращает список всех вакансий, указывая
        компанию работодателя
        название вакансии
        зарплату
        ссылку на вакансию
        '''
        list_of_vacancies = []
        conn = psycopg2.connect(dbname=self.__database_name, **self.__params)

        with conn.cursor() as cur:
            # Достаем нужные данные из таблицы employers
            cur.execute(
                """
                SELECT * FROM vacancies
                JOIN employers USING (employer_id) 
                """
            )

            # Выводим данные в нормальном формате
            data = cur.fetchall()
            for row in data:
                # print(f'Вакансия: {row[2]}, от компании компании {row[7]}.\n'
                #       f'{row[5]}.\n'
                #       f'Ссылка на вакансию {row[6]}')
                list_of_vacancies.append({
                    'Вакансия': row[2],
                    'Компания': row[7],
                    'Зарплата от': row[3],
                    'Зарплата до': row[4],
                    'Зарплата для печати': row[5],
                    'Ссылка на вакансию': row[6]
                })

        conn.close()
        return list_of_vacancies

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





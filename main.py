from src.utils import get_hh_data, create_database, save_data_to_database, DBManager
from config import config


def main(lost_of_companies: list[str], db_name) -> None:
    """
    Программа скачает вам вакансии компаний из списка,
    пересоздаст базу данных db_name
    и запишет найденные данные в нее
    :param lost_of_companies: список компаний
    :param db_name: имя будущей базы данных
    :return: None
    """

    params = config()

    data = get_hh_data(lost_of_companies)
    create_database(db_name, params)
    save_data_to_database(data, db_name, params)


if __name__ == '__main__':
    """
    Если вы запускаете программу не в первый раз, то закоментируйте строку 37. 
    Отобрать нужные вакансии, можно со строки 41

    Можете поправить данные перед запуском. 
    interesting_companies --- список компаний которые вам интересны.
    database_name --- имя базы данных, которая будет пересоздана и куда запишутся данные.
    
    В процессе скачивания данных программа будет выводить информацию о своем прогрессе
    """
    interesting_companies = ['Printum', 'HARTUNG', 'Сбер Лигал', 'Яндекс.Такси', 'Яндекс Практикум', 'Яндекс.Еда', 'Компания Самолет', 'SberTech', 'Ostrovok.ru', 'HeadHunter', ]
    database_name = 'hh_vacansies'

    # скачивание данных
    # main(interesting_companies, database_name)

    params = config()
    # Ниже примеры, как можно из сформированной базы данных
    DB = DBManager(database_name, params)

    # print(DB)

    # DB.get_companies_and_vacancies_count()
    # print(DB.get_companies_and_vacancies_count())
    # DB.get_all_vacancies()
    # print(len(DB.get_all_vacancies()))

    DB.get_avg_salary()
    print(DB.get_avg_salary())

    # for dict in DB.get_all_vacancies():
    #     print(dict)
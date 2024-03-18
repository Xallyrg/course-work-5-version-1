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
    Отобрать нужные вакансии, можно со строки 40

    Можете поправить данные перед запуском. 
    interesting_companies --- список компаний которые вам интересны.
    database_name --- имя базы данных, которая будет пересоздана и куда запишутся данные.
    
    В процессе скачивания данных программа будет выводить информацию о своем прогрессе
    """
    interesting_companies = ['Printum', 'HARTUNG', 'Сбер Лигал', 'Яндекс.Такси', 'Яндекс Практикум', 'Яндекс.Еда', 'Компания Самолет', 'SberTech', 'Ostrovok.ru', 'HeadHunter', ]
    database_name = 'hh_vacansies'

    # скачивание данных
    main(interesting_companies, database_name)

    # Ниже примеры, как можно из сформированной базы данных получить какие-то конкретные значения
    DB = DBManager(database_name, config())
    print('')

    # Получить списком словарей названия компаний и количество вакансий в них
    DB.get_companies_and_vacancies_count()
    print(f'Всего компаний: {len(DB.get_companies_and_vacancies_count())}')

    # Получить списком словарей все вакансии
    DB.get_all_vacancies()
    print(f'Всего вакансий: {len(DB.get_all_vacancies())}')

    # Получить среднюю минимальную зарплату по вакансиям в которых она указана
    DB.get_avg_salary()
    print(f'Средняя зарплата по вакансиям: {int(DB.get_avg_salary())}')

    # Получить списком словарей все вакансии у которых минимальная ЗП больше средней
    DB.get_vacancies_with_higher_salary()
    print(f'Вакансий с высокой зарплатой: {len(DB.get_vacancies_with_higher_salary())}')

    # Получить списком словарей все вакансии в названии которых встречаются слова
    keywords = ['водитель', 'инженер']
    DB.get_vacancies_with_keyword(keywords)
    print(f'Вакансий в названии которых встречаются слова "{'", "'.join(keywords)}": {len(DB.get_vacancies_with_keyword(keywords))}')
    # print(DB.get_vacancies_with_keyword(['водитель', 'инженер']))
    # print(len(DB.get_vacancies_with_keyword(['водитель', 'инженер'])))

    # for dict in DB.get_vacancies_with_keyword(['водитель', 'инженер']):
    #     print(dict)

    # keywords = ['водитель', 'инженер']
    # request = ('SELECT * FROM vacancies\n'
    #            'JOIN employers USING (employer_id)\n'
    #            'WHERE ')
    # for word in keywords:
    #     request += f"LOWER(vacancy_name) LIKE '%{word}%' OR\n"
    # request += f'1=0'
    #
    # print(request)
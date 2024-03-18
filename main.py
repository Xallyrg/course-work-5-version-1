from src.utils import get_hh_data, create_database, save_data_to_database, DBManager
from config import config


def main():
    interesting_companies = ['Printum', 'Сбер Лигал', 'Яндекс.Такси', 'Яндекс Практикум', 'Яндекс.Еда',
                             'Компания Самолет', 'HARTUNG', 'HeadHunter', 'SberTech', 'Ostrovok.ru', ]

    params = config()

    data = get_hh_data(interesting_companies)
    print(len(data))
    print(data)
    create_database('hh_vacansies', params)
    save_data_to_database(data, 'hh_vacansies', params)


if __name__ == '__main__':
    main()
    # print('asd')

    # DB = DBManager('hh_vacansies')

    # print(DB)

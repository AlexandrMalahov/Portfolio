"""Python 3.7 Training task. Parsing of PizzaRicca"""
import re
import requests
import time

from lxml import html


def time_count(func):
    """Calculating functions lead time."""
    def wrapper(*arg):
        start_time = time.time()
        func(*arg)
        stop_time = time.time()
        print('Function {0} run time: {1:.2f} sec.'
              .format(func.__name__, stop_time - start_time))
    return wrapper


def get_parse_data():
    """Installing connect with site and geting data."""
    response = requests.get('https://pizzaricca.ru/', verify=False).content
    tree = html.fromstring(response)
    data = tree.xpath(
        '/html/body/div[@id="content"]'
        '/article/ul[@id="pizzalist"]/li'
    )
    return data


def get_pizza_names(data):
    """Searching names of pizzas."""
    names_list = [info.xpath('h2//text()')[0] for info in data]
    return names_list


def get_parts(data):
    """Searching parts of pizzas."""
    pizza_parts = [[', '.join(
        re.findall(
            r'[А-Яа-я]+\s[А-Яа-я]+|[А-Яа-я]+',
            info.xpath('div[@class="parts"]')[0].text
        )
    )] for info in data]
    return pizza_parts


def get_label(data):
    """Searching size and weight of pizzas."""
    pizza_label = [
        re.findall(
            r'\d+\s[А-Я-а-я]+.',
            ' '.join(info.xpath(
                'div[@class="labels"]'
                '/label/div//text()')
            )
        )
        for info in data
    ]
    return pizza_label


def get_price(data):
    """Searching price of pizzas."""
    price_1 = [info.xpath('div[@class="labels"]/label/input')[0].get('price') for info in data]
    price_2 = [info.xpath('div[@class="labels"]/label/input')[1].get('price') for info in data]
    return price_1, price_2


@time_count
def print_data(data):
    """Printing treated data."""
    names = get_pizza_names(data)
    pizza_parts = get_parts(data)
    labels_weight = get_label(data)
    pizza_price = get_price(data)
    for i in range(len(names)):
        print('Пицца:', names[i], '\n')
        print('Состав: ', pizza_parts[i][0])
        print(
            'Размер пиццы: {0}, цена: '
            '{1} рублей, вес: {2}'.format(
                labels_weight[i][0], pizza_price[0][i], labels_weight[i][1]
            )
        )
        print(
            'Размер пиццы: {0}, цена: '
            '{1} рублей, вес: {2}'.format(
                labels_weight[i][2], pizza_price[1][i], labels_weight[i][3]
            )
        )
        print('\n')


@time_count
def users_request(data):
    """Printing information about chosen pizza."""
    names = get_pizza_names(data)
    pizza_parts = get_parts(data)
    labels_weight = get_label(data)
    pizza_price = get_price(data)
    while True:
        pizza_name = input('Введите название пиццы: ')
        if pizza_name in names:
            index = names.index(pizza_name)
            print('Пицца:', pizza_name)
            print('Состав:', pizza_parts[index][0])
            print(
                'Размер: {0}, цена: {1} рублей, '
                'вес: {2}'.format(
                    labels_weight[index][0],
                    pizza_price[0][index],
                    labels_weight[index][1]
                )
            )
            print(
                'Размер: {0}, цена: {1} рублей, '
                'вес: {2}'.format(
                    labels_weight[index][2],
                    pizza_price[1][index],
                    labels_weight[index][3]
                )
            )
            break
        else:
            print('Нет такой пиццы.')
            time.sleep(2)
            print('Выберите из списка: ')
            time.sleep(2)
            for name in names:
                print(name)
                time.sleep(1)


if __name__ == '__main__':
    DATA = get_parse_data()
    while True:
        CHOICE = input(
            'Выберите тип просмотра'
            '(чтобы посмотреть весь список, '
            'введите "все"; чтобы узнать '
            'инфорамацию о конкретной пицце, '
            'введите "пицца"; Для выхода введите "выход"): '
        )
        if CHOICE == 'все':
            print_data(DATA)
        elif CHOICE == 'пицца':
            users_request(DATA)
        elif CHOICE == 'выход':
            print('\n')
            print('До свидания. Заходите ещё!')
            break
        else:
            print('\n')
            print('Неверная команда. Выберите тип просмотра.')

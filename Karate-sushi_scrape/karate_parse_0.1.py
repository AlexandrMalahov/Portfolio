"""Python 3.7. Scrape Karate-Sushi."""
import collections
import re
import requests
import sys
from lxml import html


class KarateSushiScrape:
    def __init__(self, url):
        self.url = url

    def get_menu_categories(self):
        """Get available menu categories."""
        response = requests.get(self.url).content
        tree = html.fromstring(response)
        data = tree.xpath(
            '/html/body/div[@class="main wrapper"]'
            '/div[@class="container-fluid"]'
            '/div[@class="row category-list"]/div')
        return data

    def get_categories_links(self):
        """Get categories links."""
        categories_deq = collections.deque()
        categories = self.get_menu_categories()
        for category in categories:
            categories_deq.append(
                {'name': category.xpath('a/h3')[0].text,
                 'link': category.xpath('a')[0].get('href')}
            )
        return categories_deq

    def show_categories(self):
        """Show categories names."""
        for category in self.get_categories_links():
            print(category['name'])

    def choose_category(self):
        """Select a category by user request."""
        category = str(input(
            'Введите название категории, чтобы выбрать блюдо меню.\n'
            'Нажмите "Enter" для просмотра категорий.\n'
            'Введите "выход", чтобы выйти из программы.\n'
        )).lower()  # User request.
        names_and_links = self.get_categories_links()
        category_names = collections.deque(
            [name['name'] for name in names_and_links])
        if category == '':  # If user request is empty (User pressed "Enter").
            self.show_categories()  # Show available categories.
            self.choose_category()
        elif category.capitalize() in category_names:
            link = [
                name['link'] for name in names_and_links
                if category == name['name'].lower()
            ][0]  # get category link.
            print(link)  # print category link.
            menu = self.get_menu(self._get_category(link), category)  # Get dishes data.
            self.print_menu(menu, category)  # Output for user.
        elif category == 'выход':
            sys.exit('До свидания! Заходите ещё!')
        else:
            print('Нет такой категориию Попробуйте ещё раз.')
            self.choose_category()

    @staticmethod
    def _get_category(url):
        """Get category by request. Method is static and protected."""
        response = requests.get(url).content
        tree = html.fromstring(response)
        data = tree.xpath(
            '/html/body/div[@class="main wrapper"]'
            '/div[@class="container-fluid"]/div[@class="category-items"]/div')
        return data

    def get_menu(self, category_data, category):
        """Get menu data."""
        menu_data = collections.deque()
        for menu in category_data:
            menu_data.append(
                {'name': menu.xpath('div')[0].get('data-ss-cart-name'),
                 'composition': self.get_menu_info(menu, category),
                 'price': menu.xpath('div')[0].get('data-ss-cart-price'),
                 'weight': menu.xpath('div')[0].get('data-ss-cart-size'),
                 'link': menu.xpath('div')[0].get('data-ss-cart-url')}
            )
        return menu_data

    @staticmethod
    def get_menu_info(menu, category):
        """Get info about dishes."""
        if category == 'сеты':  # Category "Сеты" have different structure then another categories.
            dishes_data = menu.xpath('div/div/div[1]/p')
            dishes = collections.deque()
            for dish in dishes_data:
                dishes.append(
                    {'name': dish.xpath('b')[0].text,
                     'composition': dish.xpath('span')[0].text}
                )
        elif category == 'лапша и плов':
            # Category "лапша и плов" have dish constructor. It needs own method. It will be add in further.
            dishes = collections.deque()
        else:
            dishes_data = menu.xpath('div/div/div')[0].text
            dishes = re.findall('\t{7}(.+)\n', dishes_data)[0]
        return dishes

    @staticmethod
    def print_menu(menu, category):
        """Print information about menu."""
        print(menu)
        for dish in menu:
            print('Название: {}'.format(dish['name']))
            print('Вес: {}'.format(dish['weight']))
            if category == 'сеты':
                print('Состав сета:')
                for composition in dish['composition']:
                    print('\n\tНазвание блюда: {}'.format(composition['name']))
                    print('\tСостав блюда: {}\n'.format(composition['composition']))
            elif category == 'лапша и плов':
                pass
            else:
                print('Состав блюда: {}'.format(dish['composition']))
            print('Цена: {} рублей'.format(dish['price']))
            print('Ссылка на блюдо: {}\n'.format(dish['link']))


if __name__ == '__main__':
    KarateSushiScrape('https://sushi-karate.ru/menu').choose_category()

import os
import requests

from lxml import html


class ImageLinksGetter:
    def __init__(self, url):
        self.url = url

    def get_page(self):
        tree = html.fromstring(requests.get(self.url).content)
        return tree

    def get_links(self):
        tree = self.get_page()
        xpath_links = tree.xpath('/html/body/div[@class="container-fluid thb-large-box"]'
                           '/div[@class="item-list item-list-page"]/div/div/a/img')
        links = [{link.get('title'): link.get('data-src')} for link in xpath_links]
        return links


class ImageSaver:
    def __init__(self, url):
        self.url = url

    def save_image(self):
        links = ImageLinksGetter(self.url).get_links()
        for link in links:
            name = '{title}.jpg'.format(
                    title=list(link.keys())[0].split('/')[-1].split(':')[-1].split('?')[-1])
            if name not in os.listdir('static/images'):
                with open('static/images/{name}'.format(name=name), 'wb') as img:
                    img.write(requests.get(list(link.values())[0]).content)
                    print('Picture "{name}" has been saved.'.format(name=name))
            else:
                print('Picture "{name}" is already exist.'.format(name=name))
                continue

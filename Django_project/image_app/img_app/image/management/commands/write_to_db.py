import os

from django.core.files import File
from django.core.management import BaseCommand
from image.models import Images
from .image_extracter import ImageLinksGetter, ImageSaver


class Command(BaseCommand):
    url = 'https://www.dreamstime.com/free-images_pg1'

    @staticmethod
    def __save_to_db(link):
        name = list(link.keys())[0].split('/')[-1].split(':')[-1].split('?')[-1]
        record = Images(name=name, date_of_create=os.path.getctime('static/images/{name}.jpg'.format(name=name)),
                        image=File(open('static/images/{name}.jpg'.format(name=name), 'rb')))
        record.save()

    def handle(self, *args, **options):
        ImageSaver(self.url).save_image()
        for link in ImageLinksGetter(self.url).get_links():
            self.__save_to_db(link)

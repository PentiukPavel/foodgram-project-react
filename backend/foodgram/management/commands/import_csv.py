import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from foodgram.models import Ingredients


class Command(BaseCommand):
    help = 'Импорт ингредиентов из файл csv.'

    def handle(self, *args, **kwargs):
        with open(
            os.path.join(
                settings.BASE_DIR,
                '..',
                'data',
                'ingredients.csv'
            ),
            encoding='utf-8'
        ) as data:
            for line in csv.reader(data):
                Ingredients.objects.create(
                    name=line[0],
                    measurement_unit=line[1]
                )

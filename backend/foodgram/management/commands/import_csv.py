import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из csv файла.'

    def handle(self, *args, **kwargs):
        if Ingredient.objects.all().exists():
            pass
        else:
            with open(
                os.path.join(
                    settings.BASE_DIR,
                    '..',
                    'data',
                    'ingredients.csv'
                ),
                encoding='utf-8'
            ) as data:
                Ingredient.objects.bulk_create(
                    [Ingredient(
                        name=line[0],
                        measurement_unit=line[1]
                    ) for line in csv.reader(data)]
                )

import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует данные ингредиентов из JSON-файла'

    def handle(self, *args, **options):
        try:
            # Путь к файлу с ингредиентами
            data_path = os.path.join(settings.BASE_DIR, '..', 'data', 'ingredients.json')
            
            if not os.path.exists(data_path):
                raise CommandError(f'Файл {data_path} не найден')
            
            with open(data_path, encoding='utf-8') as f:
                ingredients_data = json.load(f)
            
            # Счетчики для статистики
            created_count = 0
            existing_count = 0
            
            for ingredient in ingredients_data:
                name = ingredient.get('name')
                measurement_unit = ingredient.get('measurement_unit')
                
                if not name or not measurement_unit:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Пропускаем запись: неверный формат данных - {ingredient}'
                        )
                    )
                    continue
                
                obj, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
                
                if created:
                    created_count += 1
                else:
                    existing_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Импорт завершен: {created_count} ингредиентов добавлено, '
                    f'{existing_count} уже существовало'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Ошибка при импорте ингредиентов: {e}')
 
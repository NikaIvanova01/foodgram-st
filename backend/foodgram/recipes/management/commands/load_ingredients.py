import json

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            with transaction.atomic():
                ingredients_to_create = [
                    Ingredient(
                        name=item["name"].lower(),
                        measurement_unit=item["measurement_unit"].lower(),
                    )
                    for item in data
                ]

                # Используем bulk_create для эффективной вставки
                Ingredient.objects.bulk_create(
                    ingredients_to_create,
                    ignore_conflicts=True,
                )

            total_ingredients = len(ingredients_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully loaded {total_ingredients} ingredients"
                )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(f"File {file_path} is not valid JSON")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error loading ingredients: {str(e)}")
            )

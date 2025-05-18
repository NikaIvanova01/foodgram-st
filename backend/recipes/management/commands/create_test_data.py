from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Команда для создания тестовых данных."""
    
    help = 'Создает тестовые данные для проекта'
    
    def handle(self, *args, **options):
        self.stdout.write('Начало создания тестовых данных')
        
        # Создаем теги
        self._create_tags()
        
        # Создаем пользователей
        self._create_test_users()
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы')
        )
    
    def _create_tags(self):
        """Создает базовые теги для рецептов."""
        tags_data = [
            {
                'name': 'Завтрак',
                'color': '#E26C2D',
                'slug': 'breakfast'
            },
            {
                'name': 'Обед',
                'color': '#49B64F',
                'slug': 'lunch'
            },
            {
                'name': 'Ужин',
                'color': '#8775D2',
                'slug': 'dinner'
            },
            {
                'name': 'Десерт',
                'color': '#FF69B4',
                'slug': 'dessert'
            },
            {
                'name': 'Напиток',
                'color': '#32CD32',
                'slug': 'drink'
            },
        ]
        
        created_count = 0
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            f'Создано {created_count} тегов из {len(tags_data)}'
        )
    
    def _create_test_users(self):
        """Создает тестовых пользователей."""
        users_data = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'password': 'password1'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'first_name': 'Петр',
                'last_name': 'Петров',
                'password': 'password2'
            },
            {
                'username': 'user3',
                'email': 'user3@example.com',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'password': 'password3'
            },
        ]
        
        created_count = 0
        for user_data in users_data:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                created_count += 1
        
        self.stdout.write(
            f'Создано {created_count} пользователей из {len(users_data)}'
        ) 
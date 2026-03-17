import json
import os
from django.core.management.base import BaseCommand
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Загружает тестовые данные из фикстур, предварительно очищая базу'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаем загрузку тестовых данных...'))

        # Очищаем существующие данные
        self.stdout.write('Очищаем базу данных...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('База данных очищена'))

        # Путь к файлам фикстур
        fixtures_dir = 'catalog/fixtures'

        # Загружаем категории
        categories_file = os.path.join(fixtures_dir, 'categories.json')
        if os.path.exists(categories_file):
            self.stdout.write('Загружаем категории...')
            with open(categories_file, 'r', encoding='utf-8') as f:  # Явно указываем utf-8
                categories_data = json.load(f)
                for item in categories_data:
                    fields = item['fields']
                    Category.objects.create(
                        id=item['pk'],
                        name=fields['name'],
                        description=fields.get('description', '')
                    )
            self.stdout.write(self.style.SUCCESS(f'Загружено {len(categories_data)} категорий'))
        else:
            self.stdout.write(self.style.WARNING('Файл categories.json не найден, создаем категории вручную'))
            # Создаем категории вручную
            categories = [
                {'name': 'Электроника', 'description': 'Товары для дома и офиса'},
                {'name': 'Одежда', 'description': 'Мужская и женская одежда'},
                {'name': 'Книги', 'description': 'Художественная и учебная литература'},
            ]
            for cat_data in categories:
                Category.objects.create(**cat_data)
            self.stdout.write(self.style.SUCCESS(f'Создано {len(categories)} категорий'))

        # Загружаем продукты
        products_file = os.path.join(fixtures_dir, 'products.json')
        if os.path.exists(products_file):
            self.stdout.write('Загружаем продукты...')
            with open(products_file, 'r', encoding='utf-8') as f:  # Явно указываем utf-8
                products_data = json.load(f)
                for item in products_data:
                    fields = item['fields']
                    category = Category.objects.get(id=fields['category'])
                    Product.objects.create(
                        name=fields['name'],
                        description=fields.get('description', ''),
                        price=fields['price'],
                        category=category,
                        # image поле пропускаем
                    )
            self.stdout.write(self.style.SUCCESS(f'Загружено {len(products_data)} продуктов'))
        else:
            self.stdout.write(self.style.WARNING('Файл products.json не найден, создаем продукты вручную'))
            # Получаем категории
            electronics = Category.objects.get(name='Электроника')
            clothing = Category.objects.get(name='Одежда')
            books = Category.objects.get(name='Книги')

            # Создаем продукты
            products = [
                {'name': 'Смартфон XYZ', 'description': 'Новейший смартфон с отличной камерой', 'price': 27999.99,
                 'category': electronics},
                {'name': 'Ноутбук Pro', 'description': 'Мощный ноутбук для работы и игр', 'price': 59999.99,
                 'category': electronics},
                {'name': 'Футболка', 'description': 'Хлопковая футболка', 'price': 999.99, 'category': clothing},
                {'name': 'Джинсы', 'description': 'Классические джинсы', 'price': 2499.99, 'category': clothing},
                {'name': 'Python для начинающих', 'description': 'Книга по программированию на Python',
                 'price': 1299.99, 'category': books},
            ]
            for prod_data in products:
                Product.objects.create(**prod_data)
            self.stdout.write(self.style.SUCCESS(f'Создано {len(products)} продуктов'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены!'))

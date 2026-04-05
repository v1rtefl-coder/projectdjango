from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создает группы модераторов и настраивает права доступа'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем создание групп...')

        # Создаем группу "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" создана'))
        else:
            self.stdout.write('Группа "Модератор продуктов" уже существует')

        # Получаем ContentType для модели Product
        product_content_type = ContentType.objects.get_for_model(Product)

        # Получаем или создаем разрешение на отмену публикации
        unpublish_permission, _ = Permission.objects.get_or_create(
            codename='can_unpublish_product',
            name='Может отменять публикацию продукта',
            content_type=product_content_type
        )

        # Получаем разрешение на удаление
        delete_permission = Permission.objects.get(
            codename='delete_product',
            content_type=product_content_type
        )

        # Назначаем разрешения группе
        moderator_group.permissions.set([unpublish_permission, delete_permission])

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы и настроены!'))

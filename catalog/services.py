from django.core.cache import cache
from django.conf import settings
from .models import Product, Category


def get_products_by_category(category_id, use_cache=True):
    """
    Сервисная функция для получения списка продуктов в указанной категории.

    Args:
        category_id: ID категории
        use_cache: Использовать ли кеширование

    Returns:
        QuerySet продуктов в категории
    """
    cache_key = f'products_by_category_{category_id}'

    if use_cache and settings.CACHE_ENABLED:
        # Пытаемся получить из кеша
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            return cached_products

    # Получаем продукты из базы данных
    products = Product.objects.filter(
        category_id=category_id,
        is_published=True
    ).select_related('category', 'owner')

    # Кешируем результат
    if use_cache and settings.CACHE_ENABLED:
        cache.set(cache_key, products, 60 * 10)  # 10 минут

    return products


def get_all_categories():
    """Сервисная функция для получения всех категорий"""
    cache_key = 'all_categories'

    if settings.CACHE_ENABLED:
        cached_categories = cache.get(cache_key)
        if cached_categories is not None:
            return cached_categories

    categories = Category.objects.all()

    if settings.CACHE_ENABLED:
        cache.set(cache_key, categories, 60 * 60)  # 1 час

    return categories


def invalidate_product_cache(product_id=None, category_id=None):
    """
    Инвалидация кеша при изменении данных

    Args:
        product_id: ID продукта (опционально)
        category_id: ID категории (опционально)
    """
    if product_id:
        cache.delete(f'product_detail_{product_id}')

    if category_id:
        cache.delete(f'products_by_category_{category_id}')

    # Очищаем кеш списка всех категорий
    cache.delete('all_categories')

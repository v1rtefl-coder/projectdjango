from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.conf import settings
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """Контроллер для главной страницы с низкоуровневым кешированием"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        """Получаем продукты с низкоуровневым кешированием"""
        from .services import get_all_categories

        # Ключ для кеша
        cache_key = 'home_products_page_{}'.format(self.request.GET.get('page', 1))

        # Пытаемся получить из кеша
        cached_products = cache.get(cache_key)

        if cached_products is not None and settings.CACHE_ENABLED:
            return cached_products

        # Получаем из БД
        products = Product.objects.filter(is_published=True).select_related('category', 'owner')

        # Сохраняем в кеш
        if settings.CACHE_ENABLED:
            cache.set(cache_key, products, 60 * 5)  # 5 минут

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .services import get_all_categories
        context['categories'] = get_all_categories()
        return context


class ProductDetailView(DetailView):
    """Контроллер для страницы одного товара с кешированием"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Показываем опубликованные продукты или разрешаем доступ владельцу/модератору"""
        user = self.request.user
        if user.is_authenticated and user.has_perm('catalog.can_unpublish_product'):
            return Product.objects.all()
        return Product.objects.filter(is_published=True)

    @method_decorator(cache_page(60 * 15))  # Кешируем на 15 минут
    @method_decorator(vary_on_headers('Cookie'))  # Учитываем cookies
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """Получаем объект с проверкой кеша"""
        pk = self.kwargs.get('pk')
        cache_key = f'product_detail_{pk}'

        # Пытаемся получить из кеша
        cached_product = cache.get(cache_key)

        if cached_product is not None and not self.request.user.is_authenticated:
            # Для неавторизованных пользователей возвращаем из кеша
            return cached_product

        # Получаем объект из БД
        product = super().get_object(queryset)

        # Кешируем для неавторизованных пользователей
        if not self.request.user.is_authenticated:
            cache.set(cache_key, product, 60 * 15)  # 15 минут

        return product


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания продукта (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_published = False
        response = super().form_valid(form)

        # Инвалидируем кеш категорий и главной страницы
        from .services import invalidate_product_cache
        invalidate_product_cache(category_id=form.instance.category_id)
        cache.delete_pattern('home_products_page_*')

        messages.success(self.request, 'Продукт успешно создан!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Контроллер для редактирования продукта (только для владельца)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, является ли пользователь владельцем продукта"""
        product = self.get_object()
        return self.request.user == product.owner

    def handle_no_permission(self):
        """Если пользователь не владелец, возвращаем ошибку 403"""
        if self.request.user.is_authenticated:
            messages.error(self.request, 'У вас нет прав для редактирования этого продукта.')
            raise PermissionDenied('Вы не можете редактировать чужой продукт.')
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        old_category_id = self.get_object().category_id
        response = super().form_valid(form)

        # Инвалидируем кеш
        from .services import invalidate_product_cache
        invalidate_product_cache(product_id=self.object.pk, category_id=old_category_id)
        invalidate_product_cache(category_id=self.object.category_id)
        cache.delete_pattern('home_products_page_*')

        messages.success(self.request, 'Продукт успешно обновлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Контроллер для удаления продукта (владелец или модератор)"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, может ли пользователь удалить продукт"""
        product = self.get_object()
        user = self.request.user

        # Владелец может удалить
        if user == product.owner:
            return True

        # Модератор может удалить любой продукт
        if user.has_perm('catalog.delete_product'):
            return True

        return False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'У вас нет прав для удаления этого продукта.')
            raise PermissionDenied('Вы не можете удалить этот продукт.')
        return super().handle_no_permission()

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        category_id = product.category_id

        from .services import invalidate_product_cache
        invalidate_product_cache(product_id=product.pk, category_id=category_id)
        cache.delete_pattern('home_products_page_*')

        messages.success(self.request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


class ProductModerationView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Контроллер для модерации продукта (отмена публикации)"""
    model = Product
    fields = ['is_published']
    template_name = 'catalog/product_moderate.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def test_func(self):
        """Проверяем, есть ли у пользователя право на отмену публикации"""
        return self.request.user.has_perm('catalog.can_unpublish_product')

    def form_valid(self, form):
        action = "снята с публикации" if not form.instance.is_published else "опубликован"
        messages.success(self.request, f'Продукт успешно {action}!')
        return super().form_valid(form)


class ContactsView(TemplateView):
    """Контроллер для страницы контактов (общедоступный)"""
    template_name = 'catalog/contacts.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print(f'Получено сообщение от {name}: {message}, тел: {phone}')
        return HttpResponse('Спасибо за ваше сообщение!')


class CategoryProductsView(ListView):
    """Контроллер для отображения продуктов в указанной категории"""
    model = Product
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Получаем продукты в категории через сервисную функцию"""
        from .services import get_products_by_category
        category_id = self.kwargs.get('category_id')
        return get_products_by_category(category_id, use_cache=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .services import get_all_categories
        category_id = self.kwargs.get('category_id')
        context['current_category'] = get_object_or_404(Category, id=category_id)
        context['categories'] = get_all_categories()
        return context

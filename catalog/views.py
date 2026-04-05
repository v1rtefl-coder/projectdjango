from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from .models import Product, Category
from .forms import ProductForm


class HomeView(ListView):
    """Контроллер для главной страницы (общедоступный)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        """Показываем только опубликованные продукты"""
        return Product.objects.filter(is_published=True)


class ProductDetailView(DetailView):
    """Контроллер для страницы одного товара (общедоступный)"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Показываем опубликованные продукты или разрешаем доступ владельцу/модератору"""
        user = self.request.user
        if user.is_authenticated and (user.has_perm('catalog.can_unpublish_product') or user == product.owner):
            return Product.objects.all()
        return Product.objects.filter(is_published=True)


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания продукта (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')
    login_url = '/users/login/'

    def form_valid(self, form):
        """Автоматически привязываем продукт к текущему пользователю"""
        form.instance.owner = self.request.user
        form.instance.is_published = False  # Новые продукты не публикуются автоматически
        messages.success(self.request, 'Продукт успешно создан! Он будет опубликован после проверки модератором.')
        return super().form_valid(form)

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
        messages.success(self.request, 'Продукт успешно обновлен!')
        return super().form_valid(form)

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


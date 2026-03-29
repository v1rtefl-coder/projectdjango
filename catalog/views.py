from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Category


class HomeView(ListView):
    """Контроллер для главной страницы"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        """Получаем все продукты"""
        return Product.objects.all()


class ProductDetailView(DetailView):
    """Контроллер для страницы одного товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ContactsView(TemplateView):
    """Контроллер для страницы контактов"""
    template_name = 'catalog/contacts.html'

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса из формы"""
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print(f'Получено сообщение от {name}: {message}, тел: {phone}')
        return HttpResponse('Спасибо за ваше сообщение!')

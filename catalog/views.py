from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Category


def home(request):
    """Контроллер для домашней страницы"""
    products = Product.objects.all()  # Получаем все продукты
    return render(request, 'catalog/home.html', {'products': products})


def contacts(request):
    """Контроллер для страницы контактов"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print(f'Получено сообщение от {name}: {message}, тел: {phone}')
        return HttpResponse('Спасибо за ваше сообщение!')

    return render(request, 'catalog/contacts.html')


def product_detail(request, pk):
    """Контроллер для страницы одного товара"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'product': product})

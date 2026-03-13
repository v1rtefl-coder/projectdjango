from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Контроллер для домашней страницы"""
    return render(request, 'catalog/home.html')


def contacts(request):
    """Контроллер для страницы контактов с обработкой формы"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Здесь можно добавить логику отправки email или сохранения в БД
        print(f'Получено сообщение от {name}: {message}, тел: {phone}')

        # Можно вернуть сообщение об успехе
        return HttpResponse('Спасибо за ваше сообщение!')

    return render(request, 'catalog/contacts.html')

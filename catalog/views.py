from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm


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


class ProductCreateView(CreateView):
    """Контроллер для создания продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        """Дополнительная логика при успешном создании"""
        messages.success(self.request, 'Продукт успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Логика при ошибках валидации"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(UpdateView):
    """Контроллер для редактирования продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        """После успешного редактирования возвращаемся на страницу товара"""
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(DeleteView):
    """Контроллер для удаления продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


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

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from .models import User


class UserRegistrationView(CreateView):
    """Контроллер для регистрации пользователя"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Дополнительная логика при успешной регистрации"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Регистрация прошла успешно! На вашу почту отправлено приветственное письмо. '
            'Теперь вы можете войти в систему.'
        )
        return response

    def form_invalid(self, form):
        """Логика при ошибках валидации"""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class UserLoginView(LoginView):
    """Контроллер для авторизации пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        """URL для перенаправления после успешного входа"""
        return reverse_lazy('catalog:home')

    def form_valid(self, form):
        """Дополнительная логика при успешной авторизации"""
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)


def user_logout(request):
    """Контроллер для выхода пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('catalog:home')

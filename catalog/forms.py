from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продукта"""

    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'is_published']
        labels = {
            'name': 'Наименование',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена (₽)',
            'is_published': 'Опубликован',
        }

    def clean_name(self):
        """Валидация названия на запрещенные слова"""
        name = self.cleaned_data.get('name')
        if name:
            name_lower = name.lower()
            for forbidden_word in self.FORBIDDEN_WORDS:
                if forbidden_word in name_lower:
                    raise forms.ValidationError(
                        f'Название содержит запрещенное слово: "{forbidden_word}"'
                    )
        return name

    def clean_description(self):
        """Валидация описания на запрещенные слова"""
        description = self.cleaned_data.get('description')
        if description:
            description_lower = description.lower()
            for forbidden_word in self.FORBIDDEN_WORDS:
                if forbidden_word in description_lower:
                    raise forms.ValidationError(
                        f'Описание содержит запрещенное слово: "{forbidden_word}"'
                    )
        return description

    def clean_price(self):
        """Валидация цены (не может быть отрицательной)"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        return price

    def __init__(self, *args, **kwargs):
        """Стилизация формы"""
        super().__init__(*args, **kwargs)

        # Добавляем классы Bootstrap для всех полей
        for field_name, field in self.fields.items():
            if field_name == 'category':
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'is_published':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            # Добавляем placeholder
            if field_name == 'name':
                field.widget.attrs.update({'placeholder': 'Введите название продукта'})
            elif field_name == 'description':
                field.widget.attrs.update({'placeholder': 'Введите описание продукта'})
            elif field_name == 'price':
                field.widget.attrs.update({'placeholder': 'Введите цену в рублях'})

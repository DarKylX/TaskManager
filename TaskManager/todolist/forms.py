from django import forms
from .models import UserProfile, UserBIO


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }

    # Добавим метод для инициализации формы с существующими данными
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email


class UserBIOForm(forms.ModelForm):
    class Meta:
        model = UserBIO
        fields = ['company', 'role', 'age', 'avatar']
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название компании'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Возраст',
                'min': '18',
                'max': '100'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'company': 'Компания',
            'role': 'Роль',
            'age': 'Возраст',
            'avatar': 'Фото профиля'
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 18 or age > 100):
            raise forms.ValidationError("Возраст должен быть от 18 до 100 лет")
        return age

    def save(self, commit=True, *args, **kwargs):
        self.full_clean()
        if commit:
            super().save(*args, **kwargs)
        return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказки для полей
        self.fields['company'].help_text = 'Укажите название вашей компании'
        self.fields['role'].help_text = 'Выберите вашу роль в компании'
        self.fields['avatar'].help_text = 'Загрузите фото профиля (макс. размер 5MB)'

        # Делаем поля необязательными, если нужно
        self.fields['avatar'].required = False

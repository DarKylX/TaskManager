from django import forms
from django.contrib.auth import get_user_model

from .models import UserProfile, UserBIO, Subtask


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Фамилия"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance

        if email and email != user.email:  # Если email изменился
            if get_user_model().objects.exclude(id=user.id).filter(email=email).exists():
                raise forms.ValidationError('Пользователь с таким email уже существует')

        return email

    # Добавим метод для инициализации формы с существующими данными
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["first_name"].initial = self.instance.first_name
            self.fields["last_name"].initial = self.instance.last_name
            self.fields["email"].initial = self.instance.email


class UserBIOForm(forms.ModelForm):
    class Meta:
        model = UserBIO
        fields = ["company", "role", "age", "avatar", "bio_description"]
        widgets = {
            "company": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название компании"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
            "age": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Возраст",
                    "min": "18",
                    "max": "100",
                }
            ),
            "avatar": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "bio_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Расскажите о себе",
                }
            ),
        }
        labels = {
            "company": "Компания",
            "role": "Роль",
            "age": "Возраст",
            "avatar": "Фото профиля",
            "bio_description": "Доп. информация",
        }

    def clean_age(self):
        age = self.cleaned_data.get("age")
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
        self.fields["company"].help_text = "Укажите название вашей компании"
        self.fields["role"].help_text = "Выберите вашу роль в компании"
        self.fields["avatar"].help_text = "Загрузите фото профиля (макс. размер 5MB)"

        # Делаем поля необязательными, если нужно
        self.fields["avatar"].required = False


class SubtaskForm(forms.ModelForm):
    class Meta:
        model = Subtask
        fields = ["name", "description", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название подзадачи",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Описание подзадачи",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "name": "Название подзадачи",
            "description": "Описание",
            "status": "Статус",
        }
        help_texts = {
            "name": "Введите краткое название подзадачи",
            "description": "Подробно опишите, что нужно сделать",
            "status": "Выберите текущий статус подзадачи",
        }
        error_messages = {
            "name": {
                "required": "Это поле обязательно для заполнения",
                "max_length": "Название слишком длинное",
            }
        }

    def __init__(self, *args, **kwargs):
        self.parent_task = kwargs.pop("parent_task", None)  # Извлекаем task из kwargs
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_task:
            instance.task = self.parent_task
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if self.parent_task and self.parent_task.subtasks.count() >= 5:
            raise forms.ValidationError(
                "Невозможно добавить подзадачу. Достигнут максимум (5 подзадач)."
            )
        return cleaned_data

    class Media:
        css = {"all": ("css/subtask_form.css",)}

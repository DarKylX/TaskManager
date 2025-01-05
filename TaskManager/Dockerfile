# Используем базовый образ Python
FROM python:3.11

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Устанавливаем команду запуска Gunicorn
CMD ["gunicorn", "--chdir", "TaskManager", "--bind", "0.0.0.0:8000", "TaskManager.wsgi:application"]

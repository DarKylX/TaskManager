FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /code/

# Collect static files
RUN python TaskManager/manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--chdir", "TaskManager", "--bind", "0.0.0.0:8000", "TaskManager.wsgi:application"]

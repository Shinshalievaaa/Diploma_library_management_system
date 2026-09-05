FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Установка системных зависимостей и Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

# Копируем конфигурацию зависимостей
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем зависимости без создания виртуального окружения внутри контейнера
RUN poetry install --no-interaction --no-root --no-ansi

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
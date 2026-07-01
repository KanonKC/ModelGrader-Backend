# Stage 1: Build dependencies
FROM python:3.11.3-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.11.3-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=Backend.settings

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8000

CMD ["gunicorn", "Backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

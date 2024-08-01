FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY app .

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
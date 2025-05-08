FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry

COPY . /app/

RUN poetry install

RUN mkdir -p /app/staticfiles

RUN poetry run python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.10-bullseye

WORKDIR /code

COPY pyproject.toml /code/pyproject.toml

RUN pip install -e .

COPY ./ /code/

CMD ["alembic", "upgrade", "head", ";", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
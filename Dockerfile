FROM dockerhub.timeweb.cloud/python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /app

WORKDIR /app


RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev

ADD pyproject.toml /app



RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

EXPOSE 587
EXPOSE 80
COPY . /app/

FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app
COPY poetry.lock pyproject.toml ./
COPY manage.py ./
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install "poetry>=1.3.0,<1.4.0" && poetry config virtualenvs.create false

COPY . /app

RUN poetry install 
RUN poetry run python manage.py collectstatic


EXPOSE 8000

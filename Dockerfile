FROM python
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app
COPY poetry.lock pyproject.toml ./
COPY manage.py ./
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install poetry && poetry config virtualenvs.create false

COPY . /app

RUN poetry install 
RUN poetry run python manage.py collectstatic


EXPOSE 8000

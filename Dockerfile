FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY poetry.lock pyproject.toml ./
COPY manage.py ./
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install poetry==1.3.2 && poetry config virtualenvs.create false

COPY . /app

RUN poetry install 

#cmd setting
EXPOSE 8000

CMD [ "gunicorn", "fsd_medic.asgi:application", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker" ]

# CMD [ "poetry", "run", "python", "manage.py", "runserver" ]

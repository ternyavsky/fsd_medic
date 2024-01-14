FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
COPY manage.py ./
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install -r requirements.txt

COPY . /app


#cmd setting
EXPOSE 8000

#CMD [ "gunicorn", "fsd_medic.asgi:application", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker" ]

CMD [ "python", "manage.py", "runserver" "0.0.0.0:8000" ]

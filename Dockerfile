FROM python
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt

COPY . /app
EXPOSE 8000
CMD ["python", "manage.py", "migrate"]
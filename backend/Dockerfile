FROM python:3.7-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY backend/ .

CMD python manage.py makemigrations 

CMD python manage.py migrate

CMD python manage.py import_csv

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 

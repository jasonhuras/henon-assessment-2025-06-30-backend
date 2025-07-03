FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 8000
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver
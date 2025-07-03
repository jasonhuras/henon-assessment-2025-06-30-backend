FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD python manage.py makemigrations && python manage.py cmigrate && python manage.py runserver
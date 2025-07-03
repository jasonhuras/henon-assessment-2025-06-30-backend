FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 8000
CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 henon_dashboard.wsgi:application
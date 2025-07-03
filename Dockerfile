FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "henon_dashboard.wsgi:application"]
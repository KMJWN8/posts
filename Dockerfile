FROM python:3.12-slim

WORKDIR /app

ENV HTTP_PROXY=http://10.0.219.4:1118
ENV HTTPS_PROXY=http://10.0.219.4:1118

EXPOSE 8000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python3 manage.py migrate && gunicorn --bind 0.0.0.0:8000 blog.wsgi:application"]

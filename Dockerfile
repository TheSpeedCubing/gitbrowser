FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 5011

CMD ["gunicorn", "-c", "gunicorn_config.py", "-w", "4", "-b", "0.0.0.0:5011", "app:app"]

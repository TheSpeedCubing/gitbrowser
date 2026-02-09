FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 5011

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5011", "app:app"]

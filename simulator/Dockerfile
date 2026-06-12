FROM python:3.13-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY simulate.py .

USER appuser
CMD ["python", "simulate.py"]

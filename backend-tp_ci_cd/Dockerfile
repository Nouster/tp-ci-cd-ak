FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend-tp_ci_cd/ .

EXPOSE 5000

CMD ["python", "app.py"]

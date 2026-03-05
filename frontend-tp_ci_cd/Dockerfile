FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend-tp_ci_cd/ .

EXPOSE 5001

CMD ["python", "app.py"]

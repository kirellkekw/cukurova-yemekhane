FROM python:3.9

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2000"]
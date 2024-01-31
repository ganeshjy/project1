FROM python:3.8.10-slim

WORKDIR /app

# COPY requirements.txt .

COPY . .

RUN pip install python-dotenv confluent_kafka

CMD [ "python", "producer.py" ]

EXPOSE 8000


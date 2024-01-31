FROM python:3.8.10-slim

WORKDIR /app

COPY . .

RUN pip install confluent_kafka pymongo python-dotenv 


CMD ["python", "consumer.py"]

EXPOSE 8000

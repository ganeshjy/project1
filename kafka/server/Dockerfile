FROM python:3.8.10-slim

WORKDIR /app

# COPY requirements.txt .

COPY . .

RUN pip install python-dotenv 

CMD [ "python", "server.py" ]

EXPOSE 8000


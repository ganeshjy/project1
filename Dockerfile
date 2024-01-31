FROM python:3.8.10-slim 

WORKDIR /app


COPY . /app

RUN pip install -r requirements.txt

CMD [ "uvicorn", "main:app", "--reload", "--host=0.0.0.0" ]

EXPOSE 8000
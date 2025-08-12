FROM python:3.13-alpine

COPY requirements.txt requirements.txt 

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "uvicorn", "app.main:app", "--host", "0.0.0.0" ]
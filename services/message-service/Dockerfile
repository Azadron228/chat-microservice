FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libstdc++ \
    lz4-dev \
    make

COPY requirements.txt requirements.txt 

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "-m", "app.main"]

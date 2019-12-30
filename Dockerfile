FROM python:3.7-alpine

COPY src/requirements.txt /

RUN apk update && apk upgrade
RUN apk add --no-cache python3-dev gcc libc-dev linux-headers

RUN pip install -r requirements.txt

COPY src/ /app
WORKDIR /app

CMD ["python", "main.py"]
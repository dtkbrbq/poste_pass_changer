FROM python:alpine

COPY ["app.py", "requirements.txt", "./app/"]
WORKDIR /app

RUN pip install --upgrade pip
RUN apk update && apk add --no-cache py3-pip curl
RUN pip install -r requirements.txt

CMD [ "python3", "./app.py" ]


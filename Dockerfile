FROM python:3.7-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY src/requirements.txt /requirements.txt

RUN apk add --no-cache zlib-dev jpeg-dev openssl-dev libffi-dev musl-dev make gcc
RUN pip install --prefix=/install --no-warn-script-location errbot==6.1.4 slackclient -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY src /app/plugins/tradingpost-errbot

WORKDIR /app

RUN ["errbot", "-c /etc/tradingpost-errbot/config.py", "-i"]
CMD ["errbot", "-c /etc/tradingpost-errbot/config.py"]

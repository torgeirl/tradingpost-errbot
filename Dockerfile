FROM python:3.7-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apk add --no-cache zlib-dev jpeg-dev openssl-dev libffi-dev musl-dev make gcc
RUN pip install --prefix=/install --no-warn-script-location -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY config.py /app/config.py
COPY src /app/plugins/tradingpost-errbot

WORKDIR /app

RUN ["errbot", "-i"]
CMD ["errbot"]

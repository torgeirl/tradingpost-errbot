FROM python:3.7-slim as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends libjpeg62-turbo-dev zlib1g-dev
RUN pip install --prefix=/install --no-warn-script-location -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY config.py /app/config.py
COPY src /app/plugins/tradingpost-errbot

WORKDIR /app

RUN ["errbot", "-i"]
CMD ["errbot"]

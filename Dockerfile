FROM python:3.11-slim as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends libjpeg62-turbo-dev zlib1g-dev git && \
    pip install --prefix=/install --no-warn-script-location -r /requirements.txt

FROM base

RUN apt-get update && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

COPY --from=builder /install /usr/local
COPY errbot-config.py /app/errbot-config.py
COPY plugins/tradingpost-errbot /app/plugins/tradingpost-errbot
COPY plugins/random-errbot /app/plugins/random-errbot

WORKDIR /app

RUN ["errbot", "--init"]
RUN rm -rf plugins/err-example
CMD ["errbot", "--config", "errbot-config.py"]

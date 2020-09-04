FROM python:3.7-slim as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends libjpeg62-turbo-dev zlib1g-dev git
RUN pip install --prefix=/install --no-warn-script-location errbot[slack]==6.1.4
RUN pip install --prefix=/install --no-warn-script-location -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY errbot-config.py /app/errbot-config.py
COPY src /app/plugins/tradingpost-errbot

WORKDIR /app

RUN ["errbot", "--init"]
CMD ["errbot", "--config", "errbot-config.py"]

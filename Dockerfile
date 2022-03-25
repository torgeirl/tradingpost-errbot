FROM python:3.10-slim as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends libjpeg62-turbo-dev zlib1g-dev git
RUN pip install --prefix=/install --no-warn-script-location -r /requirements.txt

RUN mkdir /backends
WORKDIR /backends
RUN git clone https://github.com/errbotio/err-backend-slackv3
RUN pip install --prefix=/install --no-warn-script-location -r err-backend-slackv3/requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY errbot-config.py /app/errbot-config.py
COPY --from=builder /backends/err-backend-slackv3 /app/backends/err-backend-slackv3
COPY plugins/tradingpost-errbot /app/plugins/tradingpost-errbot
COPY plugins/random-errbot /app/plugins/random-errbot

WORKDIR /app

RUN ["errbot", "--init"]
RUN rm -rf plugins/err-example
CMD ["errbot", "--config", "errbot-config.py"]

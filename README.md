tradingpost-errbot
=============

![Docker](https://github.com/torgeirl/tradingpost-errbot/workflows/Docker/badge.svg)

## Overview
A simple Magic: the Gathering bot, implemented as an Errbot plugin.

## Deployment 
Create a config file for your installation:
  - `$ cp config.py-example config.py`
  - `$ vim config.py # update BOT_IDENTITY and BOT_ADMINS`

Store `config.py` as a secret in k8s before creating the k8s deployment:
  - `$ kubectl create secret generic tradingpost-config --from-file=./config.py`
  - `$ kubectl create -f deploy/tradingpost-errbot.yaml`

## Credits
  - tradingpost-errbot is a port of [tradingpost-beepboop](https://github.com/torgeirl/tradingpost-beepboop), a [BeepBoop](https://beepboophq.com/docs/article/overview)-hostable Slack bot. I got the inspiration to make tradingpost-beepboop after seeing Filip Söderholm's [cardfetcher bot](https://github.com/fiso/cardfetcher) in action, and I have re-used part of his code while making Tradingpost.

  - The Sutcliffe canvas itself is [Athena's creation](https://twitter.com/_Elantris_/status/1103775781543530496) while [Anthony Martin inspired the bot command](https://twitter.com/Martony101/status/1103858795371851777).

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).

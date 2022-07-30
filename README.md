tradingpost-errbot
=============

![Errbot plugin](https://github.com/torgeirl/tradingpost-errbot/actions/workflows/python-tests.yml/badge.svg)
![Docker](https://github.com/torgeirl/tradingpost-errbot/workflows/Docker/badge.svg)

## Overview
A simple Magic: the Gathering bot for Slack, implemented as an Errbot plugin and deployed with Kubernetes.

## Deployment (kubectl)
[Edit an existing or create a new Slack app](http://api.slack.com/apps), and make the following adjustment to enable the app to run Trading Post:
  - create a new App-Level Token with the `connections:write` scope
  - set the app name to `tradingpost`
  - enable Socket Mode
  - allow users to send Slash commands and messages from the messages tab
  - subscribe to the following bot events: `file_create`, `file_public`, `message.channels`, `message.groups` and `message.im`
  - add the follwing OAuth scopes: `channels:history`, `channels:read`, `chat:write`, 'files:read`, `files:write`, `groups:history`, `groups:read`, `im:history`, `im:read`, `mpim:read`, `team:read`, and `users:read` 

Save your bot's Slack token, signing secret, app token and the username(s) of the bot's admin(s) as secrets:
  - `$ kubectl create secret generic tradingpost-configi --from-literal='errbot-token=xoxb-4426949411-aEM7...' --from-literal='errbot-signing-secret="<hexadecimal value>" --from-literal='errbot-app-token=xapp-A111-222-xyz...' --from-literal='errbot-admins=["Uxxxxxxxx", "Uxxxxxxxx"]'`

Deploy the bot:
  - `$ kubectl create -f deploy/tradingpost-errbot.yaml`

You can see the bot's pod by listing pods:
  - `$ kubectl get pods`

The Errbot logs are available from Kubernetes:
  - `$ kubectl logs tradingpost-deployment-<pod-identifier>`

Recreate the deployment to update the bot to the latest version:
  - `$ kubectl delete -f deploy/tradingpost-errbot.yaml`
  - `$ kubectl create -f deploy/tradingpost-errbot.yaml`

## Emojis ##
Add [Scryfall's Manamoji emojis](https://github.com/scryfall/manamoji-slack/) as custom emojis in your Slack workspace for the MtG symbols to render correctly.

## History and credits
  - Tradingpost was first created in 2016 as [tradingpost-beepboop](https://github.com/torgeirl/tradingpost-beepboop), a [Beep Boop](https://github.com/BeepBoopHQ/starter-python-bot)-hostable Slack bot. The inspiration to make it came from seeing Filip Söderholm's [cardfetcher bot](https://github.com/fiso/cardfetcher) in action, and part of his code was re-used while making Tradingpost.

  - Tradingpost was ported from BeepBoop to [Errbot](https://github.com/errbotio/errbot) in November 2017. [Scryfall](https://scryfall.com/docs/api) was adapted as the backend around the same time.

  - [The Sutcliffe canvas](src/assets/sutcliffe-canvas.png) is [Athena's creation](https://twitter.com/_Elantris_/status/1103775781543530496) while [Anthony Martin inspired the bot command](https://twitter.com/Martony101/status/1103858795371851777).

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).

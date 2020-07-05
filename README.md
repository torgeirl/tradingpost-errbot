tradingpost-errbot
=============

![Docker](https://github.com/torgeirl/tradingpost-errbot/workflows/Docker/badge.svg)

## Overview
A simple Magic: the Gathering bot, implemented as an Errbot plugin.

## Deployment 
### Plugin for existing Errbot
If you already have a Errbot installation running you can install tradingpost-errbot as a plugin with the command `!repos install https://github.com/torgeirl/tradingpost-errbot`. See [Errbot's documentation](http://errbot.io/en/latest/user_guide/administration.html) for further instructions.

### Slack installation
tradingpost-errbot is included as a submodule in self-assembler-bot, an Errbot-based Slack bot design for self-hosting of a Slack bot with tradingpost-errbot. See [self-assembler-bot](https://github.com/torgeirl/self-assembler-bot) for futher instructions.

## Credits
  - tradingpost-errbot is a port of [tradingpost-beepboop](https://github.com/torgeirl/tradingpost-beepboop), a [BeepBoop](https://beepboophq.com/docs/article/overview)-hostable Slack bot. I got the inspiration to make tradingpost-beepboop after seeing Filip Söderholm's [cardfetcher bot](https://github.com/fiso/cardfetcher) in action, and I have re-used part of his code while making Tradingpost.

  - The Sutcliffe canvas itself is [Athena's creation](https://twitter.com/_Elantris_/status/1103775781543530496) while [Anthony Martin inspired the bot command](https://twitter.com/Martony101/status/1103858795371851777).

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).

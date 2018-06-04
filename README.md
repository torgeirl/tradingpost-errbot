tradingpost-errbot
=============

## Overview
A simple Magic: the Gathering bot, implemented as an Errbot plugin.

## Deployment 
### Plugin for existing Errbot
If you already have a Errbot installation running you can install tradingpost-errbot as a plugin with the command `!repos install https://github.com/torgeirl/tradingpost-errbot`. See [Errbot's documentation](http://errbot.io/en/latest/user_guide/administration.html) for further instructions.

### Slack installation
tradingpost-errbot is included as a submodule in self-assembler-bot, an Errbot-based Slack bot design for self-hosting of a Slack bot with tradingpost-errbot. See [self-assembler-bot](https://github.com/torgeirl/self-assembler-bot) for futher instructions.

### Rocket.Chat installation (experimental!)
`$ git clone https://github.com/cardoso/errbot-rocketchat.git`

`$ cd errbot-rocketchat`

`$ virtualenv venv`

`$ venv/bin/python setup.py install`

`$ cd src/aoikrocketchaterrbot`

`$ vim config.py` (edit `BOT_ADMINS`, `SERVER_URI`, `LOGIN_USERNAME` and `LOGIN_PASSWORD`)

Create a systemd file similar to [self-assembler-bot](https://github.com/torgeirl/self-assembler-bot#configure-deamon) with these changes:

`ExecStart=/home/username/errbot-rocketchat/venv/bin/python -m errbot.cli`

`WorkingDirectory=/home/username/errbot-rocketchat/src/aoikrocketchaterrbot`.

## Credits
tradingpost-errbot is a port of [tradingpost-beepboop](https://github.com/torgeirl/tradingpost-beepboop), a [BeepBoop](https://beepboophq.com/docs/article/overview)-hostable Slack bot. I got the inspiration to make tradingpost-beepboop after seeing Filip Söderholm's [cardfetcher bot](https://github.com/fiso/cardfetcher) in action, and I have re-used part of his code while making Tradingpost.

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).

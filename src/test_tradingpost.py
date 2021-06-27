import tradingpost
from errbot.backends.test import testbot
from errbot import plugin_manager


class TestTradingpost(object):
    extra_plugin_dir = '.'

    def test_flavor(self, testbot):
        testbot.push_message('!flavor lava axe (ulg)')
        result = testbot.pop_message()
        assert(result == '"Catch!"')

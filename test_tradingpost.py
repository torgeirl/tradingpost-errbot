from errbot.backends.test import testbot
import tradingpost

class TestTradingpost(object):
    extra_plugin_dir = '.'

    def test_roll(self, testbot):
        testbot.push_message('!roll six')
        assert 'Please supply a valid number of sides.' in testbot.pop_message()
    
    #TODO do more tests

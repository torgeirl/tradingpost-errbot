from errbot import BotPlugin, botcmd, re_botcmd
import json
import logging
from os import getcwd
from os.path import dirname, join, realpath
import random
import requests
from time import sleep

__location__ = realpath(join(getcwd(), dirname(__file__)))
logger = logging.getLogger(__name__) #TODO: still valid for errbot?

class Tradingpost(BotPlugin):
    '''Event handler: looks for bot mentions and bot commands.'''
    
    def callback_mention(self, message, mentioned_people):
        #TODO: add greeting
        if self.bot_identifier in mentioned_people:
            return '{}: use a command if you want my help.'.format(message.frm)
    
    @botcmd
    def card(self, msg, args):
        card = get_card(args)
        if card:
            most_recent_printing = card['editions'][0]
            self.send_card(title=card['name'].replace('\'', '\\\''),
                body='{} ({})'.format(most_recent_printing['set'], most_recent_printing['set_id']),
                image=most_recent_printing['image_url'],
                in_reply_to=msg)
        else:
            return 'Card not found.'
    
    @botcmd
    def joke(self, msg, args):
        '''Warning: the jokes are really, really bad.'''
        with open(join(__location__, 'jokes.json'), 'r') as infile:
            joke = random.choice(json.load(infile))
        yield joke['setup']
        sleep(1) #TODO is there a 'send_user_typing_pause()' equivalent for errbot?
        yield joke['punchline']
    
    @botcmd
    def oracle(self, msg, args):
        return write_oracle(args)
    
    @botcmd
    def price(self, msg, args):
        return write_price(args)
    
    @botcmd
    def pwp(self, msg, args):
        return write_pwp(args)
    
    @botcmd
    def roll(self, msg, args):
        '''Rolls a die with N sides; defaults to D6.'''
        sides = 6 if args == '' else args
        if sides.isdigit():
            yield 'Rolled a {}-sided die, and the result is...'.format(sides)
            sleep(1) #TODO is there a 'send_user_typing_pause()' equivalent for errbot?
            yield '... {}! :game_die:'.format(random.randint(1, int(sides)))
        else:
            yield 'Please supply a valid number of sides.'


def emoji_filter(input):
    #TODO another py3 issue?
    ret = input.replace('{', ':_')
    ret = ret.replace('}', '_:')
    lastpos = None
    while ret.rfind('_:', 0, lastpos) != -1:
        end = ret.rfind('_:', 0, lastpos)
        lastpos = ret.rfind(':_', 0, lastpos)
        start = lastpos + 2
        content = ret[start:end]
        content = content.lower()
        content = content.replace('/', '')
        ret = ret[:start] + content + ret[end:]
    return ret


def find_index_of_sequence(data, sequence, start_index=0):
    #TODO: error with !price ("a bytes-like object is required, not 'str'")
    index = start_index
    for token in sequence:
        index = data.find(token, index)
        if index == -1:
            return -1
    return index + len(sequence[-1])


def get_card(name):
    query_url = 'http://api.deckbrew.com/mtg/cards?name=%s' % name
    r = requests.get(query_url)
    try:
        cards = r.json()
    except ValueError:
        logging.error(u'No JSON object could be decoded from API response: %s' % r)
        return None
    
    if len(cards) < 1:
        return None
    
    card = None
    for element in cards:
        if element['name'].lower() == name.lower():
            card = element
    return card


def get_card_value(card_name, set_code):
    url = 'http://www.mtggoldfish.com/widgets/autocard/%s [%s]' % (card_name, set_code)
    headers = {
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,de;q=0.6,sv;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Referer': 'http://www.mtggoldfish.com/widgets/autocard/%s' % card_name,
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    }
    response = requests.get(url, headers=headers)
    index = find_index_of_sequence(response.content, ['tcgplayer', 'btn-shop-price', '$'])
    end_index = response.content.find('\\n', index)
    try:
        value = float(response.content[index + 2:end_index].replace(',', ''))
    except ValueError:
        value = 0
    return value


def get_seasons(dci_number):
    '''Returns to current and last season for that DCI number'''
    url = 'http://www.wizards.com/Magic/PlaneswalkerPoints/JavaScript/GetPointsHistoryModal'
    headers = {
        'Pragma': 'no-cache',
        'Origin': 'http://www.wizards.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,de;q=0.6,sv;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*', 
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'f5_cspm=1234; BIGipServerWWWPWPPOOL01=353569034.20480.0000; __utmt=1; BIGipServerWWWPool1=3792701706.20480.0000; PlaneswalkerPointsSettings=0=0&lastviewed=9212399887; __utma=75931667.1475261136.1456488297.1456488297.1456488297.1; __utmb=75931667.5.10.1456488297; __utmc=75931667; __utmz=75931667.1456488297.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'Connection': 'keep-alive',
        'Referer': 'http://www.wizards.com/Magic/PlaneswalkerPoints/%s' % dci_number
    }
    data = {'Parameters': {'DCINumber': dci_number, 'SelectedType': 'Yearly'}}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code is 200:
        seasons = []
        try:
            response_data = response.json()
            markup = response_data['ModalContent']
            search_position = markup.find('SeasonRange')

            while search_position != -1:
                pointsvalue = 'PointsValue\">'
                search_position = markup.find(pointsvalue, search_position)
                search_position += len(pointsvalue)
                end_position = markup.find('</div>', search_position)
                if end_position != -1:
                    value = markup[search_position:end_position]
                    seasons.append(int(value))
                search_position = markup.find('SeasonRange', search_position)
        except ValueError:
            logging.error(u'No JSON object could be decoded from API response: %s' % response)
            return 'Garbled response from backend. Please try again later.'

        try:
            return {'currentSeason': seasons[0], 'lastSeason': seasons[1]}
        except IndexError:
            return 'DCI# %s not found.' % dci_number
    else:
        logging.error(u'No response from API (HTTP code %i)' % response.status_code)
        return 'No response from backend. Please try again later.'


def write_oracle(search_term):
    card = get_card(search_term)
    
    if card:
        typeline = ''
        if 'supertypes' in card:
            for supertype in card['supertypes']:
                typeline += supertype.capitalize() + ' '
        if 'types' in card:
            for cardtype in card['types']:
                typeline += cardtype.capitalize() + ' '
        if 'subtypes' in card:
            typeline += '- '
        if 'subtypes' in card:
            for subtype in card['subtypes']:
                typeline += subtype.capitalize() + ' '
        txt = u'*%s %s*\n%s\n%s' % (card['name'], card['cost'], typeline, card['text'])
        if 'power' in card and 'toughness' in card:
            txt += u'\n*`%s/%s`*' % (card['power'], card['toughness'])
        if 'loyalty' in card:
            txt += u'\n*`%s`*' % card['loyalty']
        txt = emoji_filter(txt)
    else:
        txt = 'Card not found.'
    return txt


def write_price(search_term):
    card = get_card(search_term)
    
    if card:
        most_recent_printing = card['editions'][0]
        card['value'] = get_card_value(card['name'], most_recent_printing['set_id'])
        txt = 'Unable to find price information for %s' % card['name']
        if card['value'] > 0:
            txt = 'Current market price for most recent printing of {} ({}) - ${.1f}'.format(
                card['name'], most_recent_printing['set'], card['value'])
    else:
        txt = 'Card not found.'
    return txt


def write_pwp(dci_number):
    if dci_number.isdigit():
        response = get_seasons(dci_number)
        
        if isinstance(response, dict):
            txt = ('DCI# %s has %s points in the current season, and %s points last season.\nCurrently ' % (dci_number, response['currentSeason'], response['lastSeason']))
        
            if response['currentSeason'] >= 2250 or response['lastSeason'] >= 2250:
                txt += 'eligible for 2 GP byes.'
            elif response['currentSeason'] >= 1300 or response['lastSeason'] >= 1300:
                txt += 'eligible for 1 GP bye.'
            else:
                txt += 'not eligible for GP byes.'
        else:
            txt = response
    else:
        txt = '\'%s\' doesn\'t look like a DCI number. Try again, but with an actual number.' % dci_number
    return txt

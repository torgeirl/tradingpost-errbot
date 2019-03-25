from errbot import BotPlugin, botcmd
from json import dumps as json_dumps, load as json_load
import logging
from os import getcwd
from os.path import dirname, join, realpath
from random import choice as random_choice, randint as random_randint
from re import search as re_search, match as re_match
from requests import get as requests_get, post as requests_post
from tempfile import TemporaryFile
from time import sleep
from io import BytesIO

from PIL import Image

__location__ = realpath(join(getcwd(), dirname(__file__)))
logger = logging.getLogger(__name__)


class Tradingpost(BotPlugin):
    '''Plugin that fetches MtG card pictures, oracle texts, prices and player's planeswalker points on request.'''

    @botcmd
    def card(self, msg, args):
        '''I\'ll post a picture of the named card. :frame_with_picture:'''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            return e.msg

        body = '{} ({})'.format(card['set_name'], card['set'].upper())
        if card['layout'] == 'transform':
            for face in card['card_faces']:
                self.send_card(title=face['name'],
                               body=body,
                               image=face['image_uris']['normal'],
                               in_reply_to=msg)
        else:
            self.send_card(title=card['name'],
                           body=body,
                           image=card['image_uris']['normal'],
                           in_reply_to=msg)

    @botcmd
    def coinflip(self, msg, args):
        '''Need to toss a coin in these cash-free times? Look no further.'''
        return random_choice(['HEADS!', 'TAILS!'])

    @botcmd
    def joke(self, msg, args):
        '''Tells you a random joke. Warning: the jokes are really, really bad. :laughing:'''
        with open(join(__location__, 'assets/jokes.json'), 'r') as infile:
            joke = random_choice(json_load(infile))
        yield joke['setup']
        sleep(1)  # TODO is there a 'send_user_typing_pause()' equivalent for errbot?
        yield joke['punchline']

    @botcmd
    def list(self, msg, args):
        '''Lists all printings of a card.'''
        try:
            prints = get_card(args, listing=True)
        except CardNotFoundException as e:
            return e.msg
        if prints['total_cards'] < 50:
            txt = 'Printings of {} ({}):\n'.format(prints['data'][0]['name'], prints['total_cards'])
            for card in prints['data']:
                txt += '•{} ({}): '.format(card['set_name'], card['set'].upper())
                txt += '${} — '.format(card['prices']['usd']) if card['prices']['usd'] else 'n/a — '
                txt += '€{} — '.format(card['prices']['eur']) if card['prices']['eur'] else 'n/a — '
                txt += '{} Tix'.format(card['prices']['tix']) if card['prices']['tix'] else 'n/a'
                txt += ' — 1 {} wildcard\n'.format(card['rarity']) if 'arena' in card['games'] else '\n'
            return txt
        else:
            return 'Too many reprints ({})'.format(prints['total_cards'])

    @botcmd
    def oracle(self, msg, args):
        '''Fetches the named card\'s oracle text. :book:'''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            return e.msg

        if 'card_faces' in card:
            return '\n--\n'.join(card_text(face) for face in card['card_faces'])
        else:
            return card_text(card)

    @botcmd
    def price(self, msg, args):
        '''Fetches the named card\'s current market prices. :moneybag:'''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            e.msg

        if 'usd' in card or 'eur' in card or 'tix' in card['prices']:
            txt = 'Prices for {} from {} ({}):\n'.format(card['name'], card['set_name'], card['set'].upper())
            txt += '${} — '.format(card['prices']['usd']) if card['prices']['usd'] else 'n/a — '
            txt += '€{} — '.format(card['prices']['eur']) if card['prices']['eur'] else 'n/a — '
            txt += '{} Tix'.format(card['prices']['tix']) if card['prices']['tix'] else 'n/a'
            txt += ' — 1 {} wildcard'.format(card['rarity']) if 'arena' in card['games'] else ''
            return txt
        else:
            return 'Unable to find any price information for {} ({})'.format(card['name'], card['set'])

    @botcmd
    def pwp(self, msg, args):
        '''Fetches the PWP score and bye eligibility for a DCI number :trophy:'''
        if args.isdigit() and 0 < len(args) <= 18:
            return write_pwp(args)
        return '\'{}\' doesn\'t look like a DCI number. Try again, but with an actual number.'.format(args)

    @botcmd
    def roll(self, msg, args):
        '''Rolls one or more dice with N sides; defaults to 1D6. :game_die:'''
        match = re_match(r'(?:(?P<number>\d+)d)?(?P<sides>\d+)?$', args)
        if not match:
            yield 'Please supply a valid number sufficient for rolling.'
            return

        number = int(match.group('number') or 1)  # default to 1 die rolled
        sides = int(match.group('sides') or 6)  # default to 6 sides
        logging.info('{}d{}'.format(number, sides))

        if not 1 < sides <= 10**6:
            yield 'Please supply a valid number of sides.'
            return
        elif not 0 < number <= 100:
            yield 'Please supply a valid number of dice.'
            return

        results = [str(random_randint(1, sides)) for _ in range(number)]
        roll_msg = 'Rolled {} {}-sided dice, and the result is...'
        yield roll_msg.format(number if number > 1 else 'a', sides)
        sleep(1)  # TODO is there a 'send_user_typing_pause()' equivalent for errbot?
        yield '... {}! :game_die:'.format(' '.join(results))

    @botcmd
    def rulings(self, msg, args):
        '''Fetches the official rulings for the card. :scales:'''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            return e.msg
        rulings = get_card_rulings(card['id'])
        if rulings:
            counter = 0
            txt = ''
            for rule in rulings['data']:
                if rule['source'] == 'wotc':
                    counter += 1
                    txt += '\n• {} ({})'.format(rule['comment'], rule['published_at'])
            if counter > 0:
                return 'Rulings for {} ({}):{}'.format(card['name'], counter, txt)
            else:
                return 'There are no official rulings for {}.'.format(card['name'])
        else:
            return 'Couldn\'t find any rulings for {}.'.format(card['name'])

    @botcmd
    def sutcliffe(self, msg, args):
        '''Sutcliffe meme generator. :hand: / :point_right:'''
        syntax = '!sutcliffe cardname A / cardname B'
        try:
            card1, card2 = args.split('/')
        except ValueError:
            return 'Argument error (expected \'{}\')'.format(syntax)
        card_images = []
        try:
            image1 = download_card_image(card1)
            image2 = download_card_image(card2)
        except CardNotFoundException as e:
            return e.msg

        sutcliffe_template = Image.open('plugins/tradingpost-errbot/assets/sutcliffe-canvas.png')

        card_positions = ((490, 25), (490, 435))

        sutcliffe_template.paste(image1, box=card_positions[0])
        sutcliffe_template.paste(image2, box=card_positions[1])

        sutcliffe_bytes = BytesIO()
        sutcliffe_template.save(sutcliffe_bytes, format='PNG')

        self.send_stream_request(msg.frm, sutcliffe_bytes)


class CardNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg


def card_text(card):
    txt = u'{} {}\n{}\n{}'.format(card['name'], card['mana_cost'], card['type_line'], card['oracle_text'])
    if 'power' in card and 'toughness' in card:
        txt += u'\n`{}/{}`'.format(card['power'], card['toughness'])
    if 'loyalty' in card:
        txt += u'\n`{}`'.format(card['loyalty'])
    return emoji_filter(txt)


def emoji_filter(input):
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
    index = start_index
    for token in sequence:
        index = data.find(token, index)
        if index == -1:
            return -1
    return index + len(sequence[-1])


def get_card(args, listing=False):
    match = re_search(r'\((.+)\)', args)
    name = args.split('(')[0] if match else args
    preference = match.group(1) if match else None
    mode = 'search?unique=prints&order=released&q=!"{}"' if listing else 'named?exact={}'
    query_url = 'https://api.scryfall.com/cards/{}'.format(mode).format(name)
    if preference and not listing:
        query_url += '&set={}'.format(preference)
    logging.info(u'Connecting to https://api.scryfall.com')
    response = requests_get(query_url)
    if response.status_code is 200:
        try:
            return response.json()
        except ValueError:
            logging.error(u'No JSON object could be decoded from API response: {}'.format(response))
            raise CardNotFoundException("Card '{}' not found.".format(name))
    else:
        raise CardNotFoundException("Card '{}' not found.".format(name))


def get_card_rulings(scryfall_id):
    query_url = 'https://api.scryfall.com/cards/{}/rulings'.format(scryfall_id)
    logging.info(u'Connecting to https://api.scryfall.com')
    response = requests_get(query_url)
    if response.status_code is 200:
        try:
            return response.json()
        except ValueError:
            logging.error(u'No JSON object could be decoded from API response: {}'.format(response))
            return None
    else:
        return None


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
        'Referer': 'http://www.wizards.com/Magic/PlaneswalkerPoints/{}'.format(dci_number)
    }
    data = {'Parameters': {'DCINumber': dci_number, 'SelectedType': 'Yearly'}}
    logging.info(u'Connecting to http://www.wizards.com')
    response = requests_post(url, headers=headers, data=json_dumps(data))
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
            logging.error(u'No JSON object could be decoded from API response: {}'.format(response))
            return 'Garbled response from backend. Please try again later.'
        try:
            return {'currentSeason': seasons[0], 'lastSeason': seasons[1]}
        except IndexError:
            return 'DCI# {} not found.'.format(dci_number)
    else:
        logging.error(u'No response from API (HTTP code {})'.format(response.status_code))
        return 'No response from backend. Please try again later.'


def write_pwp(dci_number):
    response = get_seasons(dci_number)
    if isinstance(response, dict):
        txt = 'DCI# {} has {} points in the current season, and {} points last season.\nCurrently '.format(dci_number, response['currentSeason'], response['lastSeason'])
        if response['currentSeason'] >= 2250 or response['lastSeason'] >= 2250:
            txt += 'eligible for 2 GP byes.'
        elif response['currentSeason'] >= 1300 or response['lastSeason'] >= 1300:
            txt += 'eligible for 1 GP bye.'
        else:
            txt += 'not eligible for GP byes.'
        return txt
    else:
        return response

def download_card_image(cardname):
    card = get_card(cardname)
    image_url = card['image_uris']['normal'] # 488*680 (w*h)
    image = Image.open(BytesIO(requests_get(image_url).content))
    resize_ratio = min((0.5 * 488) / image.width, (0.5 * 680) / image.height)
    return image.resize((int(image.width*resize_ratio), int(image.height*resize_ratio)), Image.ANTIALIAS)

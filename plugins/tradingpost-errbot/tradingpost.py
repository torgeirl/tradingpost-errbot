from datetime import datetime, date
from io import BytesIO
from json import load as json_load
import logging
from os import getcwd
from os.path import dirname, join, realpath
from random import choice as random_choice
from re import search as re_search, sub as re_sub, DOTALL as re_dotall
from time import sleep

from errbot import BotPlugin, botcmd
from PIL import Image
from requests import get as requests_get

__location__ = realpath(join(getcwd(), dirname(__file__)))
logger = logging.getLogger(__name__)


class Tradingpost(BotPlugin):
    '''Plugin that fetches MtG card pictures, oracle texts, prices and flavor texts on request.'''

    @botcmd
    def card(self, msg, args):
        '''I\'ll post a picture of the named card. :frame_with_picture:'''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            return e.msg
        body = '{} ({})'.format(card['set_name'], card['set'].upper())
        if card['layout'] in ('transform', 'modal_dfc'):
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
    def flavor(self, msg, args):
        '''Full-blown vorthos or a cheesy one liner? :scroll: '''
        try:
            card = get_card(args)
        except CardNotFoundException as e:
            return e.msg
        flavor_texts = []
        if 'card_faces' in card:
            for face in card['card_faces']:
                if 'flavor_text' in face:
                    flavor_texts.append(face['flavor_text'])
        else:
            if 'flavor_text' in card:
                flavor_texts.append(card['flavor_text'])
        if flavor_texts:
            return '{}\n({} ({}))'.format('\n—\n'.join(flavor_texts), card['name'], card['set'].upper())
        else:
            return 'It seems {} ({}) doesn\'t have any flavor text.'.format(card['name'], card['set'].upper())

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
            return '\n—\n'.join(card_text(face) for face in card['card_faces'])
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
        '''Fetches available PlaneswalkerPoints for a DCI number :trophy: (deprecated)'''
        return 'Deprecated: the PWP website was closed by WotC on May 27, 2020. :cry:'

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
    def standard(self, msg, args):
        '''Gets the current Standard format from What's in Standard.'''
        sets_and_bans = get_sets_and_bans()
        rfc3339 = '%Y-%m-%dT%H:%M:%S.%f'
        today = date.today()
        released_sets = []        
        legal_sets = [] 

        # Extract only released sets
        for set in sets_and_bans['sets']:
            if set['enterDate']['exact'] is not None:
                enter_date = datetime.strptime(set['enterDate']['exact'], rfc3339).date()
            if enter_date < today:
                released_sets.append(set)

        # Remove sets that have rotated out
        for set in released_sets:
            if set['exitDate']['exact'] is not None:
                exit_date = datetime.strptime(set['exitDate']['exact'], rfc3339).date()
                if exit_date >= today:
                    legal_sets.append(set)
            else:
                legal_sets.append(set)

        # Assemble list of legal sets
        txt = f'Standard legal sets ({today}):'
        for set in legal_sets:
            txt += f'\n • {set["name"]}'
        yield txt

        # Assemble list of banned cards in currently legal sets
        banned_cards = [card['cardName'] for card in sets_and_bans['bans']
                if card['setCode'] in [set['code'] for set in legal_sets]]
        if banned_cards:
            txt = f'\n\nCards banned in Standard ({len(banned_cards)}):'
            for card in banned_cards:
                txt += f'\n • {card}'
            yield txt

        # Add information about rotating sets and entering sets if requested
        if 'future' in args:
            txt = '\n\nUpcoming sets:'
            upcoming_sets = []
            tbd_sets = []
            for set in sets_and_bans['sets']:
                if set['enterDate']['exact'] is not None:
                    enter_date = datetime.strptime(set['enterDate']['exact'], rfc3339).date()
                    if enter_date >= today:
                        upcoming_sets.append((set['name'], (enter_date - today).days))
                else:
                    tbd_sets.append(set['name'])
            for name, days in sorted(upcoming_sets, key=lambda e: e[1]):
                txt += f'\n • {name} (Releases in {days} days)'
            for name in tbd_sets:
                txt += f'\n • {name} (Release date T.B.D.)'

            rotating_sets = []
            for set in legal_sets:
                if set['exitDate']['exact'] is not None:
                    exit_date = datetime.strptime(set['exitDate']['exact'], rfc3339).date()
                    days = (exit_date - today).days
                    rotating_sets.append([set['name'], days])
            if rotating_sets:
                txt += f'\n\nSets rotating out:'
                for name, days in rotating_sets:
                    txt += f'\n • {name} (Legal for another {days} days)'
            yield txt


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
        size = sutcliffe_bytes.getbuffer().nbytes
        sutcliffe_bytes.seek(0)

        name = 'sutcliffe-{}.png'.format(datetime.now().strftime('%Y%m%d-%H%M'))
        self.send_stream_request(msg.frm, sutcliffe_bytes, name=name, size=size, stream_type='image/png')


class CardNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg


class UnexpectedStatusCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


def card_text(card):
    text = u'{} {}\n{}\n{}'.format(card['name'], card['mana_cost'], card['type_line'], card['oracle_text'])
    if 'power' in card and 'toughness' in card:
        text += u'\n`{}/{}`'.format(card['power'], card['toughness'])
    if 'loyalty' in card:
        text += u'\n`{}`'.format(card['loyalty'])
    return re_sub('{([a-zA-Z\d\/]+)}',
                  lambda match: ':mana-{}:'.format(match.group(1).replace('/', '').lower()),
                  text, flags=re_dotall)


def get_card(args, listing=False):
    match = re_search(r'\((.+)\)', args)
    name = args.split('(')[0] if match else args
    preference = match.group(1) if match else None
    mode = 'search?unique=prints&order=released&q=!"{}"' if listing else 'named?exact={}'
    query_url = 'https://api.scryfall.com/cards/{}'.format(mode).format(name)
    if preference and not listing:
        query_url += '&set={}'.format(preference)
    logger.info(u'Connecting to https://api.scryfall.com')
    response = requests_get(query_url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            logger.error(u'No JSON object could be decoded from API response: {}'.format(response))
            raise CardNotFoundException('Card \'{}\' not found.'.format(name))
    else:
        raise CardNotFoundException('Card \'{}\' not found.'.format(name))


def get_card_rulings(scryfall_id):
    query_url = 'https://api.scryfall.com/cards/{}/rulings'.format(scryfall_id)
    logger.info(u'Connecting to https://api.scryfall.com')
    response = requests_get(query_url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            logger.error(u'No JSON object could be decoded from API response: {}'.format(response))
            return None
    else:
        return None


def get_sets_and_bans():
    query_url = 'https://whatsinstandard.com/api/v6/standard.json'
    logger.info(u'Connecting to https://whatsinstandard.com')
    response = requests_get(query_url)
    if response.status_code == 200:
        try:
            dataset = response.json()
            if dataset['deprecated']:
                logger.warning(u'{} is marked as deprecated.'.format(query_url))
            return dataset
        except ValueError:
            logger.error(u'No JSON object could be decoded from API response: {}'.format(response))
            raise ValueError('Reponse from https://whatsinstandard.com could not be decoded.')
    else:
        logger.error(u'Unexpected status code ({}) fetching {}'.format(response.status_code, query_url))
        raise UnexpectedStatusCode(response.status_code)


def download_card_image(cardname):
    card = get_card(cardname)
    image_url = card['image_uris']['normal'] # 488*680 (w*h)
    image = Image.open(BytesIO(requests_get(image_url).content))
    resize_ratio = min((0.5 * 488) / image.width, (0.5 * 680) / image.height)
    return image.resize((int(image.width*resize_ratio), int(image.height*resize_ratio)), Image.ANTIALIAS)

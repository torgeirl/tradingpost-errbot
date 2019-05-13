import requests
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class UnexpectedStatusCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


def _parse_seasonal_points(html):
    soup = BeautifulSoup(html, 'html.parser')
    points = soup.find('div', {'class': 'SeasonPointsValuesValue'}).text
    season = soup.find('div', {'class': 'SeasonRange'}).text
    seasonal_dict = {
        'season': season.replace('(', '').replace(')', ''),
        'points': points
    }
    return seasonal_dict


def _parse_pwp(json_dict):
    data = json_dict['Data']
    points = []
    for element in data:
        key, value = element['Key'], element['Value']
        if key == 'CompetitivePoints':
            points.append(_parse_seasonal_points(value))
        if key == 'LifetimePoints':
            points.append({'season': 'Lifetime', 'points': value})
    return points


def _get_pwp(dci_number):
    logging.info(u'Connecting to http://www.wizards.com/')
    url = 'https://www.wizards.com/Magic/PlaneswalkerPoints/JavaScript/GetPointsSummary/{}'.format(dci_number)
    response = requests.post(url, verify=False)

    if response.status_code is 200:
        return _parse_pwp(response.json())
    else:
        logging.error('Unexpected status code ({}) fetching {}'.format(response.status_code, url))
        raise UnexpectedStatusCode(response.status_code)


def get_pwp(dci_number):
    pwp = _get_pwp(dci_number)

    if isinstance(pwp, list):
        response = 'Planeswalker Points for DCI# {}:\n'.format(dci_number)
        for entry in pwp:
            response += '{}: **{}** points\n'.format(entry['season'], entry['points'])
        return response
    else:
        logger.error('Received malformed response from PlaneswalkerPoints. Expected list, got {}'.format(type(pwp)))
        raise ValueError('Malformed PlaneswalkerPoints response')

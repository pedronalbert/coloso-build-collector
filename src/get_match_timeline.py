import requests

from utils import API_KEY
from errors import RiotLimitError, RiotServerError

def getMatchTimeline(gameId, platformId, logger):
    logger.info('Fetching match timeline #{}'.format(gameId))

    url = 'https://{}.api.riotgames.com/lol/match/v3/timelines/by-match/{}'.format(platformId, gameId)
    response = requests.get(url, params = { "api_key": API_KEY })

    if response.status_code == 200:
        logger.debug('Fetch Success')
        timeLines = response.json()

        return timeLines
    elif response.status_code == 429:
        retryAfter = int(response.headers['retry-after'])
        logger.warning('Fetch failed limit reached, retry after ' + str(retryAfter) + ' seconds')

        raise RiotLimitError(retryAfter)
    else:
        logger.warning('Fetch failed CODE: ' + str(response.status_code))
        raise RiotServerError('RiotServerError CODE: ' + str(response.status_code))

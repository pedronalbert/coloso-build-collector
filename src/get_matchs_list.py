import requests
from pydash.arrays import sort

from errors import RiotLimitError, RiotServerError
from utils import URID, regionToPlatform, getLogger, API_KEY

def getMatchsList(proSummoner):
    region = URID.getRegion(proSummoner.summonerId)
    logger = getLogger(region)

    logger.info('Fetching matchs list account #' + str(proSummoner.accountId))

    url = "https://{}.api.riotgames.com/lol/match/v3/matchlists/by-account/{}".format(regionToPlatform(region), proSummoner.accountId)
    response = requests.get(url, params = { "api_key": API_KEY, "beginTime": proSummoner.lastCheck + 1 })

    if response.status_code == 200 or response.status_code == 404:
        logger.debug('Fetch success')
        jsonResponse = response.json()

        if 'matches' in jsonResponse:
            matches = jsonResponse['matches']
        else:
            matches = []

        matches = sort(matches, key = lambda m: m['timestamp'])
        matches = [match for match in matches if match['queue'] == 420 or match['queue'] == 440]
        logger.info(str(len(matches)) + ' Matches found account #' + str(proSummoner.accountId))

        return matches
    elif response.status_code == 429:
        retryAfter = int(response.headers['retry-after'])

        logger.warning('Fetch failed, limit reached, retry after ' + str(retryAfter) + ' seconds')

        raise RiotLimitError(retryAfter)
    else:
        logger.warning('Fetch failed CODE: ' + str(response.status_code))
        raise RiotServerError

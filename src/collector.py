import os, requests, time, traceback, json
from pydash.collections import find as _find
from pydash.arrays import drop_right_while as _drop_right_while, sort as _sort
from datetime import datetime
from retrying import retry
import logging

from models import ProSummoner, ProBuild
from errors import RiotLimitError, RiotServerError
from utils import URID

API_KEY = os.environ['RIOT_API_KEY']

def riotRetryFilter(exception):
    return isinstance(exception, RiotLimitError)

class Collector():
    def __init__(self, region, interval, logLevel):
        self.region = region
        self.interval = interval
        self.logger = self.getLogger()

    def getLogger(self):
        logger = logging.getLogger(self.region)
        handler = logging.FileHandler('./logs/' + self.region + '.txt')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)

        return logger

    def start(self):
        while True:
            proSummoners = ProSummoner.select().where(ProSummoner.summonerUrid.regexp(self.region))

            if len(proSummoners) <= 0:
                self.logger.critical('No hay summoners en esta region')
                return

            self.logger.info('Collector Init')
            for proSummoner in proSummoners:
                try:
                    matches = self.getMatchesList(proSummoner)
                    time.sleep(self.interval)
                    for match in matches:
                        try:
                            matchData = self.getMatchData(match)

                            if matchData['matchDuration'] < 600:
                                self.updateSummonerLastCheckTime(proSummoner, matchData['matchCreation'])
                                continue

                            proBuild = self.getProBuild(matchData, proSummoner)

                            if self.saveProBuild(proBuild):
                                self.updateSummonerLastCheckTime(proSummoner, matchData['matchCreation'])

                            time.sleep(self.interval)
                        except Exception as e:
                            time.sleep(self.interval)
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(self.interval)

    def updateSummonerLastCheckTime(self, proSummoner, newTime):
        self.logger.debug('Updating lastCheck summoner #' + proSummoner.summonerUrid)
        proSummoner.lastCheck = newTime
        proSummoner.updated_at = datetime.utcnow()

        if proSummoner.save() > 0:
            self.logger.debug('Updating success')
        else:
            self.logger.error('Updating failed')

    @retry(retry_on_exception = riotRetryFilter, stop_max_attempt_number = 3)
    def getMatchesList(self, proSummoner):
        sumId = URID.getId(proSummoner.summonerUrid)

        self.logger.info('Fetching matches list summoner #' + proSummoner.summonerUrid)

        url = 'https://' + self.region.lower() + '.api.pvp.net/api/lol/' + self.region.lower() + '/v2.2/matchlist/by-summoner/' + str(sumId)
        response = requests.get(url, params = { "api_key": API_KEY, "beginTime": proSummoner.lastCheck + 1 })

        if response.status_code == 200:
            self.logger.debug('Fetching success')
            jsonResponse = response.json()

            if 'matches' in jsonResponse:
                matches = jsonResponse['matches']
            else:
                matches = []

            self.logger.info(str(len(matches)) + ' Matches found summoner #' + proSummoner.summonerUrid)
            matches = _sort(matches, key = lambda m: m['timestamp'])

            return matches
        elif response.status_code == 429:
            if 'retry-after' in response.headers:
                retryAfter = int(response.headers['retry-after']) + self.interval
            else:
                retryAfter = self.interval

            self.logger.warning('Fetch limit reached, retry in ' + str(retryAfter) + ' seconds')
            time.sleep(retryAfter)

            raise RiotLimitError
        else:
            self.logger.warning('Fetch Error CODE: ' + str(response.status_code))
            raise RiotServerError

    def saveProBuild(self, proBuild):
        self.logger.info('Storing build')
        query = ProBuild(
            matchUrid = URID.generate(proBuild['region'], proBuild['matchId']),
            matchCreation = proBuild['matchCreation'],
            region = proBuild['region'],
            spell1Id = proBuild['spell1Id'],
            spell2Id = proBuild['spell2Id'],
            championId = proBuild['championId'],
            highestAchievedSeasonTier = proBuild['highestAchievedSeasonTier'],
            masteries = json.dumps(proBuild['masteries']),
            runes = json.dumps(proBuild['runes']),
            stats = json.dumps(proBuild['stats']),
            itemsOrder = json.dumps(proBuild['itemsOrder']),
            skillsOrder = json.dumps(proBuild['skillsOrder']),
            pro_summoner_id = proBuild['proSummonerId'],
            created_at = datetime.utcnow(),
            updated_at = datetime.utcnow()
        )

        if query.save() > 0:
            self.logger.debug('Storing success')
            return True
        else:
            self.logger.error('Storing failed')
            return False

    def getProBuild(self, matchData, proSummoner):
        self.logger.debug('Parsing build')
        summonerId = URID.getId(proSummoner.summonerUrid)
        proBuild = {}
        participantId = _find(matchData['participantIdentities'], lambda identity: identity['player']['summonerId'] == summonerId)['participantId']
        participantData = _find(matchData['participants'], lambda participant: participant['participantId'] == participantId)

        proBuild['matchId'] = matchData['matchId']
        proBuild['matchCreation'] = matchData['matchCreation']
        proBuild['proSummonerId'] = proSummoner.id
        proBuild['region'] = matchData['region']
        proBuild['spell1Id'] = participantData['spell1Id']
        proBuild['spell2Id'] = participantData['spell2Id']
        proBuild['championId'] = participantData['championId']
        proBuild['highestAchievedSeasonTier'] = participantData['highestAchievedSeasonTier']
        proBuild['masteries'] = participantData['masteries']
        proBuild['runes'] = participantData['runes']
        proBuild['stats'] = participantData['stats']

        frames = matchData['timeline']['frames']
        frames = [frame for frame in frames if 'events' in frame]
        events = []

        for frame in frames:
            for event in frame['events']:
                if 'participantId' in event and event['participantId'] == participantId:
                    events.append(event)

        itemsOrder = []
        skillsOrder = []

        for event in events:
            eventType = event['eventType']

            if eventType == 'ITEM_PURCHASED':
                itemsOrder.append({
                    "itemId": event['itemId'],
                    "timestamp": event['timestamp']
                })

            if eventType == 'ITEM_UNDO':
                itemBefore = event['itemBefore']

                _drop_right_while(itemsOrder, lambda item: item['itemId'] == itemBefore)

            if eventType == 'ITEM_SOLD':
                _drop_right_while(itemsOrder, lambda item: item['itemId'] == event['itemId'])

            if eventType == 'SKILL_LEVEL_UP':
                skillsOrder.append({
                    "skillSlot": event['skillSlot'],
                    "levelUpType": event['levelUpType'],
                    "timestamp": event['timestamp'],
                })

        proBuild['itemsOrder'] = itemsOrder
        proBuild['skillsOrder'] = skillsOrder

        return proBuild

    @retry(retry_on_exception = riotRetryFilter, stop_max_attempt_number = 3)
    def getMatchData(self, match):
        region = match['region']

        self.logger.info('Fetching match data match #' + region.upper() + '_' + str(match['matchId']))

        url = 'https://' + region.lower() + '.api.pvp.net/api/lol/' + region.lower() + '/v2.2/match/' + str(match['matchId'])
        response = requests.get(url, params = { "api_key": API_KEY, "includeTimeline": True })

        if response.status_code == 200:
            self.logger.debug('Datos obtenidos correctamente')
            matchData = response.json()

            return matchData
        elif response.status_code == 429:
            retryAfter = int(response.headers['retry-after']) + self.interval
            self.logger.warning('Fetch limit reached, retry in ' + str(retryAfter) + ' seconds')
            time.sleep(retryAfter)

            raise RiotLimitError
        else:
            self.logger.warning('Fetch Error CODE: ' + str(response.status_code))
            raise RiotServerError

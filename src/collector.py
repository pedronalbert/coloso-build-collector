import time, json, logging
from datetime import datetime
import traceback

from models import ProSummoner, ProBuild
from errors import RiotLimitError
from utils import getLogger
from .get_matchs_list import getMatchsList
from .get_match_data import getMatchData
from .get_match_timeline import getMatchTimeline
from .parse_pro_build import parseProBuild

# Disable requests logging
logging.getLogger("requests.packages.urllib3").propagate = False

def riotRetryFilter(exception):
    return isinstance(exception, RiotLimitError)

class Collector():
    def __init__(self, region, interval):
        self.region = region
        self.interval = interval
        self.logger = getLogger(region)

    def start(self):
        while True:
            proSummoners = ProSummoner.select().where(ProSummoner.summonerId.regexp(self.region))

            if len(proSummoners) <= 0:
                self.logger.critical('There is no summoners in this region')
                return

            self.logger.info('Collector Init')
            for proSummoner in proSummoners:
                try:
                    matches = getMatchsList(proSummoner, self.logger)
                    time.sleep(self.interval)
                    for match in matches:
                        try:
                            matchData = getMatchData(match['gameId'], match['platformId'], self.logger)

                            if matchData['gameDuration'] < 600:
                                self.updateSummonerLastCheckTime(proSummoner, matchData['gameCreation'])
                                time.sleep(self.interval)
                                continue

                            try:
                                timeLines = getMatchTimeline(matchData['gameId'], matchData['platformId'], self.logger)
                            except RiotLimitError as e:
                                time.sleep(e.retryAfter * 2)
                                continue

                            proBuild = parseProBuild(matchData, timeLines, proSummoner, self.logger)

                            if self.saveProBuild(proBuild):
                                self.updateSummonerLastCheckTime(proSummoner, matchData['gameCreation'])

                            time.sleep(self.interval)
                        except Exception as e:
                            self.logger.warning(e)
                            traceback.print_exc()
                            time.sleep(self.interval)
                except Exception as e:
                    self.logger.warning(e)
                    traceback.print_exc()
                    time.sleep(self.interval)

    def updateSummonerLastCheckTime(self, proSummoner, newTime):
        self.logger.debug('Updating lastCheck summoner #' + proSummoner.summonerId)
        proSummoner.lastCheck = newTime
        proSummoner.updated_at = datetime.utcnow()

        if proSummoner.save() > 0:
            self.logger.debug('Update success')
        else:
            self.logger.error('Update failed')

    def saveProBuild(self, proBuild):
        self.logger.info('Storing build')

        query = ProBuild(
            gameId = proBuild['gameId'],
            seasonId = proBuild['seasonId'],
            queueId = proBuild['queueId'],
            gameVersion = proBuild['gameVersion'],
            platformId = proBuild['platformId'],
            gameMode = proBuild['gameMode'],
            mapId = proBuild['mapId'],
            gameType = proBuild['gameType'],
            gameDuration = proBuild['gameDuration'],
            gameCreation = proBuild['gameCreation'],
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

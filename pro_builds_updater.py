import logging, colorlog, time
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from models import mysql_db, ProBuild, ProSummoner
from utils import URID, regionToPlatform
from src.get_match_data import getMatchData
from src.get_match_timeline import getMatchTimeline
from src.parse_pro_build import parseProBuild

mysql_db.connect()

logging.basicConfig(level=logging.INFO)
# Disable requests logging
logging.getLogger("requests.packages.urllib3").propagate = False


def createLogger():
    logger = logging.getLogger('pro_builds_updater')
    logger.propagate = False

    #configura handlers
    handler = logging.FileHandler('./logs/pro_builds_updater.txt')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    chandler = colorlog.StreamHandler()
    chandler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

    logger.addHandler(handler)
    logger.addHandler(chandler)

    return logger

def init():
    logger = createLogger()

    for proBuild in ProBuild.select().where(ProBuild.platformId == None).order_by(ProBuild.id.desc()):
        logger.info('Init updater for proBuild #' + str(proBuild.id))

        gameUrid = proBuild.gameId
        region = URID.getRegion(gameUrid)
        platformId = regionToPlatform(region)
        gameId = URID.getId(gameUrid)

        try:
            matchData = getMatchData(gameId, platformId, logger)
            matchTimeline = getMatchTimeline(gameId, platformId, logger)
            proSummoner = ProSummoner.get(ProSummoner.id == proBuild.pro_summoner_id)
            parsedProBuild = parseProBuild(matchData, matchTimeline, proSummoner, logger)

            proBuild.seasonId = parsedProBuild['seasonId']
            proBuild.queueId = parsedProBuild['queueId']
            proBuild.gameVersion = parsedProBuild['gameVersion']
            proBuild.platformId = parsedProBuild['platformId']
            proBuild.mapId = parsedProBuild['mapId']
            proBuild.gameType = parsedProBuild['gameType']
            proBuild.gameDuration = parsedProBuild['gameDuration']
            proBuild.gameMode = parsedProBuild['gameMode']

            if proBuild.save():
                logger.info('ProBuild update success')
            else:
                logger.info('ProBuild update failed')

            time.sleep(0.5)
        except Exception as e:
            logger.warning(e)

init()

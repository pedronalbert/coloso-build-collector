from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import logging
from models import mysql_db, ProBuild, ProSummoner
from utils import URID, regionToPlatform
from src.get_match_data import getMatchData
from src.get_match_timeline import getMatchTimeline
from src.parse_pro_build import parseProBuild

mysql_db.connect()

logging.basicConfig(level=logging.INFO)

def init():
    for proBuild in ProBuild.select().where(ProBuild.platformId == None).order_by(ProBuild.id.desc()):
        logging.info('Init updater for proBuild #' + str(proBuild.id))

        gameUrid = proBuild.gameId
        region = URID.getRegion(gameUrid)
        platformId = regionToPlatform(region)
        gameId = URID.getId(gameUrid)

        try:
            matchData = getMatchData(gameId, platformId, logging)
            matchTimeline = getMatchTimeline(gameId, platformId, logging)
            proSummoner = ProSummoner.get(ProSummoner.id == proBuild.pro_summoner_id)
            parsedProBuild = parseProBuild(matchData, matchTimeline, proSummoner, logging)

            proBuild.seasonId = parsedProBuild['seasonId']
            proBuild.queueId = parsedProBuild['queueId']
            proBuild.gameVersion = parsedProBuild['gameVersion']
            proBuild.platformId = parsedProBuild['platformId']
            proBuild.mapId = parsedProBuild['mapId']
            proBuild.gameType = parsedProBuild['gameType']
            proBuild.gameDuration = parsedProBuild['gameDuration']
            proBuild.gameMode = parsedProBuild['gameMode']

            if proBuild.save():
                logging.info('ProBuild update success')
            else:
                logging.info('ProBuild update failed')
        except Exception as e:
            logging.warning(e)
init()

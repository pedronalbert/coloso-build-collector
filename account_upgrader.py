from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import requests
from models import mysql_db, ProSummoner
from utils import URID, regionToPlatform

mysql_db.connect()

API_KEY = os.environ['RIOT_API_KEY']

def init():
    for proSummoner in ProSummoner.select().where(ProSummoner.accountId == None):
        print("Requesting summonerUrid: %s", proSummoner.summonerId)

        region = URID.getRegion(proSummoner.summonerId)
        summonerId = URID.getId(proSummoner.summonerId)
        url = "https://{}.api.riotgames.com/lol/summoner/v3/summoners/{}".format(regionToPlatform(region), summonerId)

        response = requests.get(url, params = { "api_key": API_KEY })

        if response.status_code == 200:
            print("Request success")
            jsonResponse = response.json()

            proSummoner.accountId = jsonResponse["accountId"]

            if proSummoner.save():
                print("Summoner update success")
            else:
                print("Summoner update fail")
        else:
            print("Request failed")
init()

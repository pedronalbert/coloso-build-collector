from models import mysql_db, ProSummoner, ProBuild
from pydash.collections import find as _find
from pydash.arrays import drop_right_while as _drop_right_while
import os
import requests
import time
import pprint
import traceback
import json
from datetime import datetime

pp = pprint.PrettyPrinter(indent=1)
mysql_db.connect()

API_KEY = os.environ['RIOT_API_KEY']
BASIC_INTERVAL = 5
proSummoners = ProSummoner.select()

class RiotLimitError(Exception):
    pass

class RiotServerError(Exception):
    pass


def getMatchData(match):
    print('Obteniendo datos para la partida #' + str(match['matchId']))

    url = 'https://' + match['region'] + '.api.pvp.net/api/lol/' + match['region'] + '/v2.2/match/' + str(match['matchId'])
    response = requests.get(url, params = { "api_key": API_KEY, "includeTimeline": True })

    if response.status_code == 200:
        print('Fetching matchData Sucess!')
        matchData = response.json()

        return matchData
    elif response.status_code == 429:
        retryAfter = int(response.headers['retry-after']) + 5
        print('Limit reached, repeating after: ' + str(retryAfter) + ' seconds')
        time.sleep(retryAfter)

        raise RiotLimitError
    else:
        print('Riot server error')
        raise RiotServerError


def getMatchesList(proSummoner):
    print('Obteniendo lista de juegos para el proSummoner #' + str(proSummoner.summonerId))

    url = 'https://' + proSummoner.region + '.api.pvp.net/api/lol/' + proSummoner.region + '/v2.2/matchlist/by-summoner/' + str(proSummoner.summonerId)
    response = requests.get(url, params = { "api_key": API_KEY, "beginTime": proSummoner.lastCheck + 1 })

    if response.status_code == 200:
        matches = response.json()['matches']
        print(str(len(matches)) + ' Matches found')
        sorted(matches, key = lambda m: m['timestamp'], reverse = True)

        return matches
    elif response.status_code == 429:
        if 'retry-after' in response.headers:
            retryAfter = int(response.headers['retry-after']) + BASIC_INTERVAL
        else:
            retryAfter = BASIC_INTERVAL

        print('Limit reached, repeating after: ' + str(retryAfter) + ' seconds')
        time.sleep(retryAfter)

        raise RiotLimitError
    else:
        print('Riot server error')
        raise RiotServerError

def getProBuild(matchData, proSummoner):
    print('Realizando el parseo de la build')
    proBuild = {}
    participantId = _find(matchData['participantIdentities'], lambda identity: identity['player']['summonerId'] == proSummoner.summonerId)['participantId']
    participantData = _find(matchData['participants'], lambda participant: participant['participantId'] == participantId)

    proBuild['matchId'] = matchData['matchId']
    proBuild['matchCreation'] = matchData['matchCreation']
    proBuild['proSummonerId'] = proSummoner.id
    proBuild['region'] = matchData['region'].lower()
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

def saveProBuild(proBuild):
    print('Guardando la Build en la base de datos...')
    query = ProBuild(
        matchId = proBuild['matchId'],
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
        print('Build Guardada exitosamente!')
        return True
    else:
        print('Error al guardar la build en la base de datos!')
        return False

def updateCheckTime(proSummoner, newTime):
    print('Actualizando el tiempo para el proSummoner #' + str(proSummoner.id) + ' a: ' + str(newTime))
    proSummoner.lastCheck = newTime
    proSummoner.updated_at = datetime.utcnow()
    proSummoner.save()
    print('Tiempo actualizado!')

for proSummoner in proSummoners:
    try:
        matches = getMatchesList(proSummoner)
        time.sleep(BASIC_INTERVAL)
        for match in matches:
            try:
                matchData = getMatchData(match)

                if matchData['matchDuration'] < 600:
                    continue

                proBuild = getProBuild(matchData, proSummoner)
                if saveProBuild(proBuild):
                    updateCheckTime(proSummoner, matchData['matchCreation'])
                time.sleep(BASIC_INTERVAL)
            except Exception as e:
                traceback.print_exc()
                time.sleep(BASIC_INTERVAL)
    except Exception as e:
        traceback.print_exc()
        time.sleep(BASIC_INTERVAL)

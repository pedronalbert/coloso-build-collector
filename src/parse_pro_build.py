from pydash.collections import find
from pydash.arrays import drop_right_while

from utils import URID, platformToRegion

def parseProBuild(matchData, timeLines, proSummoner, logger):
    region = platformToRegion(matchData['platformId'])

    logger.debug('Parsing Pro Build')
    proBuild = {}
    participantId = find(matchData['participantIdentities'], lambda identity: identity['player']['accountId'] == proSummoner.accountId or identity['player']['currentAccountId'] == proSummoner.accountId)['participantId']
    participantData = find(matchData['participants'], lambda participant: participant['participantId'] == participantId)

    proBuild['gameId'] = URID.generate(region, matchData['gameId'])
    proBuild['seasonId'] = matchData['seasonId']
    proBuild['queueId'] = matchData['queueId']
    proBuild['gameVersion'] = matchData['gameVersion']
    proBuild['gameDuration'] = matchData['gameDuration']
    proBuild['platformId'] = matchData['platformId']
    proBuild['gameMode'] = matchData['gameMode']
    proBuild['mapId'] = matchData['mapId']
    proBuild['gameType'] = matchData['gameType']
    proBuild['gameDuration'] = matchData['gameDuration']
    proBuild['gameCreation'] = matchData['gameCreation']
    proBuild['spell1Id'] = participantData['spell1Id']
    proBuild['spell2Id'] = participantData['spell2Id']
    proBuild['championId'] = participantData['championId']
    proBuild['highestAchievedSeasonTier'] = participantData['highestAchievedSeasonTier']
    proBuild['masteries'] = participantData['masteries']
    proBuild['runes'] = participantData['runes']
    proBuild['stats'] = participantData['stats']
    proBuild['proSummonerId'] = proSummoner.id

    frames = timeLines['frames']
    frames = [frame for frame in frames if 'events' in frame]
    events = []

    for frame in frames:
        for event in frame['events']:
            if 'participantId' in event and event['participantId'] == participantId:
                events.append(event)

    itemsOrder = []
    skillsOrder = []

    for event in events:
        eventType = event['type']

        if eventType == 'ITEM_PURCHASED':
            itemsOrder.append({
                "itemId": event['itemId'],
                "timestamp": event['timestamp']
            })

        if eventType == 'ITEM_UNDO':
            itemBefore = event['beforeId']

            drop_right_while(itemsOrder, lambda item: item['itemId'] == itemBefore)

        if eventType == 'ITEM_SOLD':
            drop_right_while(itemsOrder, lambda item: item['itemId'] == event['itemId'])

        if eventType == 'SKILL_LEVEL_UP':
            skillsOrder.append({
                "skillSlot": event['skillSlot'],
                "levelUpType": event['levelUpType'],
                "timestamp": event['timestamp'],
            })

    proBuild['itemsOrder'] = itemsOrder
    proBuild['skillsOrder'] = skillsOrder

    logger.debug('Pro Build parsed success')

    return proBuild

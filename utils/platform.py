def regionToPlatform(region):
    region = region.upper()

    if region == 'BR':
        return 'br1'
    elif region == 'EUNE':
        return 'eun1'
    elif region == 'EUW':
        return 'euw1'
    elif region == 'JP':
        return 'jp1'
    elif region == 'KR':
        return 'kr'
    elif region == 'LAN':
        return 'la1'
    elif region == 'LAS':
        return 'la2'
    elif region == 'NA':
        return 'na1'
    elif region == 'OCE':
        return 'oc1'
    elif region == 'RU':
        return 'ru'
    elif region == 'TR':
        return 'tr1'

def platformToRegion(platform):
    platform = platform.lower()

    if platform == 'br1':
        return 'BR'
    elif platform == 'eun1':
        return 'EUNE'
    elif platform == 'euw1':
        return 'EUW'
    elif platform == 'jp1':
        return 'JP'
    elif platform == 'kr':
        return 'KR'
    elif platform == 'la1':
        return 'LAN'
    elif platform == 'la2':
        return 'LAS'
    elif platform == 'na1':
        return 'NA'
    elif platform == 'oc1':
        return 'OCE'
    elif platform == 'ru':
        return 'RU'
    elif platform == 'tr1':
        return 'TR'

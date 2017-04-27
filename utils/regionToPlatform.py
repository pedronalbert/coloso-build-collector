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

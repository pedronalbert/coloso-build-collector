import logging

loggers = {}

def getLogger(region):
    region = region.upper()

    if region in loggers.keys():
        return loggers[region]

    logger = logging.getLogger(region)
    handler = logging.FileHandler('./logs/' + region + '.txt')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)

    loggers[region] = logger

    return logger

import logging, colorlog, os

logLevel = os.environ['COLOSO_COLLECTOR_LOG_LEVEL']
logging.basicConfig(level = getattr(logging, logLevel))

loggers = {}

def getLogger(region):
    region = region.upper()

    if region in loggers.keys():
        return loggers[region]

    logger = logging.getLogger(region)
    logger.propagate = False

    #configura handlers
    handler = logging.FileHandler('./logs/' + region + '.txt')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    chandler = colorlog.StreamHandler()
    chandler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(name)s\t| %(message)s'))

    logger.addHandler(handler)
    logger.addHandler(chandler)

    loggers[region] = logger

    return logger

import logging
from threading import Thread
from pick import pick

from src.collector import Collector
from models import mysql_db

mysql_db.connect()

logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
regions = ['NA', 'EUW', 'BR', 'OCE', 'KR']

logLevel, logLevelIndex = pick(logLevels, 'Log Level')
interval = float(input('Interval (segundos): '))

logging.basicConfig(level = getattr(logging, logLevel))

def initCollector(region):
    collector = Collector(region, interval, logLevel)
    collector.start()

for region in regions:
    Thread(target = initCollector, args=(region,)).start()

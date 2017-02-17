import logging, os
from threading import Thread

from src.collector import Collector
from models import mysql_db

mysql_db.connect()

regions = ['NA', 'EUW', 'BR', 'OCE', 'KR']

logLevel = os.environ['COLOSO_COLLECTOR_LOG_LEVEL']
interval = float(os.environ['COLOSO_COLLECTOR_INTERVAL_SECONDS'])

logging.basicConfig(level = getattr(logging, logLevel))

def initCollector(region):
    collector = Collector(region, interval, logLevel)
    collector.start()

for region in regions:
    Thread(target = initCollector, args=(region,)).start()

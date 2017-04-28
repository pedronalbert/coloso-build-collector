import os
from threading import Thread
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from src.collector import Collector
from models import mysql_db

mysql_db.connect()

regions = ['NA', 'EUW', 'BR', 'OCE', 'KR']

interval = float(os.environ['COLOSO_COLLECTOR_INTERVAL_SECONDS'])

def initCollector(region):
    collector = Collector(region, interval)
    collector.start()

for region in regions:
    Thread(target = initCollector, args=(region,)).start()

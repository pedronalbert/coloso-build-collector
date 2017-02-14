import os
from peewee import MySQLDatabase, Model
from playhouse.shortcuts import RetryOperationalError

class MyDB(RetryOperationalError, MySQLDatabase):
        pass

mysql_db = MyDB(host = 'db', user = 'coloso', passwd = os.environ['COLOSO_MYSQL_PASSWORD'], database='coloso')

class BaseModel(Model):
    class Meta:
        database = mysql_db

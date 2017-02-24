import os
from peewee import MySQLDatabase, Model
from playhouse.shortcuts import RetryOperationalError

class MyDB(RetryOperationalError, MySQLDatabase):
        pass

mysql_db = MyDB(host = os.environ['COLOSO_MYSQL_HOST'], user = os.environ['COLOSO_MYSQL_USER'], passwd = os.environ['COLOSO_MYSQL_PASSWORD'], database='coloso')

class BaseModel(Model):
    class Meta:
        database = mysql_db

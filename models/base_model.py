import os
from peewee import MySQLDatabase, Model, IntegerField, CharField, DateTimeField, TextField
from playhouse.shortcuts import RetryOperationalError

class MyDB(RetryOperationalError, MySQLDatabase):
        pass

mysql_db = MyDB(host = 'localhost', user = 'root', passwd = os.environ['COLOSO_DB_PASSWORD'], database='coloso')

class BaseModel(Model):
    class Meta:
        database = mysql_db

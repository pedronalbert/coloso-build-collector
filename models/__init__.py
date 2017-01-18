from peewee import MySQLDatabase, Model, IntegerField, CharField, DateTimeField, TextField

mysql_db = MySQLDatabase(host = 'localhost', user = 'root', passwd = '123456', database='cena_rails')

class BaseModel(Model):
    class Meta:
        database = mysql_db

class ProSummoner(BaseModel):
    id = IntegerField()
    summonerId = IntegerField()
    region = CharField()
    lastCheck = IntegerField()
    pro_player_id = IntegerField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    class Meta:
        db_table = 'pro_summoners'

class ProBuild(BaseModel):
    matchId = IntegerField()
    matchCreation = IntegerField()
    region = CharField()
    spell1Id = IntegerField()
    spell2Id = IntegerField()
    championId = IntegerField()
    highestAchievedSeasonTier = CharField()
    masteries = TextField()
    runes = TextField()
    stats = TextField()
    itemsOrder = TextField()
    skillsOrder = TextField()
    pro_summoner_id = IntegerField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        db_table = 'pro_builds'

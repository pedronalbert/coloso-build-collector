from .base_model import BaseModel
from peewee import CharField, IntegerField, DateTimeField, TextField

class ProBuild(BaseModel):
    gameId = CharField()
    seasonId = IntegerField()
    queueId = IntegerField()
    gameVersion = CharField()
    platformId = CharField()
    gameMode = CharField()
    mapId = IntegerField()
    gameType = CharField()
    gameDuration = IntegerField()
    gameCreation = IntegerField()
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

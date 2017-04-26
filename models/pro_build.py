from .base_model import BaseModel
from peewee import CharField, IntegerField, DateTimeField, TextField

class ProBuild(BaseModel):
    matchId = CharField()
    matchCreation = IntegerField()
    matchDuration = IntegerField()
    region = CharField()
    season = CharField()
    matchVersion = CharField()
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

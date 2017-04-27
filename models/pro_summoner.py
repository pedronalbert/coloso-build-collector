from .base_model import BaseModel
from peewee import IntegerField, DateTimeField, TextField

class ProSummoner(BaseModel):
    id = IntegerField()
    summonerId = TextField()
    accountId = TextField()
    lastCheck = IntegerField()
    pro_player_id = IntegerField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    class Meta:
        db_table = 'pro_summoners'

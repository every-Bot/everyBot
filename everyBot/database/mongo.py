from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Document, EmbeddedDocument, Instance, fields
from datetime import datetime

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_db_secrets(secret) -> str:
    with open('.secrets.json') as file:
        data = json.load(file)
        return data[secret]

db = AsyncIOMotorClient(fetch_db_secrets("db_uri"))
collection = db[fetch_db_secrets("db_name")]
instance = Instance(collection)

@instance.register
class Member(Document):
    class Meta:
        strict = False
    
    id = fields.IntegerField(attribute="_id")
    coins = fields.IntegerField(default=0)
    last_collected = fields.DateTimeField(default=datetime.min)

@instance.register
class Guild(Document):
    class Meta:
        strict = False

    id = fields.IntegerField(attribute="_id")
    guild_id = fields.IntegerField(required=True)
    # channels = fields.ListField(fields.IntegerField, default=list)
    prefix = fields.StringField(default=None)
    installed_modules = fields.ListField(fields.StringField, default=list)
    disabled_commands = fields.ListField(fields.StringField, default=list)

@instance.register
class MemberWarning(Document):
    id = fields.IntegerField(attribute="_id")
    member_id = fields.IntegerField(required=True)
    reason = fields.StringField(default=None)
    active = fields.BooleanField(default=True)
    date_issued = fields.DateTimeField(default=datetime.min)

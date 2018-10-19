# from peewee import *
from config import CONFIG
# import importlib
# vipdb = importlib.import_module("vdbs.vip-1.5")
from vdbs.vip_1_5 import *
# from datetime import datetime
# dbname = CONFIG['database.path'] + __version__

# db = SqliteDatabase(CONFIG['database.path'])
db.init(CONFIG['database.path'])

# class BaseModel(Model):
#     class Meta:
#         database = db


# class DownList(BaseModel):
#     raw = CharField()
#     thumb = CharField()
#     set = CharField()
#     uid = CharField()
#     source = CharField()
#     resize = BooleanField(default=True)
#     status = CharField(null=True)

# class SetList(BaseModel):
#     filename = CharField(unique=True)
#     keywords = CharField(null=True)

# class Bookmarks(BaseModel):
#     url = CharField()
#     set = CharField()
#     date = DateTimeField(default=datetime.now())

if not DownList.table_exists():
    # db.connect()
    db.create_tables([DownList, SetList])
    db.close()

if not SetList.table_exists():
    # db.connect()
    db.create_tables([SetList])
    db.close()




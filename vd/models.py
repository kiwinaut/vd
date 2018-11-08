from config import CONFIG
from vdbs.vip_1_5 import *
db.init(CONFIG['database.path'])


if not DownList.table_exists():
    # db.connect()
    db.create_tables([DownList, SetList])
    db.close()

if not SetList.table_exists():
    # db.connect()
    db.create_tables([SetList])
    db.close()




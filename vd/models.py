from config import CONFIG
from vdbs.vip_2_0 import *
db.init(CONFIG['database.path'])

if not Sets.table_exists():
    # db.connect()
    db.create_tables([Sets, Urls])
    # db.close()






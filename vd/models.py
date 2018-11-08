from config import CONFIG
from vdbs.vip_2_0 import *
db.init(CONFIG['database.path'])

if not Sets.table_exists():
    # db.connect()
    db.create_tables([Sets, Urls])
    # db.close()

def migrate():
    from vdbs.vip_1_5 import db as db_old
    from vdbs.vip_1_5 import DownList
    from urllib.parse import urlparse

    db_old.init('/home/soni/.cache/vip1.5.db')
    qu = DownList.select(DownList, fn.COUNT(DownList.id).alias('m_count')).order_by(DownList.id).group_by(DownList.uid).objects()
    for q in qu:
        srow = Sets.create(setname=q.set, count=int(q.m_count), done=0, host=urlparse(q.raw)[1])
        du = DownList.select().where(DownList.uid==q.uid)
        for d in du:
            Urls.create(raw=d.raw, thumb=d.thumb, resize=d.resize, set=srow)
        print(q.set)

# migrate()





from config import CONFIG
from gi.repository import Gtk, GObject
from models import Sets, Urls
from constants import Status

class SetModel(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, int, object, str, str, int, int, int, str)

    def load_sets(self):
        if CONFIG['filter']:
            qu = Sets.select().where(Sets.setname ** f"%{CONFIG['filter']}%")
        else:
            qu = Sets.select()
            
        for i, q in enumerate(qu, start=1):
            self.append((q.id, Status.SLEEP, q.setname, q.host, q.done, q.count, i, q.error))

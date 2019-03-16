from gi.repository import GObject
import threading
from vip_tools.downloader import Downloader2
from vip_tools.solver import VLink
from vip_tools.saver import FileSaver
from queue import Queue
# from collections import deque
# import time
from models import Sets, Urls
from constants import Status
from resources import set_model, info
from config import CONFIG
import shutil


def idle_add(func):
    def callback(*args):
        GObject.idle_add(func, *args)
    return callback

# class VLink:
#     def __init__(self, id, raw, set, source, resize=True):
#         self.id = id
#         self.raw = raw
#         self.source = source
#         self.set = set
#         self.resize = resize
#         self.host = 'None.com'
#         # self.img_url = 'www.solved.com'

#     @property
#     def img_url(self):
#         time.sleep(0.1)
#         return 'www.solved.com'

# class Downloader:
#     """docstring for Downloader"""
#     def __init__(self, viplink, *streams):
#         self.vl = viplink
#         self.streams = streams

#     def download(self, cb=None):
#         total = 100000
#         cur = 0
#         for i in range(40):
#             cur += 8000
#             if cb:
#                 cb(cur, total)
#             time.sleep(0.1)

_sentinel = object()

class Pool:
    def __init__(self):
        self.que = Queue()
        self.threads = []
        self.max = 4
        info.worker_count = self.max
        # self.sc = SpeedChecker()

    def set_worker_limit(self, value):
        self.max = value
        self.init_workers()

    def play(self):
        self.init_workers()
        info.set_status('running') 

    def que_clean(self):
        self.pause()
        self.que = Queue()
        # self.sc.kill()

    def pause(self):
        for t in self.threads:
            t.running = False
        # self.sc.kill()
        self.threads = []
        info.set_status('paused') 

    def init_workers(self):
        self.threads = [t for t in self.threads if t.is_alive()]
        if self.que.empty():
            return
        else:
            count = self.max - len(self.threads)
            if count > 0:
                for i in range(count):
                    t = Worker(self.que)
                    self.threads.append(t)
                    t.start()
                # self.sc.start(self.threads)
            elif count < 0:
                for n in range(abs(count)):
                    t = self.threads.pop()
                    t.running = False
            else:
                return
        info.worker_count = len(self.threads)

    def append_from_id(self, id, set_iter):
        qu = Urls.select(Urls, Sets).join(Sets).where(Urls.set_id==id).dicts()
        for q in qu:
            # print(q)
            self.que.put((q, set_iter,))
        info.que_len += self.que.qsize()


class SpeedChecker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.running = True

    def run(self, threads):
        self.running = True
        while self.running:
            time.sleep(1)
            summ = sum([t.bps for t in threads])
            avg = summ // len(threads)

    def kill(self):
        self.running = False

class Worker(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que
        self.running = True
        self.spath = CONFIG['save_location']
        self.bps = 0


    def run(self):
        get = self.que.get
        while self.running and not self.que.empty():
            # {'id': 300, 'raw': '', 'thumb': None, 'resize': True, 'status': None, 'set': 5, 'setname': '', 'keywords': None, 'done': 0, 'count': 60, 'host': ''}

            t = get()
            # @idle_add
            # def step1():
            #     downmodel[self.pr_iter][1] = Status.SOLVING
            # self.step1()

            set_iter = t[1] #careful coming arguments with get!
            row = t[0]
            # print(row)
            try:
                vlink = VLink(row['id'], row['raw'], row['setname'], None, row['resize'])
                _ = vlink.img_url

                self.step2(set_iter)

                saver = FileSaver(vlink, self.spath)

                @idle_add
                def progress(bps):
                    pass
                    # print(f"{bps//1000}kB/s")

                d = Downloader2(vlink, saver)
                d.download(progress)

                self.finish(set_iter, row, saver.tarpath)

            except Exception as e:
                print(threading.current_thread(), e)
                @idle_add
                def steperr(row, set_iter, e):
                    # set_model[set_iter][1] = Status.ERROR #active
                    set_model[set_iter][7] += 1
                    Sets.update(error=set_model[set_iter][7]).where(Sets.id==row['set']).execute()
                    Urls.update(status=str(e)).where(Urls.id==row['id']).execute()
                steperr(row, set_iter, e)
                continue
        # end
        # @idle_add
        # def end():
        #     downmodel.remove(self.pr_iter)
        # end()

    # @idle_add
    # def step1(self):
    #     downmodel[self.pr_iter][1] = Status.SOLVING

    @idle_add
    def step2(self, set_iter):
         set_model[set_iter][1] = Status.ACTIVE #active

    # finish
    @idle_add
    def finish(self, set_iter, row, tarpath):
        set_model[set_iter][4] += 1
        count = set_model[set_iter][5]
        done = set_model[set_iter][4]
        Sets.update(done=done).where(Sets.id==row['set']).execute()
        if done == count:
            set_model.remove(set_iter)
            # move file
            shutil.move(tarpath, CONFIG['complete_path'])
            # clean set in db 
            Sets.delete().where(Sets.id==row['set']).execute()
            # register archive database?
        Urls.delete().where(Urls.id==row['id']).execute()


from gi.repository import GObject
import threading
from vip_tools.downloader import Downloader
from vip_tools.solver import VLink
from vip_tools.saver import FileSaver
from queue import Queue
# from collections import deque
# import time
from models import DownList
from constants import Status
from resources import set_model, downmodel

def idle_add(func):
    def callback(*args):
        GObject.idle_add(func, *args)
    return callback

# class VLink:
#     def __init__(self, raw, set, source, resize=True):
#         self.raw = raw
#         self.source = source
#         self.set = set
#         self.resize = resize
#         self.host = 'None.com'
#         # self.img_url = 'www.solved.com'

#     @property
#     def img_url(self):
#         time.sleep(1)
#         return 'www.solved.com'

# class Downloader:
#     """docstring for Downloader"""
#     def __init__(self, viplink, *streams):
#         self.vl = viplink
#         self.streams = streams

#     def download(self, cb=None):
#         total = 400000
#         cur = 0
#         for i in range(40):
#             cur += 8000
#             cb(cur, total)
#             time.sleep(0.1)

# _sentinel = object()

class Pool:
    def __init__(self):
        self.que = Queue()
        self.threads = []
        self.max = 4

    def set_worker_limit(self, value):
        self.max = value
        self.init_workers()

    def play(self):
        self.init_workers()

    def pause(self):
        for t in self.threads:
            t.running = False
        self.threads = []

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
            elif count < 0:
                for n in range(abs(count)):
                    t = self.threads.pop()
                    t.running = False
            else:
                return


    def append_from_uid(self, uid, set_iter):
        qu = DownList.select().where(DownList.uid==uid)
        for q in qu:
            self.que.put((q.id, q.raw, q.set, q.resize, set_iter,))


class Worker(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que
        self.running = True
        self.pr_iter = downmodel.append((None, Status.SLEEP, None, None, "", ""))


    def run(self):
        get = self.que.get
        while self.running and not self.que.empty():
            row = get()
            # @idle_add
            # def step1():
            #     downmodel[self.pr_iter][1] = Status.SOLVING
            self.step1()

            set_iter = row[4] #careful coming arguments with get!
            try:
                vlink = VLink(*row)
                _ = vlink.img_url
                # raise Exception('dsd')

                self.step2(row, vlink)

                saver = FileSaver(vlink)

                @idle_add
                def progress(current, total):
                    downmodel[self.pr_iter][2] = current * 100 // total
                    downmodel[self.pr_iter][3] = total

                d = Downloader(vlink, saver)
                d.download(progress)

                self.finish(set_iter, row[0])

            except Exception as e:
                print(threading.current_thread(), e)
                @idle_add
                def step2(row, set_iter, e):
                    downmodel[self.pr_iter][1] = Status.ERROR
                    set_model[set_iter][1] = Status.ERROR #active
                    DownList.update(status=str(e)).where(DownList.id==row[0]).execute()
                step2(row, set_iter, e)
                continue
        # end
        @idle_add
        def end():
            downmodel.remove(self.pr_iter)
        end()

    @idle_add
    def step1(self):
        downmodel[self.pr_iter][1] = Status.SOLVING

    @idle_add
    def step2(self, row, vlink):
        downmodel[self.pr_iter][1] = Status.DOWNLOAD
        downmodel[self.pr_iter][5] = vlink.host
        downmodel[self.pr_iter][4] = vlink.set
        downmodel[self.pr_iter][0] = row[0]
        set_iter = row[4]
        set_model[set_iter][1] = Status.ACTIVE #active

    # finish
    @idle_add
    def finish(self, set_iter, id):
        count = set_model[set_iter][2]
        # self.set_model[set_iter][1] = 0 #active
        count -= 1
        if count <= 0:
            set_model.remove(set_iter)
        else:
            set_model[set_iter][2] = count
        DownList.delete().where(DownList.id==id).execute()


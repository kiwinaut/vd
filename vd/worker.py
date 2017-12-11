from gi.repository import GObject
import threading
# from vip_tools.downloader import Downloader
# from vip_tools.solver import VLink
from vip_tools.saver import FileSaver
from queue import Queue
from collections import deque
from print_pretty import pretty_size
import time
from models import DownList, fn
from constants import Status

def idle_add(func):
    def callback(*args):
        GObject.idle_add(func, *args)
    return callback

class VLink:
    def __init__(self, raw, set, source, resize=True):
        self.raw = raw
        self.source = source
        self.set = set
        self.resize = resize
        self.host = 'None.com'
        # self.img_url = 'www.solved.com'

    @property
    def img_url(self):
        time.sleep(1)
        return 'www.solved.com'

class Downloader:
    """docstring for Downloader"""
    def __init__(self, viplink, *streams):
        self.vl = viplink
        self.streams = streams

    def download(self, cb=None):
        total = 400000
        cur = 0
        for i in range(40):
            cur += 8000
            cb(cur, total)
            time.sleep(0.1)

_sentinel = object()

class Pool:
    def __init__(self, pmodel, smodel):
        self.que = Queue()
        self.threads = []
        self.max = 4

        self.p_model = pmodel
        self.s_model = smodel

    def set_worker_limit(self, value):
        for t in self.threads:
            t.running = False
        self.max = value
        self.init_workers()

    def play(self):
        self.init_workers()

    def pause(self):
        if self.que.empty():
            for i in range(self.max):
                self.que.put(_sentinel)
            return
        else:
            for t in self.threads:
                t.running = False

    def init_workers(self):
        if not self.que.empty():
            for i in range(self.max):
                p_iter = self.p_model.append((None, Status.DOWNLOAD, None, None, "", ""))
                t = Worker(self.que, self.s_model, self.p_model, p_iter)
                self.threads.append(t)
                t.start()

    def append_from_uid(self, uid, set_iter):
        qu = DownList.select().where(DownList.uid==uid)
        for q in qu:
            self.que.put((q.id, q.raw, q.set, q.resize, set_iter,))


class Worker(threading.Thread):
    def __init__(self, que, set_model, pr_model, pr_iter):
        threading.Thread.__init__(self)
        self.que = que
        self.running = True
        self.set_model = set_model
        self.pr_model = pr_model
        self.pr_iter = pr_iter


    def run(self):
        get = self.que.get
        while self.running and not self.que.empty():
            row = get()
            # if row is _sentinel:
            #     # self.que.put((_sentinel, None,))
            #     break
            @idle_add
            def step1():
                self.pr_model[self.pr_iter][1] = Status.SOLVING
            step1()

            vlink = VLink(*row[1:])
            _ = vlink.img_url
            set_iter = row[4] #careful coming arguments with get!

            @idle_add
            def start(row, set_iter):
                self.pr_model[self.pr_iter][1] = Status.DOWNLOAD
                self.pr_model[self.pr_iter][5] = vlink.host
                self.pr_model[self.pr_iter][4] = vlink.set
                self.pr_model[self.pr_iter][0] = row[0]
                self.set_model[set_iter][1] = Status.ACTIVE #active
            start(row, set_iter)

            saver = FileSaver(vlink)

            @idle_add
            def progress(current, total):
                self.pr_model[self.pr_iter][2] = current * 100 // total
                self.pr_model[self.pr_iter][3] = total

            d = Downloader(vlink, saver)
            d.download(progress)

            # finish
            @idle_add
            def finish(set_iter):
                count = self.set_model[set_iter][2]
                # self.set_model[set_iter][1] = 0 #active
                count -= 1
                if count <= 0:
                    self.set_model.remove(set_iter)
                else:
                    self.set_model[set_iter][2] = count
            finish(set_iter)

        # end
        @idle_add
        def end():
            self.pr_model.remove(self.pr_iter)
        end()

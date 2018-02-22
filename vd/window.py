from gi.repository import Gtk, GObject, Gdk
from models import DownList, fn
import views
from worker import Pool
from constants import Status
from resources import set_model, downmodel
from config import CONFIG
from urllib.parse import urlparse






class Window(Gtk.Window):
    # __gsignals__ = {
    #   'scope-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }
    def __init__(self):
        Gtk.Window.__init__(self, title="VD", gravity=1)
        # self.set_border_width(0)
        self.set_default_size(500, 900)
        self.connect("delete-event", self.on_window_delete_event)

        box = Gtk.Box.new(orientation=1, spacing=2)
        box.set_property('margin',2)
        self.add(box)

        downview = views.ProgWindow()

        downview.set_model(downmodel)

        downscroll = Gtk.ScrolledWindow()
        downscroll.set_shadow_type(1)
        downscroll.add(downview)
        downscroll.set_size_request(-1, 160)

        box.pack_start(downscroll, False, True, 0)



        set_menu = Gtk.Menu()

        set_view = views.SetWindow(menu=set_menu)

        item = Gtk.MenuItem.new_with_label('Append')
        item.connect('activate', self.on_set_append_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Peek')
        item.connect('activate', self.on_set_peek_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Go to Source')
        # item.connect('activate', self.on_set_peek_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Delete')
        item.connect('activate', self.on_set_delete_activated, set_view)
        set_menu.append(item)

        set_menu.show_all()

        set_view.set_model(set_model)

        set_scroll = Gtk.ScrolledWindow()
        set_scroll.add(set_view)
        set_scroll.set_shadow_type(1)

        butbox = Gtk.Box.new(orientation=0, spacing=0)
        butbox.get_style_context().add_class("linked")

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.pack_start(butbox)
        self.set_titlebar(header)
        img = Gtk.Image.new_from_icon_name('media-playback-start-symbolic', 2)
        but = Gtk.Button(image=img)
        but.connect('clicked', self.on_play_clicked)
        butbox.pack_start(but, False, False, 0)
        img = Gtk.Image.new_from_icon_name('media-playback-pause-symbolic', 2)
        but = Gtk.Button(image=img)
        but.connect('clicked', self.on_pause_clicked)
        butbox.pack_start(but, False, False, 0)

        but = Gtk.SpinButton.new_with_range(1, 20, 1)
        but.set_value(CONFIG['worker_count'])
        but.connect('value-changed', self.on_limit_changed)
        butbox.pack_start(but, False, False, 0)


        box.pack_start(set_scroll, True, True, 0)

        self.init_sets(set_model)

        self.p = Pool()

        self.show_all()

    def on_limit_changed(self, widget):
        value = widget.get_value_as_int()
        self.p.set_worker_limit(value)

    def on_play_clicked(self, widget):
        self.p.play()

    def on_pause_clicked(self, widget):
        self.p.pause()

    def on_set_append_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            uid = model[iter][5]
            model[iter][1] = Status.QUEUED
            self.p.append_from_uid(uid, iter)

    def on_set_peek_activated(self, widget, view):
        pass

    def on_set_delete_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            uid = model[iter][5]
            DownList.delete().where(DownList.uid==uid).execute()
            model.remove(iter)

    def init_sets(self, model):
        i = 1
        qu = DownList.select(DownList, fn.COUNT(DownList.id).alias('m_count')).order_by(DownList.id).group_by(DownList.uid).naive()
        for q in qu:
            host = urlparse(q.raw)[1]
            model.append((i, Status.SLEEP, q.m_count, q.set, host, q.uid))
            i += 1


    def on_window_delete_event(self, widget, event):
        Gtk.main_quit()
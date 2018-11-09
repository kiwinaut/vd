from gi.repository import Gtk, Gio
from models import Sets, Urls
import views
from worker import Pool
from constants import Status
from resources import set_model#, filter_model
from config import CONFIG
# from urllib.parse import urlparse
from urllib import request
from vip_tools.headers import firefox
from gi.repository.GdkPixbuf import Pixbuf 




class Window(Gtk.Window):
    # __gsignals__ = {
    #   'scope-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }
    def __init__(self):
        Gtk.Window.__init__(self, title="VD", gravity=1)
        # self.set_border_width(0)
        self.set_default_size(750, 500)
        self.connect("delete-event", self.on_window_delete_event)

        box = Gtk.Box.new(orientation=1, spacing=0)
        # box.set_property('margin',2)
        self.add(box)

        # downview = views.ProgWindow()

        # downview.set_model(downmodel)

        # downscroll = Gtk.ScrolledWindow()
        # downscroll.set_shadow_type(1)
        # downscroll.add(downview)
        # downscroll.set_size_request(-1, 160)

        # box.pack_start(downscroll, False, True, 0)



        set_menu = Gtk.Menu()

        set_view = views.SetWindow(menu=set_menu)

        item = Gtk.MenuItem.new_with_label('Append')
        item.connect('activate', self.on_set_append_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Peek')
        item.connect('activate', self.on_set_peek_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Copy Sample Url')
        item.connect('activate', self.on_csu_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Go to Source')
        # item.connect('activate', self.on_set_peek_activated, set_view)
        set_menu.append(item)
        item = Gtk.MenuItem.new_with_label('Delete')
        item.connect('activate', self.on_set_delete_activated, set_view)
        set_menu.append(item)

        set_menu.show_all()

        # filter_model.set_visible_func(self.filter_func)
        # self.filter_text = None
        set_view.set_model(set_model)
        set_view.connect('row-activated', self.on_row_activated)
        # entry = set_view.get_search_entry()
        # entry.connect('activate', self.filter_activated)


        set_scroll = Gtk.ScrolledWindow()
        set_scroll.set_overlay_scrolling(False)
        set_scroll.add(set_view)
        # set_scroll.set_shadow_type(1)

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

        img = Gtk.Image.new_from_icon_name('edit-clear-all-symbolic', 2)
        but = Gtk.Button(image=img)
        but.connect('clicked', self.on_que_clean_clicked)
        butbox.pack_start(but, False, False, 0)

        box.pack_start(set_scroll, True, True, 0)

        self.init_sets(set_model)

        self.p = Pool()
        # self.thumb_view = ThumbPopOver(self)


        self.show_all()

    def on_limit_changed(self, widget):
        value = widget.get_value_as_int()
        self.p.set_worker_limit(value)

    def on_play_clicked(self, widget):
        self.p.play()

    def on_pause_clicked(self, widget):
        self.p.pause()

    def on_que_clean_clicked(self, widget):
        self.p.que_clean()
        #clean status

    def on_set_append_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            id = model[iter][0]
            model[iter][1] = Status.QUEUED
            self.p.append_from_id(id, iter)

    def on_set_peek_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            uid = model[iter][5]
            model[iter][1] = Status.QUEUED
            self.p.append_from_uid(uid, iter, peek=True)

    def on_csu_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        raws = ''
        for path in paths:
            iter = model.get_iter(path)
            raw = model[iter][6]
            print(raw)
            raws += raw
        #TODO copy to clipboard

    def on_set_delete_activated(self, widget, view):
        selection = view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            id = model[iter][0]
            Sets.delete().where(Sets.id==id).execute()
            Urls.delete().where(Urls.set_id==id).execute()
            model.remove(iter)


    def on_row_activated(self, tree_view, path, column):
            model = tree_view.get_model()
            iter = model.get_iter(path)
            id = model[iter][0]
            qu = Urls.select(Urls.thumb).where(Urls.set_id==id).limit(3)
            for q in qu:
                popover = tree_view.thumb_view
                # self.on_get_screenshot(tree_view, model, iter)
                rect = tree_view.get_background_area(path, column)
                rect.y = rect.y + 24
                popover.set_pointing_to(rect)
                #
                req = request.Request(q.thumb, headers=firefox)
                response = request.urlopen(req)
                input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None) 
                pixbuf = Pixbuf.new_from_stream(input_stream, None)
                #
                popover.add_image(pixbuf, id)
                popover.popup()

    def init_sets(self, model):
        # model.append((1, Status.SLEEP, 'Fashion-Land Mika Fashion Model Set 110 (x159 cover)',  'imx.to', 'q.thumb', 10, 45))
        # model.append((1, Status.SLEEP, 'Fashion-Land Mika Fashion Model Set 110 (x159 cover)',  'imx.to', 'q.thumb', 45, 45))
        # i = 1
        qu = Sets.select()
        # qu = DownList.select(DownList, fn.COUNT(DownList.id).alias('m_count')).order_by(DownList.id).group_by(DownList.uid).objects()
        for q in qu:
            # host = urlparse(q.raw)[1]
            model.append((q.id, Status.SLEEP, q.setname, q.host, q.done, q.count))
            # i += 1


    def on_window_delete_event(self, widget, event):
        Gtk.main_quit()

    def filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.filter_text is None:
            return True
        else:
            return self.filter_text in model[iter][2]


    def filter_activated(self, widget):
        text = widget.get_text()
        print(text)

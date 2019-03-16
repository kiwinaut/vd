from gi.repository import Gtk, GObject, Gdk
from constants import Status
import resources
from print_pretty.pretty_size import psize

# from gi.repository.GdkPixbuf import Pixbuf 
# from gi.repository import Gio 

color_red= Gdk.RGBA(red=1.0, green=0.0, blue=0.0, alpha=1.0)
color_green= Gdk.RGBA(red=0.0, green=1.0, blue=0.0, alpha=1.0)
color_yellow= Gdk.RGBA(red=1.0, green=1.0, blue=0.0, alpha=1.0)
color_orange= Gdk.RGBA(red=1.0, green=0.537, blue=0.0, alpha=1.0)
color_grey= Gdk.RGBA(red=0.5, green=0.5, blue=0.5, alpha=1.0)
color_black= Gdk.RGBA(red=0, green=0, blue=0, alpha=1.0)

def status_size_data_func(tree_column, cell, tree_model, iter, data):
    size = tree_model[iter][3]
    cell.set_property('text', psize(size))
    
def error_set_data_func(tree_column, cell, tree_model, iter, data):
    error = tree_model[iter][7]
    if error > 0:
        cell.set_property('foreground-rgba', color_red)
    else:
        cell.set_property('foreground-rgba', None)

    
def status_set_data_func(tree_column, cell, tree_model, iter, data):
    status = tree_model[iter][1]
    # set = tree_model[iter][2]
    # cell.set_property('text', tree_model[iter][2])
    if status == Status.ACTIVE:
        cell.set_property('cell-background-rgba', color_green)
    elif status == Status.SLEEP:
        cell.set_property('cell-background-rgba', None)
    elif status == Status.QUEUED:
        cell.set_property('cell-background-rgba', color_orange)
    elif status == Status.ERROR:
        cell.set_property('cell-background-rgba', color_red)

    
def status_cell_data_func(tree_column, cell, tree_model, iter, data):
    status = tree_model[iter][1]
    if status == Status.ACTIVE:
        cell.set_property('pixbuf', resources.active_pixbuf)
    elif status == Status.SLEEP:
        cell.set_property('pixbuf', None)
    elif status == Status.QUEUED:
        cell.set_property('pixbuf', resources.queued_pixbuf)
    elif status == Status.SOLVING:
        cell.set_property('pixbuf', resources.solving)
    elif status == Status.DOWNLOAD:
        cell.set_property('pixbuf', resources.download_pixbuf)
    elif status == Status.ERROR:
        cell.set_property('pixbuf', resources.error)

def progress_text_cell_data_func(tree_column, cell, tree_model, iter, data):
    done = tree_model[iter][4]
    total = tree_model[iter][5]
    value = done*100//total
    # cell.set_property('text', f'{done}/{total}  {value}%')
    cell.set_property('text', f'{done}/{total}')
    cell.set_property('value', value)


class ThumbPopOver(Gtk.Popover):
    def __init__(self, widget):
        Gtk.Popover.__init__(self)
        self.set_relative_to(widget)
        # self.set_pointing_to(rect)

        self.set_position(Gtk.PositionType.LEFT)

        # self.i1 = Gtk.Image()
        # self.i2 = Gtk.Image()
        box = Gtk.Box.new(orientation=0, spacing=0)
        self.add(box)
        self.last_id = None
        # img.show_all()

    def set_image(self, pixbuf):
        self.get_child().set_from_pixbuf(pixbuf)

    def add_image(self, pixbuf, id):
        box = self.get_child()
        if id != self.last_id:
            def cb(w,d):
                box.remove(w)
            box.foreach(cb,None)
        self.last_id = id
        img = Gtk.Image()
        img.set_from_pixbuf(pixbuf)
        box.pack_start(img, False, False, 0)
        box.show_all()


class ProgWindow(Gtk.TreeView):
    # __gsignals__ = {
    #   'scope-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }
    def __init__(self):
        Gtk.TreeView.__init__(self)

        self.get_selection().set_mode(0)
        # downview.set_rubber_banding(True)
        self.set_property('headers-visible', False)

        column = Gtk.TreeViewColumn('id')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 0)
        self.append_column(column)

        column = Gtk.TreeViewColumn('status')
        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, status_cell_data_func, func_data=None)
        self.append_column(column)

        column = Gtk.TreeViewColumn('progress')
        column.set_fixed_width(120)
        renderer = Gtk.CellRendererProgress()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'value', 2)
        self.append_column(column)

        column = Gtk.TreeViewColumn('size')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, status_size_data_func, func_data=None)
        # column.add_attribute(renderer, 'text', 3)
        self.append_column(column)

        column = Gtk.TreeViewColumn('host')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 5)
        self.append_column(column)

        column = Gtk.TreeViewColumn('err')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 6)
        self.append_column(column)

        column = Gtk.TreeViewColumn('set')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 4)
        self.append_column(column)


class SetWindow(Gtk.TreeView):
    # __gsignals__ = {
    #   'scope-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }
    def __init__(self, menu):
        Gtk.TreeView.__init__(self, has_tooltip=True)
        # self.connect('query-tooltip', self.on_tooltip_queried)

        self.menu = menu

        self.get_selection().set_mode(3)
        self.set_rubber_banding(True)
        # self.set_property('headers-visible', False)


        column = Gtk.TreeViewColumn('id')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 6)
        self.append_column(column)

        column = Gtk.TreeViewColumn('set')
        column.set_fixed_width(450)
        column.set_resizable(True)
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 2)
        column.set_cell_data_func(renderer, status_set_data_func, func_data=None)
        self.append_column(column)

        # column = Gtk.TreeViewColumn('status')
        # renderer = Gtk.CellRendererPixbuf()
        # column.pack_start(renderer, False)
        # # column.add_attribute(renderer, 'text', 1)
        # column.set_cell_data_func(renderer, status_cell_data_func, func_data=None)
        # self.append_column(column)


        column = Gtk.TreeViewColumn('host')
        # column.set_fixed_width(100)
        column.set_resizable(True)
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 3)
        self.append_column(column)

        column = Gtk.TreeViewColumn('error')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', 7)
        column.set_cell_data_func(renderer, error_set_data_func, func_data=None)
        self.append_column(column)

        column = Gtk.TreeViewColumn('progress')
        # column.set_fixed_width(120)
        renderer = Gtk.CellRendererProgress()
        column.pack_start(renderer, False)
        # column.add_attribute(renderer, 'value', 2)
        # column.add_attribute(renderer, 'text', 2)
        column.set_cell_data_func(renderer, progress_text_cell_data_func, func_data=None)
        self.append_column(column)

        self.thumb_view = ThumbPopOver(self)
        # self.connect('row-activated', self.on_row_activated)



    def do_button_press_event(self, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            selection = self.get_selection()
            pos = self.get_path_at_pos(event.x, event.y)# path, column, cell_x, cell_y
            if pos:
                #clicked any content
                path, column, cell_x, cell_y = pos
                if selection.path_is_selected(path):
                    #clicked in selection
                    self.menu.popup(None, None, None, None, event.button, event.time)
                else:
                    #clicked outside of selection
                    Gtk.TreeView.do_button_press_event(self, event)
                    self.menu.popup(None, None, None, None, event.button, event.time)
            else:
                #clicked empty area
                selection.unselect_all()
                return False
        else:
            Gtk.TreeView.do_button_press_event(self, event)


    def on_tooltip_queried(self, widget, x, y, keyboard_mode, tooltip):
        values = self.get_path_at_pos(x,y)
        if values:
            path, column, cell_x, cell_y = values
            # if column.position == StoreMainPosition.THUMB:
            model = self.get_model()
            iter = model.get_iter(path)
            thumb_url = model[iter][7]
            if thumb_url:
                print(thumb_url)
                req = request.Request(thumb_url, headers=firefox)
                response = request.urlopen(req)
                input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None) 
                pixbuf = Pixbuf.new_from_stream(input_stream, None)
                tooltip.set_icon(pixbuf)
                return True

    # def on_row_activated(self, tree_view, path, column):
    #         model = tree_view.get_model()
    #         iter = model.get_iter(path)
    #         thumb_url = model[iter][7]
    #         if thumb_url:
    #             popover = self.thumb_view
    #             # self.on_get_screenshot(tree_view, model, iter)
    #             rect = self.get_background_area(path, column)
    #             rect.y = rect.y + 8
    #             popover.set_pointing_to(rect)
    #             #
    #             req = request.Request(thumb_url, headers=firefox)
    #             response = request.urlopen(req)
    #             input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None) 
    #             pixbuf = Pixbuf.new_from_stream(input_stream, None)
    #             #
    #             popover.set_image(pixbuf)
    #             popover.popup()

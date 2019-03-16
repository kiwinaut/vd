from gi.repository import GdkPixbuf, Gtk, GObject

# icon_theme = Gtk.IconTheme.get_default()

# queued_pixbuf = icon_theme.load_icon('appointment-soon', 16, Gtk.IconLookupFlags.USE_BUILTIN)
# active_pixbuf = icon_theme.load_icon('media-playback-start', 16, Gtk.IconLookupFlags.USE_BUILTIN)
# download_pixbuf = icon_theme.load_icon('emblem-downloads', 16, Gtk.IconLookupFlags.USE_BUILTIN)
# solving = icon_theme.load_icon('document-open-recent', 16, Gtk.IconLookupFlags.USE_BUILTIN)
# error = icon_theme.load_icon('emblem-important', 16, Gtk.IconLookupFlags.USE_BUILTIN)

# queued_pixbuf = GdkPixbuf.Pixbuf.new_from_file('appointment-soon', 2)
# active_pixbuf = GdkPixbuf.Pixbuf.new_from_file('media-playback-start', 2)
# download_pixbuf = GdkPixbuf.Pixbuf.new_from_file('emblem-downloads', 2)
# solving = GdkPixbuf.Pixbuf.new_from_file('emblem-downloads', 2)
# tag_pixbuf = GdkPixbuf.Pixbuf.new_from_file('resources/pix/emblem-generic.png')
# search_pixbuf = GdkPixbuf.Pixbuf.new_from_file('/usr/share/icons/Adwaita/16x16/places/folder-saved-search.png')

set_model = Gtk.ListStore(int, object, str, str, int, int, int, int)
# filter_model = set_model.filter_new()
# downmodel = Gtk.ListStore(int, object, int, GObject.TYPE_UINT64, str, str)
# id, status, percentage, size, set,host

# from viewmodels import UrlModel
# set_model = UrlModel()
	
class InfoModel(GObject.GObject):
    worker_count = GObject.Property(type=int)
    status = GObject.Property(type=str)
    que_len = GObject.Property(type=int)
    total_download = GObject.Property(type=int)


    def __init__(self):
        GObject.GObject.__init__(self)

    def set_status(self, value):
        self.status = value

info = InfoModel()

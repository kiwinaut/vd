import gi
gi.require_version('Gtk', '3.0')

from config import CONFIG
CONFIG.parse()

from gi.repository import Gtk
from window import Window

if __name__ == '__main__':
	Window()
	Gtk.main()
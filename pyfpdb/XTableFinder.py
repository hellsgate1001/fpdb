import gtk
import gtk.gdk as gdk
import gobject
import pygtk
import wnck

if gtk.pygtk_version < (2,0):
  print "PyGtk 2.0 is required."
  raise SystemExit

# Connect the signal handler to the single global root (screen)
root = wnck.screen_get_default()

class TableFinder(gtk.Dialog):
  """
  TableFinder

  Asks the user to click on a table window, then waits for them click
  the mouse. When the mouse is released, returns the toplevel
  window under the pointer if there is only one window at that spot,
  or prompts the user with all the windows at that spot (we don't know the
  z-order for the windows...), or NULL, if there is none.

  """

  def __init__(self, prompt, search_title):
    gtk.Window.__init__(self, gtk.WINDOW_POPUP)
    self.set_title("Table Finder")
    self.set_border_width(0)
    self.set_screen(gtk.gdk.get_default_root_window().get_screen())
    self.set_position(gtk.WIN_POS_CENTER)
    #self.set_keep_above(True)

    label = gtk.Label(prompt)
    label.set_padding(10, 10)
    self.vbox.pack_start(label, True, True, 0)
    label.show()

    self.cursors = {}
    pbuf = gdk.pixbuf_new_from_file("../gfx/search.png")
    self.cursors['search'] = gdk.Cursor(self.get_display(), pbuf, 6, 6);
    self.search_title = search_title
    hwnd = None

    self.show_all()
    self.mouse_clicked = False
    self.pointer_position = {}
    self.grabbed = False

  def run(self):
    global mouse_clicked
    global pointer_position

    self.display = self.get_display()
    cursor = gtk.gdk.Cursor(self.display, gtk.gdk.CROSSHAIR)
    
    main_context = gobject.main_context_default()

    self.mouse_clicked = False
    self.pointer_position = {}
      
    if (gdk.pointer_grab(self.window, True, gdk.BUTTON_RELEASE_MASK,
                         None, self.cursors['search'], 0L) == gtk.gdk.GRAB_SUCCESS):
      self.connect("button_release_event", self.button_release_event_cb)
      self.grabbed = True

      # Process events until clicked is set by button_release_event_cb.
      # We pass in may_block=True since we want to wait if there
      # are no events currently.
      #
      while self.mouse_clicked is False:
        gtk.main_iteration(False) #main_context.iteration(True)
    self.destroy()
    gtk.gdk.flush()     # Really release the grab
          
    toplevel = self.find_window_at_position(self.pointer_position)
    if (toplevel == self):
      toplevel = None;
    return toplevel

  def close(self, widget, event, data=None):
    self.closed = True
    return False

  def find_window_at_position(self, pointer_position):
    """ Find the window at position x,y """

    self.hwnd = None
    self.dia = gtk.Window(gtk.WINDOW_POPUP)
    self.dia.connect("delete_event", self.close)
    self.dia.set_title("Choose the poker table window")
    self.dia.set_border_width(0)
    self.dia.set_position(gtk.WIN_POS_CENTER)
    
    box1 = gtk.VBox(False, 0)
    self.dia.add(box1)
    box1.show()

    radio_box = gtk.VBox(False, 10)
    radio_box.set_border_width(10)
    box1.pack_start(radio_box, True, True, 0)
    radio_box.show()

    first = True
    count = 0
    wins = root.get_windows()
    for win in wins:
      ws = win.get_workspace()
      if ws is not None:
        if win.get_window_type() == wnck.WINDOW_NORMAL and \
              win.is_visible_on_workspace(ws):
            w_title = win.get_name()
            wx,wy,ww,wh = win.get_geometry()
            x,y = pointer_position
            if x >= wx and x <= wx+ww and y >= wy and y <= wy+wh:
              if first:
                button = gtk.RadioButton(None, w_title)
                button.connect("toggled", self.pick_table_window, win)
                button.set_active(True)
                self.w_table_w = win
                self.hwnd = win.get_xid()
                self.table_window_name = win.get_name()
                radio_box.pack_start(button, True, True, 0)
                button.show()
                first = False
              else:
                button = gtk.RadioButton(button, w_title)
                button.connect("toggled", self.pick_table_window, win)
                radio_box.pack_start(button, True, True, 0)
                button.show()
              count = count + 1
    if count == 1:
      # there is only one window at this spot, use it
      self.dia.destroy()
      return self.hwnd

    separator = gtk.HSeparator()
    box1.pack_start(separator, False, True, 0)
    separator.show()

    box2 = gtk.VBox(False, 10)
    box2.set_border_width(10)
    box1.pack_start(box2, False, True, 0)
    box2.show()

    button = gtk.Button("Close")
    button.connect_object("clicked", self.close, self.dia, None)
    box2.pack_start(button, True, True, 0)
    button.set_flags(gtk.CAN_DEFAULT)
    button.grab_default()
    button.show()
    self.dia.show()
    
    self.closed = False
    main_context = gobject.main_context_default()
    while self.closed is False:
      main_context.iteration(False)
    self.dia.destroy()
    return self.hwnd

  def pick_table_window(self, widget, data=None):
    if widget.get_active():
      win = data
      self.w_table_w = win
      self.hwnd = win.get_xid()
      self.table_window_name = win.get_name()

  def button_release_event_cb(self, winref, event):
    self.mouse_clicked = True
    self.pointer_position = (event.x_root, event.y_root)
    return True

if __name__ == "__main__":
  qt = TableFinder("Click the mouse pointer on the poker table window", "Chromium")
  hwnd = qt.run()
  qt.destroy()



import datetime
from os.path import abspath
import sys

import gtk
import appindicator as ind

import productivity as prod

ICONS = {
    prod.WORKING: abspath('working.svg'),
    prod.PLAYING: abspath('playing.svg'),
    prod.CRUNCH_MODE: abspath('crunch-mode.svg'),
    prod.RED_ALERT: abspath('red-alert.svg'),
}


class ProductivityIndicator(object):
    '''
    Implementation based on AppIndicator tutorial from ConjureCode:
    http://conjurecode.com/create-indicator-applet-for-ubuntu-unity-with-python/
    '''
    def __init__(self):
        self.ind = ind.Indicator('productivity', 'media-seek-forward-symbolic',
                                 ind.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(ind.STATUS_ACTIVE)
        self.menu = self.build_menu()
        self.ind.set_menu(self.menu)

        self.prod = prod.Productivity()

    def build_menu(self):
        menu = gtk.Menu()
        self.clockin_item = self.add_item(menu, prod.WORKING.label, self.clockin)
        self.clockout_item = self.add_item(menu, prod.PLAYING.label, self.clockout)
        self.add_item(menu, 'Quit', self.quit)
        return menu

    def add_item(self, menu, label, func):
        item = gtk.MenuItem(label)
        item.connect('activate', func)
        item.show()
        menu.append(item)
        return item

    def main(self):
        gtk.timeout_add(1000, self.update)
        gtk.main()

    def clockin(self, _):
        self.prod.clockin()
        self.update()

    def clockout(self, _):
        self.prod.clockout()
        self.update()

    def quit(self, _):
        self.prod.quit()
        sys.exit(0)

    def update(self):
        uptime, percentile = self.prod.uptime_and_percentile()
        uptime_str = format_timedelta(uptime)
        percentile_str = format_percentile(percentile)
        self.ind.set_label('%s [%s]' % (uptime_str, percentile_str))
        self.ind.set_icon(ICONS[self.prod.status()])

        self.clockin_item.set_label(prod.CRUNCH_MODE.label
                                    if self.prod.late else
                                    prod.WORKING.label)
        self.clockout_item.set_label(prod.RED_ALERT.label
                                     if self.prod.late else
                                     prod.PLAYING.label)

        self.clockin_item.set_sensitive(not self.prod.working)
        self.clockout_item.set_sensitive(self.prod.working)
        return True


def format_timedelta(td):
    if td < datetime.timedelta(0):
        td_str = '-' + str(-td)
    else:
        td_str = str(td)
    point = td_str.find('.')
    if point == -1:
        return td_str
    else:
        return td_str[:point]


def format_percentile(p):
    return '%d%%' % int(p)


if __name__ == '__main__':
    ProductivityIndicator().main()

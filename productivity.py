import bisect
import datetime
import os
from collections import namedtuple


Status = namedtuple('Status', ['id', 'label'])

WORKING = Status('WORKING', 'Working')
PLAYING = Status('PLAYING', 'Playing')
CRUNCH_MODE = Status('CRUNCH_MODE', 'Crunch mode')
RED_ALERT = Status('RED_ALERT', 'Red Alert!')

LOG_DIR = os.path.expanduser('~/.productivity')


def mkdirp(dirname):
    '''
    Create a directory at the path given by `dirname`, if it doesn't
    already exist.

    http://stackoverflow.com/a/14364249/4481448
    '''
    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise


class Productivity(object):
    def __init__(self):
        self.history = load_history()
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.uptime_ = self.history.uptime(t.date())
        self.status_ = PLAYING
        self.working = False
        self.log_event(t, u, 'start')
        self.last_clockin = u
        self.last_update_utc = u
        self.last_update_local = t
        self.update(t, u)

    def uptime_and_percentile(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.update(t, u)
        return self.uptime_, self.history.percentile(t.date(), self.uptime_)

    def uptime(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.update(t, u)
        return self.uptime_

    def status(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.update(t, u)
        return self.status_

    def clockin(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.log_event(t, u, 'clockin')
        self.last_clockin = u
        self.working = True
        self.update(t, u)

    def clockout(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.log_event(t, u, 'clockout')
        self.working = False
        self.update(t, u)

    def quit(self):
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.log_event(t, u, 'quit')

    def update(self, t, u):
        if self.status_ == WORKING:
            self.uptime_ += u - self.last_update_utc
        elif self.status_ == RED_ALERT:
            self.uptime_ -= u - self.last_update_utc

        if self.working and u - self.last_clockin >= self.reset_interval():
            self.working = False

        old_status = self.status_
        self.late = self.is_late(t)
        if self.late:
            self.status_ = CRUNCH_MODE if self.working else RED_ALERT
        else:
            self.status_ = WORKING if self.working else PLAYING

        if t.date() != self.last_update_local.date():
            self.log_event(t, u, 'reset')
            self.uptime_ = datetime.timedelta(0)
            self.log_event(t, u, 'update')
        elif self.status_ != old_status:
            self.log_event(t, u, 'update')

        self.last_update_utc = u
        self.last_update_local = t

    def log_event(self, t, u, name):
        self.history.add(t.date(), self.uptime_)
        t_format = format_datetime(t)
        u_format = format_datetime(u)
        up_format = format_timedelta(self.uptime_)
        log_line('\t'.join((t_format, u_format, up_format,
                            self.status_.id, name)))

    def reset_interval(self):
        return datetime.timedelta(minutes=15)

    def is_late(self, t):
        return t.hour >= 23 or t.hour <= 6


def format_datetime(t):
    return ':'.join(str(e) for e in (t.year, t.month, t.day,
                                     t.hour, t.minute, t.second, t.microsecond))


def format_timedelta(t):
    return ':'.join(str(e) for e in (t.days, t.seconds, t.microseconds))


class History(object):
    def __init__(self):
        self.date_map = {}

    def add(self, date, uptime):
        self.date_map[date] = uptime

    def uptime(self, date):
        if date in self.date_map:
            return self.date_map[date]
        else:
            return datetime.timedelta(0)

    def percentile(self, curr_date, uptime):
        uptimes = sorted([td for d, td in self.date_map.iteritems()
                          if td > datetime.timedelta(0) and d != curr_date])
        if uptimes:
            idx = bisect.bisect(uptimes, uptime)
            return idx * 100.0 / len(uptimes)
        elif uptime > datetime.timedelta(0):
            return 100.0
        else:
            return 0.0


def load_history():
    history = History()
    for line in get_events():
        localtime_str, _, uptime_str = line.split('\t')[:3]
        date = datetime.datetime(*[int(num) for num in localtime_str.split(':')]).date()
        uptime = datetime.timedelta(*[int(num) for num in uptime_str.split(':')])
        history.add(date, uptime)
    return history


def get_events():
    mkdirp(LOG_DIR)
    with open(os.path.join(LOG_DIR, 'events.log'), 'a+') as logfile:
        logfile.seek(0)
        for line in logfile:
            yield line


def log_line(line):
    with open(os.path.join(LOG_DIR, 'events.log'), 'a') as outfile:
        outfile.write(line + '\n')
    print(line)


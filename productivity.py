import os
import datetime
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
        self.uptime_ = load_uptime()
        self.status_ = PLAYING
        self.working = False
        t, u = datetime.datetime.now(), datetime.datetime.utcnow()
        self.log_event(t, u, 'start')
        self.last_clockin = u
        self.last_update_utc = u
        self.last_update_local = t
        self.update(t, u)

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


def load_uptime():
    line = get_last_event()
    if line is None:
        return datetime.timedelta(0)

    localtime_str, _, uptime_str = line.split('\t')[:3]
    localtime = datetime.datetime(*[int(num) for num in localtime_str.split(':')])
    now = datetime.datetime.now()
    if localtime.date() == now.date():
        return datetime.timedelta(*[int(num) for num in uptime_str.split(':')])
    else:
        return datetime.timedelta(0)


def get_last_event():
    mkdirp(LOG_DIR)
    line = None
    with open(os.path.join(LOG_DIR, 'events.log'), 'a+') as logfile:
        logfile.seek(0)
        for line in logfile:
            pass
    return line


def log_line(line):
    with open(os.path.join(LOG_DIR, 'events.log'), 'a') as outfile:
        outfile.write(line + '\n')
    print(line)


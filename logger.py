import time

class logger:
    
    @staticmethod
    def log(message):
        now = time.localtime()
        timeStamp = '{y}.{mon}.{d} {h}:{min}:{s}'.format(y=now.tm_year, mon=now.tm_mon, d=now.tm_mday, h=now.tm_hour, min=now.tm_min, s=now.tm_sec)
        print( timeStamp + ' => ' + message )
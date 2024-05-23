
import time  # needed for ntptime
import ntptime
from machine import RTC
from config import config


def ntp_sync():
    # print("Local time before synchronization：%s" %str(time.localtime()))
    print("Local time before synchronization： {}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(RTC().datetime()[0], RTC().datetime()[1], RTC().datetime()[2], RTC().datetime()[4], RTC().datetime()[5],RTC().datetime()[6]))
    ntptime.host = config.NTP_SERVER
    ntptime.settime()
    # print("Local time after synchronization：%s" %str(time.localtime()))
    (year, month, mday, week_of_year, hour, minute, second, milisecond)=RTC().datetime()
    hour = hour + config.NTP_HOUR_ADJUST
    RTC().init((year, month, mday, week_of_year, hour, minute, second, milisecond))
    # print("Local time after timezone offset: %s" %str(time.localtime()))
    print("Local time after synchronization: {}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(RTC().datetime()[0], RTC().datetime()[1], RTC().datetime()[2], RTC().datetime()[4], RTC().datetime()[5],RTC().datetime()[6]))

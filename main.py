import sched, time
from classes.classSpeedTestRegister import SpeedTestRegister

HOST = 'http://www.google.com/'
TIMEOUT = 5 #timeout when checking connection (check_internet_connection)
SHELVNAME = 'database/NetworkSpeedHistory'
LOGBRIEF = 10 # every LOGBRIEF measurements, it'll read the date and log a report
REPLAY = 60 # time between every measument (do_test_report)

objSpeedTest = SpeedTestRegister(HOST, TIMEOUT, SHELVNAME, LOGBRIEF, REPLAY)

objScheduler = sched.scheduler(time.time, time.sleep)
objScheduler.enter(REPLAY, 1, objSpeedTest.do_test_report, (objScheduler,))
objScheduler.run()
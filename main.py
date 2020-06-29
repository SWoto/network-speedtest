import sched, time
from classes.classSpeedTestRegister import SpeedTestRegister

HOST = 'http://www.google.com/'
TIMEOUT = 5 #timeout when checking connection (check_internet_connection)
SHELVNAME = 'database/NetworkSpeedHistory'
LOGBRIEF = 2 # every LOGBRIEF measurements, it'll read the date and log a report
REPLAY = 60 # time between every measument (do_test_report)
PLOT_CHART = True # it will plot some chart if you have any data every LOGBRIEF*REPLAY seconds

objSpeedTest = SpeedTestRegister(HOST, TIMEOUT, SHELVNAME, LOGBRIEF, REPLAY, PLOT_CHART)
print("Running Network Speed Test")
print("\tAll your LOGS will be saved at 'logs' folder")
print("\tAll your CHARTS will be saved 'charts' folder with .html format")
print("\tEvery {} seconds, a new Brief will be logged and a new Chart saved".format(REPLAY*LOGBRIEF))

objScheduler = sched.scheduler(time.time, time.sleep)
objScheduler.enter(REPLAY, 1, objSpeedTest.do_test_report, (objScheduler,))
objScheduler.run()
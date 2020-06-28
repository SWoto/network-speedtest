import sched, time
import os
import requests
import json
import shelve #persistent, dictionary-like object
from classes.speedtest import Speedtest
from classes.classLogger import EscritorDeLog

class NetworkSpeedTestRegister(EscritorDeLog):
    def __init__(self, host='http://www.google.com/', timeout = 5, shelvename = 'NetworkSpeedHistory', logbrief=10, replay=60):
        super().__init__()
        self.host = host
        self.timeout = timeout
        self.shelvename = shelvename
        self._counter = 0
        self.logbrief = logbrief
        self.replay = replay

    def check_internet_connection(self) -> bool:
        try:
            _ = requests.get(self.host, timeout = self.timeout)
            return True
        except requests.ConnectionError:
            self.escreve_log.warning("The device is offline")
            return False
        except Exception:
            self.escreve_log.exception('Could\'t check connection')
            return False

    def do_speedtest(self):
        try:
            self.speedtest = Speedtest()
            self.speedtest.get_servers()
            self.speedtest.get_best_server()
            self.speedtest.download()
            self.speedtest.upload()
            return True
        except Exception:
            self.escreve_log.exception('Speedtest Failure')
            return False     

    def do_test_report(self, schedulerExecutions):
        self._counter = self._counter + 1
        try:
            with shelve.open(self.shelvename) as db:
                if self.check_internet_connection() and self.do_speedtest():
                    json_object = self.speedtest.results.dict()
                else:  
                    json_object = {"download": 0, "upload": 0,  "ping": 999}
                key = str(int(time.time()))
                db[key] = json_object
            schedulerExecutions.enter(self.replay, 1, self.do_test_report, (schedulerExecutions,))
            
            if self._counter % self.logbrief == 0: 
                self.do_log_report()
        except Exception:
            self.escreve_log.exception('Failed to write to db at {}'.format(self._counter))
        
    def do_log_report(self):
        try:
            download = 0
            upload = 0
            ping = 0
            offline = 0
            with shelve.open(self.shelvename) as db:
                my_keys = list(db.keys())
                my_keys.sort()
                my_keys = my_keys[-self.logbrief:]
                for key in my_keys:
                    measure = db[key]
                    download = download + measure.get('download')
                    upload = upload + measure.get('upload')
                    ping = ping + measure.get('ping')
                    if download == 0 and upload == 0:
                        offline = offline + 1
            
            download = download / len(my_keys) / 1024 / 1024  
            upload = upload / len(my_keys) / 1024 / 1024
            ping = ping / len(my_keys)

            message = "Average of {} measurements. Download = {:.2f} [Mb/s], Upload = {:.2f} [Mb/s], " \
                        "ping = {} [ms], Number of times offline: {}".format(self.logbrief, 
                        download, upload, int(ping), offline)
            self.escreve_log.info(message)

        except Exception:
            self.escreve_log.exception('Could write log brief')

HOST = 'http://www.google.com/'
TIMEOUT = 5 #timeout when checking connection (check_internet_connection)
SHELVNAME = 'database/NetworkSpeedHistory'
LOGBRIEF = 10 # every LOGBRIEF measurements, it'll read the date and log a report
REPLAY = 60 # time between every measument (do_test_report)

objSpeedTest = NetworkSpeedTestRegister(HOST, TIMEOUT, SHELVNAME, LOGBRIEF, REPLAY)

objScheduler = sched.scheduler(time.time, time.sleep)
objScheduler.enter(REPLAY, 1, objSpeedTest.do_test_report, (objScheduler,))
objScheduler.run()
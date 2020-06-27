import sched, time
import os
import requests
import json
import shelve #persistent, dictionary-like object
from classes.speedtest import Speedtest
from classes.classLogger import EscritorDeLog

class NetworkSpeedTestRegister(EscritorDeLog):
    def __init__(self, host='http://www.google.com/', timeout = 5, shelvename = 'NetworkSpeedHistory'):
        super().__init__()
        self.host = host
        self.timeout = timeout
        self.shelvename = shelvename
        self.thread_job = None

    def check_internet_connection(self) -> bool:
        self.escreve_log.debug("Testing connection")
        #conn = httplib.HTTPConnection(self.host, timeout=self.timeout)
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
        self.escreve_log.debug('Running SpeedTest')
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
        self.escreve_log.debug('Writing test report')
        # write header to new csv
        # dir = os.path.dirname(__file__)
        # out_path = os.path.join(dir, self.filename)
        
        try:
            with shelve.open(self.shelvename) as db:
                if self.check_internet_connection() and self.do_speedtest():
                    # Serializing json  
                    json_object = self.speedtest.results.dict()
                else:  
                    json_object = {"download": 0, "upload": 0,  "ping": 999}
                    #json_object = json.dumps(dictionary)
                key = str(int(time.time()))
                db[key] = json_object
            schedulerExecutions.enter(60, 1, self.do_test_report, (schedulerExecutions,))
        except Exception:
            self.escreve_log.exception('Failed to write to db')


HOST = 'http://www.google.com/'
TIMEOUT = 6
SHELVNAME = 'database/NetworkSpeedHistory'

objSpeedTest = NetworkSpeedTestRegister(HOST, TIMEOUT, SHELVNAME)

objScheduler = sched.scheduler(time.time, time.sleep)
objScheduler.enter(60, 1, objSpeedTest.do_test_report, (objScheduler,))
objScheduler.run()
import os
import sys
import logging
import logging.config
from threadjob import ThreadJob
from speedtest import Speedtest
from datetime import datetime as dt
import requests


def get_env_variable(var_name, default=None) -> str:
    """Get the environment variable or return False"""
    try:
        return os.environ[var_name]
    except KeyError:
        return False


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


class NetworkSpeedTestRegister():
    def __init__(self, host='http://www.google.com/', timeout = 5, filename = 'NetworkSpeedHistory.csv', log_name = 'basicLog'):
        self.host = host
        self.timeout = timeout
        self.filename = filename
        self.speedtest = None
        self.logger = logging.getLogger(log_name + '.' + type(self).__name__)
        self.thread_job = None

    def check_internet_connection(self) -> bool:
        self.logger.info('Testing connection')
        #conn = httplib.HTTPConnection(self.host, timeout=self.timeout)
        try:
            _ = requests.get(self.host, timeout = self.timeout)
            return True
        except requests.ConnectionError:
            self.logger.debug('The device is offline')
            return False
        except Exception:
            self.logger.exception('Could\'t check connection')
            return False

    def check_path(self, path):
        self.logger.info('Checking if path/file exist')
        if os.path.exists(path):
            return True
        else:
            return False

    def do_speedtest(self):
        self.logger.info('Running SpeedTest')
        try:
            self.speedtest = Speedtest()
            self.speedtest.get_servers()
            self.speedtest.get_best_server()
            self.speedtest.download()
            self.speedtest.upload()
            return True
        except Exception:
            self.logger.exception('Speedtest Failure')
            return False     

    def do_test_report(self):
        self.logger.info('Writing test report')
        # write header to new csv
        dir = os.path.dirname(__file__)
        out_path = os.path.join(dir, self.filename)
        if not(self.check_path(out_path)):
            try:
                with open(out_path, 'w') as f:
                    f.write('timestamp, status, download [MB/s], upload[MB/s], ping [ms]\n')
            except Exception:
                self.logger.exception('Couldn\'t write header in file.')

        #write data into csv
        try:         
            with open(out_path, 'a') as f:
                ts = dt.now()
                if self.check_internet_connection() and self.do_speedtest():
                    res = self.speedtest.results.dict()
                    download = res.get("download")
                    upload = res.get("upload")
                    ping = res.get("ping")
                    string = 'connected;{:.2f};{:.2f};{:.2f}\n'.format(download / 1024 / 1024, upload / 1024 / 1024, ping)
                    f.write('{};{}'.format(ts, string))
                    print('{};{}'.format(ts, string))
                else:             
                    f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                    print('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
        except Exception:
                self.logger.exception('Couldn\'t write header in file.')


    def set_threading(self, time) -> None:
        self.logger.info('Starting Thread')
        self.thread_job = ThreadJob(interval = time, execute = self.do_test_report)
        self.thread_job.start()

    def stop_threading(self) -> None:
        self.logger.info('Stoping Thread')
        self.thread_job.stop()

#create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('basicLog')

file = 'NetworkSpeedHistory.csv'
out_path = os.path.join(os.path.dirname(__file__), file)
print('Saving tests in: {}'.format(out_path))

NST = NetworkSpeedTestRegister(log_name = 'basicLog')
NST.set_threading(20)

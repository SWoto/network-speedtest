import logging
from threading import Thread, Event

class ThreadJob(Thread):
    def __init__(self, interval, execute, log_name = None, *args, **kwargs):
        Thread.__init__(self)
        self.daemon = False
        self.stopped = Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        self.logger = self.set_logger(log_name)
        
    def set_logger(self, log_name):
        if log_name == None:
            return logging.getLogger(__name__)
        else:
            logging.getLogger(log_name + '.' + type(self).__name__)

    def stop(self):
        self.logger.info('Stopping thread {}'.format(self.execute.__name__))
        self.stopped.set()
        self.join()

    def run(self):
        self.logger.info('Running thread {}'.format(self.execute.__name__))
        while not self.stopped.wait(self.interval):
            self.execute(*self.args, **self.kwargs)
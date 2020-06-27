import logging
from datetime import datetime


class EscritorDeLog():
    """ Class that implement the logger"""
    def __init__(self, *args, **kwargs):
        formatter = logging.Formatter('[%(levelname)-8s] [%(asctime)s] - %(name)s:%(funcName)s:%(lineno)d - %(message)s', 
            "%Y-%m-%d %H:%M:%S")
        handler = logging.FileHandler('logs/networkspeedtest-{:%Y%m%d}.log'.format(datetime.now()), mode='a+')
        handler.setFormatter(formatter)
        self.escreve_log = logging.getLogger(self.__class__.__name__)
        self.escreve_log.setLevel(logging.DEBUG)
        self.escreve_log.handlers = []
        self.escreve_log.addHandler(handler)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.escreve_log.addHandler(console)

        
import speedtest
from datetime import datetime as dt
import os
import threading
import logging
import logging.config
try:
    import httplib
except:
    import http.client as httplib

def checkFolderOrFile(path):
    if os.path.exists(path):
        return True
    else:
        return False

    
def haveInternet(logger):
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        logging.debug('Successful Request')
        return True
    except Exeption as e:
        conn.close()
        logging.exception('Request Failure')
        return False

    
def test(logger):
    try:
        s = speedtest.Speedtest()
        s.get_servers()
        s.get_best_server()
        s.download()
        s.upload()
        res = s.results.dict()
        logging.debug('Speedtest successfully made')
        return res.get("download"), res.get("upload"), res.get("ping")
    except Exeption as e:
        logging.exception('Speedtest Failure')
        return None        


def textReport(logger, path,file):
    # write header to new csv
    if not(checkFolderOrFile(logger,path+file)):
        try:
            with open(path+file, 'w') as f:
                f.write('timestamp, status, download [MB/s], upload[MB/s], ping [ms]\n')
                logger.debug('The header has been written.')
        except Exeption as e:
            logger.exception('Couldn\'t write the header into file.')
        
    #write data into csv        
    with open(path+file, 'a') as f:
        ts = dt.now()
        if haveInternet(logger):
            print('Testing...')
            try:
                d, u, p = test(logger)
                f.write('{};connected;{:.2f};{:.2f};{:.2f}\n'.format(ts, d / 1024 / 1024, u / 1024 / 1024, p))
                logger.debug('Speedtest has been written.')
            except Exception as e:
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                logger.exception('Couldn\'t execute/write speedtest.')
        else:
            try:                  
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                logger.debug('Current Status has been written.')
            except Exception as e:
                logger.exception('Couldn\'t write into file.')


def main(logger):
    #run every five minutes = 300 seconds
    threading.Timer(300.0, main, [logger, path, file]).start()  
    textReport(logger, path, file)
      
        
logging.basicConfig(filename='speedtest.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Get the logger specified in the file
logger = logging.getLogger(__name__)
path = ''
file = 'speedhistory.csv'

main(logger, path, file)

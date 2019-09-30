import speedtest
from datetime import datetime as dt
import os
import threading
import logging
try:
    import httplib
except:
    import http.client as httplib

    
logging.basicConfig(filename='speedtest.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def checkFolderOrFile(path):
    if os.path.exists(path):
        return True
    else:
        return False

    
def haveInternet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        logging.debug('Successful Request')
        return True
    except Exeption as e:
        conn.close()
        logging.debug('Request Failure. Error: {}'.format(e))
        return False

    
def test():
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
        logging.debug('Speedtest Failure. Error: {}'.format(e))
        return None        


def textReport(path,file):
    # write header to new csv
    if not(checkFolderOrFile(path+file)):
        try:
            with open(path+file, 'w') as f:
                f.write('timestamp, status, download [MB/s], upload[MB/s], ping [ms]\n')
                logging.debug('The header has been written.')
        except Exeption as e:
            logging.warning('Couldn\'t write the header into file. Error: {}'.format(e))
        
    #write data into csv        
    with open(path+file, 'a') as f:
        ts = dt.now()
        if haveInternet():
            print('Testing...')
            try:
                d, u, p = test()
                f.write('{};connected;{:.2f};{:.2f};{:.2f}\n'.format(ts, d / 1024 / 1024, u / 1024 / 1024, p))
                logging.debug('Speedtest has been written.')
            except Exception as e:
                logging.warning('Couldn\'t execute/write speedtest. Error: {}'.format(e))
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
        else:
            try:                  
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                logging.debug('Current Status has been written.')
            except Exception as e:
                logging.warning('Couldn\'t write into file. Error: {}'.format(e))


def main():
    #run every five minutes = 300 seconds
    threading.Timer(300.0, main).start()  
    path = ''
    file = 'file.csv'
    textReport(path,file)
      

main()

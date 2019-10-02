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

def checkFolderOrFile(pathFile):
    if os.path.exists(pathFile):
        return True
    else:
        return False

    
def haveInternet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        #logging.debug('Successful Request')
        return True
    except Exception as e:
        conn.close()
        print(e)
        #logging.exception('Request Failure')
        return False

    
def test():
    try:
        s = speedtest.Speedtest()
        s.get_servers()
        s.get_best_server()
        s.download()
        s.upload()
        res = s.results.dict()
        #logging.debug('Speedtest successfully made')
        return res.get("download"), res.get("upload"), res.get("ping")
    except Exception as e:
        #logging.exception('Speedtest Failure')
        print(e)
        return None        


def textReport(path, file):
    # write header to new csv
    if not(checkFolderOrFile(path+file)):
        try:
            with open(path+file, 'w') as f:
                f.write('timestamp, status, download [MB/s], upload[MB/s], ping [ms]\n')
                #logger.debug('The header has been written.')
        except Exception as e:
            #logger.exception('Couldn\'t write the header into file.')
            print(e)
        
    #write data into csv        
    with open(path+file, 'a') as f:
        ts = dt.now()
        if haveInternet():
            print('{}: Testing... '.format(ts), end='')
            try:
                d, u, p = test()
                string = 'connected;{:.2f};{:.2f};{:.2f}\n'.format(d / 1024 / 1024, u / 1024 / 1024, p)
                f.write('{};{}'.format(ts, string))
                print(string)
                #logger.debug('Speedtest has been written.')
            except Exception as e:
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                print(e)
                #logger.exception('Couldn\'t execute/write speedtest.')
        else:
            try:                  
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
                #logger.debug('Current Status has been written.')
            except Exception as e:
                print(e)
                #logger.exception('Couldn\'t write into file.')


def main(path, file):
    #run every five minutes = 300 seconds
    threading.Timer(300.0, main, [path, file]).start()  
    textReport(path, file)
      
dir = os.path.dirname(__file__)
file = 'speedhistory.csv'
out_path = os.path.join(dir, file)
#log_path = os.path.join(dir, 'speedtest.log')
print(out_path)
#logging.basicConfig(filename=log_path, filemode='a+', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Get the logger specified in the file



main(out_path, file)

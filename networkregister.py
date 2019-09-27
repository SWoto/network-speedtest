import speedtest
from datetime import datetime as dt
import os
import threading
try:
    import httplib
except:
    import http.client as httplib


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
        return True
    except:
        conn.close()
        return False


def test():
    s = speedtest.Speedtest()
    s.get_servers()
    s.get_best_server()
    s.download()
    s.upload()
    res = s.results.dict()
    #print(res)
    return res["download"], res["upload"], res["ping"]


def textReport(path,file):
    # write header to new csv
    if not(checkFolderOrFile(path+file)):
        with open('file.csv', 'w') as f:
            f.write('timestamp, status, download [MB/s], upload[MB/s], ping [ms]\n')
    
    #write data into csv        
    with open('file.csv', 'a') as f:
        ts = dt.now().time()
        if haveInternet:
            print('Testing...')
            try:
                d, u, p = test()
                f.write('{};connected;{:.2f};{:.2f};{:.2f}\n'.format(ts, d / 1024 / 1024, u / 1024 / 1024, p))
            except Exception as e:
                print(e)
                f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))
        else:
            f.write('{};disconnected;{:.2f};{:.2f};{}\n'.format(ts, 0., 0., 'inf'))


def main():
    #run every five seconds
    threading.Timer(300.0, main).start()  
    path = ''
    file = 'file.csv'
    textReport(path,file)
      

main()

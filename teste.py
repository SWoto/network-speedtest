import shelve

SHELVNAME = 'database/NetworkSpeedHistory'
LOGBRIEF = 2 # every LOGBRIEF measurements, it'll read the date and log a report

try:
    download = 0
    upload = 0
    ping = 0
    offline = 0
    i = 0
    with shelve.open(SHELVNAME) as db:
        my_keys = list(db.keys())
        my_keys.sort(reverse=True)
        for key in my_keys:
            i = i + 1
            measure = db[key]
            download = download + measure.get('download')
            upload = upload + measure.get('upload')
            ping = ping + measure.get('ping')
            if download == 0 and upload == 0:
                offline = offline + 1
            if i == LOGBRIEF:
                break
    
    download = download / i / 1024 / 2014  
    upload = upload / i / 1024 / 2014
    ping = ping / i 

    message = "Average of {} measurements. Download = {:.2f} [Mb/s], Upload = {:.2f} [Mb/s], " \
                "ping = {} [ms], Number of times offline: {}".format(LOGBRIEF, 
                download, upload, int(ping), offline)
    print(message)

except Exception as e:
    print(e)
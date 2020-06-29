import sched, time
import requests

#persistent, dictionary-like object
import shelve 

# to use plot some charts
try:
    import pandas as pd
    import plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    _PLOT_CHATS = True
except ImportError:
    _PLOT_CHATS = False

# user defined functins
from classes.speedtest import Speedtest
from classes.classLogger import EscritorDeLog

class SpeedTestRegister(EscritorDeLog):
    def __init__(self, host='http://www.google.com/', timeout = 5, shelvename = 'NetworkSpeedHistory', logbrief=10, replay=60, plot_charts = True):
        super().__init__()
        self.host = host
        self.timeout = timeout
        self.shelvename = shelvename
        self._counter = 0
        self.logbrief = logbrief
        self.replay = replay
        self.plot_charts = plot_charts

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
            if self._counter % self.logbrief == 0: 
                self.do_log_report()
                self.plot_grafics_browser()
        except Exception:
            self.escreve_log.exception('Failed to write to db at {}'.format(self._counter))
        finally:
            schedulerExecutions.enter(self.replay, 1, self.do_test_report, (schedulerExecutions,))
        
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

    def plot_grafics_browser(self):
        if(_PLOT_CHATS and self.plot_charts):
            df = pd.DataFrame()
            with shelve.open(self.shelvename) as db:
                for measure in db:
                    df = df.append(db[measure], ignore_index=True)

            if len(df.index) > self.logbrief:
                df = df.sort_values(by=['timestamp'])
                df['download'] = df['download']/1024/1024
                df['upload'] = df['upload']/1024/1024

                fig = make_subplots(rows=3, cols=1, 
                    shared_xaxes=True, 
                    subplot_titles=("Download", "Upload", "Ping"))

                # add values
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['download']),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['upload']),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['ping']),
                    row=3, col=1
                )

                # change yaxis label
                fig.update_yaxes(title_text="[Mb/s]", row=2, col=1)
                fig.update_yaxes(title_text="[Mb/s]", row=1, col=1)
                fig.update_yaxes(title_text="[ms]", row=3, col=1)

                plotly.offline.plot(fig, filename='charts/speedtest.html', auto_open=False)
                #fig.show()
        elif not(_PLOT_CHATS) and self.plot_charts:
            self.escreve_log.warning('You need to install plotly to generate some charts')

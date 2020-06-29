import sched, time
import requests
import json

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
                    # get last used client
                    # ATENTION: if the first test happens to be offline, 
                    # it will be empty, and if the you have tested with another
                    # network and the first one with the new network is offline
                    # the offline result will be given to the former 
                    self.escreve_log.warning("You're offline")
                    key = max(list(db.keys()))
                    client = db[key].get('client')
                    json_object = {"download": 0, "upload": 0,  "ping": 999, 'client': client}
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
                clients = {}
                for measure in db:
                    client_dict = db[measure].get('client')
                    client_str = json.dumps(client_dict)
                    if not(client_str in clients) and client_str and client_dict:
                        clients[client_str] = client_dict.get('ip') + ' - ' + client_dict.get('isp')
                    if client_str and client_dict:
                        new_measure = db[measure]
                        new_measure['client'] = clients[client_str]
                        df = df.append(new_measure, ignore_index=True)

            if len(df.index) > self.logbrief:
                df = df.sort_values(by=['timestamp'])
                df['download'] = df['download']/1024/1024
                df['upload'] = df['upload']/1024/1024

                fig = make_subplots(rows=3, cols=1, 
                    shared_xaxes=True, 
                    subplot_titles=("Download", "Upload", "Ping"))

                clients = df.client.unique()
                buttons = []
                for i, client in enumerate(clients, 1):
                    df_unique = df[df['client']==client]
                    fig.add_trace(
                        go.Scatter(x=df_unique['timestamp'], y=df_unique['download']),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df_unique['timestamp'], y=df_unique['upload']),
                        row=2, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df_unique['timestamp'], y=df_unique['ping']),
                        row=3, col=1
                    )

                    button_dict =   dict(label=client,
                                        method="update",
                                        args=[{"visible": [False]*(i-1)*3 + [True]*3 + [False]*(len(clients)-i)*3}]
                                    )
                    buttons.append(button_dict)

                # change yaxis label
                fig.update_yaxes(title_text="[Mb/s]", row=2, col=1)
                fig.update_yaxes(title_text="[Mb/s]", row=1, col=1)
                fig.update_yaxes(title_text="[ms]", row=3, col=1)

                fig.update_layout(
                    margin=dict(t=100, b=0, l=0, r=0),
                )

                fig.update_layout(
                    updatemenus=[
                        dict(
                            direction="down",
                            buttons=buttons,
                            showactive=True,
                            x=0.58,
                            xanchor="left",
                            y=1.08,
                            yanchor="top"
                        ),
                    ])

                plotly.offline.plot(fig, filename='charts/speedtest.html', auto_open=False)
                #fig.show()
        elif not(_PLOT_CHATS) and self.plot_charts:
            self.escreve_log.warning('You need to install plotly to generate some charts')

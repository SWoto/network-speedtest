# network-speedtest
Created to register internet speed and connection through time. Useful to places with bad internet quality. Build using speedtest-cli. 

This is build to measure network's speed (download, upload, ping) and save them using a nosql database (shelve). 

You can also cofigure to plot the data every some seconds and add a brief to the log. 
```
LOGBRIEF = 10 # every LOGBRIEF measurements, it'll read the date and log a report
REPLAY = 60 # time between every measument (do_test_report)
PLOT_CHART = True # it will plot some chart if you have any data every LOGBRIEF*REPLAY seconds
```

**Brief Example**
```
[INFO    ] [2020-06-28 15:20:31] - Average of 10 measurements. Download = 19.59 [Mb/s], Upload = 2.47 [Mb/s], ping = 36 [ms], Number of times offline: 0

```

**Chart Example**
![Download/Upload/Ping](images/chart_example.png?raw=true)

## How to use
1. Clone the repository
1. Open your terminal and go to the downloaded folder
1. Execute `python3 main.py` in your terminal.

**Obs.:** Might be needed to install `plotly` if you don't have it yet.
`conda install -c plotly plotly `
`pip3 install plotly`
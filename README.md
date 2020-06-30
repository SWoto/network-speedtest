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
The new chart version supports more than one network test. For example, if you test in you house and then in your work, the chart will show you a dropdown menu so you can chose which one do you want to see.
![Download/Upload/Ping](images/chart_example.png?raw=true)

## How to use
1. Clone the repository
1. Open your terminal and go to the downloaded folder
1. Execute `python3 main.py` in your terminal.

**Obs.:** Might be needed to install `plotly` or other libraries if you don't have them.

`sudo pip3 install -r requirements.txt`

## Set it to run on boot
**Tested on raspberry pi only**

1. Copy the my_speedtest.service to /etc/systemd/system
`sudo cp my_speedtest.service /etc/systemd/system/my_speedtest.service`

2.  Now, try to start it
`sudo systemctl start my_speedtest.service`

3. Check if its working
`sudo systemctl status my_speedtest.service`

4. Than enable it to start on boot
`sudo systemctl enable my_speedtest`

Any more information, check https://www.raspberrypi.org/documentation/linux/usage/systemd.md
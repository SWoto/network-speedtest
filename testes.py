import shelve
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots



SHELVNAME = 'database/NetworkSpeedHistory'  
df = pd.DataFrame()
with shelve.open(SHELVNAME) as db:
    for measure in db:
        df = df.append(db[measure], ignore_index=True)

df = df.sort_values(by=['timestamp'])
df['download'] = df['download']/1024/1024
df['upload'] = df['upload']/1024/1024

fig = make_subplots(rows=3, cols=1, 
    shared_xaxes=True, 
    subplot_titles=("Download", "Upload", "Ping"))

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['download']),
    row=1, col=1
)
fig.update_yaxes(title_text="[Mb/s]", row=1, col=1)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['upload']),
    row=2, col=1
)
fig.update_yaxes(title_text="[Mb/s]", row=2, col=1)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['ping']),
    row=3, col=1
)
fig.update_yaxes(title_text="[ms]", row=3, col=1)

fig.show()


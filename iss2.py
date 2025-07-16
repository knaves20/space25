# satellite orbit positons
import numpy as np
import requests
from skyfield.api import load, EarthSatellite
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = 'browser'

#bring down live TLE
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle"
response = requests.get(url)
lines = response.text.strip().split("\n")

ts = load.timescale()
now = ts.now()

N = len(lines) // 3
satellites = []
names = []
for i in range(N):
    name = lines[3*i].strip()
    line1 = lines[3*i + 1].strip()
    line2 = lines[3*i + 2].strip()
    sat = EarthSatellite(line1, line2, name, ts)
    satellites.append(sat)
    names.append(name)

#timings
orbit_minutes = 1440
num_points = 1440
minutes_ahead = np.linspace(0, orbit_minutes, num_points)
times = now + (minutes_ahead / (24 * 60))

#satellite positions
positions = []
for sat in satellites:
    pos = sat.at(times).position.km
    positions.append(pos)

#earth
radius_earth = 6371
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
earth_x = radius_earth * np.outer(np.cos(u), np.sin(v))
earth_y = radius_earth * np.outer(np.sin(u), np.sin(v))
earth_z = radius_earth * np.outer(np.ones_like(u), np.cos(v))

#build figure
fig = go.Figure()

fig.add_trace(go.Surface(
    x=earth_x, y=earth_y, z=earth_z,
    colorscale='Blues',
    opacity=0.5,
    showscale=False,
    name = 'Earth'
))

#satellites
fig.add_trace(go.Scatter3d(
    x=[positions[i][0][0] for i in range(N)],
    y=[positions[i][1][0] for i in range(N)],
    z=[positions[i][2][0] for i in range(N)],
    mode='markers',
    marker=dict(size=3, color='black'),
    text=names, hoverinfo='text',
    name='Satellites'
))

#plot
frames = []
for f in range(num_points):
    frames.append(go.Frame(data=[
        go.Surface(
            x=earth_x, y=earth_y, z=earth_z,
            colorscale='Blues', opacity=0.5, showscale=False,
            name='Earth'
        ),
        go.Scatter3d(
            x=[positions[i][0][f] for i in range(N)],
            y=[positions[i][1][f] for i in range(N)],
            z=[positions[i][2][f] for i in range(N)],
            mode='markers',
            marker=dict(size=3, color='black'),
            text=names, hoverinfo='text',
            name='Satellites'
        )
    ]))

fig.frames = frames

fig.update_layout(
    title='Orbits of 100 Brightest Satellites',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    ),
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        buttons=[
            dict(label="Play",
                 method="animate",
                 args=[None, {"frame": {"duration":200, "redraw": True},
                              "fromcurrent":True, "transition": {"duration": 0}}]),
            dict(label="Pause",
                 method="animate",
                 args=[[None], {"frame": {"duration":0, "redraw": False},
                                "mode":"immediate",
                                "transition": {"duration": 0}}])
        ],
        x=0.1, y=0
    )]
)

fig.show()

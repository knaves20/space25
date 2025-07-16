# satellite orbit positons
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import matplotlib.cm as cm
import requests
#from mpl_toolkits.mplot3d import Axes3D
from skyfield.api import load, EarthSatellite

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

# orbit times
orbit_minutes = 1440
num_points = 1440
minutes_ahead = np.linspace(0, orbit_minutes, num_points)
times = now + (minutes_ahead / (24 * 60))

#positions for each satellite
positions_list = []
for sat in satellites:
    pos = sat.at(times).position.km  # shape (3, num_points)
    positions_list.append(pos)

#setup plot
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1,1,1])

#earth
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
earth_x = 6371 * np.cos(u)*np.sin(v)
earth_y = 6371 * np.sin(u)*np.sin(v)
earth_z = 6371 * np.cos(v)
ax.plot_surface(earth_x, earth_y, earth_z, color='lightblue', alpha=0.5)

colors = plt.get_cmap('tab20', N)

#orbit line, current point
lines = []
points = []
for i in range(N):
    line, = ax.plot([], [], [], lw=1, color=colors(i), label=names[i])
    point, = ax.plot([], [], [], 'o', color=colors(i), markersize=2)
    lines.append(line)
    points.append(point)

#animation functions
def init():
    for line, point in zip(lines, points):
        line.set_data([], [])
        line.set_3d_properties([])
        point.set_data([], [])
        point.set_3d_properties([])
    return lines + points

def update(frame):
    for i in range(N):
        x, y, z = positions_list[i]
        #lines[i].set_data(x[:frame], y[:frame])
        #lines[i].set_3d_properties(z[:frame])
        points[i].set_data([x[frame]], [y[frame]])
        points[i].set_3d_properties([z[frame]])
    return lines + points

#ax.plot3D(x, y, z, 'r', label='ISS orbit')

#axis scaling
padding = 500  # add extra space beyond the current max_range
max_range = 7000
ax.set_xlim(-max_range - padding, max_range + padding)
ax.set_ylim(-max_range - padding, max_range + padding)
ax.set_zlim(-max_range - padding, max_range + padding)

#labels/legends
ax.set_xlabel('X (km)')
ax.set_ylabel('Y (km)')
ax.set_zlabel('Z (km)')
ax.set_title('Orbits of 100 Brightest Satellites')

ax.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=4, fontsize='x-small', borderaxespad=0.)

#animation speed (adjustable)
time_compression = 50  # e.g. 60 means animation runs 60x faster than real time
seconds_per_frame_real = (orbit_minutes * 60) / num_points
interval_ms = (seconds_per_frame_real * 1000) / time_compression

ani = animation.FuncAnimation(fig, update, frames=num_points, init_func=init, blit=True, interval=interval_ms)

plt.tight_layout()
plt.subplots_adjust(right=0.75)
plt.show()

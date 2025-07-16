#live solar system 

from datetime import datetime, timedelta
from astroquery.jplhorizons import Horizons
from astropy.time import Time
from vpython import sphere, vector, color, rate

PLANETS = {
    'Mercury': {'id': 199, 'color': color.gray(0.5), 'radius': 0.0000169},  # AU
    'Venus':   {'id': 299, 'color': color.orange,    'radius': 0.0000414},
    'Earth':   {'id': 399, 'color': color.blue,      'radius': 0.0000435},
    'Mars':    {'id': 499, 'color': color.red,       'radius': 0.0000232},
    'Jupiter': {'id': 599, 'color': color.orange,    'radius': 0.0004779},
    'Saturn':  {'id': 699, 'color': color.yellow,    'radius': 0.000402},
    'Uranus':  {'id': 799, 'color': color.cyan,      'radius': 0.000175},
    'Neptune': {'id': 899, 'color': color.blue,      'radius': 0.00017}
}

SCALE_DIST = 1   # AU to VPython units
SCALE_SIZE = 5  # inflate planet radius visually

#get positions from horizons
def get_positions(epoch_jd):
    positions = {}
    for name, data in PLANETS.items():
        obj = Horizons(id=data['id'], location='500@10', epochs=[epoch_jd])
        vec = obj.vectors()
        x, y, z = float(vec['x'][0]), float(vec['y'][0]), float(vec['z'][0])
        positions[name] = vector(x, y, z)
    return positions

#vpython visuals

#sun
sun_radius = 0.00465
sun = sphere(pos=vector(0,0,0), radius=sun_radius*20, color=color.yellow, emissive=True)

planet_spheres = {}

#current time as string
now = datetime.now()
t = Time(now, scale='utc')
jd_now = t.jd

#get initial positions
positions = get_positions(jd_now)

#create planet spheres
for name, data in PLANETS.items():
    pos = positions[name] * SCALE_DIST
    planet = sphere(pos=pos, radius=data['radius']*SCALE_SIZE,
                    color=data['color'], make_trail=True, retain=200)
    planet_spheres[name] = planet

#animation
day = 0
while True:
    rate(60) #frames per sec
    day += 3.04
    #get new positons from horizons each +5 day
    future_time = now + timedelta(days=day)
    future_jd = Time(future_time, scale='utc').jd
    positions = get_positions(future_jd)

    for name, planet in planet_spheres.items():
        planet.pos = positions[name] * SCALE_DIST


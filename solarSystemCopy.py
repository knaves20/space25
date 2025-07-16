from astroquery.jplhorizons import Horizons
from astropy.time import Time

# Convert datetime to JD
t = Time('2025-07-14T00:00:00', format='isot', scale='utc')
jd = t.jd  # Julian Date as float

print("Julian Date:", jd)

obj = Horizons(id=399, location='@sun', epochs=[jd])
vec = obj.vectors()

print(f"Position (x,y,z): {vec['x'][0]}, {vec['y'][0]}, {vec['z'][0]}")

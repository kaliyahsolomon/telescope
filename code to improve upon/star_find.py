# telscope pointing code
from astroplan import Observer, FixedTarget
from astropy.time import Time, TimeDelta
import pytz
from astropy.coordinates import get_body
from astropy.time import Time
import astropy.units as u
import pytz

def get_time_list():
    utc_now = Time.now()

    # Convert UTC to Pacific Time
    pacific = pytz.timezone("America/Los_Angeles")
    local_dt = utc_now.to_datetime(timezone=pytz.utc).astimezone(pacific)

    # Convert back to Astropy Time format
    pst_time = Time(local_dt)

    # Generate list of timestamps for the next 24 hours (144 intervals of 10 minutes)
    time_list = [pst_time + TimeDelta(10 * i * 60, format='sec') for i in range(144)]  

    return Time(time_list)


def get_planet_coord_list(target_name, time_range, observer):
    target_altaz = []

    # Convert time_range list (currently string timestamps) to Astropy Time objects
    time_range = Time(time_range)  # Convert list of time strings into Astropy Time

    for time in time_range:
        planet_coord = get_body(target_name, time, observer.location)  # Keep `target_name` unchanged
        planet_altaz = planet_coord.transform_to(observer.altaz(time))  # Convert to AltAz
        target_altaz.append(planet_altaz)

    return target_altaz


def get_star_coord_list(target, time_range, observer):
    star = FixedTarget.from_name(target)
    star_altaz =[]
    for time in time_range:
        star_altaz.append(observer.altaz(time, star))
    return star_altaz 


def start_process():
    observer = Observer(latitude=34.1377*u.deg, longitude=-118.1253*u.deg, elevation=263*u.m)
    time_range = get_time_list()
    alt_az = []

    look_at = input("Do you want to look at a stars (stars, nebulas, galaxies, and clusters) or planetary objects (planets and moons)? ")
    if (look_at.lower() == "star" or look_at.lower() == "stars"):
        target = input("What star would you like to look at? ")
        alt_az = get_star_coord_list(target, time_range, observer)
    else:
        target = input("What planetary object would you like to look at? ")
        alt_az = get_planet_coord_list(target, time_range, observer)

    print(len(alt_az))
    alt_list = []
    az_list = []
    for coord in alt_az:
        alt_list.append(coord.alt.degree)
        az_list.append(coord.az.degree)
        print(f"Altitude: {coord.alt.degree:.2f} degrees, Azimuth: {coord.az.degree:.2f} degrees") 
    return alt_list, az_list

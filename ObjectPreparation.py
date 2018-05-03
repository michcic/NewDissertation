import numpy as np
import matplotlib as plt
import sunpy.map
import matplotlib.pyplot as plt
from sunpy.coordinates import frames
import astropy.units as u
import math


# Function takes array with chain codes, encode the chain code,
# then splits into array
def decode_and_split(chain_codes):
    codes = []

    for chains in chain_codes:
        if type(chains) is bytes:
            chains = chains.decode("utf-8")

        splitted_chain = list(map(int,str(chains)))
        codes.append(splitted_chain)

    return codes


# Decodes array with files names
def decode_filename(filenames):
    files = []

    for f in filenames:
        if type(f) is bytes:
            f = f.decode("utf-8")

        f = f.replace(":", "_")
        files.append(f)

    return files


# decodes array with dates of observations
def decode_date(dates):
    decoded_dates = []

    for x in dates:
        if type(x) is bytes:
            x = x.decode("utf-8")

        decoded_dates.append(x)

    return decoded_dates


# Takes chain code and position of the first pixel,
# reconstructs object in pixel coordinate, then
# it converts a object from pixel to Carrington system
def get_shape(chain, xpos, ypos, file):
    lon = []
    lat = []
    obj = []
    print(xpos)
    for d in chain:
        if d == 0:
            xpos -= 1
        elif d == 1:
            xpos -= 1
            ypos -= 1
        elif d == 2:
            ypos -= 1
        elif d == 3:
            ypos -= 1
            xpos += 1
        elif d == 4:
            xpos += 1
        elif d == 5:
            ypos += 1
            xpos += 1
        elif d == 6:
            ypos += 1
        elif d == 7:
            ypos += 1
            xpos -= 1

        obj.append([xpos, ypos])
        carr = convert_to_carrington(xpos, ypos, file)
        # Checks if result of convertion is NaN
        if not (math.isnan(carr.lon.deg) or math.isnan(carr.lat.deg)):
            lon.append(carr.lon.deg)  # Add calculated position to array
            lat.append(carr.lat.deg)
        else:
            print("Problem with converting pixel. It will be ignored.")

    return obj, lon, lat


# Function converts from pixel coordinates to Carrington
def convert_to_carrington(x, y, filename):
    filename = "images//" + filename
    map = sunpy.map.Map(filename)
    # convert from pixel to image coordinate system
    cords = map.pixel_to_world(x * u.pix, y * u.pix)
    # convert from picture coordinate frame to carrington
    carr = cords.transform_to(frames.HeliographicCarrington)

    return carr


# Visualise synthesis of features
def display_object(ar_coordinates, sp_coordinates):
    fig, ax = plt.subplots(1, figsize=(10, 5))

    latitude_start = -90
    latitude_end = 90
    longitude_start = 0
    longitude_end = 360
    break_between = 30
    break_between_minor = 10

    ax.set_xlim(longitude_start, longitude_end)
    ax.set_ylim(latitude_start, latitude_end)
    ax.set_xticks(np.arange(longitude_start, longitude_end, break_between_minor), minor=True)
    ax.set_yticks(np.arange(latitude_start, latitude_end, break_between_minor), minor=True)
    ax.set_xticks(np.arange(longitude_start, longitude_end, break_between))
    ax.set_yticks(np.arange(latitude_start, latitude_end, break_between))

    ax.grid(which='both')

    # push grid lines behind the elements
    ax.set_axisbelow(True)

    for c in ar_coordinates:
        plt.fill(c[0], c[1], "g")

    for c in sp_coordinates:
        plt.fill(c[0], c[1], "b")

    plt.show()


if __name__ == '__main__':
    # DataAccess + ObjectPreparation test
    from DataAccess import DataAccess

    ar_data = DataAccess('2003-10-24T00:00:00', '2003-10-24T02:00:00', 'AR', 'SOHO', 'MDI')
    chain = decode_and_split(ar_data.get_chain_code())
    date = decode_date(ar_data.get_date())
    filename = decode_filename(ar_data.get_filename())

    print("CHAIN_CODE", type(chain[0][0]))
    print("DATE", type(date[0]))
    print("FILENAME", type(filename[0]))

    print("decode_and_split() TEST", chain)
    print("decode_date() TEST", date)
    print("decode_filename() TEST", filename)
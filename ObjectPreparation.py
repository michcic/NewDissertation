import numpy as np
import matplotlib as plt
from astropy.coordinates import SkyCoord
import sunpy.map
import matplotlib.pyplot as plt
from sunpy.coordinates import frames
import astropy.units as u
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import math
from descartes import PolygonPatch
from PIL import Image
import cv2
import json
import sqlite3
import Database as db


# Function takes array with chain codes, encode the chain code,
# then splits into array
def encode_and_split(chain_codes):
    print("encode_and_split() START")
    codes = []

    for chains in chain_codes:
        if type(chains) is bytes:
            chains = chains.decode("utf-8")

        splitted_chain = list(map(int,str(chains)))
        codes.append(splitted_chain)

    return codes


def encode_filename(filenames):
    files = []

    for f in filenames:
        if type(f) is bytes:
            f = f.decode("utf-8")

        f = f.replace(":", "_")
        files.append(f)

    return files

def encode_date(dates):
    decoded_dates = []

    for x in dates:
        if type(x) is bytes:
            x = x.decode("utf-8")

        decoded_dates.append(x)

    return decoded_dates


def get_shape(coords, xpos, ypos, file):
    lon = []
    lat = []
    ar = []
    for d in coords:
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

        ar.append([xpos, ypos])
        carr = convert_to_carrington(xpos, ypos, file)
        if not (math.isnan(carr.lon.deg) or math.isnan(carr.lat.deg)):
            lon.append(carr.lon.deg)  # Add calculated position to array
            lat.append(carr.lat.deg)
        else:
            print("Problem with converting pixel. It will be ignored.")

    return ar, lon, lat


# Function converts from pixel coordinates to Carrington
def convert_to_carrington(lon, lat, filename):
    #print("convert_to_carrington() START ")
    #print('long = {0} lat =  {1}'.format(lon, lat))
    filename = "images//" + filename
    map = sunpy.map.Map(filename)
    # convert from pixel to picture coordinate system
    cords = map.pixel_to_world(lon * u.pix, lat * u.pix)
    # convert from picture coordinate frame to carrington
    carr = cords.transform_to(frames.HeliographicCarrington)

    return carr


def display_object(ar_coordinates):
    print("display_object() START ")
    # fig = plt.figure(1, figsize=(10, 5), dpi=90)
    # ax = fig.add_subplot(111)
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
        #plt.scatter(c[0], c[1], marker='o', s=1)
        plt.fill(c[0], c[1])

    # for c in sp_coordinates:
    #     #plt.scatter(c[0], c[1], marker='o', s=1)
    #     plt.fill(c[0], c[1])

    plt.show()
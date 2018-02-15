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
import ObjectPreparation as prep
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename, sp_id, date):
    print("get_shapes() START")
    filename = prep.encode_filename(filename)
    date = prep.encode_date(date)
    all_coords_carr = []
    all_contours_pix = []
    counter = 0
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        s_id = sp_id[counter]
        print("ID", s_id)
        file = filename[counter]
        sp_date = date[counter]
        # Check if exists in database
        result = db.load_sp_from_database(s_id)
        if not result == ([], []):
            print("RESULT NOT NULL")
            # check if object go through the end of map and finish at the beginning
            broken = (max(result[0][0][0]) - min(result[0][0][0])) > 358
            if not broken:
                all_coords_carr += result[0]
                all_contours_pix += (result[1])
        else:
            print("RESULT NULL")
            # Calculate ar contour in pixel, carrington longitude and latitude
            sp_pix, lon, lat = prep.get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)
            print("pix", sp_pix)
            all_contours_pix.append(sp_pix)
            db.add_sunspot_to_database(sp_id=s_id, date=sp_date, carr_coords=[lon, lat], pix_coords=sp_pix)

            broken = max(lon) - min(lon) > 358  # check if object go through the end of map and finish at the beginning
            if not broken:
                all_coords_carr.append([lon, lat])

        counter += 1

    return all_coords_carr, all_contours_pix



# Some of the active regions cover themselfs
# To avoid drawing sunspots more than one time
# We gonna merge sp with id to be sure that is drawn only once
# def merge_sunspotid_with_pixel(sp_id, pixel_coordinates):
#
def make_sp_synthesis(ar_contour, sp_carr):
    # For each active region (after synthesis), every point of
    # each sunspot is tested.
    # If proportion of success tests and the length of
    # array containing sunspots points is > 50%, then
    # sunspot will be drawn on map.
    sunspots = []

    for sp in sp_carr:  # go through each sp
        sp_zip = list(zip(sp[0], sp[1]))
        for ar in ar_contour:  # go through each ar
            ar_zip = list(zip(ar[0], ar[1]))
            ar = Polygon(np.array(ar_zip))
            print("AR in SP SYN", ar)
            result = []
            for p in sp_zip:  # go through each point of sp
                p = Point(p[0], p[1])
                test = ar.contains(p)
                print(test)
                if test:
                    result.append(test)

            proportion = len(result)/len(sp_zip)
            if proportion == 1.0:
                sunspots.append(sp)
                print("ADDED")
                break
            print("Proportion:", len(result)/len(sp_zip))
    print("Sunspots len", len(sunspots))
    return sunspots


def display_object(ar_patch):
    print("display_object() START ")
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
    from descartes import PolygonPatch
    ax.set_axisbelow(True)
    ar_patch = PolygonPatch(ar_patch)
    ax.add_patch(ar_patch)

    plt.show()

if __name__ == '__main__':
    from DataAccess import DataAccess
    data = DataAccess('2003-10-21T00:00:00', '2003-10-24T00:00:00', 'SP')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    carr_synthesis = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                               data.get_filename(), data.get_sp_id(), data.get_date())

    prep.display_object(carr_synthesis)

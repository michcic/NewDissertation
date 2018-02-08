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
                all_contours_pix.append(result[1])
        else:
            print("RESULT NULL")
            # Calculate ar contour in pixel, carrington longitude and latitude
            sp_pix, lon, lat = prep.get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)
            print(sp_pix)
            all_contours_pix.append(sp_pix)
            db.add_sunspot_to_database(sp_id=s_id, date=sp_date, carr_coords=[lon, lat], pix_coords=sp_pix)

            broken = max(lon) - min(lon) > 358  # check if object go through the end of map and finish at the beginning
            if not broken:
                all_coords_carr.append([lon, lat])

        counter += 1

    return all_coords_carr



# Some of the active regions cover themselfs
# To avoid drawing sunspots more than one time
# We gonna merge sp with id to be sure that is drawn only once
# def merge_sunspotid_with_pixel(sp_id, pixel_coordinates):


def make_sp_synthesis(ar_contour, sp_contour):
    # For each active region (after synthesis), every point of
    # each sunspot is tested.
    # If proportion of success tests and the length of
    # array containing sunspots points is > 50%, then
    # sunspot will be drawn on map.
    sunspots = []

    for sp in sp_contour:  # go through each sp
        print("SP", sp)
        for ar in ar_contour:  # go through each ar
            result = []
            ar = np.array(ar)
            for s in sp:  # go through each point of sp
                s = (s[0], s[1])
                point_test = cv2.pointPolygonTest(ar, s, False)
                print(point_test)
                if point_test == 1.0 or 0.0:
                    result.append(point_test)

            proportion = len(result)/len(sp)
            if(proportion == 1.0):
                sunspots.append(sp_contour)
            print("Proportion:", len(result)/len(sp))


if __name__ == '__main__':
    from DataAccess import DataAccess
    data = DataAccess('2010-01-01T00:00:00', '2010-01-01T02:59:00', 'SP')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    carr_synthesis = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                               data.get_filename(), data.get_sp_id(), data.get_date())

    prep.display_object(carr_synthesis)

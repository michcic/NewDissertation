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
def get_shapes(chains, startx, starty, filename, fil_id, date):
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
        f_id = fil_id[counter]
        print("ID", f_id)
        file = filename[counter]
        fil_date = date[counter]
        # Check if exists in database
        result = db.load_sp_from_database(f_id)
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
            fil_pix = get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)
            print("pix", fil_pix)
            all_contours_pix.append(fil_pix)
            #db.add_sunspot_to_database(sp_id=f_id, date=fil_date, carr_coords=[lon, lat], pix_coords=sp_pix)

            # broken = max(lon) - min(lon) > 358  # check if object go through the end of map and finish at the beginning
            # if not broken:
            #     all_coords_carr.append([lon, lat])

        counter += 1

    return all_coords_carr, all_contours_pix


def get_shape(coords, xpos, ypos, file):
    lon = []
    lat = []
    ar = []
    print(xpos)
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


    print("AR", ar)

    return ar



if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2003-09-26T00:00:00', '2003-09-27T00:00:00', 'FIL')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    carr_synthesis, pix = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                     data.get_filename(), data.get_fil_id(), data.get_date())

    npa = np.array([pix[0]], dtype=np.int32)
    print(npa)

    im = Image.new('RGB', (1200, 1200), (255, 255, 255))

    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=npa, color=(0, 0, 0))

    cv2.imshow("", cv_image)
    cv2.waitKey(0)
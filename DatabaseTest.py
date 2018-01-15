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

# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename, track_id, ar_id, date):
    print("get_shapes() START")
    #db.delete_from_database() # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    all_contours_carr = []
    all_contours_pix = []
    filename = encode_filename(filename)
    date = encode_date(date)
    print("date", date)
    all_track = []
    all_intensities = []
    all_coords_carr = []
    counter = 0
    id_checker = -1
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        t_id = track_id[counter]
        a_id = ar_id[counter]
        print("ID", a_id)
        file = filename[counter]
        ar_date = date[counter]
        lon = []
        lat = []
        ar = []
        # Check if exists in database
        result = db.load_from_database(a_id)
        if not result == ([], [], []):
            print("RESULT NOT NULL")
            broken = max(result[2][0][0]) - min(result[2][0][0]) > 355
            if not broken:
                all_track += result[0]
                all_intensities += result[1]
                all_coords_carr += result[2]

        else:
            print("RESULT NULL")
            for d in c:
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

            ar_inten = calculate_ar_intensity(ar, file)
            db.add_to_database(a_id, ar_date, t_id, ar_inten, [lon, lat])

            broken = max(lon) - min(lon) > 355  # check if object go through the end of map and finish at the beginning
            if not broken:
                # print("T_ID", t_id)
                # print("AR_INTEN", ar_inten)
                # print("[lon, lat", [lon, lat])
                all_track.append(t_id)
                all_intensities.append(ar_inten)
                all_coords_carr.append([lon, lat])

        counter += 1

    mer = merge_id_with_ar(all_coords_carr, all_track, all_intensities)
    syn = make_synthesis(mer)

    return syn


# Function converts from pixel coordinates to carrington
def convert_to_carrington(lon, lat, filename):
    #print("convert_to_carrington() START ")
    #print('long = {0} lat =  {1}'.format(lon, lat))
    map = sunpy.map.Map(filename)
    # convert from pixel to picture coordinate system
    cords = map.pixel_to_world(lon * u.pix, lat * u.pix)
    # convert from picture coordinate frame to carrington
    carr = cords.transform_to(frames.HeliographicCarrington)

    return carr


# Creates dictionary where key is track_id of active region
# and values are pixel coordinates of active region
def merge_id_with_ar(coords, track_id, ar_intensity):
    print("merge_id_with_ar START")
    print("track", track_id)
    ar_with_id = {}
    ar_with_id[track_id[0]] = [(ar_intensity[0], coords[0])]

    if len(coords) == len(track_id):
        for x in range(1, len(track_id)):
            if track_id[x] in ar_with_id:
                ar_with_id[track_id[x]].append((ar_intensity[x], coords[x]))
                print("appending")
                print(track_id[x], [track_id[x]])
            else:
                ar_with_id[track_id[x]] = [(ar_intensity[x], coords[x])]
                print("creating")
                print(track_id[x], ar_with_id[track_id[x]])

    return ar_with_id


# Finds pixel coordinates of pixels inside the ar contour
def get_contour_pixels_indexes(contour, image_shape):
    print("get_contour_pixels_indexes() START ")
    contour = np.array(contour)
    im = Image.new('RGB', (4096, 4096), (0, 0, 0))  # create blank image of FITS image size
    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[contour], color=(255, 255, 255))  # draw active region
    indexes = np.where(cv_image == 255)  # get all indexes of active region pixels

    return indexes


# coord - coordinates of contour of ar
# filename - FITS file associated with that ar
def calculate_ar_intensity(coord, filename):
    print("calculate_ar_intensity() START ")
    coord = get_contour_pixels_indexes(coord, filename)  # find all pixels inside the contour
    pixels_number = len(coord)
    intensity = 0.0
    map = sunpy.map.Map(filename)
    # calculate intensity
    for x in range(0, pixels_number):
        intensity = intensity + map.data[coord[0][x]][coord[1][x]]

    return intensity


# Function takes dictionary with AR coords and their track_id
# Goes through dictionary, calculates the intensity of each AR
# makes synthesis by calculating the average of the same AR and by
# choosing the closest AR to the average
def make_synthesis(ar_with_id):
    all_contours_carr = []
    for id, coords in ar_with_id.items():
        regions = []  # contain the intensity values of AR with track_id=id
        ar_intensity_with_cords = {} # key = ar_intensity, value = coords
        for y in coords:
            regions.append(y[0])
            ar_intensity_with_cords[y[0]] = y[1]

        print("id = ", id)
        print("regions = ", regions)
        average = calculate_average_ar_intensity(regions)  # calculate the average intenisty value
        print("average = ", average)
        # from all intensities from track_id = id, choose value which is the closest
        # to the average value
        closest_to_average = min(regions, key=lambda x: abs(x - average))
        maximum = max(regions)
        print("closest", closest_to_average)
        print("max", maximum)
        # synthesis[id] = intensity_cords[closest_to_average]
        synthesis = ar_intensity_with_cords[maximum]

        all_contours_carr.append(synthesis)

    return all_contours_carr


# ar_intensities - array with ar intensities
def calculate_average_ar_intensity(ar_intensities):
    print("calculate_average_ar_intensity() START ")
    sum = 0
    # go through array of pixel values and add them
    for x in ar_intensities:
        sum += x

    average = sum / len(ar_intensities) # calculate average
    return average


# coordinates - array with numpy arrays with coordinates of the contour of the object
# Function creates polygon by using array with coordinates of the contour of the object
def display_object(coordinates):
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

    for c in coordinates:
        #plt.scatter(c[0], c[1], marker='o', s=1)
        plt.fill(c[0], c[1])

    plt.show()


if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2011-07-30T00:00:24', '2011-07-30T03:00:24')

    chain_encoded = encode_and_split(data.get_chain_code())

    cords2 = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(), data.get_filename(), data.get_track_id(), data.get_ar_id(), data.get_date())
    # test = [[123,3556,342,324,234], [144,4], [144,4], [144,4], [144,4], [144,4]]
    # nid = np.array(data.get_track_id())

    # ar_id = merge_id_with_ar(cords2, data.get_track_id(), data.get_filename())
    #
    # syn = make_synthesis(ar_id)

    # a = add_to_database(cords2[0])
    #
    # dat = encode_date(data.get_date())
    # a = db.load_from_database(dat)
    # mer = merge_id_with_ar(a[2], a[0], a[1])
    # syn = make_synthesis(mer)
    display_object(cords2)
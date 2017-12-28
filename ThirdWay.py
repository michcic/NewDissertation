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

# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename):
    print("get_shapes() START")
    contour = []  # Stores contour
    all_contours = []

    counter = 0
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        lon = []
        lat = []
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

            carr = convert_to_carrington(xpos, ypos, filename)
            if not (math.isnan(carr.lon.deg) or math.isnan(carr.lat.deg)):
                contour.append([carr.lon.deg, carr.lat.deg])  # Add position of the pixel to array
                lon.append(carr.lon.deg)
                lat.append(carr.lat.deg)
            else:
                print("Problem with converting one pixel. It will be ignored.")

        all_contours.append((lon, lat))
        np_all_contours = np.array(all_contours)
        counter += 1

    return all_contours


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

# coordinates - array with numpy arrays with coordinates of the contour of the object
# Function creates polygon by using array with coordinates of the contour of the object
def display_object(coordinates):
    print("display_object() START ")
    #print(coordinates)
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

    data = DataAccess('2011-07-30T00:00:24', '2011-07-30T00:00:24')

    chain_encoded = encode_and_split(data.get_chain_code())

    cords2 = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(), "aia1.fits")

    display_object(cords2)




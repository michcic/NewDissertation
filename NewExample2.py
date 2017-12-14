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

            #print('x = {0} y =  {1}'.format(xpos, ypos))
            carr = convert_to_carrington(xpos, ypos, filename)
            if not (math.isnan(carr.lon.deg) or math.isnan(carr.lat.deg)):
                contour.append([carr.lon.deg, carr.lat.deg])  # Add position of the pixel to array
                print(carr.lon.deg, carr.lat.deg)
            else:
                print("Problem with converting one pixel. It will be ignored.")

        all_contours.append(contour)
        np_all_contours = np.array(all_contours)
        counter += 1

    return np_all_contours


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
    fig = plt.figure(1, figsize=(10, 5), dpi=90)
    ax = fig.add_subplot(111)
    patches = []

    for c in coordinates:
        print(c)
        polygon = Polygon(c, True)
        patches.append(polygon)

    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=1.0)

    colors = 100 * np.random.rand(len(patches))
    p.set_array(np.array(colors))

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

    ax.add_collection(p)
    # push grid lines behind the elements
    ax.set_axisbelow(True)
    plt.show()


if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2010-01-01T00:03:02', '2010-01-01T04:03:02')

    chain_encoded = encode_and_split(data.get_chain_code())

    cords2 = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(), "2.fits")

    display_object(cords2)


# # coordinates - numpy array with coordinates of the contour of the object
# # Function convets from pixel coordinates to carrington
# # Return - numpy array with carrington coordinates
# def convert_to_carrington(coordinates, filename):
#     np_carrington_array = []
#
#     for c in coordinates:
#         np_contour = np.array(c)  # Convert list to numpy array
#         rows = np_contour.shape[0]  # get number of rows
#
#         map = sunpy.map.Map(filename)
#
#         cords = []
#         for x in range(0, rows):
#             # convert from pixel to picture coordinate system
#             arcx, arcy = map.pixel_to_data(np_contour[x][0] * u.pix, np_contour[x][1] * u.pix)
#             cord = SkyCoord(arcx, arcy, frame=map.coordinate_frame)
#             # convert from picture coordinate frame to carrington
#             carr = cord.transform_to(frames.HeliographicCarrington)
#
#             cords.append([carr.lon.deg, carr.lat.deg])
#
#         np_carrington = np.array(cords)
#         np_carrington_array.append(np_carrington)
#
#     return np_carrington_array




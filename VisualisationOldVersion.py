import numpy as np
import cv2
import matplotlib as plt
import PIL.ImageOps
from PIL import Image
from astropy.io import fits
from astropy.units import Quantity
import astropy.wcs as wcs
from astropy.coordinates import SkyCoord
import sunpy.map
import matplotlib.pyplot as plt
from sunpy.coordinates import frames
from sunpy.coordinates import transformations
import astropy.units as u
from astropy.utils.data import download_file
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


# Function takes array with chain codes, encode the chain code,
# then splits into array
def encode_and_split(chain_codes):
    codes = []

    for chains in chain_codes:
        if type(chains) is bytes:
            chains = chains.decode("utf-8")

        splitted_chain = list(map(int,str(chains)))
        codes.append(splitted_chain)

    return codes

# Go through array with chain code, draw contour of shape
# using chain code. Then fill the hole of contour.
# directions - array with chain code
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def chain_code(directions, startx, starty):
    xpos = startx  # Starting position of contour
    ypos = starty

    contour = []  # Stores contour

    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for d in directions:
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

        contour.append([xpos, ypos])  # Add position of the pixel to array

    return contour

# coordinates - numpy array with coordinates of the contour of the object
# Function convets from pixel coordinates to carrington
# Return - numpy array with carrington coordinates
def convert_to_carrington(coordinates, filename):
    np_contour = np.array(coordinates)  # Convert list to numpy array
    rows = np_contour.shape[0] # get number of rows

    map = sunpy.map.Map(filename)

    cords = []
    for x in range(0, rows):
        # convert from pixel to picture coordinate system
        arcx, arcy = map.pixel_to_data(np_contour[x][0] * u.pix, np_contour[x][1] * u.pix)
        cord = SkyCoord(arcx, arcy, frame=map.coordinate_frame)
        # convert from picture coordinate frame to carrington
        carr = cord.transform_to(frames.HeliographicCarrington)

        cords.append([carr.lon.deg, carr.lat.deg])

    np_carrington = np.array(cords)
    return np_carrington


# coordinates - array with numpy arrays with coordinates of the contour of the object
# Function creates polygon by using array with coordinates of the contour of the object
def display_object(coordinates):

    fig = plt.figure(1, figsize=(10, 5), dpi=90)
    ax = fig.add_subplot(111)
    patches = []

    for c in coordinates:
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
    # http://voparis-helio.obspm.fr/hfc-gui/showmap.php?date=2010-01-01%2000:03:02&feat=ar&style=pixel
    # http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_AR_HQI&STARTTIME=2010-01-01T00:00:00&ENDTIME=2010-01-01T01:00:00&WHERE=OBSERVAT,SOHO;INSTRUME,MDI
    dir = [4,4,4,4,4,5,4,4,4,5,5,5,5,5,6,5,5,6,5,4,4,4,4,4,4,4,4,4,4,4,4,4,3,4,4,4,4,5,4,4,4,5,4,5,5,4,4,4,3,
           4,3,4,4,4,3,4,4,4,4,4,5,4,4,4,5,4,5,4,5,5,4,4,5,4,4,4,3,3,3,3,4,3,4,4,4,3,4,4,4,4,
           4,5,4,4,4,5,5,5,5,5,5,5,5,5,5,6,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,7,6,7,7,7,0,7,7,7,7,7,7,7,7,6,6,6,6,6,6,6,6,7,
           6,7,6,7,7,7,7,0,7,0,0,7,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,1,0,0,0,0,
           0,0,0,0,0,0,0,1,0,0,1,0,1,1,0,1,1,0,1,0,1,0,1,0,1,1,0,1,1,1,1,0,1,1,1,1,1,2,2,1,2,2,2,1,2,2,2,2,2,2,2,2,3,2,2,1,1,1,1,1,1,
           2,1,2,1,2,2,2,1,2,2,3,2,2,2,3,2,3,2,3,3,3,4,3,4,4,4,3]

    # http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_AR_HQI&STARTTIME=2009-01-11T00:00:00&ENDTIME=2009-01-11T00:04:00&WHERE=OBSERVAT,SOHO;INSTRUME,MDI
    # http://voparis-helio.obspm.fr/hfc-gui/showmap.php?date=2009-01-11%2000:03:02&feat=ar&style=pixel
    dir2 = [4,4,4,4,4,4,5,4,4,4,5,5,5,5,5,5,5,6,5,6,6,6,5,4,4,4,4,4,4,5,4,4,4,5,4,5,4,5,4,5,5,5,5,5,5,5,5,6,5,5,6,5,6,6,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,7,6,7,6,7,0,7,0,7,0,0,0,0,0,0,7,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,1,1,1,1,1,1,2,1,2,1,1,2,1,1,2,1,2,2,1,2,2,2,1,2,2,2,2,3,2,2,2,3,2,3,2,3,3,3,3,3,4,3,3,3,4,3,3,4,3,4,3,4,4,4,3]

    cords = chain_code(dir, 632, 257)
    carr = convert_to_carrington(cords, "2.fits")

    from DataAccess import get_chain_code

    chain = get_chain_code('2009-01-11T00:00:00', '2009-01-17T00:04:00')



    chain_encoded = encode_and_split(chain)

    for x in chain_encoded:
        print(x)
    #
    # cords2 = chain_code(chain_encoded, 359, 675)
    # carr2 = convert_to_carrington(cords2, "4.fits")
    #
    # c = [carr, carr2]
    # display_object(c)




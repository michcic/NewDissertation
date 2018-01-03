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
import math

# Go through array with chain code, draw contour of shape
# using chain code. Then fill the hole of contour.
# directions - array with chain code
def chain_code(directions, xposs, yposs):

    xpos = xposs # Starting position of contour
    ypos = yposs
    map = sunpy.map.Map("aia1.fits")
    contour = []  # Stores contour


    # 0 right
    # 1 down-right
    # 2 down
    # 3 down left
    # 4 left
    # 5 up left
    # 6 up
    # 7 up right
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

        world = map.pixel_to_world(xpos * u.pix, ypos * u.pix)
        contour.append([xpos, ypos])  # Add position of the pixel to array



    np_contour = np.array(contour)  # Convert list to numpy array
    rows = np_contour.shape[0]
    cols = np_contour.shape[1]
    #
    lon = []
    lat = []


    for x in contour:
        lon.append(x[0])
        lat.append(x[1])


    im = Image.new('RGB', (4096, 4096), (0, 0, 0))

    data = map.data
    print(map.data.shape)

    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[np_contour], color=(255, 255, 255))

    pts = np.where(cv_image == 255)

    fig = plt.figure()
    ax = plt.subplot(projection=map)
    points = ax.scatter(pts[1], pts[0])
    artist = map.plot(axes=ax)


    plt.show()




def encode_and_split(chain_codes):
    print("encode_and_split() START")
    codes = []

    for chains in chain_codes:
        if type(chains) is bytes:
            chains = chains.decode("utf-8")

        splitted_chain = list(map(int,str(chains)))
        codes.append(splitted_chain)

    return codes

if __name__ == '__main__':
    # http://voparis-helio.obspm.fr/hfc-gui/showmap.php?date=2010-01-01%2000:03:02&feat=ar&style=pixel
    # http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_AR_HQI&STARTTIME=2010-01-01T00:00:00&ENDTIME=2010-01-01T01:00:00&WHERE=OBSERVAT,SOHO;INSTRUME,MDI
    dir = ['5656565554554555455556556554545454554444544444445444444445445445454544444332333223231222221110111111111100000100100010111000011000000111'
           '100112220711232235334544345654544532212234434343232222222222111211211110000006770666677007010707077677676767767776776776667666666666']
    from DataAccess import DataAccess

    data = DataAccess('2011-07-30T00:00:24', '2011-07-30T00:00:24')

    chain_encoded = encode_and_split(data.get_chain_code())
    chain_code(chain_encoded[0], data.get_pixel_start_x()[0], data.get_pixel_start_y()[0])

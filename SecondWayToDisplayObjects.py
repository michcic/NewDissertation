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
    im = Image.new('RGB', (2048, 2048), (255, 255, 255)) # Create new, empty, white image

    xpos = xposs  # Starting position of contour
    ypos = yposs

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

        #im.putpixel((xpos, ypos), (122, 122, 122))  # Draw pixel
        contour.append([xpos, ypos])  # Add position of the pixel to array


    np_contour = np.array(contour)  # Convert list to numpy array
    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[np_contour], color=(0, 0, 0))

    # cv2.imshow('image', cv_image)
    # cv2.waitKey(0)

    np_contour = np.array(contour)  # Convert list to numpy array
    rows = np_contour.shape[0]
    cols = np_contour.shape[1]

    map = sunpy.map.Map("aia1.fits")

    lon = []
    lat = []
    cords = []
    for x in range(0, rows):
        arcx, arcy = map.pixel_to_data(np_contour[x][0] * u.pix, np_contour[x][1] * u.pix)
        cord = SkyCoord(arcx, arcy, frame=map.coordinate_frame)
        #cordss = map.pixel_to_world(np_contour[x][0] * u.pix, np_contour[x][1] * u.pix)
        carr = cord.transform_to(frames.HeliographicCarrington)


        if not (math.isnan(carr.lon.deg) or math.isnan(carr.lat.deg)):
            contour.append([carr.lon.deg, carr.lat.deg])  # Add position of the pixel to array
            lon.append(carr.lon.deg)
            lat.append(carr.lat.deg)
        else:
            print("problem")

        cords.append([carr.lon.deg, carr.lat.deg])

    np_carrington = np.array(cords)
    #print(lon)

    # w = wcs.WCS('2.fits')
    hdulist = fits.open('eit1.fits')

    # fig, ax = plt.subplots()
    # fig = plt.figure(1, figsize=(90, 360), dpi=90)
    # polygon = Polygon(np_carrington, True)
    # patches = []
    # patches.append(polygon)
    # p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
    #
    # colors = 100 * np.random.rand(len(patches))
    # p.set_array(np.array(colors))
    #
    # #fig = plt.figure(1, figsize=(90, 360), dpi=90)
    #
    # ax.add_collection(p)
    fig = plt.figure(1, figsize=(10, 5), dpi=90)
    ax = fig.add_subplot(111)
    ax.autoscale_view()

    plt.scatter(lon, lat)
    plt.show()

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
    print(chain_encoded)
    chain_code(chain_encoded[0], data.get_pixel_start_x()[0], data.get_pixel_start_y()[0])

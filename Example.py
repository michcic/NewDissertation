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


# Go through array with chain code, draw contour of shape
# using chain code. Then fill the hole of contour.
# directions - array with chain code
def chain_code(directions):
    im = Image.new('RGB', (1024, 1024), (255, 255, 255)) # Create new, empty, white image

    xpos = 632  # Starting position of contour
    ypos = 257

    contour = []  # Stores contour

    # 0 left
    # 1 down-left
    # 2 down
    # 3 down right
    # 4 right
    # 5 up right
    # 6 down
    # 7 up left
    for d in directions:
        if d == 0:
            xpos -= 1
        elif d == 1:
            xpos -= 1
            ypos += 1

        elif d == 2:
            ypos += 1

        elif d == 3:
            ypos += 1
            xpos += 1

        elif d == 4:
            xpos += 1

        elif d == 5:
            ypos -= 1
            xpos += 1

        elif d == 6:
            ypos -= 1

        elif d == 7:
            ypos -= 1
            xpos -= 1

        im.putpixel((xpos, ypos), (122, 122, 122))  # Draw pixel
        contour.append([xpos, ypos])  # Add position of the pixel to array


    np_contour = np.array(contour)  # Convert list to numpy array
    print(np_contour[2])
    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[np_contour], color=(0, 0, 0))

    # cv2.imshow('image', cv_image)
    # cv2.waitKey(0)

    # w = wcs.WCS('2.fits')
    hdulist = fits.open('2.fits')
    map = sunpy.map.Map(cv_image, hdulist[0].header)
    #c = SkyCoord(map.data, frame=map.coordinate_frame)
    #transformations.hpc_to_hcc(map.data, frames.Heliocentric)

    # 238.080001831
    # -505.920013428

    c = SkyCoord(238.080001831*u.arcsec, -505.920013428*u.arcsec, frame=map.coordinate_frame)
    d = c.transform_to(frames.HeliographicCarrington)
    #print(d.lat.deg)

    # map.peek()
    # plt.show()

if __name__ == '__main__':
    # http://voparis-helio.obspm.fr/hfc-gui/showmap.php?date=2010-01-01%2000:03:02&feat=ar&style=pixel
    # http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_AR_HQI&STARTTIME=2010-01-01T00:00:00&ENDTIME=2010-01-01T01:00:00&WHERE=OBSERVAT,SOHO;INSTRUME,MDI
    dir = [4,4,4,4,4,5,4,4,4,5,5,5,5,5,6,5,5,6,5,4,4,4,4,4,4,4,4,4,4,4,4,4,3,4,4,4,4,5,4,4,4,5,4,5,5,4,4,4,3,
           4,3,4,4,4,3,4,4,4,4,4,5,4,4,4,5,4,5,4,5,5,4,4,5,4,4,4,3,3,3,3,4,3,4,4,4,3,4,4,4,4,
           4,5,4,4,4,5,5,5,5,5,5,5,5,5,5,6,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,7,6,7,7,7,0,7,7,7,7,7,7,7,7,6,6,6,6,6,6,6,6,7,
           6,7,6,7,7,7,7,0,7,0,0,7,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,1,0,0,0,0,
           0,0,0,0,0,0,0,1,0,0,1,0,1,1,0,1,1,0,1,0,1,0,1,0,1,1,0,1,1,1,1,0,1,1,1,1,1,2,2,1,2,2,2,1,2,2,2,2,2,2,2,2,3,2,2,1,1,1,1,1,1,
           2,1,2,1,2,2,2,1,2,2,3,2,2,2,3,2,3,2,3,3,3,4,3,4,4,4,3]

    chain_code(dir)

    hdulist = fits.open('2.fits')



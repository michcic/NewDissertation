import astropy
import sunpy.map
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
from astropy.table import Table
from astropy.io import fits
from astropy.units import Quantity
import astropy.wcs as wcs
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from sunpy.coordinates import frames
import math

if __name__ == '__main__':

    hdulist = fits.open('6.fits')
    # for f in hdulist[0].header:
    #     print(f)

    w = wcs.WCS('2.fits')
    #lon, lat = w.all_pix2world([1,2,3,1025], [1,1,1,5], 1)
   # print(lon)

    #print(hdulist[0].header)

    #[-27.7759990692139]
    #[-380.928009033203]
    map = sunpy.map.Map("eit1.fits")
    c = SkyCoord(1110 * u.arcsec, 1730 * u.arcsec)

    print(map.data[0])
    #lon, lat = map.pixel_to_data(1110 * u.pix, 1730 * u.pix)
    #cords = map.pixel_to_world(1110 * u.pix, 1730 * u.pix)
    #c = SkyCoord(cords.lon, cords.lat, frame=map.coordinate_frame)
    #d = cords.transform_to(frames.HeliographicCarrington)

    #print(d.lon.deg)



    #ax = plt.subplot(projection=map)
    #map.peek()
    #ax.plot_coord(lat, 'bx')

    #hdu = hdulist[0]
    #print(hdu.header['CRVAL1'])
    # map.peek()
    # plt.show()




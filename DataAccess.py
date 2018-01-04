import astropy
from astropy.io.votable import parse
from astropy.table import Table
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from astropy.io.votable import parse_single_table
import sunpy.map as sun
import matplotlib.pyplot as plt

import numpy as np
import cv2

class DataAccess:
    def __init__(self, start_date, end_date):
        url = 'http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_AR_HQI&STARTTIME=' + start_date + \
              '&ENDTIME=' + end_date + '&WHERE=OBSERVAT,SDO;INSTRUME,AIA'
        # make url request
        f = urllib.request.urlopen(url)
        # decode
        xmlString = f.read().decode('utf-8')
        #root = ET.fromstring(xmlString)

        # Save VOTable result to file
        with open("output.xml", "w") as f:
            f.write(xmlString)

        # Astropy table, simplify VOTable reading
        self.table = parse_single_table("output.xml")
        #print(self.table.array['FEAT_MAX_INT'])



    def get_carr_central_grav_long(self):
        s = self.table.array['FEAT_CARR_LONG_DEG']
        return s

    def get_carr_central_grav_lat(self):
        s1 = self.table.array['FEAT_CARR_LAT_DEG']
        return s1

    def get_chain_code(self):
        print("get_chain_code START")
        data = self.table.array['FEAT_AREA_DEG2']
        data1 = self.table.array['CC']

        chain_x_arc = self.table.array['CC_X_ARCSEC']
        chain_y_arc = self.table.array['CC_Y_ARCSEC']

        return data1

    def get_pixel_start_x(self):
        print("get_pixel_start_x START")
        chain_start_x = self.table.array['CC_X_PIX']
        return chain_start_x


    def get_pixel_start_y(self):
        print("get_pixel_start_y START")
        chain_start_y = self.table.array['CC_Y_PIX']
        return chain_start_y

    def get_track_id(self):
        print("get_track_id START")
        id = self.table.array['TRACK_ID']
        return id

    def get_noaa_number(self):
        print("get_noaa_number START")
        noaa = self.table.array['NOAA_NUMBER']
        return noaa

    def get_filename(self):
        print("get_filename START")
        filename = self.table.array['FILENAME']
        return filename


if __name__ == '__main__':
    data = DataAccess('2011-07-30T00:00:24', '2011-07-30T04:00:24')
    print(data.get_filename())
    #print(data.get_noaa_number())






import urllib.request
import urllib.parse
from astropy.io.votable import parse_single_table


class DataAccess:
    def __init__(self, start_date, end_date, feature, observatory, instrument):
        url = 'http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_' + feature + '_HQI,&STARTTIME=' + start_date + \
              '&ENDTIME=' + end_date + '&WHERE=OBSERVAT,' + observatory + ';INSTRUME,' + instrument

        # url = 'http://voparis-helio.obspm.fr/helio-hfc/HelioQueryService?FROM=VIEW_' + feature + '_HQI,&STARTTIME=' + start_date + \
        #            '&ENDTIME=' + end_date + '&WHERE=OBSERVAT,SOHO;INSTRUME,MDI'
        # make url request
        f = urllib.request.urlopen(url)
        # decode
        xmlString = f.read().decode('utf-8')

        # Save VOTable result to file
        with open("output.xml", "w") as f:
            f.write(xmlString)

        # Astropy table, simplify VOTable reading
        self.table = parse_single_table("output.xml")

    # Returns the chain codes of objects
    def get_chain_code(self):
        data1 = self.table.array['CC']
        return data1

    # Returns X pixel coordinates from where chain starts to draw
    def get_pixel_start_x(self):
        chain_start_x = self.table.array['CC_X_PIX']
        return chain_start_x

    # Returns Y pixel coordinates from where chain starts to draw
    def get_pixel_start_y(self):
        chain_start_y = self.table.array['CC_Y_PIX']
        return chain_start_y

    # Returns track_id of objects
    def get_track_id(self):
        id = self.table.array['TRACK_ID']
        return id

    # Returns NOAA numbers of objects
    def get_noaa_number(self):
        noaa = self.table.array['NOAA_NUMBER']
        return noaa

    # Returns file names of original FITS images
    # From where objects were taken
    def get_filename(self):
        filename = self.table.array['FILENAME']
        return filename

    # Returns observation dates of objects
    def get_date(self):
        date = self.table.array['DATE_OBS']
        return date

    # Returns active regions id
    def get_ar_id(self):
        id = self.table.array['ID_AR']
        return id

    # Returns sunspots id
    def get_sp_id(self):
        id = self.table.array['ID_SUNSPOT']
        return id

    # Returns filaments id
    def get_fil_id(self):
        id = self.table.array['ID_FIL']
        return id

    # def get_center_x(self):
    #     print("get_center_x START")
    #     x = self.table.array['FEAT_X_PIX']
    #     return x
    #
    # def get_center_y(self):
    #     print("get_center_y START")
    #     y = self.table.array['FEAT_Y_PIX']
    #     return y
    #
    # def get_rectangle_se_x(self):
    #     print("get_rectangle_se_x START")
    #     id = self.table.array['BR_X0_PIX']
    #     return id
    #
    # def get_rectangle_ne_x(self):
    #     print("get_rectangle_ne_x START")
    #     id = self.table.array['BR_X1_PIX']
    #     return id
    #
    # def get_rectangle_se_y(self):
    #     print("get_rectangle_se_y START")
    #     id = self.table.array['BR_Y0_PIX']
    #     return id
    #
    # def get_rectangle_ne_y(self):
    #     print("get_rectangle_ne_y START")
    #     id = self.table.array['BR_Y1_PIX']
    #     return id
    #
    # def get_rectangle_nw_x(self):
    #     print("get_rectangle_nw_x START")
    #     id = self.table.array['BR_X3_PIX']
    #     return id
    #
    # def get_rectangle_nw_y(self):
    #     print("get_rectangle_nw_y START")
    #     id = self.table.array['BR_Y3_PIX']
    #     return id
    #
    # def get_center_x(self):
    #     id = self.table.array['CENTER_X']
    #     return id
    #
    # def get_center_y(self):
    #     id = self.table.array['CENTER_Y']
    #     return id
    #
    # def get_radius(self):
    #     id = self.table.array['R_SUN']
    #     return id
    #
    # def dimension1(self):
    #     id = self.table.array['NAXIS2']
    #     return id


if __name__ == '__main__':
    # DataAccess unit testing
    ar = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'AR', 'SOHO', 'MDI')
    sp = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'SP', 'SOHO', 'MDI')
    fil = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'FIL', 'MEUDON', 'SPECTROHELIOGRAPH')

    print('get_filename() TEST', ar.get_filename())
    print('get_chain_code() TEST', ar.get_chain_code())
    print('get_track_id() TEST', ar.get_track_id())
    print('get_date() TEST', ar.get_date())
    print('get_noaa_number() TEST', ar.get_noaa_number())
    print('get_pixel_start_y() TEST', ar.get_pixel_start_y())
    print('get_pixel_start_x() TEST', ar.get_pixel_start_x())
    print('get_ar_id() TEST', ar.get_ar_id())
    print('get_sp_id() TEST', sp.get_sp_id())
    print('get_fil_id() TEST', fil.get_fil_id())







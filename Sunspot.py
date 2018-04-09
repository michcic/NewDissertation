import numpy as np
from matplotlib.patches import Polygon
import Database as db
import ObjectPreparation as prep
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename, sp_id, date):
    filename = prep.decode_filename(filename)
    date = prep.decode_date(date)
    all_coords_carr = []
    all_contours_pix = []
    counter = 0
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        s_id = sp_id[counter]
        file = filename[counter]
        sp_date = date[counter]
        # Check if exists in database
        result = db.load_sp_from_database(s_id)
        if not result == ([], []):
            # check if object go through the end of map and finish at the beginning
            broken = (max(result[0][0][0]) - min(result[0][0][0])) > 358
            if not broken:
                all_coords_carr += result[0]
                all_contours_pix += (result[1])
        else:
            # Calculate ar contour in pixel, carrington longitude and latitude
            sp_pix, lon, lat = prep.get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)
            all_contours_pix.append(sp_pix)
            db.add_sunspot_to_database(sp_id=s_id, date=sp_date, carr_coords=[lon, lat], pix_coords=sp_pix)

            broken = max(lon) - min(lon) > 358  # check if object go through the end of map and finish at the beginning
            if not broken:
                all_coords_carr.append([lon, lat])

        counter += 1

    return all_coords_carr, all_contours_pix


# Returns synthesis of sunspots
def make_sp_synthesis(ar_contour, sp_carr):
    # For each active region (after synthesis), every point of
    # each sunspot is tested.
    # If proportion of success tests and the length of
    # array containing sunspots points is > 50%, then
    # sunspot will be drawn on map.
    sunspots = []

    for sp in sp_carr:  # go through each sp
        sp_zip = list(zip(sp[0], sp[1]))
        for ar in ar_contour:  # go through each ar
            # To create polygon object longitude and latitude
            # must be stored this way:[(lon,lat),(lon,lat)...]
            ar_zip = list(zip(ar[0], ar[1]))
            ar = Polygon(np.array(ar_zip))

            result = []
            for p in sp_zip:  # go through each point of sp
                p = Point(p[0], p[1])
                test = ar.contains(p)  # Return true if point is inside of the polygon
                if test:
                    result.append(test)

            # if all the points of a sunspot are inside of
            # active region then sunspot is added to array
            proportion = len(result)/len(sp_zip)
            if proportion == 1.0:
                sunspots.append(sp)
                break

    return sunspots


if __name__ == '__main__':
    # Active region + Sunspot testing
    from DataAccess import DataAccess
    import ActiveRegion as ar

    # setting active regions
    data = DataAccess('2003-10-21T00:00:00', '2003-10-24T00:00:00', 'AR', 'SOHO', 'MDI')
    chain_encoded = prep.decode_and_split(data.get_chain_code())
    ar_carr_synthesis, ar_pix_synthesis = ar.get_shapes(chain_encoded, data.get_pixel_start_x(),
                                                        data.get_pixel_start_y(),
                                               data.get_filename(),
                                               data.get_noaa_number(), data.get_ar_id(), data.get_date())

    # setting sunspots
    sp_data = DataAccess('2003-10-21T00:00:00', '2003-10-24T00:00:00', 'SP', 'SOHO', 'MDI')

    sp_chain_encoded = prep.decode_and_split(sp_data.get_chain_code())

    sp_carr, sp_pix = get_shapes(sp_chain_encoded, sp_data.get_pixel_start_x(),
                                 sp_data.get_pixel_start_y(),
                                sp_data.get_filename(), sp_data.get_sp_id(), sp_data.get_date())


    sp_synthesis = make_sp_synthesis(ar_contour=ar_carr_synthesis, sp_carr=sp_carr)

    prep.display_object(ar_carr_synthesis, sp_synthesis)
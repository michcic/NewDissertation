import Database as db
import ObjectPreparation as prep
import sunpy
from functools import reduce


# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename, track_id, fl_id, date):
    print("get_shapes() START")
    filename = prep.encode_filename(filename)
    date = prep.encode_date(date)
    all_track = []
    all_coords_carr = []
    all_contours_pix = []
    counter = 0
    print("STARTX,", startx, "STARTY", starty)
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        t_id = track_id[counter]
        f_id = fl_id[counter]
        print("ID", f_id)
        file = filename[counter]
        fl_date = date[counter]

        # Check if exists in database
        result = db.load_fl_from_database(f_id)
        if not result == ([], [], []):
            print("RESULT NOT NULL")
            # check if object go through the end of map and finish at the beginning
            broken = (max(result[1][0][0]) - min(result[1][0][0])) > 358
            if not broken:
                all_track += result[0]
                all_coords_carr += result[1]
                all_contours_pix.append(result[2])
        else:
            print("RESULT NULL")
            # Calculate ar contour in pixel, carrington longitude and latitude
            pix, lon, lat = prep.get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)
            all_contours_pix.append(pix)
            db.add_fl_to_database(f_id, fl_date, t_id, [lon, lat], pix)

            broken = max(lon) - min(lon) > 358  # check if object go through the end of map and finish at the beginning
            if not broken:
                all_track.append(str(t_id))
                all_coords_carr.append([lon, lat])

        counter += 1

    print("!!!!", len(all_coords_carr), len(all_contours_pix))
    mer = merge_id_with_object(all_coords_carr, all_contours_pix, all_track)
    #carrington_synthesis, pixel_synthesis = make_synthesis(mer)

    return mer


# Creates dictionary where key is track_id of filament
# and values are tuple of carrington coordinates and
# pixel coordinates
def merge_id_with_object(carr_coords, pix_coords, track_id):
    print("merge_id_with_ar START")
    fl_with_id = {}
    fl_with_id[track_id[0]] = [(carr_coords[0], pix_coords[0])]
    if len(carr_coords) == len(track_id):
        for x in range(1, len(track_id)):
            if track_id[x] in fl_with_id:
                fl_with_id[track_id[x]].append((carr_coords[x], pix_coords[x]))
            else:
                fl_with_id[track_id[x]] = [(carr_coords[x], pix_coords[x])]

    return fl_with_id


# # coord - coordinates of contour of ar
# # filename - FITS file associated with that ar
# def calculate_fl_average_intensity(coord, filename):
#     from ActiveRegion import get_contour_pixels_indexes
#     print("calculate_fl_average_intensity() START ")
#     filename = "images//" + filename
#     coord = get_contour_pixels_indexes(coord, filename)  # find all pixels inside the contour
#     pixels_number = len(coord)
#     pixels = []
#     map = sunpy.map.Map(filename)
#     # calculate intensity
#     for x in range(0, pixels_number):
#         pixels.append(map.data[coord[0][x]][coord[1][x]])
#
#     average = reduce(lambda x, y: x + y, pixels) / len(pixels)  # calculate average instensity of pixels
#
#     return average






if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2003-09-27T00:00:00', '2003-09-29T00:00:00', 'FIL')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    mer = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                     data.get_filename(), data.get_track_id(), data.get_fil_id(), data.get_date())

    carrington = []

    for id, coords in mer.items():
        carrington.append(coords[0][0])

    print(carrington)

    prep.display_object(carrington, "")



    # npa = np.array([pix[0]], dtype=np.int32)
    # npa2 = np.array([pix[1]], dtype=np.int32)
    # print(npa)
    #
    # im = Image.new('RGB', (1200, 1200), (255, 255, 255))
    #
    # cv_image = np.array(im)  # convert PIL image to opencv image
    # cv2.fillPoly(cv_image, pts=npa, color=(0, 0, 0))
    # cv2.fillPoly(cv_image, pts=npa2, color=(0, 0, 0))
    #
    # cv2.imshow("", cv_image)
    # cv2.waitKey(0)

    # def get_shape(coords, xpos, ypos, file):

    # lon = []
    #     lat = []
    #     ar = []
    #     print(xpos)
    #     for d in coords:
    #         if d == 0:
    #             xpos -= 1
    #         elif d == 1:
    #             xpos -= 1
    #             ypos -= 1
    #         elif d == 2:
    #             ypos -= 1
    #         elif d == 3:
    #             ypos -= 1
    #             xpos += 1
    #         elif d == 4:
    #             xpos += 1
    #         elif d == 5:
    #             ypos += 1
    #             xpos += 1
    #         elif d == 6:
    #             ypos += 1
    #         elif d == 7:
    #             ypos += 1
    #             xpos -= 1
    #
    #         ar.append([xpos, ypos])
    #
    #
    #     print("AR", ar)
    #
    #     return ar
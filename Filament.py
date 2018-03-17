import Database as db
import ObjectPreparation as prep
import sunpy
from functools import reduce
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt

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
    all_dates = []
    all_chains = []
    all_start_pos = []
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
            #broken = (max(result[1][0][0]) - min(result[1][0][0])) > 358
            broken = False
            if not broken:
                all_track += result[0]
                all_dates += result[1]
                all_chains += result[2]
                all_start_pos.append([xpos,ypos])
                # all_coords_carr += result[1]
                # all_contours_pix.append(result[2])
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

    #print("!!!!", len(all_coords_carr), len(all_contours_pix))
    mer = merge_id_with_object(all_dates, all_chains, all_start_pos, all_track)
    #carrington_synthesis, pixel_synthesis = make_synthesis(mer)

    return mer


# Creates dictionary where key is track_id of filament
# and values are tuple of carrington coordinates and
# pixel coordinates
def merge_id_with_object(dates, chains, start_pos, track_id):
    print("merge_id_with_ar START")
    fl_with_id = {}
    fl_with_id[track_id[0]] = [(dates[0], chains[0], start_pos[0])]
    if len(dates) == len(track_id):
        for x in range(1, len(track_id)):
            if track_id[x] in fl_with_id:
                fl_with_id[track_id[x]].append((dates[x], chains[x], start_pos[x]))
            else:
                fl_with_id[track_id[x]] = [(dates[x], chains[x], start_pos[x])]

    return fl_with_id


def make_synthesis(merged_objects):
    # go through filament chain code, dates, and starting position of pixel
    for id, chain_a_date in merged_objects.items():
        date_with_chain_pos = []
        chain_lenghts = []
        # creates new list with dates, chain code and starting position only
        # also, calculates filaments length
        for single_chain_date_pos in chain_a_date:
            date_with_chain_pos.append([single_chain_date_pos[0], single_chain_date_pos[1], single_chain_date_pos[2]])
            chain_lenghts.append(len(single_chain_date_pos[1]))

        biggest = chain_lenghts.index(max(chain_lenghts))  # return position of the biggest filament

        # reconstruct the biggest filament in the pixel coordinate system
        bigg_fil = get_shape(date_with_chain_pos[biggest][1], date_with_chain_pos[biggest][2][0],
                             date_with_chain_pos[biggest][2][1])

        # there start_pos of the biggest filament need to be used!
        small_fil = []

        # reconstruct the rest of the filaments
        for x in range(0,len(date_with_chain_pos)):
            if not x == biggest:
                smaller = get_shape(date_with_chain_pos[x][1], date_with_chain_pos[biggest][2][0],
                          date_with_chain_pos[biggest][2][1])

                smaller = np.array([smaller], dtype=np.int32)
                # find the smallest x and y
                x = np.min(np.min(smaller, axis=1), axis=0)

                # find the smallest distance between min point of
                # smaller filament and some point of biggest filament!!!
                # WORKS!
                from scipy.spatial.distance import cdist
                npa = np.array(bigg_fil, dtype=np.int32)
                c = cdist(npa, [x]).argmin()

                print("npa", npa)
                dist = int(c)
                print("X", x)
                print("NPA MIN",npa[dist])

                small_fil.append(smaller)

                fig, ax = plt.subplots(1, figsize=(10, 5))

                latitude_start = 0
                latitude_end = 500
                longitude_start = 0
                longitude_end = 500
                break_between = 30
                break_between_minor = 10

                ax.set_xlim(longitude_start, longitude_end)
                ax.set_ylim(latitude_start, latitude_end)
                ax.set_xticks(np.arange(longitude_start, longitude_end, break_between_minor), minor=True)
                ax.set_yticks(np.arange(latitude_start, latitude_end, break_between_minor), minor=True)
                ax.set_xticks(np.arange(longitude_start, longitude_end, break_between))
                ax.set_yticks(np.arange(latitude_start, latitude_end, break_between))

                for c in npa:
                    plt.plot(c[0], c[1], 'go')

                smaller = np.array(smaller, dtype=np.int32)

                for sm in smaller:
                    for s in sm:
                        print("S", s)
                        print("npa", npa)
                        closest = cdist([s], npa).argmin()
                        dist = int(closest)
                        plt.plot(npa[dist][0], npa[dist][1], 'bo')

                for sm in smaller:
                    for s in sm:
                        plt.plot(s[0], s[1], 'ro')

                plt.show()

        # ------------------------------------
        # npa = np.array([bigg_fil], dtype=np.int32)
        # npa2 = np.array([small_fil], dtype=np.int32)
        #
        # im = Image.new('RGB', (1200, 1200), (255, 255, 255))
        #
        # cv_image = np.array(im)  # convert PIL image to opencv image
        # cv2.fillPoly(cv_image, pts=npa, color=(0, 0, 0))
        #
        # from random import randint
        #
        # for npa2 in small_fil:
        #     cv2.fillPoly(cv_image, pts=npa2, color=(0, randint(100,255), randint(50,255)))
        #
        # cv2.imshow("", cv_image)
        # cv2.waitKey(10000)




def get_shape(coords, xpos, ypos):

    lon = []
    lat = []
    ar = []
    print(xpos)
    for d in coords:
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

        ar.append([xpos, ypos])

    print("AR", ar)

    return ar










if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2003-09-27T00:00:00', '2003-09-29T00:00:00', 'FIL')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    mer = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                     data.get_filename(), data.get_track_id(), data.get_fil_id(), data.get_date())

    make_synthesis(mer)

    # for id, coords in mer.items():
    #     carrington.append(coords[0][0])

    # for x in range(1,6):
    #     carrington.append(mer["50988"][x][0])
    #
    # prep.display_object(carrington, "")



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


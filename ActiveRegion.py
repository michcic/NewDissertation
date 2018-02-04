import numpy as np
import sunpy.map
import math
from PIL import Image
import cv2
import Database as db
import ObjectPreparation as prep



# Go through array with chain code, convert to carrington, draw contour of shape
# using chain code.
# chains - 2D array with chain codes
# startx - x coordinate of chain code start position in pixels
# starty - y coordinate of chain code start position in pixels
# return - array with coordinates of the contour of the object
def get_shapes(chains, startx, starty, filename, track_id, ar_id, date):
    print("get_shapes() START")
    #db.delete_from_database() # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    all_contours_pix = []
    filename = prep.encode_filename(filename)
    date = prep.encode_date(date)
    print("chains length", date)
    all_track = []
    all_intensities = []
    all_coords_carr = []
    counter = 0
    # Loop goes through array of chain code
    # and calculates coordinate of each of the pixel of the contour
    for c in chains:
        xpos = startx[counter]  # Starting position of contour
        ypos = starty[counter]
        t_id = track_id[counter]
        a_id = ar_id[counter]
        print("ID", a_id)
        file = filename[counter]
        ar_date = date[counter]
        # Check if exists in database
        result = db.load_from_database(a_id)
        if not result == ([], [], []):
            print("RESULT NOT NULL")
            broken = (max(result[2][0][0]) - min(result[2][0][0])) > 358
            print("MAX - MIN", result[0][0])
            if not broken:
                all_track += result[0]
                all_intensities += result[1]
                all_coords_carr += result[2]
        else:
            print("RESULT NULL")
            ar, lon, lat = prep.get_shape(coords=c, xpos=xpos, ypos=ypos, file=file)

            all_contours_pix.append(ar)
            ar_inten = calculate_ar_intensity(ar, file)
            db.add_to_database(a_id, ar_date, t_id, ar_inten, [lon, lat])

            broken = max(lon) - min(lon) > 355  # check if object go through the end of map and finish at the beginning
            if not broken:
                all_track.append(str(t_id))
                all_intensities.append(ar_inten)
                all_coords_carr.append([lon, lat])

        counter += 1

    mer = merge_id_with_ar(all_coords_carr, all_track, all_intensities)
    syn = make_synthesis(mer)

    return syn

# Creates dictionary where key is track_id of active region
# and values are pixel coordinates of active region
def merge_id_with_ar(coords, track_id, ar_intensity):
    print("merge_id_with_ar START")
    ar_with_id = {}
    ar_with_id[track_id[0]] = [(ar_intensity[0], coords[0])]
    if len(coords) == len(track_id):
        for x in range(1, len(track_id)):
            if track_id[x] in ar_with_id:
                ar_with_id[track_id[x]].append((ar_intensity[x], coords[x]))
            else:
                ar_with_id[track_id[x]] = [(ar_intensity[x], coords[x])]

    return ar_with_id


# Finds pixel coordinates of pixels inside the ar contour
# Ar contour is drawn using pixel coordinate system
# AR is filled with black colour
# Function checks then which pixels are black and reveal indexes of these pixels
def get_contour_pixels_indexes(contour, image_shape):
    print("get_contour_pixels_indexes() START ")
    contour = np.array(contour)
    im = Image.new('RGB', (4096, 4096), (0, 0, 0))  # create blank image of FITS image size
    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[contour], color=(255, 255, 255))  # draw active region
    indexes = np.where(cv_image == 255)  # get all indexes of active region pixels

    return indexes


# coord - coordinates of contour of ar
# filename - FITS file associated with that ar
def calculate_ar_intensity(coord, filename):
    print("calculate_ar_intensity() START ")
    filename = "images//" + filename
    coord = get_contour_pixels_indexes(coord, filename)  # find all pixels inside the contour
    pixels_number = len(coord)
    intensity = 0.0
    map = sunpy.map.Map(filename)
    # calculate intensity
    for x in range(0, pixels_number):
        intensity = intensity + map.data[coord[0][x]][coord[1][x]]

    return intensity


# Function takes dictionary with AR coords and their track_id
# Goes through dictionary, calculates the intensity of each AR
# makes synthesis by calculating the average of the same AR and by
# choosing the closest AR to the average
def make_synthesis(ar_with_id):
    all_contours_carr = []
    for id, coords in ar_with_id.items():
        regions = []  # contain the intensity values of AR with track_id=id
        ar_intensity_with_cords = {}  # key = ar_intensity, value = coords
        for y in coords:
            regions.append(y[0])
            ar_intensity_with_cords[y[0]] = y[1]

        average = calculate_average_ar_intensity(regions)  # calculate the average intenisty value

        # from all intensities from track_id = id, choose value which is the closest
        # to the average value
        closest_to_average = min(regions, key=lambda x: abs(x - average))
        maximum = max(regions)
        synthesis = ar_intensity_with_cords[maximum]

        all_contours_carr.append(synthesis)

    return all_contours_carr


# ar_intensities - array with ar intensities
def calculate_average_ar_intensity(ar_intensities):
    print("calculate_average_ar_intensity() START ")
    sum = 0
    # go through array of pixel values and add them
    for x in ar_intensities:
        sum += x

    average = sum / len(ar_intensities)  # calculate average
    return average


if __name__ == '__main__':
    from DataAccess import DataAccess

    data = DataAccess('2003-09-26T00:00:00', '2003-10-24T00:00:00', 'AR')

    chain_encoded = prep.encode_and_split(data.get_chain_code())

    cords2 = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(), data.get_filename(),
                         data.get_noaa_number(), data.get_ar_id(), data.get_date())

    prep.display_object(cords2)



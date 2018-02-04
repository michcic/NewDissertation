import numpy as np
import cv2

from PIL import Image

import sunpy.map


# Go through array with chain code, draw contour of shape
# using chain code. Then fill the hole of contour.
# directions - array with chain code


def chain_code(directions, xposs, yposs):
    xpos = xposs  # Starting position of contour
    ypos = yposs
    contour = []  # Stores contour

    print("dir", directions)

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

        #world = map.pixel_to_world(xpos * u.pix, ypos * u.pix)
        contour.append([xpos, ypos])  # Add position of the pixel to array

    return contour


def draw(ar_contour, sp):
    ar_np_contour = np.array(ar_contour)  # Convert list to numpy array
    sp_np_contour = np.array(sp)
    im = Image.new('RGB', (800, 800), (255, 255, 255))

    cv_image = np.array(im)  # convert PIL image to opencv image
    cv2.fillPoly(cv_image, pts=[ar_np_contour], color=(0, 0, 0))
    cv2.fillPoly(cv_image, pts=[sp_np_contour], color=(125, 125, 125))

    cv2.imshow("", cv_image)
    cv2.waitKey(0)


def encode_and_split(chain_codes):
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

    from DataAccess import DataAccess

    data = DataAccess('2010-01-01T00:00:00', '2010-01-01T02:59:00', 'AR')
    chain_encoded = encode_and_split([data.get_chain_code()[0]])

    sp_data = DataAccess('2010-01-01T00:00:00', '2010-01-01T02:59:00', 'SP')
    sp_chain = encode_and_split([sp_data.get_chain_code()[0]])

    ar = chain_code(chain_encoded[0], data.get_pixel_start_x()[0], data.get_pixel_start_y()[0])
    sp = chain_code(sp_chain[0], sp_data.get_pixel_start_x()[0], sp_data.get_pixel_start_y()[0])

    draw(ar, sp)

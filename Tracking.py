import cv2
import numpy as np
from Filament import get_shapes
import ObjectPreparation as prep
from DataAccess import DataAccess
import sunpy.map


# data = DataAccess('2003-09-26T00:00:00', '2003-09-27T00:00:00', 'FIL')
#
# chain_encoded = prep.encode_and_split(data.get_chain_code())
#
# carr_synthesis, pix = get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
#                                  data.get_filename(), data.get_fil_id(), data.get_date())

map = sunpy.map.Map("images/mh030927.063210.fits")
img = np.array(map.data, dtype=np.int16)
print(img)
#frame = np.zeros((800, 800, 3), np.uint8)
frame = img
last_measurement = current_measurement = np.array((2,1),
np.float32)
last_prediction = current_prediction = np.zeros((2,1), np.float32)


def mousemove(event, x, y, s, p):
    global frame, current_measurement, measurements, last_measurement, current_prediction, last_prediction
    last_prediction = current_prediction
    last_measurement = current_measurement
    current_measurement = np.array([[np.float32(x)],[np.float32(y)]])
    kalman.correct(current_measurement)
    current_prediction = kalman.predict()
    lmx, lmy = last_measurement[0], last_measurement[1]
    cmx, cmy = current_measurement[0], current_measurement[1]
    lpx, lpy = last_prediction[0], last_prediction[1]
    cpx, cpy = current_prediction[0], current_prediction[1]
    cv2.line(frame, (lmx, lmy), (cmx, cmy), (0,100,0))
    cv2.line(frame, (lpx, lpy), (cpx, cpy), (0,0,200))


if __name__ == '__main__':
    cv2.namedWindow("kalman_tracker")
    cv2.setMouseCallback("kalman_tracker", mousemove)
    kalman = cv2.KalmanFilter(4, 2)
    kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)

    kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
    while True:
        cv2.imshow("kalman_tracker", frame)
        if (cv2.waitKey(30) & 0xFF) == 27:
            break
    cv2.destroyAllWindows()
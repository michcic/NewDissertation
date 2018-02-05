import numpy as np
import matplotlib as plt
from astropy.coordinates import SkyCoord
import sunpy.map
import matplotlib.pyplot as plt
from sunpy.coordinates import frames
import astropy.units as u
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import math
from descartes import PolygonPatch
from PIL import Image
import cv2
import json
import sqlite3
import Database as db


def make_sp_synthesis(ar_contour, sp_contour):
    for ar in ar_contour:
        ar = np.array(ar)
        for sp in sp_contour:
            result = []
            for s in sp:
                s = (s[0], s[1])
                point_test = cv2.pointPolygonTest(ar, s, False)
                print(point_test)
                if point_test == 1.0 or 0.0:
                    result.append(point_test)

            print("Proportion:", len(result)/len(sp))

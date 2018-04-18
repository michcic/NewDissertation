from DataAccess import DataAccess
import ObjectPreparation as prep
import ActiveRegion as ar
import numpy as np
import Database as db


def test_active_regions(ar_id, grav_long, grav_lat):


# Active regions position testing
if __name__ == '__main__':
    ar_data = DataAccess('2003-09-26T00:00:00', '2003-09-26T01:00:00', 'AR', 'SOHO', 'MDI')
    ar_chain_encoded = prep.decode_and_split(ar_data.get_chain_code())
    ar_id = ar_data.get_ar_id()
    ar_centers_lon = ar_data.get_grav_center_long()
    ar_centers_lat = ar_data.get_grav_center_lat()



    ar = ar_carr_synthesis[3]

    prep.display_object([ar], "")

    ar2 = np.array(ar)

    x = ar2[0]
    y = ar2[1]
    length = len(ar2[0]) + len(ar2[1])
    centroid = (sum(x) / len(ar2[0]), sum(y) / len(ar2[1]))
    print(centroid)

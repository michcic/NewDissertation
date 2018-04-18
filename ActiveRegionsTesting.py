from DataAccess import DataAccess
import ObjectPreparation as prep
import ActiveRegion as ar
import numpy as np
import Database as db


def test_active_regions(ar_id, grav_long, grav_lat):
    fail = 0
    success = 0
    for id, long, lat in zip(ar_id, grav_long, grav_lat):
        db_result = db.load_ar_from_database(id)
        carr_coords = db_result[2]

        broken = (max(carr_coords[0][0]) - min(carr_coords[0][0])) > 358

        if not broken:
            x = carr_coords[0][0]
            y = carr_coords[0][1]
            centroid = (sum(x) / len(x), sum(y) / len(y))
            lon_diff = centroid[0] - long
            lat_diff = centroid[1] - lat

            width = max(carr_coords[0][0]) - min(carr_coords[0][0])
            height = max(carr_coords[0][1]) - min(carr_coords[0][1])

            if lon_diff < width and lat_diff < height:
                print("SUCCESS", lon_diff)
                success += 1
            else:
                print("FAIL", lon_diff)
                print("long_center:", long)
                print("calculated:", centroid[0])
                fail += 1
                # prep.display_object(carr_coords, [])

    print("successes = ", success)
    print("fail = ", fail)


# Active regions position testing
if __name__ == '__main__':
    ar_data = DataAccess('2003-09-28T00:00:00', '2003-10-23T01:00:00', 'AR', 'SOHO', 'MDI')
    ar_chain_encoded = prep.decode_and_split(ar_data.get_chain_code())
    ar_id = ar_data.get_ar_id()
    ar_centers_lon = ar_data.get_grav_center_long()
    ar_centers_lat = ar_data.get_grav_center_lat()

    test_active_regions(ar_id, ar_centers_lon, ar_centers_lat)
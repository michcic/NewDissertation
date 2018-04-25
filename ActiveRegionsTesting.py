from DataAccess import DataAccess
import ObjectPreparation as prep
import Database as db


# Functions test Carrington position of active regions
# against gravity center values from HFC database
def test_active_regions(ar_id, grav_long, grav_lat):
    fail = 0
    success = 0
    ignored = 0
    for id, long, lat in zip(ar_id, grav_long, grav_lat):
        db_result = db.load_ar_from_database(id)
        carr_coords = db_result[2]

        # Before testing the object three conditions are checked
        # 1. check if object go through the end of map and finish at the beginning
        # if yes, then ignore
        # Check if gavity_longitude and grav_latitude values from HFC database are valid i.e they
        # are withing appropriate range (long: 0 to 360 and lat: -90 to 90)
        broken = (max(carr_coords[0][0]) - min(carr_coords[0][0])) > 358
        valid_long = 0 <= long <= 360
        valid_lat = -90 <= lat <= 90

        if not broken and valid_lat and valid_long:
            x = carr_coords[0][0]
            y = carr_coords[0][1]
            centroid = (sum(x) / len(x), sum(y) / len(y))
            lon_diff = centroid[0] - long
            lat_diff = centroid[1] - lat

            width = max(carr_coords[0][0]) - min(carr_coords[0][0])
            height = max(carr_coords[0][1]) - min(carr_coords[0][1])

            # if the longitude difference is smaller than width of ar
            # and latitude is smaller than height of ar then is success
            # otherwise fail
            if lon_diff < width and lat_diff < height:
                print("SUCCESS", lon_diff)
                success += 1
            else:
                print("FAIL", lon_diff)
                print("long_center:", long)
                print("calculated:", centroid[0])
                fail += 1
                # prep.display_object(carr_coords, [])
        else:
            ignored += 1

    print("successes = ", success)
    print("fail = ", fail)
    print("ignored = ", ignored)


# Active regions position testing
if __name__ == '__main__':
    ar_data = DataAccess('2003-09-28T00:00:00', '2003-10-23T01:00:00', 'AR', 'SOHO', 'MDI')
    ar_chain_encoded = prep.decode_and_split(ar_data.get_chain_code())
    ar_id = ar_data.get_ar_id()
    ar_centers_lon = ar_data.get_grav_center_long()
    ar_centers_lat = ar_data.get_grav_center_lat()

    test_active_regions(ar_id, ar_centers_lon, ar_centers_lat)
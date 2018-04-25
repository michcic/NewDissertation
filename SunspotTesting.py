from DataAccess import DataAccess
import ObjectPreparation as prep
import Database as db


# Functions test Carrington position of sunspots
# against gravity center values from HFC database
def test_sunspots(sp_id, grav_long, grav_lat):
    fail = 0
    success = 0
    ignored = 0
    for id, long, lat in zip(sp_id, grav_long, grav_lat):
        db_result = db.load_sp_from_database(id)
        carr_coords = db_result[0]

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
            # Calculate center of sp
            centroid = (sum(x) / len(x), sum(y) / len(y))
            # Calculate difference between calculated center and
            # the center value from HFC database
            lon_diff = centroid[0] - long
            lat_diff = centroid[1] - lat

            # if the longitude difference is smaller than 1.0
            # and latitude is smaller than 1.0 then is success
            # otherwise fail
            if lon_diff < 1.0 and lat_diff < 1.0:
                print("SUCCESS", lon_diff)
                success += 1
            else:
                print("FAIL", lon_diff)
                print("long_center:", long)
                print("calculated:", centroid[0])
                fail += 1
        else:
            ignored += 1

    print("successes = ", success)
    print("fail = ", fail)
    print("ignored = ", ignored)


# Sunspots position testing
if __name__ == '__main__':
    sp_data = DataAccess('2003-09-28T00:00:00', '2003-10-23T01:00:00', 'SP', 'SOHO', 'MDI')
    sp_chain_encoded = prep.decode_and_split(sp_data.get_chain_code())
    sp_id = sp_data.get_sp_id()
    sp_centers_lon = sp_data.get_grav_center_long()
    sp_centers_lat = sp_data.get_grav_center_lat()

    test_sunspots(sp_id, sp_centers_lon, sp_centers_lat)
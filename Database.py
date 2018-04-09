import sqlite3
import json
import numpy as np


# Adds active region to database
def add_ar_to_database(ar_id, date, track_id, ar_intensity, carr_coords, pix_coords):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()

    ar_id = str(ar_id)
    date = str(date)
    track_id = str(track_id)

    # curs.execute('''CREATE TABLE ar_test3(ar_id PRIMARY KEY, date, track_id,
    # ar_intensity, coordinates)''')

    carr_js = json.dumps(carr_coords)
    pix_js = json.dumps(pix_coords, cls=Encoder)
    curs.execute('''INSERT INTO ar_test2(ar_id, date, track_id,
     ar_intensity, coordinates, pixel_coordinates) VALUES(?,?,?,?,?,?)''', (ar_id, date, track_id, ar_intensity, carr_js, pix_js, ))

    conn.commit()
    conn.close()


def add_sunspot_to_database(sp_id, date, carr_coords, pix_coords):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()

    sp_id = str(sp_id)
    date = str(date)

    # curs.execute('''CREATE TABLE ar_test3(ar_id PRIMARY KEY, date, track_id,
    #  ar_intensity, coordinates)''')

    carr_js = json.dumps(carr_coords)
    pix_js = json.dumps(pix_coords, cls=Encoder)
    curs.execute('''INSERT INTO sunspots(sp_id, date, carrington_coordinates, pixel_coordinates) VALUES(?,?,?,?)''',
                 (sp_id, date, carr_js, pix_js, ))

    conn.commit()
    conn.close()


def load_ar_from_database(ar_id):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()
    sql = 'SELECT track_id, ar_intensity, coordinates, pixel_coordinates FROM ar_test2 WHERE ar_id = ?'
    id = str(ar_id)

    c = curs.execute(sql, (id,)).fetchall()

    track_id = []
    ar_intensity = []
    decoded_carr_coords = []
    decoded_pix_coords = []

    for result in c:
        track_id.append(result[0])
        ar_intensity.append(result[1])
        decoded_carr_coords.append(json.loads(result[2]))
        decoded_pix_coords.append(json.loads(result[3]))

    conn.close()
    print("TRACK_ID", track_id)

    return track_id, ar_intensity, decoded_carr_coords, decoded_pix_coords


def load_sp_from_database(ar_id):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()
    sql = 'SELECT carrington_coordinates, pixel_coordinates FROM sunspots WHERE sp_id = ?'
    id = str(ar_id)

    c = curs.execute(sql, (id,)).fetchall()

    decoded_carr_coords = []
    decoded_pix_coords = []

    for result in c:
        decoded_carr_coords.append(json.loads(result[0]))
        decoded_pix_coords.append(json.loads(result[1]))

    conn.close()

    return decoded_carr_coords, decoded_pix_coords


# Adds active region to database
def add_fl_to_database(fl_id, date, track_id, carr_coords, pix_coords):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()

    fl_id = str(fl_id)
    date = str(date)
    track_id = str(track_id)

    # encode coordinates to json
    carr_js = json.dumps(carr_coords)
    pix_js = json.dumps(pix_coords, cls=Encoder)
    curs.execute('''INSERT INTO filaments(fl_id, date, track_id, carrington_coordinates, 
        pixel_coordinates) VALUES(?,?,?,?,?)''', (fl_id, date, track_id, carr_js, pix_js,))

    conn.commit()
    conn.close()


# Retrieves filaments data from the database
def load_fl_from_database(fl_id):
    conn = sqlite3.connect('map.db')
    curs = conn.cursor()
    sql = 'SELECT track_id, date, carrington_coordinates  FROM filaments WHERE fl_id = ?'
    id = str(fl_id)

    # execute sql query
    c = curs.execute(sql, (id,)).fetchall()

    track_id = []
    date = []
    decoded_carr_coords = []

    # go through the result and append data to arrays
    for result in c:
        track_id.append(result[0])
        date.append(result[1])
        # decode the coordinates
        decoded_carr_coords.append(json.loads(result[2]))

    conn.close()
    print("TRACK_ID", track_id)

    return track_id, date, decoded_carr_coords


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(Encoder, self).default(obj)


if __name__ == '__main__':
    # DataAccess + Database testing
    from DataAccess import DataAccess

    ar = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'AR', 'SOHO', 'MDI')
    sp = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'SP', 'SOHO', 'MDI')
    fil = DataAccess('2003-10-06T08:54:09', '2003-10-09T10:54:09', 'FIL', 'MEUDON', 'SPECTROHELIOGRAPH')

    ar_id = ar.get_ar_id()[0]
    sp_id = sp.get_sp_id()[0]
    fil_id = fil.get_fil_id()[0]

    print("load_ar_from_database() TEST", load_ar_from_database(ar_id))
    print("load_sp_from_database() TEST", load_sp_from_database(sp_id))
    print("load_fil_from_database() TEST", load_fl_from_database(fil_id))



    # conn = sqlite3.connect('map.db')
    # curs = conn.cursor()
    # # c = curs.execute('''PRAGMA table_info(ar_test2) ''')
    # # curs.execute('''CREATE TABLE filaments(fl_id PRIMARY KEY, date, track_id, carrington_coordinates, pixel_coordinates)''')
    # # curs.execute('''DROP TABLE filaments''')
    # # curs.execute('''DELETE from filaments''')
    # # curs.execute('''ALTER TABLE filaments ADD COLUMN chain_code''')
    # # for r in c:
    # #     print(r)
    # conn.commit()
    # conn.close()
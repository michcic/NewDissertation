import sqlite3
import json
import numpy as np


# Adds active region to database
def add_to_database(ar_id, date, track_id, ar_intensity, carr_coords, pix_coords):
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()

    ar_id = str(ar_id)
    date = str(date)
    track_id = str(track_id)

    # curs.execute('''CREATE TABLE ar_test3(ar_id PRIMARY KEY, date, track_id,
    #  ar_intensity, coordinates)''')

    carr_js = json.dumps(carr_coords)
    pix_js = json.dumps(pix_coords, cls=Encoder)
    curs.execute('''INSERT INTO ar_test2(ar_id, date, track_id,
     ar_intensity, coordinates, pixel_coordinates) VALUES(?,?,?,?,?,?)''', (ar_id, date, track_id, ar_intensity, carr_js, pix_js, ))

    conn.commit()
    conn.close()


def add_sunspot_to_database(sp_id, date, carr_coords, pix_coords):
    conn = sqlite3.connect('ar_carrington.db')
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


def fullfill_pixel_coords(coords, ar_id):
    print("fullfill_pixel_coords START")
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()

    js = json.dumps(coords, cls=Encoder)
    sql = 'UPDATE ar_test2 SET pixel_coordinates = ? WHERE ar_id = ?'

    task = (js, str(ar_id))
    curs.execute(sql, task)

    conn.commit()
    conn.close()


def load_from_database(ar_id):
    conn = sqlite3.connect('ar_carrington.db')
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
    conn = sqlite3.connect('ar_carrington.db')
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


def delete_from_database():
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()
    curs.execute('''DELETE FROM ar_test2 WHERE track_id='11039' ''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()
    #curs.execute('''ALTER TABLE ar_test2 ADD pixel_coordinates''')
    #conn.commit()
    #conn.close()

    c = curs.execute('''PRAGMA table_info(ar_test2)''')
    for r in c:
        print(r)


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
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()
    #c = curs.execute('''PRAGMA table_info(ar_test2) ''')
    curs.execute('''CREATE TABLE sunspots(sp_id PRIMARY KEY, date, carrington_coordinates, pixel_coordinates)''')
    #curs.execute('''DROP TABLE sunspots''')
    # for r in c:
    #     print(r)
    conn.commit()
    conn.close()
import sqlite3
import json


def add_to_database(ar_id, date, track_id, ar_intensity, coords):
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()

    ar_id = str(ar_id)
    date = str(date)
    track_id = str(track_id)

    # curs.execute('''CREATE TABLE ar_test3(ar_id PRIMARY KEY, date, track_id,
    #  ar_intensity, coordinates)''')

    js = json.dumps(coords)
    curs.execute('''INSERT INTO ar_test2(ar_id, date, track_id,
     ar_intensity, coordinates) VALUES(?,?,?,?,?)''', (ar_id, date, track_id, ar_intensity, js, ))

    conn.commit()
    conn.close()


def load_from_database(ar_id):
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()
    sql = 'SELECT track_id, ar_intensity, coordinates FROM ar_test2 WHERE ar_id = ?'
    id = str(ar_id)

    c = curs.execute(sql, (id,)).fetchall()

    track_id = []
    ar_intensity = []
    decoded_coords = []

    for result in c:
        track_id.append(result[0])
        ar_intensity.append(result[1])
        decoded_coords.append(json.loads(result[2]))

    conn.close()
    print("TRACK_ID", track_id)

    return track_id, ar_intensity, decoded_coords


def delete_from_database():
    conn = sqlite3.connect('ar_carrington.db')
    curs = conn.cursor()
    curs.execute('''DELETE FROM ar_test2 WHERE track_id='11039' ''')
    conn.commit()
    conn.close()
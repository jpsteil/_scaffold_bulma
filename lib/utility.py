from ..common import db
import csv
import os
import sqlite3
from dateutil.parser import parse

def export_to_csv():
    left = [
        db.speaker.on(db.session.speaker == db.speaker.id),
        db.room.on(db.session.room == db.room.id),
    ]

    with open(
        os.path.join("/home", "jim", "Documents", "sessions.csv"), "w"
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', lineterminator="\r\n", quotechar='"')
        for row in db(db.session.id > 0).select(
            db.session.ALL, db.speaker.ALL, db.room.ALL, left=left
        ):
            csv_writer.writerow(
                [
                    row.session.start_time.strftime("%m/%d/%Y %H:%M:%S"),
                    row.session.name,
                    row.session.description,
                    row.speaker.first_name,
                    row.speaker.last_name,
                    row.speaker.company,
                    row.speaker.title,
                    row.speaker.bio,
                    row.room.name,
                ]
            )

def import_data():
    conn = sqlite3.connect(os.path.join('/home', 'jim', 'Documents', 'wmcpa.db'))
    c = conn.cursor()

    #  create speaker table
    sql = "DROP TABLE IF EXISTS session"
    c.execute(sql)
    sql = "DROP TABLE IF EXISTS room"
    c.execute(sql)
    sql = "DROP TABLE IF EXISTS speaker"
    c.execute(sql)

    sql = """
    CREATE TABLE speaker 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
    first_name CHAR(20), 
    last_name CHAR(20), 
    bio TEXT, 
    title CHAR(100), 
    company CHAR(100))
    """
    c.execute(sql)

    sql = """
    CREATE TABLE room 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name CHAR(100))
    """
    c.execute(sql)

    sql = """
    CREATE TABLE session 
    ("id" INTEGER PRIMARY KEY AUTOINCREMENT, 
    "start_time" TIMESTAMP, 
    "name" CHAR(100), 
    "description" TEXT, 
    "speaker" INTEGER REFERENCES speaker (id) ON DELETE CASCADE ON UPDATE CASCADE, 
    "room" INTEGER REFERENCES room (id) ON DELETE CASCADE ON UPDATE CASCADE)
    """
    c.execute(sql)

    conn.commit()

    with open(os.path.join("/home", "jim", "Documents", "sessions.csv"), "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csv_reader:
            start_time = row[0]
            session_name = row[1]
            session_description = row[2]
            speaker_first = row[3]
            speaker_last = row[4]
            speaker_company = row[5]
            speaker_title =row[6]
            speaker_bio = row[7]
            room = row[8]

            #  check for room
            room_id = None
            c.execute("SELECT id FROM room WHERE name = ?", [room])
            for room_id in c.fetchall():
                room_id = room_id[0]

            if not room_id:
                c.execute('INSERT INTO room (name) VALUES(?)', [room])
                room_id = c.lastrowid
            
            #  check for speaker
            speaker_id = None
            c.execute('SELECT id FROM speaker where first_name = ? and last_name = ?', [speaker_first, speaker_last])
            for speaker_id in c.fetchall():
                speaker_id = speaker_id[0]

            if not speaker_id:
                c.execute("INSERT INTO speaker (first_name, last_name, company, title, bio) VALUES (?, ?, ?, ?, ?)", [speaker_first, speaker_last, speaker_company, speaker_title, speaker_bio])
                speaker_id = c.lastrowid
            
            #  build the session
            c.execute('INSERT INTO session ("start_time", name, description, speaker, room) VALUES (?, ?, ?, ?, ?)', [parse(start_time).strftime('%Y-%m-%d %I:%M:00'), session_name, session_description, speaker_id, room_id])
    conn.commit()
    # 

    c.close()
    conn.close()

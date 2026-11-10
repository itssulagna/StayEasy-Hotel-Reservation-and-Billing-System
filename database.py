import sqlite3
import csv

conn = sqlite3.connect("stayeasy.db")
cursor=conn.cursor()
cursor.execute("create table if not exists guest_details(name varchar(50), mob_no varchar(20) primary key, email text)")
conn.commit()

cursor.execute("create table if not exists rooms(room_no int primary key, room_type text, floor int)")
with open("rooms.csv", "r") as file:
    data = csv.DictReader(file)
    for row in data:
        try:
            if row["room_no"].strip() == "":
                raise ValueError("Room number is blank")

            cursor.execute("insert or ignore into rooms(room_no, room_type, floor) values(?,?,?)",
                           (int(row["room_no"]), row["room_type"].strip().lower(), int(row["floor"])))

        except (ValueError, TypeError) as e:
            with open("app.log", "a") as log:
                log.write(f"Invalid room record: {row} - {e}\n")

    conn.commit()


rooms=[]
with open("rooms.csv", "r") as file:
    data=csv.DictReader(file)
    for line in data:
        if line["room_no"].strip() != "":
            rooms.append(line)
# print(rooms)

# cursor.execute("create table if not exists bookings(booking_id integer primary key autoincrement, name text,mobile text,email text, room_no int, no_of_guest int, check_in text, check_out text,status text, total_amount int )")
cursor.execute("create table if not exists bookings(booking_id integer primary key autoincrement, name text, mobile text, email text, room_no integer, no_of_guest integer, check_in text, check_out text, status text, total_amount REAL, refund_amount REAL, retained_amount REAL)")
cursor.execute("UPDATE bookings SET refund_amount = ?, retained_amount = ? WHERE booking_id = ?",
               (3360, 3360, 1))

cursor.execute("UPDATE bookings SET refund_amount = ?, retained_amount = ? WHERE booking_id = ?",
               (16461, 16461, 2))
conn.commit()



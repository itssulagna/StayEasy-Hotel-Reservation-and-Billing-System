import csv
from exceptions import InvalidInputError
from exceptions import RoomUnavailable
from exceptions import InvalidDate
from models import Guest
from database import conn, cursor
from database import rooms
from datetime import datetime, date
# from menu import display_menu

from pricing import calculate_booking_amount
# from menu import display_menu
# display_menu()

def guest_data():
    guest_list = []

    while True:
        try:
            name = input("Enter name: ").strip().lower()

            if name == "":
                raise InvalidInputError("Name cannot be blank")

            mob_no = input("Enter mobile number: ").strip()

            if mob_no == "":
                raise InvalidInputError("Mobile number cannot be blank")

            if not mob_no.isdigit() or len(mob_no) != 10 or not mob_no.startswith(("6", "7", "8", "9")):
                raise InvalidInputError("Invalid mobile number")

            email = input("Enter email: ").strip().lower()

            if "@" not in email or "." not in email.split("@")[-1]:
                raise InvalidInputError("Invalid email ID")


            guest = Guest(name, mob_no, email)

            guest_list.append(guest)

            cursor.execute("select * from guest_details where mob_no=?",(mob_no,))

            existing_guest = cursor.fetchone()

            if existing_guest is None:

                cursor.execute("""insert into guest_details(name, mob_no, email )values(?,?,?) """,(name, mob_no, email))

                conn.commit()

            else:

                print("Returning Guest Found")

            # cursor.execute("insert into guest_details(name, mob_no, email) values(?,?,?)", (name, mob_no, email))
            # conn.commit()
            cursor.execute("select * from guest_details")
            data = cursor.fetchall()
            print(data)
            return name, mob_no, email


        except InvalidInputError as e:
            print(e)

        except ValueError:
            print("Enter a valid number")
# guest_data()

# cursor.execute("""insert into bookings(name,mobile,email,room_no,no_of_guest,check_in,check_out,status,total_amount) values(?,?,?,?,?,?,?,?,?)
# """, ("Test", "9876543210", "test@gmail.com", 101, 2,
#       "2026-11-10", "2026-11-13", "CONFIRMED", 10000))
# cursor.execute("drop table bookings")
# conn.commit()


def date_validation(check_in, check_out):
    while True:
        try:
            check_in=datetime.strptime(check_in,"%d-%m-%Y").date()
            check_out=datetime.strptime(check_out,"%d-%m-%Y").date()

        except ValueError:
            raise InvalidDate("Invalid date")

        if check_out <= check_in:
            raise InvalidDate("check out date should be greater than check in")

        today = date.today()
        if check_in < today:
            raise InvalidDate("Check in date cannot be less than todays day")


        no_of_nights = (check_out - check_in).days

        if no_of_nights < 1 or no_of_nights > 30:
            raise InvalidDate( "Stay must be between 1 and 30 nights" )

        days_difference = (check_in - today).days

        if days_difference > 180:
            raise InvalidDate("Check-in cannot be more than 180 days from today")


        return check_in, check_out


def validate_room_and_guests(room_type, no_of_guest):
    room_data = {
        "standard": 2,
        "deluxe": 3,
        "suite": 4
    }

    room_type = room_type.lower()
    if room_type not in room_data:
        raise InvalidInputError("Invalid room type")
    if no_of_guest < 1:
        raise InvalidInputError("Guests must be at least 1")
    if no_of_guest > room_data[room_type]:
        raise InvalidInputError("Reaching maximum no of guest: for standard 2 max, deluxe 3, suite 4")
    return True


def search_available_room(room_type, check_in, check_out):
    check_in = datetime.strptime(check_in, "%d-%m-%Y").date()
    check_out = datetime.strptime(check_out, "%d-%m-%Y").date()

    cursor.execute("""SELECT room_no FROM rooms WHERE lower(room_type) = ? ORDER BY room_no""", (room_type.lower(),))

    rooms = cursor.fetchall()

    for room in rooms:
        room_no = room[0]

        cursor.execute("""SELECT check_in, check_out FROM bookings WHERE room_no = ? AND status IN ('CONFIRMED', 'CHECKED_IN')""", (room_no,))

        bookings = cursor.fetchall()

        available = True

        for booking in bookings:
            booked_check_in = datetime.strptime(booking[0], "%d-%m-%Y").date()
            booked_check_out = datetime.strptime(booking[1], "%d-%m-%Y").date()

            if check_in < booked_check_out and check_out > booked_check_in:
                available = False
                break

        if available:
            return room_no

    raise RoomUnavailable("No rooms available for selected dates")


def create_booking():

    while True:

        try:

            room_type = input("Enter room type: ").strip().lower()

            no_of_guest = int( input("Enter number of guests: "))

            check_in = input( "Enter check-in date: ")

            check_out = input("Enter check-out date: ")

            check_in, check_out = date_validation(check_in,check_out)

            validate_room_and_guests(room_type,no_of_guest)

            room_no = search_available_room(room_type, check_in.strftime("%d-%m-%Y"), check_out.strftime("%d-%m-%Y"))

            print("Room Allotted:", room_no)

            print("\nBOOKING DETAILS")
            print(f"Room Type : {room_type}")
            print(f"Room No   : {room_no}")
            print(f"Guests    : {no_of_guest}")
            print(f"Check In  : {check_in}")
            print(f"Check Out : {check_out}")

  
            name, mobile, email = guest_data()

            bill = calculate_booking_amount(
                room_type,
                check_in,
                check_out,
                no_of_guest,
                0,     
                False  
            )

            print("\n******* AMOUNT DETAILS ********")

            print("Room Charge:",
                  bill["room_charge"])

            print("Extra Guest Charge:",
                  bill["extra_guest_charge"])

            print("Breakfast Charge:",
                  bill["breakfast_charge"])

            print("Long Stay Discount:",
                  bill["long_stay_discount"])

            print("Loyalty Discount:",
                  bill["loyalty_discount"])

            print("GST:",
                  bill["gst_amount"])

            print("Total Amount:",
                  bill["total_amount"])

            total_amount = bill["total_amount"]

            cursor.execute("""INSERT INTO bookings(name,mobile, email, room_no, no_of_guest, check_in, check_out, status, total_amount) VALUES(?,?,?,?,?,?,?,?,?)""",(name,mobile,email,room_no, no_of_guest, check_in.strftime("%d-%m-%Y"),check_out.strftime("%d-%m-%Y"),"CONFIRMED",total_amount))

            conn.commit()
            cursor.execute("""
            SELECT booking_id
            FROM bookings
            ORDER BY booking_id DESC
            LIMIT 1
            """)

            booking_id = cursor.fetchone()[0]

            print("Booking ID :", booking_id)

            break

        except (InvalidDate,InvalidInputError,RoomUnavailable ) as e:

            print(e)

        except ValueError:

            print("Enter valid input")



def view_booking_details():

    booking_id = input("Enter Booking ID: " ).strip()
    try:

        cursor.execute("""SELECT * FROM bookings WHERE booking_id = ?""", (booking_id,))

        booking = cursor.fetchone()
        if booking is None:
            print("Booking not found")
            return

        print("\n******* BOOKING DETAILS *******")

        print("Booking ID :", booking[0])

        print("Name :", booking[1])

        print("Mobile :", booking[2])

        print("Email :", booking[3])

        print("Room No :", booking[4])

        print("No Of Guests :", booking[5])

        print("Check In :", booking[6])

        print("Check Out :", booking[7])

        print("Status :", booking[8])

        print("Total Amount :", booking[9])

    except ValueError:

        print("Invalid Booking ID")


def check_in():

    booking_id = input("Enter booking id: ")

    cursor.execute("""SELECT booking_id,status,check_in FROM bookings WHERE booking_id=? """,(booking_id,))
    data = cursor.fetchone()

    if data is None:
        print("Booking not found")
        return

    status = data[1]

    if status != "CONFIRMED":
        print("Only confirmed bookings can check in")
        return

    today = date.today()

    check_in_date = datetime.strptime(data[2],"%d-%m-%Y").date()

    if today != check_in_date:
        print("Check in allowed only on check in date")
        return

    cursor.execute("""UPDATE bookings SET status=? WHERE booking_id=? """,("CHECKED_IN",booking_id))

    conn.commit()

    print("Check in successful")



from datetime import datetime, date


def cancel_booking():
    try:

        booking_id = input("Enter Booking ID: " ).strip()

        cursor.execute("""SELECT booking_id,status,check_in,total_amount FROM bookings WHERE booking_id = ?""", (booking_id,))
        booking = cursor.fetchone()

        if booking is None:
            print("Booking not found")
            return
        status = booking[1]
        if status != "CONFIRMED":
            print( "Only CONFIRMED bookings can be cancelled")
            return

        check_in_date = datetime.strptime(booking[2],"%d-%m-%Y").date()

        today = date.today()

        days_before = (check_in_date - today).days

        total_amount = float(booking[3])

        if days_before >= 7:

            refund_amount = total_amount

        elif 2 <= days_before <= 6:

            refund_amount = total_amount * 0.50

        else:

            refund_amount = 0

        retained_amount = total_amount - refund_amount

        cursor.execute("""UPDATE bookings SET status = ?, refund_amount = ?, retained_amount = ? WHERE booking_id = ?""",("CANCELLED", refund_amount, retained_amount, booking_id))
        conn.commit()

        print("\nBooking Cancelled Successfully")

        print( f"Refund Amount :{refund_amount}")

    except ValueError:

        print("Invalid Booking ID")



def check_out():
    try:
        booking_id = input("Enter Booking ID: ").strip()

        cursor.execute("""SELECT * FROM bookings WHERE booking_id = ?""", (booking_id,))

        booking = cursor.fetchone()

        if booking is None:
            print("Booking not found")
            return
        status = booking[8]

        if status != "CHECKED_IN":

            print("Only CHECKED_IN bookings can be checked out" )
            return

        cursor.execute("""UPDATE bookings SET status = ? WHERE booking_id = ?""", ("CHECKED_OUT", booking_id))

        conn.commit()

        print("Check Out Successful")

    except ValueError:

        print("Invalid Booking ID")


def generate_invoice(booking):

    booking_id = booking[0]
    invoice = open(f"BK{booking_id}.txt", "w")
    invoice.write("******** STAYEASY HOTEL ********\n\n")

    invoice.write( f"Booking ID : {booking[0]}\n" )

    invoice.write(f"Guest Name : {booking[1]}\n")

    invoice.write(f"Mobile Number : {booking[2]}\n")

    invoice.write(f"Email : {booking[3]}\n")

    invoice.write(f"Room Number : {booking[4]}\n")

    invoice.write(f"Number Of Guests : {booking[5]}\n")

    invoice.write(f"Check In Date : {booking[6]}\n")

    invoice.write(f"Check Out Date : {booking[7]}\n")

    invoice.write( f"Booking Status : {booking[8]}\n" )

    invoice.write(f"Total Amount : ₹{booking[9]}\n")

    invoice.write("\nThank You For Staying With StayEasy")

    invoice.close()

    print("Invoice Generated Successfully")

def check_out():

    try:

        booking_id = input("Enter Booking ID: " ).strip()

        cursor.execute("""SELECT * FROM bookings WHERE booking_id = ? """,(booking_id,))
        booking = cursor.fetchone()
        if booking is None:
            print("Booking not found")
            return
        if booking[8] != "CHECKED_IN":

            print("Only checked in  bookings can be checked out")
            return

        generate_invoice(booking)

        cursor.execute("""UPDATE bookings SET status = ? WHERE booking_id = ?""",("CHECKED_OUT", booking_id))
        conn.commit()

        print("Check Out Successful")

    except ValueError:
        print("Invalid Booking ID")



def guest_history():

    mobile = input("Enter Mobile Number: ").strip()

    cursor.execute("""SELECT * FROM bookings WHERE mobile = ?""",(mobile,))
    bookings = cursor.fetchall()

    if bookings == []:
        print("No Stay History Found")
        return

    print("\n***** GUEST STAY HISTORY *****\n")

    for booking in bookings:

        print("Booking ID:", booking[0])
        print("Name:", booking[1])
        print("Mobile:", booking[2])
        print("Email:", booking[3])
        print("Room No:", booking[4])
        print("Guests:", booking[5])
        print("Check In:", booking[6])
        print("Check Out:", booking[7])
        print("Status:", booking[8])
        print("Total Amount:", booking[9])

        print("----"*15)


import csv


def export_bookings():

    cursor.execute(""" SELECT * FROM bookings """)
    bookings = cursor.fetchall()

    file = open("bookings_export.csv","w",newline="")
    writer = csv.writer(file)
    writer.writerow(["booking_id","name","mobile","email","room_no","no_of_guest","check_in","check_out","status","total_amount" ])

    for booking in bookings:
        writer.writerow(booking)
    file.close()

    print("Bookings Exported Successfully" )


from datetime import datetime, timedelta


def occupancy_report():
    try:
        start_date = input("Enter start date: ").strip()
        end_date = input("Enter end date : ").strip()
        start_date = datetime.strptime(start_date,"%d-%m-%Y").date()
        end_date = datetime.strptime(end_date,"%d-%m-%Y" ).date()
        cursor.execute(""" SELECT COUNT(*) FROM rooms""")

        total_rooms = cursor.fetchone()[0]
        current_date = start_date

        total_percentage = 0
        number_of_days = 0

        print("\n***** OCCUPANCY REPORT *****\n")

        while current_date <= end_date:

            occupied_rooms = 0

            cursor.execute("""SELECT room_no,check_in,check_out,status FROM bookings WHERE status IN ('CONFIRMED','CHECKED_IN')""")

            bookings = cursor.fetchall()

            for booking in bookings:

                check_in = datetime.strptime(booking[1],"%d-%m-%Y" ).date()

                check_out = datetime.strptime(booking[2],"%d-%m-%Y").date()

                if check_in <= current_date < check_out:

                    occupied_rooms += 1

            occupancy_percentage = (occupied_rooms / total_rooms) * 100

            print( current_date," | Occupied:", occupied_rooms," | Total:", total_rooms," | Occupancy:",round(occupancy_percentage, 2), "%")

            total_percentage += occupancy_percentage

            number_of_days += 1

            current_date = current_date + timedelta(days=1)

        average_occupancy = (total_percentage /number_of_days)

        print("\nAverage Occupancy:", round(average_occupancy, 2),"%" )

    except ValueError:

        print("Invalid Date Format")

def revenue_report():

    room_types = ["standard", "deluxe", "suite"]

    print("\n******** REVENUE REPORT ********\n")

    for room_type in room_types:

        cursor.execute("""SELECT COUNT(*), SUM(total_amount) FROM bookings
        WHERE status='CHECKED_OUT'
        AND room_no IN (SELECT room_no FROM rooms WHERE lower(room_type)=?)""",(room_type,))

        data = cursor.fetchone()
        completed_stays = data[0]
        revenue = data[1]

        if revenue is None:
            revenue = 0

        cursor.execute("""SELECT SUM(retained_amount) FROM bookings
        WHERE status='CANCELLED'
        AND room_no IN (SELECT room_no FROM rooms WHERE lower(room_type)=?)""",(room_type,))

        cancellation_retained = cursor.fetchone()[0]

        if cancellation_retained is None:
            cancellation_retained = 0

        print(f"Room Type : {room_type}")
        print(f"Completed Stays : {completed_stays}")
        print(f"Revenue : ₹{revenue}")
        # print(f"GST Collected : Calculate from completed invoices")
        print(f"Cancellation Amount Retained : ₹{cancellation_retained}")

        print("--"*15)


        cursor.execute("SELECT booking_id, room_no, total_amount, refund_amount, retained_amount, status FROM bookings")
        print(cursor.fetchall())


# display_menu()
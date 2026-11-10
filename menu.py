from exceptions import InvalidInputError, RoomUnavailable, InvalidDate
from datetime import datetime
from database import rooms, cursor
import main
# from main import guest_data
# from main import create_booking


def display_menu():
    while True:
        print("*******WELCOME TO STAYEASY********")
        print("1. Search room availability")
        print("2. Create booking")
        print("3. Check in")
        print("4. Check out / generate invoice")
        print("5. Cancel booking")
        print("6. View booking details")
        print("7. Guest stay history by mobile number")
        print("8. Occupancy report for a date range")
        print("9. Revenue report")
        print("10. Export all bookings to CSV")
        print("11. Exit")
        try:
            choice = int(input("Enter your choice: "))

            if choice == 1:
                room_availability_search()

            elif choice == 2:
               main.create_booking()
                # guest_data()

            elif choice == 3:
                main.check_in()

            elif choice == 4:
                main.check_out()

            elif choice == 5:
                main.cancel_booking()

            elif choice == 6:
                print("********booking details********")
                main.view_booking_details()

            elif choice == 7:
                main.guest_history()

            elif choice == 8:
                main.occupancy_report()

            elif choice == 9:
                main.revenue_report()

            elif choice == 10:
               main.export_bookings()

            elif choice == 11:
                print("Thank you for using StayEasy!")
                break

            else:
                print("Invalid choice. Please select between 1 and 11.")
 
        except ValueError:
            print("Please enter a valid number.")

   

def room_availability_search():
    while True:
        try:
            room_type = input("Enter room you need: ").strip().lower()

            if room_type not in ["standard", "deluxe", "suite"]:
                raise RoomUnavailable("Room types are standard, deluxe and suite")
            break
        except RoomUnavailable as r:
            print(r)

    while True:
        try:
            check_in = input("Enter check-in date: ").strip()
            check_in = datetime.strptime(check_in, "%d-%m-%Y").date()
            today = datetime.today().date()

            if check_in < today or (check_in - today).days > 180:
                raise InvalidDate("Enter valid check-in date")
            break

        except InvalidDate as d:
            print(d)
        except ValueError:
            print("Invalid date format. Use DD-MM-YYYY.")

    while True:
        try:
            check_out = input("Enter check-out date: ").strip()
            check_out = datetime.strptime(check_out,"%d-%m-%Y" ).date()

            if check_out <= check_in:
                raise InvalidDate("Check-out must be after check-in")

            if (check_out - check_in).days > 30:
                raise InvalidDate("Stay can be upto 30 days")
            break
        except InvalidDate as d:
            print(d)
        except ValueError:
            print("Invalid date format.")

    while True:
        try:
            no_of_guest = int(input("Enter number of guests: "))

            if no_of_guest < 1:
                raise InvalidInputError("Enter valid number of guests")
            break
        except InvalidInputError as e:
            print(e)
        except ValueError:
            print("Please enter a valid number.")

    print("\nSearch details:")
    print("Room Type:", room_type)
    print("Check-in:", check_in)
    print("Check-out:", check_out)
    print("Number of Guests:", no_of_guest)

    room_capacity={
        "standard":2,
        "deluxe":3,
        "suite":4
    }

    if no_of_guest > room_capacity[room_type]:
        print( f"{room_type} room can accommodate only "f"{room_capacity[room_type]} guests")
        return

    cursor.execute("select room_no, check_in, check_out from bookings where status in (?,?)",("CONFIRMED", "CHECKED_IN"))
    booking_data=cursor.fetchall()
    
    available_rooms=[]
    for room in rooms:
        if room["room_type"].strip().lower() ==room_type:
            room_no =int(room["room_no"])
            available=True

            for booking in booking_data:
                booked_room_no=booking[0]
                booked_check_in = datetime.strptime(booking[1], "%d-%m-%Y").date()
                booked_check_out=datetime.strptime(booking[2],"%d-%m-%Y").date()
                if room_no == booked_room_no:
                    if check_in < booked_check_out and check_out > booked_check_in:
                        available = False
                        break
            if available:
                    available_rooms.append(room_no)
    # print(available_rooms)
    if available_rooms:
        # print("Available Rooms: ")
        lowest_room = min(available_rooms)
        print(f"Lowest avialable rooms are: {lowest_room}")
        # for room_no in available_rooms:
        #     print(room_no, room_type)
    else:
        print("Rooms are fully booked")

display_menu()
# room_availability_search()








   
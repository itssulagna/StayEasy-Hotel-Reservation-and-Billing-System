
from abc import ABC, abstractmethod

class Room(ABC):
    def __init__(self, room_no, floor):
        self.__room_no = room_no
        self.__floor = floor

    @property
    def room_no(self):
        return self.__room_no

    @property
    def floor(self):
        return self.__floor

    @abstractmethod
    def get_base_rate(self):
        pass

    @abstractmethod
    def get_maximum_guest(self):
        pass

    @abstractmethod
    def get_breakfast(self):
        pass

    def __str__(self):
        return ( f"Room No: {self.room_no}, " f"Floor: {self.floor}" )


class StandardRoom(Room):
    def get_base_rate(self):
        return 2500

    def get_maximum_guest(self):
        return 2

    def get_breakfast(self):
        return 350


class DeluxeRoom(Room):
    def get_base_rate(self):
        return 4000

    def get_maximum_guest(self):
        return 3

    def get_breakfast(self):
        return 0


class SuiteRoom(Room):
    def get_base_rate(self):
        return 7500

    def get_maximum_guest(self):
        return 4

    def get_breakfast(self):
        return 0


class Guest:
    def __init__(self, name, mob_no, email):
        self.__name = name
        self.__mob_no = mob_no
        self.__email = email

    @property
    def name(self):
        return self.__name

    @property
    def mob_no(self):
        return self.__mob_no

    @property
    def email(self):
        return self.__email

    def __str__(self):
        return f"Name: {self.name}, Mobile: {self.mob_no}, Email: {self.email}"

class Booking:

    def __init__(self, booking_id,room_no, check_in, check_out, status):
        self.__booking_id = booking_id
        self.__room_no = room_no
        self.__check_in = check_in
        self.__check_out = check_out
        self.__status = status

    @property
    def booking_id(self):
        return self.__booking_id

    @property
    def room_no(self):
        return self.__room_no

    @property
    def check_in(self):
        return self.__check_in

    @property
    def check_out(self):
        return self.__check_out

    @property
    def status(self):
        return self.__status

    def __str__(self):

        return (
            f"Booking ID: {self.booking_id}, "
            f"Room No: {self.room_no}, "
            f"Check In: {self.check_in}, "
            f"Check Out: {self.check_out}, "
            f"Status: {self.status}"
        )
class StayEasyException(Exception):
    pass
class RoomUnavailable(StayEasyException):
    pass
class InvalidDate(StayEasyException):
    pass
class InvalidStatus(StayEasyException):
    pass
class BookingNotFound(StayEasyException):
    pass
class InvalidGuestDetails(StayEasyException):
    pass
class InvalidInputError(StayEasyException):
    pass


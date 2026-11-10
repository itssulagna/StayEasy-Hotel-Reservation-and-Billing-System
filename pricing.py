from datetime import timedelta
def calculate_booking_amount(room_type, check_in, check_out,no_of_guest, completed_stays,breakfast_required):
    room_rates = {
        "standard": 2500,
        "deluxe": 4000,
        "suite": 7500
    }
    no_of_nights = (check_out - check_in).days

    room_charge = 0
    extra_guest_charge = 0
    breakfast_charge = 0
    gst_amount = 0

    current_date = check_in

    while current_date < check_out:

        daily_rate = room_rates[room_type.lower()]

        if current_date.weekday() in [4, 5]:
            daily_rate = daily_rate + (daily_rate * 20 / 100)
        room_charge += daily_rate

        if room_type.lower() in ["deluxe", "suite"] and no_of_guest > 2:
            daily_extra_guest = (no_of_guest - 2) * 800
            extra_guest_charge += daily_extra_guest
        
        if room_type.lower() == "standard" and breakfast_required:
            breakfast_charge += no_of_guest * 350

        current_date += timedelta(days=1)

    subtotal = room_charge + extra_guest_charge + breakfast_charge

    long_stay_discount = 0
    if no_of_nights >= 7:
        long_stay_discount = subtotal * 0.10

    subtotal -= long_stay_discount


    loyalty_discount = 0
    if completed_stays >= 3:
        loyalty_discount = subtotal * 0.05

    subtotal -= loyalty_discount


    if subtotal <= 7500 * no_of_nights:
        gst_amount = subtotal * 0.12
    else:
        gst_amount = subtotal * 0.18

    total_amount = subtotal + gst_amount

    return {
        "room_charge": round(room_charge, 2),
        "extra_guest_charge": round(extra_guest_charge, 2),
        "breakfast_charge": round(breakfast_charge, 2),
        "long_stay_discount": round(long_stay_discount, 2),
        "loyalty_discount": round(loyalty_discount, 2),
        "gst_amount": round(gst_amount, 2),
        "total_amount": round(total_amount, 2)
    }



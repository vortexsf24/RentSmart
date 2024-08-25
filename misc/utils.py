def otodom_format_rooms_number(number):
    room_numbers = {
        'ONE': '1',
        'TWO': '2',
        'THREE': '3',
        'FOUR': '4',
        'FIVE': '5',
        'SIX': '6',
        'SEVEN': '7',
        'EIGHT': '8',
        'NINE': '9',
        'TEN': '10',
        'MORE': '10+',
    }

    return room_numbers.get(number, 'Zapytaj')


def otodom_format_floor_number(number):
    floor_numbers = {
        'GROUND': '0',
        'FIRST': '1',
        'SECOND': '2',
        'THIRD': '3',
        'FOURTH': '4',
        'FIFTH': '5',
        'SIXTH': '6',
        'SEVENTH': '7',
        'EIGHTH': '8',
        'NINTH': '9',
        'TENTH': '10',
        'ABOVE_TENTH': '10+',
    }

    return floor_numbers.get(number, 'Zapytaj')

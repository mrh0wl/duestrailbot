import re
from datetime import date, datetime
from typing import Union

w_day_re = '((?:19|20)\\d\\d)[\\/.\\s-](0?[1-9]|1[012])[\\/.\\s-]([12][0-9]|3[01]|0?[1-9])'
w_month_re = '((?:19|20)\\d\\d)[\\/.\\s-](0?[1-9]|1[012])'
year_re = '((?:19|20)\\d\\d)'


def calculate_age(born: Union[int, str]) -> int:
    ''' Calculate the age of a person
    :param born: The date of birth of the person. It must be in the in the next formats:
        [YYYY-MM-DD, YYYY-MM] (ex. 1999-01-01)
        [YYYY/MM/DD, YYYY/MM] (ex. 1999/01/01)
        [YYYY MM DD, YYYY MM] (ex. 1999 01 01)
        [YYYYMMDD, YYYYMM] (ex. 19900101)
        [YYYY] (ex. 1999)
    :return: The age of the person
    '''
    try:
        # try to cast the parameter to an integer
        int(born)
        born = str(born)

        year_int = int(born[:4])
        month_int = int(born[4:6]) if len(born) > 4 else 7
        day_int = int(born[6:8]) if len(born) > 6 else 2

        born = date(
            year_int,
            month_int,
            day_int
        )
    except ValueError:
        # if it's not an integer, it must be a string
        if re.match(w_day_re, born):
            match = re.match(w_day_re, born)
        elif re.match(w_month_re, born):
            match = re.match(w_month_re, born)
        elif re.match(year_re, born):
            match = re.match(year_re, born)

        born_year = int(match.group(1))
        born_month = int(match.group(2)) if len(match.groups()) > 1 else 7
        born_day = int(match.group(3)) if len(match.groups()) > 2 else 2

        born = date(born_year, born_month, born_day)

    today = date.today()
    year = today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))

    return year


def date_regex(text: str) -> Union[float, None]:
    date_re = r'^(0?[1-9]|[12][0-9]|3[01])[|\\/-](0[1-9]|1[012])$'
    time_re = r'^([0-1]?[0-9]|2[0-3]):?([0-5][0-9])?$'
    split_date = text.split()

    if not re.search(date_re, split_date[0]):
        return None

    date_match = re.match(date_re,
                          split_date[0])
    time_match = re.match(time_re,
                          split_date[1]
                          if len(split_date) == 2
                          else '12:00')

    day = date_match.group(1)
    month = date_match.group(2)
    year = datetime.utcnow().year if datetime.utcnow().month != 1 else str(int(datetime.utcnow().year) - 1)
    hour = time_match.group(1) if time_match.group(1) is not None else '12'
    mins = time_match.group(2) if time_match.group(2) is not None else '00'
    valid_date = datetime.strptime(
        f'{day}-{month}-{year} {hour}:{mins}:00', '%d-%m-%Y %H:%M:%S')

    return valid_date

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
    date_re = r'^((?:20)\d\d)-(0?[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])$'
    split_date = text.split()

    if not re.search(date_re, split_date[0]):
        return None

    date_match = re.match(date_re,
                          split_date[0])

    year = date_match.group(1)
    day = date_match.group(2)
    month = date_match.group(3)
    valid_date = datetime.strptime(f'{day}-{month}-{year} 6', '%d-%m-%Y %H')

    return valid_date

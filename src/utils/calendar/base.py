import calendar
import random
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from pyrogram.types import InlineKeyboardButton

from ..docs import ListEnum

calendar.setfirstweekday(calendar.MONDAY)

CB_CALENDAR = "cbcal"

MONTHS = {
    'en': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    'eo': ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aŭg", "sep", "okt", "nov", "dec"],
    'ru': ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"],
    'ukr': ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"],
}

DAYS_OF_WEEK = {
    'en': ["M", "T", "W", "T", "F", "S", "S"],
    'eo': ["L", "M", "M", "Ĵ", "V", "S", "D"],
    'ru': ["П", "В", "С", "Ч", "П", "С", "В"],
    'ukr': ["П", "В", "С", "Ч", "П", "С", "Н"],
}


class CalendarFormat(ListEnum):
    YEAR = 'y'
    MONTH = 'm'
    DAY = 'd'
    SELECT = "s"
    GOTO = "g"
    NOTHING = "n"
    LSTEP = {'y': 'year', 'm': 'month', 'd': 'day'}


class TGCalendar:
    months = MONTHS
    days_of_week = DAYS_OF_WEEK
    prev_button = "<<"
    next_button = ">>"
    middle_button_day = "{month} {year}"
    middle_button_month = "{year}"
    middle_button_year = " "
    back_to_button = "<<< {name}"
    empty_nav_button = "×"
    empty_day_button = " "
    empty_month_button = " "
    empty_year_button = " "
    size_year = 2
    size_year_column = 2
    size_month = 3
    size_day = 7
    size_additional_buttons = 2
    _keyboard = None
    step = None

    def __init__(self, platform=None, plan=None, current_date=None, additional_buttons=None, locale='en', min_date=None,
                 max_date=None, is_random=True, **kwargs):
        """
        :param date current_date: Where calendar starts, if None the current date is used
        :param view: The type of the calendar: either detailed, w/month, or w/year
        """

        self.platform = platform
        self.plan = plan
        self.locale = locale

        self.current_date = current_date or date.today()
        self.max_date = max_date or date.today()
        self.min_date = min_date or self.max_date - timedelta(31)

        # whether to add random numbers to callbacks
        self.is_random = is_random

        if not additional_buttons:
            additional_buttons = []
        self.additional_buttons = rows(
            additional_buttons, self.size_additional_buttons)

        self.prev_button_year = self.prev_button
        self.next_button_year = self.next_button
        self.prev_button_month = self.prev_button
        self.next_button_month = self.next_button
        self.prev_button_day = self.prev_button
        self.next_button_day = self.next_button

        self.nav_buttons = {
            CalendarFormat.YEAR.value: [self.prev_button_year, self.middle_button_year, self.next_button_year],
            CalendarFormat.MONTH.value: [self.prev_button_month, self.middle_button_month, self.next_button_month],
            CalendarFormat.DAY.value: [self.prev_button_day, self.middle_button_day, self.next_button_day],
        }

    def build(self):
        if not self._keyboard:
            self._build()
        return self._keyboard, self.step

    def process(self, call_data):
        return self._process(call_data)

    def _build(self, *args, **kwargs):
        """
        Build the keyboard and set _keyboard.
        """

    def _process(self, call_data, *args, **kwargs):
        """
        :param call_data: callback data
        :return: (result, keyboard, message); if no result: result = None
        """

    def _build_callback(self, action: CalendarFormat, step, data, *args, is_random=False, **kwargs):
        if action == CalendarFormat.NOTHING:
            params = [CB_CALENDAR, str(self.platform), str(self.plan), action.value]
        else:
            data = list(map(str, data.timetuple()[:3]))
            params = [CB_CALENDAR, str(self.platform), str(self.plan), action.value, step] + data

        # Random is used here to protect bots from being spammed by some 'smart' users.
        # Random callback data will not produce api errors "Message is not modified".
        # However, there is still a chance (1 in 1e18) that the same callbacks are created.
        salt = "_" + str(random.randint(1, 1e18)) if is_random else ""

        return "_".join(params) + salt

    def _build_button(self, text, action, step=None, data=None, is_random=False, **kwargs):
        return InlineKeyboardButton(text=str(text), callback_data=self._build_callback(action, step.value if step else step, data, is_random=is_random))

    def _build_keyboard(self, buttons):
        return self._build_json_keyboard(buttons)

    def _build_json_keyboard(self, buttons):
        """
        Build keyboard in json to send to Telegram API over HTTP.
        """
        return buttons + self.additional_buttons

    def _valid_date(self, d):
        return self.min_date <= d <= self.max_date

    def _get_period(self, step, start, diff, *args, **kwargs):
        """
        Used for getting period of dates with a given step, start date and difference.
        It allows to create empty dates if they are not in the given range.
        """
        lstep = CalendarFormat.LSTEP.value[step.value] + "s"
        dates = []

        empty_before = 0
        empty_after = 0

        for i in range(diff):
            n_date = start + relativedelta(**{lstep: i})
            if self.min_date > max_date(n_date, step):
                empty_before += 1
            elif self.max_date < min_date(n_date, step):
                empty_after += 1
            else:
                dates.append(n_date)
        return [None] * empty_before + dates + [None] * empty_after


def rows(buttons, row_size):
    """
    Build rows for the keyboard. Divides list of buttons to list of lists of buttons.
    """
    return [buttons[i:i + row_size] for i in range(0, max(len(buttons) - row_size, 0) + 1, row_size)]


def max_date(d, step):
    """
    Returns the "biggest" possible date for a given step.
    It is used for navigations buttons when it is needed to check if prev/next page exists.
    :param d datetime
    :param step current step
    """
    if step == CalendarFormat.YEAR:
        return d.replace(month=12, day=31)
    elif step == CalendarFormat.MONTH:
        return d.replace(day=calendar.monthrange(d.year, d.month)[1])
    else:
        return d


def min_date(d, step):
    if step == CalendarFormat.YEAR:
        return d.replace(month=1, day=1)
    elif step == CalendarFormat.MONTH:
        return d.replace(day=1)
    else:
        return d

# imports from standar lib
import difflib
import re
from datetime import datetime, timedelta
from enum import Enum
from functools import reduce
from typing import List, Union, Tuple

import pytz
# imports from pyrogram lib
from pyrogram import enums
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQuery, InlineQueryResultArticle,
                            InputTextMessageContent, Message)

# imports from src
from src import utils
from src.models import (Payment, PlatformModel, Platforms, Subscription,
                        TotalPay)
from src.services import PaymentDB, UserDB

Subscriptions = List[Subscription]
Payments = Union[Payment, List[Payment]]


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class ListEnum(Enum):
    @classproperty
    def values(cls):
        return list(map(lambda c: c.value, cls))


class InfoMode(ListEnum):
    START = 'welcome'
    CREATOR = 'creator'


class PlatformMode(ListEnum):
    REPEATED = 'sub_exist'
    ACTION = 'add_platform'
    CONTINUE = 'sub_resume_content'
    STARTED = 'started_content'
    SUCCESS = 'started_success'
    FAILURE = 'started_failure'
    CANCEL = 'cancel_content'
    REMOVE = 'sub_deleted'
    END = 'sub_added'


class Docs:
    HELP_BOT = 'https://i.imgur.com/ww8otDw.png'
    DONATION = 'https://i.imgur.com/sOCjzED.png'
    DESCRIPTION_MAX_LEN = 60

    class GetSubscriptions:
        def __get_sub_time(months: int, i18n: utils.I18n):
            y = i18n.t('year') if months//12 == 1 else i18n.t('years')
            m = i18n.t('month') if months == 1 else i18n.t('months')
            y_c = months // 12
            m_c = months % 12
            return f'{y_c} {y}, {m_c} {m}' if y_c > 0 else f'{m_c} {m}'

        def get_text(cls, subscription: Subscription, userDB: UserDB, i18n: utils.I18n) -> str:
            utc = pytz.UTC
            remaining = (subscription.due_date -
                         utc.localize(datetime.utcnow())).days
            months_paid = subscription.months_paid or 0
            price = subscription.payment.plan.price
            if remaining <= 0:
                subscription.start_at = subscription.due_date
                subscription.due_date += timedelta(30)
                subscription.months_paid = months_paid + 1
                discounts = reduce((lambda x, y: x+y), subscription.payment.discounts) if len(
                    subscription.payment.discounts) else 0
                extra_fees = reduce((lambda x, y: x+y), subscription.payment.extra_fees) if len(
                    subscription.payment.extra_fees) else 0
                total = price + discounts - extra_fees
                if subscription.payment.total_pay[-1].months < 12:
                    subscription.payment.total_pay[-1].months += 1
                    subscription.payment.total_pay[-1].paid += total
                else:
                    subscription.payment.total_pay.append(
                        TotalPay.fromJson({1: total}))
                subscription = userDB.subscription(subscription)
            return i18n.t("list_content", {
                'platform': subscription.name,
                'price': price,
                'plan': subscription.payment.plan.name,
                'remaining': f'{remaining} {i18n.t("day")}{"" if remaining == 1 else "s"}',
                'sub_time': cls.__get_sub_time(months=months_paid, i18n=i18n),
                'last_year_dues': '${:.2f}'.format(subscription.payment.total_pay[-2]) if len(subscription.payment.total_pay) > 1 else 'N/A',
                'current_year_dues': '${:.2f}'.format(subscription.payment.total_pay[-1]),
                'total_spends': '${:.2f}'.format(reduce((lambda x, y: x+y), [n.paid for n in subscription.payment.total_pay]))}
            )

        def __new__(cls, userDB: UserDB, subscription: Subscription = None):
            user = userDB.getUser()
            i18n = utils.I18n(user.language, 'inline_query_messages')
            subscriptions: Subscriptions = userDB.listSubscriptions()
            result = []
            if subscription:
                return cls.get_text(cls, subscription, userDB, i18n)

            for subscription in subscriptions:
                subscription: Subscription
                platform = PlatformModel(
                    subscription.id.lower(),
                    i18n
                )
                if not subscription.inPartFilled:
                    text = cls.get_text(cls, subscription, userDB, i18n)
                    result.append(
                        InlineQueryResultArticle(
                            title=f"{subscription.name}",
                            description=i18n.t("list_short", {
                                "plan": subscription.payment.plan.name,
                                "price": subscription.payment.plan.price
                            }),
                            input_message_content=InputTextMessageContent(
                                text,
                                disable_web_page_preview=True,
                            ),
                            thumb_url=platform.logo,
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text=i18n.t('sub_reload'), callback_data=f'reload_{platform.id}'),
                                    InlineKeyboardButton(text=i18n.t('sub_edit'), callback_data=f'edit_{platform.id}')],
                                    [InlineKeyboardButton(text=i18n.t('sub_remove'), callback_data=f'remove_{platform.id}')]]),
                        )
                    )
            return result

    class SearchText:
        def __getMatch(a: str, b: str, percentage: float = 0.7) -> bool:
            return difflib.SequenceMatcher(a=a.lower(), b=b.lower()).ratio() > percentage

        def __new__(cls, query: InlineQuery) -> List[InlineQueryResultArticle]:
            results = dict()
            i18n = utils.I18n(
                query.from_user.language_code,
                'platform_model_messages'
            )
            for item in Platforms:
                item: Platforms
                platform = PlatformModel(
                    item.name.lower(),
                    i18n
                )
                isValid = any(cls.__getMatch(
                    a=query.query.strip(), b=text) for text in re.split(r'\s+|/', f'{platform.short.strip()} {platform.name.strip()}'))
                if (isValid or query.query.strip() == '!a'):
                    results[platform.id] = InlineQueryResultArticle(
                        title=f"{platform.name}",
                        description=platform.short,
                        input_message_content=InputTextMessageContent(
                            f'{i18n.t("title", {"platform": platform.name})}\n'
                            f'{platform.description.strip()}',
                            disable_web_page_preview=True,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text=i18n.t('add'), callback_data=f'add_{platform.id}')]]),
                        thumb_url=platform.logo,
                    )
            return list(results.values())

    def __init__(self, query: [InlineQuery, Message],
                 i18n_file: str, **kwargs):
        self.query = query
        self.locale = self.query.from_user.language_code
        self.i18n_file = i18n_file
        self.i18n = utils.I18n(self.locale, self.i18n_file)
        self.donate = self.i18n.t('support')
        self.arguments = kwargs

    # update function to update the __init__ function
    def update(cls, query: [InlineQuery, Message, None] = None,
               i18n_file: [str, None] = None, **kwargs):
        cls.query = query if query else cls.query
        cls.i18n_file = i18n_file if i18n_file else cls.i18n_file
        return cls.__init__(cls.query, cls.i18n_file,
                            **{**cls.arguments, **kwargs})

    def get_default_results(cls) -> List[InlineQueryResultArticle]:
        i18n = cls.i18n.update(filename='inline_query_message')

        is_private = enums.ChatType.BOT == cls.query.chat_type
        help = i18n.t('help_content')

        inline_list = [
            InlineQueryResultArticle(
                title=i18n.t('help_title'),
                input_message_content=InputTextMessageContent(
                    help,
                    disable_web_page_preview=True,
                ),
                description=i18n.t('help_preview'),
                thumb_url=cls.HELP_BOT,
                reply_markup=None if is_private else InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            text="🤖 ChatBot",
                            url="https://t.me/duestrailbot")],
                    ]
                ),
            ),
            InlineQueryResultArticle(
                title=i18n.t('donation_title'),
                input_message_content=InputTextMessageContent(
                    i18n.t('donation_content'),
                    disable_web_page_preview=True,
                ),
                description=i18n.t('donation_preview'),
                thumb_url=cls.DONATION,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            text=cls.donate,
                            url="https://linktr.ee/mrh0wl")],
                    ]
                )
            ),
        ]

        return inline_list

    def get_message(cls, mode: Union[InfoMode, PlatformMode]) -> [str, dict]:
        if mode in InfoMode:
            return cls.i18n.t(mode.value, {'age': utils.calculate_age(19990417)})

        elif mode in PlatformMode:
            if 'key' in cls.arguments:
                return cls.i18n.t(cls.arguments['key'])
            if mode == PlatformMode.FAILURE and 'failure' in cls.arguments and isinstance(cls.arguments['failure'], dict):
                return cls.i18n.t(cls.arguments['failure']['message'])
            return cls.i18n.t(mode.value, {'platform': cls.arguments['platform']} if 'platform' in cls.arguments else {})

    def get_inline_with_message(cls, mode: Union[InfoMode, PlatformMode]) -> Tuple[str, InlineQueryResultArticle]:
        message = cls.get_message(mode)
        inline_markup = cls.__get_info_results(mode)

        return message, inline_markup

    def get_inline(cls, mode: Union[InfoMode, PlatformMode]) -> [InlineQueryResultArticle]:
        return cls.__get_info_results(mode)

    def __get_info_results(cls,
                           mode: Union[InfoMode, PlatformMode],
                           message: dict = None) -> InlineKeyboardMarkup:
        button = 'cancel_button'
        inline_cancel_button = InlineKeyboardButton(
            text=cls.i18n.t(button), callback_data='cancel')

        validateFailure = 'failure' in cls.arguments and isinstance(
            cls.arguments['failure'], dict)
        inline_skip_button = InlineKeyboardButton(text=cls.i18n.t(
            'started_success_button'),
            callback_data=cls.arguments['failure']['callback']['skip']
            if validateFailure and 'skip' in cls.arguments['failure']['callback']
            else 'skipped_months')

        if mode == InfoMode.START:
            search = 'lazy_search'
            showall = 'lazy_all'
            inline_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=cls.i18n.t(search), switch_inline_query_current_chat=''),
                 InlineKeyboardButton(text=cls.i18n.t(showall), switch_inline_query_current_chat='!a')],
                [InlineKeyboardButton(
                    cls.donate,
                    url='https://linktr.ee/mrh0wl')]
            ])
        elif mode == InfoMode.CREATOR:
            inline_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=cls.donate, url='https://linktr.ee/mrh0wl')],
                [InlineKeyboardButton(text='🤖 Github', url='https://github.com/mrh0wl'),
                 InlineKeyboardButton(text='📸 Instagram',
                                      url='https://www.instagram.com/mrh0wl'),
                 InlineKeyboardButton(text='🐦 Twitter', url='https://twitter.com/mrh0wl')]
            ])

        elif mode == PlatformMode.ACTION:
            paymentDB: Payments = PaymentDB(
                cls.arguments['id'].lower(), None)
            inlineButtons = [InlineKeyboardButton(
                text=f'{paymentDB[i].plan.name}: ${paymentDB[i].plan.price}',
                callback_data=f'cbcal_{cls.arguments["id"].lower()}_{paymentDB[i].plan.name}')
                for i in range(0, len(paymentDB))]
            inlineButtonsMatrix = [inlineButtons[i:i+3]
                                   for i in range(0, len(inlineButtons), 3)]
            inlineButtonsMatrix.append(
                [inline_cancel_button])
            inline_markup = InlineKeyboardMarkup(inlineButtonsMatrix)
        elif mode == PlatformMode.STARTED:
            inline_markup = InlineKeyboardMarkup([
                [inline_cancel_button]
            ])
        elif mode == PlatformMode.SUCCESS:
            inline_markup = InlineKeyboardMarkup([
                [inline_cancel_button]
            ])
        elif mode == PlatformMode.FAILURE:
            inline_buttons = [[inline_cancel_button]]
            if 'failure' in cls.arguments:
                inline_buttons[0].insert(0, InlineKeyboardButton(
                    text=cls.i18n.t('failure_button'),
                    callback_data=cls.arguments['failure']['callback']['fail'] if validateFailure else 'start_at'
                ))
                if validateFailure and 'skip' in cls.arguments['failure']['callback']:
                    inline_buttons.insert(0, [inline_skip_button])
            inline_markup = InlineKeyboardMarkup(inline_buttons)
        elif mode == PlatformMode.CANCEL:
            search = 'lazy_search'
            showall = 'lazy_all'
            delete = 'cancel_delete'
            inline_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=cls.i18n.t(search), switch_inline_query_current_chat=''),
                 InlineKeyboardButton(text=cls.i18n.t(showall), switch_inline_query_current_chat='!a')],
                [InlineKeyboardButton(text=cls.i18n.t(
                    delete), callback_data='delete')]
            ])
        elif mode == PlatformMode.END:
            search = 'lazy_search'
            showall = 'lazy_all'
            inline_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=cls.i18n.t('show_list'),
                    switch_inline_query_current_chat='!p')],
                [InlineKeyboardButton(text=cls.i18n.t(search), switch_inline_query_current_chat=''),
                 InlineKeyboardButton(text=cls.i18n.t(showall), switch_inline_query_current_chat='!a')],
            ])
        elif mode == PlatformMode.CONTINUE:
            inline_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=cls.i18n.t('sub_resume'), callback_data=f'{cls.arguments["callback_data"]} {cls.arguments["id"]}'),
                 InlineKeyboardButton(text=cls.i18n.t('sub_restart'), callback_data=f'remove_{cls.arguments["id"]}')],
            ])
        return inline_markup

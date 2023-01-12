# import from asyncio
import asyncio
from datetime import datetime, timedelta
from functools import reduce

# imports from pyrogram lib
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
from pyrogram.handlers import MessageHandler
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

# imports from src
from src.models import Subscription, TotalPay
from src.services import PaymentDB, UserDB
from src.utils.calendar.detailed import CalendarFormat, DTGCalendar
from src.utils.docs import Docs, PlatformMode


class Valid:
    def __new__(self, state: bool) -> bool:
        return state


async def func(flt, __, ___):
    return flt.valid


message_ids = {}


class Callback:
    def __init__(self, client: Client, message: [Message, CallbackQuery]) -> None:
        self.client = client
        self.message: Message = message if isinstance(
            message, Message) else message.message
        self.callback: CallbackQuery = message if isinstance(
            message, CallbackQuery) else None
        self.docs = Docs(message, 'sticker_inline_messages')
        self.userDB = UserDB(message=message)
        self.user = self.userDB.getUser()
        self.subscription = Subscription()
        loop = asyncio.new_event_loop()
        if self.callback:
            loop.run_until_complete(self.callback_handler())
        loop.close()

    def started_date(self, valid: bool):
        return filters.create(func, valid=valid)

    def months_paid(self, valid: bool):
        return filters.create(func, valid=valid)

    async def __set_months_paid(self, client: Client, message: Message, count: int = 0):
        isValid = message.text.isdigit()
        self.docs.update(**{
            'failure': {
                'message': 'months_failure',
                'callback': {
                    'skip': 'skipped_months',
                    'fail': f'months_paid {self.subscription.id.lower()}',
                }
            }
        })
        text, inline = self.docs.get_inline_with_message(
            mode=PlatformMode.SUCCESS
            if isValid
            else PlatformMode.FAILURE
        )

        if isValid:
            self.subscription.months_paid = int(message.text)
            months_paid = [
                self.subscription.payment.plan.price for x in range(self.subscription.months_paid)]
            months_lst = [months_paid[i:i+12]
                          for i in range(0, len(months_paid), 12)]
            split_lastyear = months_lst[-1][:-datetime.utcnow().month]
            if split_lastyear:
                split_thisyear = months_lst[-1][len(split_lastyear):]
                months_lst[-1] = split_lastyear
                months_lst.sort(key=len)
                months_lst.append(split_thisyear)
            self.subscription.payment.total_pay = [TotalPay([len(elem), float(
                '{:.2f}'.format(reduce((lambda x, y: x+y), elem)))]) for elem in months_lst]
            self.subscription = self.userDB.subscription(self.subscription)
            if self.subscription.isEditing:
                self.docs.update(
                    **{'platform': self.subscription.name, 'key': 'sub_edited'})
            else:
                self.docs.update(**{'platform': self.subscription.name})
            text, inline = self.docs.get_inline_with_message(
                mode=PlatformMode.END)
            await client.delete_messages(message.chat.id, message.id + count)
            await self.client.edit_message_text(
                chat_id=self.user.chat_id,
                message_id=message_ids[self.user.chat_id] -
                1 if self.user.chat_id in message_ids else message.id - 1,
                text=text,
                reply_markup=inline,
            )
            return client.remove_handler(*self.handler)
        else:
            client.remove_handler(*self.handler)
        await client.delete_messages(message.chat.id, message.id + count)
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_ids[self.user.chat_id] -
            1 if self.user.chat_id in message_ids else message.id - 1,
            text=text,
            reply_markup=inline
        )

    async def calendar_handler(self):
        result, key, step = DTGCalendar(platform=self.subscription.id, plan=self.subscription.payment.plan.name).process(self.callback.data)
        if not result and key:
            await self.client.edit_message_text(
                self.callback.message.chat.id,
                self.callback.message.id,
                f"Select {CalendarFormat.LSTEP.value[step.value]}",
                reply_markup=InlineKeyboardMarkup(key)
            )
        elif result:
            text, inline = self.docs.get_inline_with_message(
                mode=PlatformMode.SUCCESS)
            await self.client.edit_message_text(
                chat_id=self.callback.message.chat.id,
                message_id=self.callback.message.id,
                text=text,
                reply_markup=inline
            )
            validDate = datetime.strptime(f'{result} 6', '%Y-%m-%d %H')
            self.subscription.start_at = validDate
            self.subscription.due_date = validDate + timedelta(days=30)
            self.userDB.subscription(self.subscription)
            self.handler = self.client.add_handler(
                MessageHandler(
                    self.__set_months_paid,
                    filters.chat(self.user.chat_id) & filters.text & self.months_paid(
                        Valid(state=True))
                )
            )

    async def callback_handler(self) -> None:
        if self.callback.data == 'cancel':
            try:
                message, inline = self.docs.get_inline_with_message(
                    mode=PlatformMode.CANCEL)
                await self.callback.edit_message_text(text=message, reply_markup=inline)
            except Exception:
                pass

        elif self.callback.data == 'delete':
            if hasattr(Callback, 'valid'):
                del self.valid
                self.client.remove_handler(*self.handler)
            await self.client.delete_messages(self.user.chat_id, [self.message.id, self.message.id - 1])

        elif self.callback.data.startswith('remove_'):
            self.userDB.removeSubscription(self.callback.data.split('_')[1])
            await self.callback.edit_message_reply_markup()
            text = self.docs.get_message(mode=PlatformMode.CANCEL)
            inline = self.docs.get_inline(mode=PlatformMode.END)
            await self.client.send_message(self.user.chat_id, text=text, reply_markup=inline)

        elif self.callback.data.startswith('add_'):
            platform = self.callback.data.split('_')[1].lower()
            self.subscription.id = platform
            self.subscription = self.userDB.subscription(self.subscription)
            args = {'platform': self.subscription.name,
                    'id': self.subscription.id}
            self.docs.update(**args)
            partFilled = self.subscription.inPartFilled
            if partFilled:
                args['callback_data'] = partFilled
                self.docs.update(**args)
                text, inline = self.docs.get_inline_with_message(
                    mode=PlatformMode.CONTINUE)
            elif not self.subscription.isEmpty:
                text = self.docs.get_message(mode=PlatformMode.REPEATED)
                inline = self.docs.get_inline(mode=PlatformMode.END)

            else:
                text, inline = self.docs.get_inline_with_message(
                    mode=PlatformMode.ACTION)

            await self.callback.edit_message_reply_markup()
            await self.client.send_message(
                chat_id=self.user.chat_id,
                text=text,
                reply_markup=inline,
            )

        elif self.callback.data.startswith('cbcal'):
            params = self.callback.data.split('_')
            platform, plan = (params[1], params[2])
            if len(params) == 3:
                text = self.docs.get_message(mode=PlatformMode.STARTED)
                calendar, step = DTGCalendar(platform, plan).build()
                await self.client.edit_message_text(
                    self.callback.message.chat.id,
                    self.callback.message.id,
                    text=f"Select {CalendarFormat.LSTEP.value[step.value]}",
                    reply_markup=InlineKeyboardMarkup(calendar)
                )
            else:
                subscription = Subscription(
                    id=platform.lower(),
                    payment=PaymentDB(
                        platform=platform.lower(),
                        plan=plan
                    )
                )
                self.subscription = self.userDB.subscription(subscription)
                await self.calendar_handler()
        elif self.callback.data.split()[0] == 'months_paid':
            text, inline = self.docs.get_inline_with_message(
                mode=PlatformMode.SUCCESS)
            self.docs.update(**{})
            try:
                self.valid = Valid()
            except TypeError:
                self.subscription = Subscription(
                    id=self.callback.data.split()[1].lower())
                self.subscription = self.userDB.subscription(self.subscription)
                self.handler = self.client.add_handler(
                    MessageHandler(
                        self.__set_months_paid,
                        (
                            filters.chat(self.user.chat_id) &
                            filters.text &
                            self.months_paid(Valid(state=True))
                        )
                    )
                )
            await self.client.edit_message_text(
                chat_id=self.user.chat_id,
                message_id=self.message.id,
                text=text,
                reply_markup=inline
            )
        elif self.callback.data == 'skipped_months':
            self.docs.update(**{
                'failure': {
                    'message': 'not_available'
                }
            })
            text = self.docs.get_message(mode=PlatformMode.FAILURE)
            await self.callback.answer(text=text, show_alert=True)

        elif self.callback.data.startswith('edit_'):
            subscriptionID = self.callback.data.split('_')[1]
            self.subscription.id = subscriptionID
            self.subscription = self.userDB.subscription(self.subscription)
            self.subscription.editing = True
            text = self.docs.get_message(mode=PlatformMode.STARTED)
            inline = self.docs.get_inline(mode=PlatformMode.FAILURE)
            await self.callback.edit_message_reply_markup()
            await self.client.send_message(
                chat_id=self.user.chat_id,
                text=text,
                reply_markup=inline
            )
            try:
                self.valid = Valid()
            except TypeError:
                self.handler = self.client.add_handler(
                    MessageHandler(
                        self.__set_start_at,
                        (
                            filters.chat(self.user.chat_id) &
                            filters.text &
                            self.started_date(Valid(state=True))
                        )
                    )
                )
        elif self.callback.data.startswith('reload_'):
            platform = self.callback.data.split('_')[1]
            subscription = self.userDB.subscription(
                Subscription(
                    id=platform.lower(),
                )
            )
            try:
                await self.client.edit_inline_text(
                    self.callback.inline_message_id,
                    text=self.docs.GetSubscriptions(self.userDB, subscription),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text=self.docs.i18n.t('sub_reload'), callback_data=f'reload_{platform}'),
                          InlineKeyboardButton(text=self.docs.i18n.t('sub_edit'), callback_data=f'edit_{platform}')],
                         [InlineKeyboardButton(text=self.docs.i18n.t('sub_remove'), callback_data=f'remove_{platform}')]])
                )
            except MessageNotModified:
                pass

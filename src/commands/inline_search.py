# imports from pyrogram lib
from pyrogram import Client
from pyrogram.types import InlineQuery
from pyrogram.enums import ChatType

# imports from src
from src.utils.docs import Docs
from src.utils.i18n import I18n
from src.services import UserDB

NEXT_OFFSET = 8
CACHE_TIME = 5


async def inline(client: Client, query: InlineQuery) -> None:
    string = query.query.lower()
    i18n = I18n(query.from_user.language_code, 'inline_query_message')
    docs = Docs(query, 'inline_query_message')
    results = docs.get_default_results()

    found = []
    offset = int(query.offset or 0)
    switch_pm_text = i18n.t('result')

    if string == '':
        await query.answer(
            results=results,
            cache_time=5,
            switch_pm_text=i18n.t('search'),
            switch_pm_parameter='help'
        )
        return

    elif string == '!t':
        i18n.update(filename='callback_message')
        await query.answer(
            results=[],
            cache_time=CACHE_TIME,
            switch_pm_text=f'⚠️ {i18n.t("not_available").split(".")[0]}.',
            switch_pm_parameter='help'
        )
    elif string == '!p':
        if query.chat_type == ChatType.BOT:
            if offset:
                await query.answer(
                    results=[],
                    cache_time=CACHE_TIME,
                    switch_pm_text=switch_pm_text,
                    switch_pm_parameter="help",
                    next_offset="",
                )
            else:
                switch_pm_text = i18n.t('list')
                userDB = UserDB(message=query)
                found = docs.GetSubscriptions(userDB)
                if found and len(found) != 0:
                    count = len(found)
                    switch_pm_text = f"{count} subscription{'s' if count > 1 else ''} found"
                    await query.answer(
                        results=found[:50],
                        cache_time=CACHE_TIME,
                        switch_pm_text=switch_pm_text,
                        switch_pm_parameter="help",
                        next_offset=str(offset + NEXT_OFFSET),
                        is_gallery=False
                    )
                else:
                    await query.answer(
                        results=[],
                        cache_time=CACHE_TIME,
                        switch_pm_text='❌ No subscriptions found',
                        switch_pm_parameter="help",
                    )
        else:
            await query.answer(
                results=[],
                cache_time=CACHE_TIME,
                switch_pm_text=i18n.t('chat_unavailable'),
                switch_pm_parameter="help",
            )
    else:
        if offset:
            await query.answer(
                results=[],
                cache_time=CACHE_TIME,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="help",
                next_offset="",
            )
        else:
            found = docs.SearchText(query)

            if len(found) != 0:
                count = len(found)
                switch_pm_text = f"{count} Result{'s' if count > 1 else ''} for \"{string}\""

                await query.answer(
                    results=found[:50],
                    cache_time=CACHE_TIME,
                    switch_pm_text=switch_pm_text,
                    switch_pm_parameter="help",
                    next_offset=str(offset + NEXT_OFFSET),
                    is_gallery=False
                )
            else:
                await query.answer(
                    results=[],
                    cache_time=CACHE_TIME,
                    switch_pm_text=f'❌ No results for "{string}"',
                    switch_pm_parameter="help",
                )

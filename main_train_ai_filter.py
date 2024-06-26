import os

import pandas
from aiogram import Bot, Dispatcher, Router, types
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
import io
import socket

token = '6497454091:AAGC6rkSP45cS91J_pr9tJYjotcnGCzRDpA'

dp = Dispatcher()
bot = Bot(token=token)
r = Router()
chat_id = -1002186252027  #Канал RSS
accepted_chai_id = -1002023007325
user_id = 421349553

split_mark = 0.576


def predict_model(content: str, mark: int) -> None:
    text = '--train\n\r' + str(mark) + '\n\r' + content + '\n\r\n\r'
    HOST = ('127.0.0.1', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(HOST)
        s.sendall(bytes(text, 'UTF-8'))
        s.close()


@r.channel_post()
async def resend_message(message: types.Message):
    if int(message.chat.id) == accepted_chai_id:
        return

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text='Подходит', callback_data='yes'),
        types.InlineKeyboardButton(text='Не подходит', callback_data='no'),
    )

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=builder.as_markup()
        )
    except:
        print('Error')


@r.callback_query()
async def add_to_csv(callback: types.CallbackQuery):
    message = callback.message

    if callback.data != 'yes' and callback.data != 'no':
        print('Exit 2')
        return

    text = message.text if message.text else message.caption

    if message.text:
        start = text.find('\n') + 1
        if text.lower().startswith('НОВОЕ В DZEN'.lower()):
            finish = text.find('https://dzen.ru/')
        else:
            finish = text.find('https://t.me/')

        text = text[start:finish].strip()

    else:
        src = message.document.file_name
        temp = io.BytesIO()
        await bot.download(message.document.file_id, temp)

        try:
            with open(src, 'wb') as file:
                file.write(temp.read())

            with open(src, 'r') as file:
                text = file.read().strip()

            os.remove(src)
        except:
            print('Error')

    text = text.replace('\n', ' ')
    if callback.data == 'yes':
        mark = 1
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text='Подходит', callback_data='None'),
        )
        await message.edit_reply_markup(
            callback.inline_message_id,
            reply_markup=builder.as_markup()
        )
    else:
        mark = 0
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text='Не подходит', callback_data='None'),
        )
        await message.edit_reply_markup(
            callback.inline_message_id,
            reply_markup=builder.as_markup()
        )

    data = [[text, mark]]
    dataframe = pandas.DataFrame(data)
    dataframe.to_csv('train.csv', header=False, index=False, mode='a')


async def start() -> None:
    dp.include_router(r)
    print('Starting')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())

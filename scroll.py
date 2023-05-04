from pyrogram.types import BotCommand, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from pyrogram import Client, filters, idle
import shelve
import asyncio


inline_keyboard = []
db = shelve.open('database')
channels = db['channels']
user_id = db['users']
if not(channels):
    channels = []

for i in channels:
     inline_keyboard.append([InlineKeyboardButton(text=i, callback_data=i)])

db.close()
print(inline_keyboard)

t_channel = -1001832418794

API_ID = 27176227
API_HASH = 'cf21cdca709530560694d9e96b264a0e'
bot_token = '5793290325:AAHdnE11llJWIg6y6_Pm98Fxm39JQZGIsPc'
PUBLIC_PUBLIC = 5793290325
PHONE_NUMBER = '+79772637073'


async def copy_to_my_bot(client, message):
    await client.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.id)


bot_commands = [
    BotCommand(
        command='start',
        description='Запуск бота'
    ),
    BotCommand(
        command='addchannel',
        description='Добваление канала'
    ),
    BotCommand(
        command='allchannels',
        description='Управление каналами'
    )
]


async def start():

    app = Client('scroll bot', api_id=API_ID, api_hash=API_HASH, bot_token=bot_token, parse_mode=ParseMode.HTML)

    nebot = Client('nescrollbot', api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

    # Функция реагирования на нажатие кнопки inline_keyboard
    @app.on_callback_query()
    async def command_channel(client: Client, call):
        global channels
        text = call.data
        db = shelve.open('database')
        channels = db['channels']
        if text == 'a' and text not in channels:
            await call.message.reply('Ты можешь прислать ссылку на тг-канал в формате "https://t.me/" и я добавлю его в подписки')
        if not (channels):
            channels = []
        print(text, channels, inline_keyboard)

        if text in channels:
            channels.remove(text)
            inline_keyboard.remove([InlineKeyboardButton(text=text, callback_data=text)])

            db['channels'] = channels
            await call.message.reply(f'Канал {call.data} успешно удалён')

            print(channels)
            db.close()

            @nebot.on_message(filters.chat(channels))
            async def new_channel_post(client, message):
                print(message)
                await client.copy_message(chat_id=t_channel, from_chat_id=message.chat.id, message_id=message.id)

    app.add_handler(MessageHandler(copy_to_my_bot, filters.chat('qwaesrdtfsxrdctfyg')))

    @nebot.on_message(filters.chat(channels))
    async def new_channel_post(client, message):
        print(message)
        await client.copy_message(chat_id=t_channel, from_chat_id=message.chat.id, message_id=message.id)


    @app.on_message(filters.command(commands='start'))
    async def command_start(client: Client, message: Message):
        global user_id
        print(message.chat.id)
        db = shelve.open('database')
        channels = db['channels']
        user_id = message.from_user.id
        db['users'] = user_id
        db.close()
        await message.reply(
            f"Здравствуй, {message.from_user.first_name}!\nТы можешь прислать ссылку на тг-канал и я добавлю его в подписки")

# Напоминалка формата отправки ссылок на каналы
    @app.on_message(filters.command(commands='addchannel'))
    async def command_addchannel(client: Client, message: Message):
        await message.reply(
            'Ты можешь прислать ссылку на тг-канал в формате "https://t.me/" и я добавлю его в подписки')

# Вывод списка всех каналов с возможностью удаления
    @app.on_message(filters.command(commands='allchannels'))
    async def command_allchannels(client: Client, message: Message):
        global inline_keyboard
        if not(inline_keyboard):
            inline_keyboard = [[InlineKeyboardButton(text='Список каналов пуст', callback_data='a')]]
        await message.reply(f'Список добавленных каналов', reply_markup=InlineKeyboardMarkup(inline_keyboard))
        if inline_keyboard == [[InlineKeyboardButton(text='Список каналов пуст', callback_data='a')]]:
            inline_keyboard = []

    @app.on_message(filters.text)
    async def listen_for_channel(client: Client, message: Message):
        global channels
        print(message)
        db = shelve.open('database')
        channels = db['channels']
        print(channels)
        if not (channels):
            channels = []

        if message.text[13:] in channels:
            await message.reply('Этот канал уже есть')
        elif message.text[:13] == 'https://t.me/':

            channels.append(message.text[13:])
            db['channels'] = channels
            print(channels)

            db.close()

            await message.reply('Канал успешно добавлен')
            inline_keyboard.append([InlineKeyboardButton(text=message.text[13:], callback_data=message.text[13:])])
            print(message)
            print(InlineKeyboardMarkup(inline_keyboard))

            @nebot.on_message(filters.chat(channels))
            async def new_channel_post(client, message):
                print(message)
                await client.copy_message(chat_id=t_channel, from_chat_id=message.chat.id, message_id=message.id)


    await app.start()
    await nebot.start()

    await app.set_bot_commands(bot_commands)

    print('Bot Started')
    await idle()
    await nebot.stop()
    await app.stop()


if __name__ == '__main__':
    asyncio.run(start())

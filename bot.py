import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import Config, load_config

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информация о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Иницилизируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher(bot)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    dp.register_message_handler(on_start, commands=['start'])
    dp.register_message_handler(on_cat_click, text='Котик 🐈')
    dp.register_message_handler(on_dog_click, text='Песик 🐶')
    dp.register_message_handler(on_fox_click, text='Лиса 🦊')
    await dp.start_polling()


# API для картинок
API_CATS_URL = 'https://api.thecatapi.com/v1/images/search'
API_DOGS_URL = 'https://random.dog/woof.json'
API_FOX_URL = 'https://randomfox.ca/floof/'
ERROR_TEXT = 'Здесь должна была быть картинка :('

# Клавиатуры
keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Котик 🐈"), KeyboardButton("Песик 🐶"), KeyboardButton("Лиса 🦊")],
], resize_keyboard=True)


# Функция для получения картинки с API для котиков
async def get_cat_image():
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(API_CATS_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0 and 'url' in data[0]:
                        return data[0]['url']
                    logging.error(f"Ошибка получения картинки, неверный формат ответа: {data}")
    except aiohttp.ClientError as e:
        logging.error(f"Aiohttp client error: {e}")
    except Exception as e:
        logging.error(f"Unknown error: {e}")
    return None


# Функция для получения картинки с API для песиков
async def get_dog_image():
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(API_DOGS_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'url' in data:
                        return data['url']
                    logging.error(f"Ошибка получения картинки, неверный формат ответа: {data}")
    except aiohttp.ClientError as e:
        logging.error(f"Aiohttp client error: {e}")
    except Exception as e:
        logging.error(f"Unknown error: {e}")
    return None


# Функция для получения картинки с API для лис
async def get_fox_image():
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(API_FOX_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'image' in data and 'link' in data:
                        return data['image']
                    logging.error(f"Ошибка получения картинки, неверный формат ответа: {data}")
    except aiohttp.ClientError as e:
        logging.error(f"Aiohttp client error: {e}")
    except Exception as e:
        logging.error(f"Unknown error: {e}")
    return None


# Функции для обработки нажатий на кнопки
async def on_start(message: types.Message):
    await message.answer("Привет! Нажми на кнопку, чтобы получить картинку или гифку",
                         reply_markup=keyboard)


async def on_cat_click(message: types.Message):
    cat_link = await get_cat_image()
    if cat_link:
        await message.answer_photo(cat_link)
    else:
        await message.answer(ERROR_TEXT, reply_markup=keyboard)


async def on_dog_click(message: types.Message):
    dog_link = await get_dog_image()
    if dog_link:
        await message.answer_photo(dog_link)
    else:
        await message.answer(ERROR_TEXT, reply_markup=keyboard)


async def on_fox_click(message: types.Message):
    fox_link = await get_fox_image()
    if fox_link:
        await message.answer_photo(fox_link)
    else:
        await message.answer(ERROR_TEXT, reply_markup=keyboard)


if __name__ == "__main__":
    asyncio.run(main())

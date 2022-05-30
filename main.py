from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from sqlighter import Sqlighter
from admin import *
from markups import mainMenu
import logging
import config

logging.basicConfig(level=logging.INFO)

db = Sqlighter("database.db")
bot = Bot(token=config.Bot_token)
dp = Dispatcher(bot)


class OrderFood(StatesGroup):
    waiting_for_name = State()
    waiting_for_product_name = State()
    waiting_for_product_amount = State()
    waiting_for_product_price = State()
    waiting_for_town = State()
    waiting_for_picture = State()


async def start_on(_):
    pass


@dp.callback_query_handler(text_contains="callDelAdm_")
async def callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    del_id = callback_query.data.split("_")[1]
    admin_name = db.get_admin_name(del_id)
    await bot.edit_message_text(f'Точно удалить {admin_name}', callback_query.from_user.id,
                                callback_query.message.message_id, reply_markup=accept_del_kb(admin_name, del_id))


@dp.callback_query_handler(text_contains="acceptCallDelAdm_")
async def callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    del_id = callback_query.data.split("_")[1]
    try:
        if db.user_is_admin(del_id):
            db.del_admin(del_id)
    except Exception:
        await bot.edit_message_text('Что-то не получилось', callback_query.from_user.id,
                                    callback_query.message.message_id)
        admins = db.get_admins()
        await bot.send_message(user_id, my_admins_text(user_id, admins), reply_markup=my_admins_kb(user_id, admins))
    else:
        admins = db.get_admins()
        await bot.edit_message_text(f'Человек успешно лишён админки \n{my_admins_text(user_id, admins)}',
                                    callback_query.from_user.id,
                                    callback_query.message.message_id,
                                    reply_markup=my_admins_kb(user_id, admins))
        await bot.send_message(del_id, 'Вас лишили прав администратора')


@dp.callback_query_handler(text_contains="cancelCallDelAdm_")
async def callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    admins = db.get_admins()
    user_id = callback_query.from_user.id
    await bot.edit_message_text(f'Действие отменено \n{my_admins_text(user_id, admins)}',
                                callback_query.from_user.id,
                                callback_query.message.message_id,
                                reply_markup=my_admins_kb(user_id, admins))


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    if message.chat.type == 'private':
        admin_invite = bool(len(message.text[:6:-1]))
        is_admin = db.user_is_admin(message.from_user.id)
        if admin_invite:
            if is_admin:
                await message.answer('Вы и так уже админ', reply_markup=adminMenu())
            else:
                await message.answer('Поздравляю, теперь вы админ', reply_markup=adminMenu())
                await bot.send_message(message.text[:6:-1], f'Через вашу ссылку человек '
                                                            f'({message.from_user.first_name}) получил права админа')
                db.add_admin(message.from_user.id, message.text[:6:-1], message.from_user.first_name)
        elif db.user_exists(message.from_user.id):
            await message.answer('Давно не виделись', reply_markup=mainMenu(is_admin))
        else:
            await message.answer('Привет, приятно познакомиться\n'
                                 'Я бот для добавления объявлений\n'
                                 'Давай сначала зарегестрируемся',
                                 reply_markup=mainMenu(is_admin))
            db.add_user(message.from_user.id)


@dp.message_handler(content_types=['text'])
async def all_messages(message: types.Message):
    if message.chat.type == 'private':
        is_admin = db.user_is_admin(message.from_user.id)
        if message.text == 'Добавить админа':
            if db.user_is_admin(message.from_user.id):
                await admin_ref(message)
            else:
                await message.answer('Вы не имеете доступа к этой команде')
        elif message.text == 'Мои админы':
            if is_admin:
                admins = db.get_admins()
                await bot.send_message(message.from_user.id, my_admins_text(message.from_user.id, admins),
                                       reply_markup=my_admins_kb(message.from_user.id, admins))
            else:
                await message.answer('У вас нет доступа к этой команде', reply_markup=mainMenu(is_admin))
        elif message.text == 'Управление админами':
            if is_admin:
                await message.answer('Управление:', reply_markup=adminMenuProfile())
            else:
                await message.answer('У вас нет доступа к этой команде', mainMenu(is_admin))
        elif message.text == "Назад":
            await message.answer('Вы вернулись назад', reply_markup=mainMenu(is_admin))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=start_on)

from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from admin import adminMenu
from loader import db


def mainMenu(user_id) -> ReplyKeyboardMarkup:
    is_admin = db.user_is_admin(user_id)
    main_Menu = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton('Добавить объявление')
    main_Menu.add(btn)
    if is_admin:
        return adminMenu(main_Menu)
    return main_Menu


def cancel_kb() -> ReplyKeyboardMarkup():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add('Отмена')
    return keyboard


def accept_ad_kb() -> ReplyKeyboardMarkup():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add('Подтвердить', 'Отмена')
    return keyboard

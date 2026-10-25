
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from dotenv import load_dotenv
from service import *
from connection import *
import asyncio
import os

load_dotenv()
token = os.getenv("BOT_TOKEN")

bot = Bot(token=token)
dp = Dispatcher()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Склад"), KeyboardButton(text="🆘 Помощь")],
        [KeyboardButton(text="⚠️ Заканчивается")],
    ],
    resize_keyboard=True,
)

@dp.message(CommandStart())
async def start_bot(message: Message):
    if await  get_user_by_id(message.from_user.id):
        await message.answer(f"👋Привет @{message.from_user.username} я бот для учёта товаров на складе.", reply_markup=main_kb)
    else:
        user = message.from_user
        await create_user(user.username, user.full_name, user.id)
        await message.answer(f"👋Привет @{message.from_user.username} я бот для учёта товаров на складе.", reply_markup=main_kb)
        

@dp.message(F.text == "🆘 Помощь")
@dp.message(Command("help"))
async def help(message: Message):
    await message.answer(
        """
        Я помогаю вести учёт товаров на складе.
        📦 /products - показать все товары
        🆘 /help - помощь
        ⚠️ /low_stock-показать товары,  которые меньше порога
        ➕ /add_product название/количество/порог
        📦 /sell продать id/количество
        📦 /restock добавить id/количество
        """
    )



@dp.message(Command("add_product"))
async def add_product_command(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "Напиши так: /add_product название/количество/порог"
        )
        return
    args = command.args.split("/")

    if len(args) !=3:
        await message.answer(
            """
            Ошибка! Используй формат: /add_product название/количество/порог"""
        )
        return
    name_product = args[0]
    quantity = args[1]
    low_stock_threshold = args[2]

    if not name_product:
        await message.answer("Название товара не может быть пустым!")
        return
    if not quantity.isdigit() or not low_stock_threshold.isdigit():
        await message.answer("Количество и порог должны быть числами!")
        return
    quantity = int(quantity)
    low_stock_threshold = int(low_stock_threshold)
    
    if quantity < 0 or low_stock_threshold < 0:
        await message.answer("Количество и порог не могут быть отрицательными!")
        return
    product = await create_product(
        name_product,
        quantity,
        low_stock_threshold
    )
    if product is None:
        await message.answer("Не удалось добавить товар.")
        return
    await message.answer(
        f"""
        ✅ Товар добавлен!
        Название: {name_product}
        Количество: {quantity}
        Порог: {low_stock_threshold}
        """
    )


@dp.message(F.text == "📦 Склад")
@dp.message(Command("products"))
async def show_products(message: Message):
    products = await get_all_products()
    if not products:
        await message.answer("На складе пока нет товаров.")
        return
    text = "📦 Товары на складе:"
    for product in products:
        text += (
            f"""
            id: {product['product_id']}
            Название: {product['name_product']}
            Количество: {product['quantity']}
            Порог: {product['low_stock_threshold']}
            """
        )
    await message.answer(text)


@dp.message(F.text == "⚠️ Заканчивается")
@dp.message(Command("low_stock"))
async def low_stock(message: Message):
    products = await get_low_stock()
    if not products:
        await message.answer("На складе нет товаров с низким запасом.")
        return
    text = "⚠️ Товары, которые заканчиваются:"
    for product in products:
        text += (
            f"""
            id: {product['product_id']}
            Название: {product['name_product']}
            Количество: {product['quantity']}
            Порог: {product['low_stock_threshold']}
            """
        )
    await message.answer(text)



@dp.message(Command("restock"))
async def restock(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Напиши так: /restock id/количество")
        return
    args = command.args.split("/")
    if len(args) != 2:
        await message.answer("Пример: /restock id/количество")
        return
    if not args[0].isdigit() or not args[1].isdigit():
        await message.answer("ID и количество должны быть числами!")
        return
    product_id = int(args[0])
    quantity = int(args[1])
    if product_id <= 0 or quantity <= 0:
        await message.answer("ID и количество должны быть больше нуля!")
        return
    result = await restock_product(product_id, quantity)
    if result == "not_found":
        await message.answer("Товар с таким ID не найден!")
    elif result == "success":
        await message.answer("✅ Товар успешно пополнен!")
    else:
        await message.answer("Ошибка при пополнении товара!")


@dp.message(Command("sell"))
async def sell(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Напиши так: /sell id/количество")
        return
    args = command.args.split("/")
    if len(args) != 2:
        await message.answer("Пример: /sell id/количество")
        return
    if not args[0].isdigit() or not args[1].isdigit():
        await message.answer("ID и количество должны быть числами!")
        return
    product_id = int(args[0])
    quantity = int(args[1])
    if product_id <= 0 or quantity <= 0:
        await message.answer("ID и количество должны быть больше нуля!")
        return
    result = await sell_product(product_id, quantity)
    if result == "not_found":
        await message.answer("Товар с таким ID не найден!")
    elif result == "not_enough":
        await message.answer("❌ На складе недостаточно товара!")
    elif result == "success":
        await message.answer("✅ Товар успешно продан!")
    else:
        await message.answer("Ошибка при продаже товара!")


async def main():
    await create_table()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

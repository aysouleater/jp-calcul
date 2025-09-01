import re
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

TOKEN = os.getenv("BOT_TOKEN")  # токен из Heroku Config Vars

# === ФУНКЦИЯ РАСЧЁТА ===
def calc_price(jpy: float) -> int:
    if jpy > 13000:
        first = jpy * 1.1 * 0.64
    else:
        first = jpy * 0.64 + 850
    second = (jpy / 140000.0) * 4000.0
    return round(first + second)

NUM_RE = re.compile(r"[\d\s,\.]+")

def extract_amount(text: str) -> float | None:
    m = NUM_RE.search(text.replace('\u00A0', ' '))
    if not m:
        return None
    raw = m.group(0).replace(',', '').replace(' ', '')
    try:
        return float(raw)
    except ValueError:
        return None

dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Привет! Пришли цену товара в йенах (например: 29000), "
        "а я посчитаю по формуле.\n"
        "Можно также использовать команду: /calc 29000"
    )

@dp.message(Command("calc"))
async def calc_cmd(m: Message):
    text = m.text.split(maxsplit=1)
    if len(text) < 2:
        await m.answer("Укажи цену: /calc 29000")
        return
    amt = extract_amount(text[1])
    if amt is None:
        await m.answer("Не понял цену. Пример: /calc 29000")
        return
    total = calc_price(amt)
    await m.answer(f"Цена по формуле: {total:,} йен".replace(",", " "))

@dp.message(F.text)
async def any_text(m: Message):
    amt = extract_amount(m.text)
    if amt is None:
        await m.answer("Пришли цену (например: 29000), и я посчитаю.")
        return
    total = calc_price(amt)
    await m.answer(f"Цена по формуле: {total:,} йен".replace(",", " "))

async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


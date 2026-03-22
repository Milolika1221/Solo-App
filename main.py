"""
RAID SYSTEM BOT - Точка входа
==============================

Этот файл является точкой входа для запуска бота.
Вся логика вынесена в отдельные модули архитектуры:

Структура проекта:
- main.py           - Точка входа (этот файл)
- bot.py            - Главный класс RaidSystemBot
- database.py       - DatabaseManager (SQLite)
- services.py       - UserService, EnglishService, QuestService
- handlers.py       - BotHandlers (обработчики команд)
- keyboards.py      - KeyboardManager (клавиатуры)
- constants.py      - Константы и эмодзи
- health_check.py   - Health check сервер для Render

Для запуска:
    python main.py

Требования:
    TELEGRAM_BOT_TOKEN в переменных окружения (.env)
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from bot import RaidSystemBot
from constants import Emoji

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logger.error(f"{Emoji.ERROR} Ошибка: TELEGRAM_BOT_TOKEN не найден!")
    logger.info(f"{Emoji.GEAR} Добавьте токен в .env файл или Environment Variables на Render")
    exit(1)

# ============================================
# ЗАПУСК БОТА
# ============================================

async def main():
    """
    Главная функция запуска бота.
    
    Создает экземпляр RaidSystemBot и запускает его.
    Бот будет работать до принудительной остановки.
    """
    logger.info(f"{Emoji.SWORD} Запуск RAID SYSTEM Bot...")
    
    # Создаем экземпляр бота
    bot = RaidSystemBot(TOKEN)
    
    # Запускаем бота
    await bot.run()


if __name__ == "__main__":
    # Запускаем главную функцию
    asyncio.run(main())

"""
BOT LAYER - Основной класс бота
=================================

Этот модуль содержит главный класс RaidSystemBot.
Объединяет все слои: базу данных, сервисы, обработчики.

Отвечает за:
- Инициализацию aiogram Bot и Dispatcher
- Запуск health check сервера
- Запуск polling бота
- Показ главного меню
"""

import asyncio
import logging
import os
from datetime import datetime, date
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import types, InlineKeyboardMarkup, InlineKeyboardButton

from database import DatabaseManager
from services import UserService, EnglishService, QuestService
from handlers import BotHandlers
from keyboards import KeyboardManager
from health_check import start_health_check
from constants import Emoji

logger = logging.getLogger(__name__)


class RaidSystemBot:
    """
    Главный класс Telegram бота RAID SYSTEM.
    
    Объединяет все слои архитектуры:
    - Database Layer (DatabaseManager)
    - Service Layer (UserService, EnglishService, QuestService)
    - Handler Layer (BotHandlers)
    - Keyboard Layer (KeyboardManager)
    
    Пример использования:
        bot = RaidSystemBot(token)
        await bot.run()
    """
    
    def __init__(self, token: str):
        """
        Инициализация бота и всех слоев.
        
        Args:
            token: Токен Telegram бота от @BotFather
        """
        # Инициализация aiogram Bot и Dispatcher (версия 3.x)
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode='HTML')
        )
        self.dp = Dispatcher()
        
        # Инициализация Database Layer
        self.db = DatabaseManager()
        
        # Инициализация Service Layer
        self.user_service = UserService(self.db)
        self.english_service = EnglishService(self.db)
        self.quest_service = QuestService(self.db)
        
        # Инициализация Handler Layer
        self.handlers = BotHandlers(self)
        
        logger.info(f"{Emoji.ROBOT} Бот инициализирован")
    
    async def show_main_menu(self, message: types.Message):
        """
        Показывает главное меню пользователю.
        
        Args:
            message: Объект сообщения для ответа
        """
        keyboard = KeyboardManager.get_main_keyboard()
        
        menu_text = f"""
{Emoji.SWORD} <b>RAID SYSTEM</b>

Главное меню. Выбери раздел:
        """
        
        await message.answer(menu_text, reply_markup=keyboard)
    
    async def run(self):
        """
        Главный метод запуска бота.
        
        Запускает:
        1. Health check сервер (для Render.com)
        2. Polling бота
        
        Бот будет работать до принудительной остановки.
        """
        try:
            # Запускаем health check сервер в отдельном потоке
            start_health_check()
            logger.info(f"{Emoji.GLOBE} Health check сервер запущен")
            
            # Запускаем систему уведомлений в фоне
            asyncio.create_task(self.start_notifications())
            logger.info(f"{Emoji.SUN} Система уведомлений активирована")
            
            # Запускаем бота
            logger.info(f"{Emoji.ROBOT} Бот начал polling...")
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Критическая ошибка запуска бота: {e}")
            raise
    
    async def start_notifications(self):
        """
        Запускает фоновую задачу для уведомлений.
        
        Отправляет напоминания:
        - 6:00 - Раннее утро (для студентов)
        - 9:00 - Утренний уход за кожей
        - 21:00 - Вечерний уход за кожей
        """
        logger.info(f"{Emoji.SUN} Система уведомлений запущена")
        
        while True:
            try:
                now = datetime.now()
                
                # Раннее утро 6:00
                if now.hour == 6 and now.minute == 0:
                    await self.send_skin_care_reminder("morning", "раннего утра")
                
                # Утро 9:00
                if now.hour == 9 and now.minute == 0:
                    await self.send_skin_care_reminder("morning", "утра")
                
                # Вечер 21:00
                if now.hour == 21 and now.minute == 0:
                    await self.send_skin_care_reminder("evening", "вечера")
                
                # Проверяем каждую минуту
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"{Emoji.ERROR} Ошибка в системе уведомлений: {e}")
                await asyncio.sleep(60)
    
    async def send_skin_care_reminder(self, time_of_day: str, time_name: str):
        """
        Отправляет напоминание об уходе за кожей всем пользователям.
        
        Args:
            time_of_day: 'morning' или 'evening'
            time_name: название времени для сообщения
        """
        try:
            cursor = self.db.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            
            tips = self.get_skin_care_tips(time_of_day)
            callback_data = f"skin_care_{time_of_day}"
            
            for (user_id,) in users:
                try:
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(
                                text=f"{Emoji.SUCCESS} Уход выполнен",
                                callback_data=callback_data
                            )]
                        ]
                    )
                    
                    await self.bot.send_message(
                        user_id,
                        f"{Emoji.SUN} <b>Доброе {time_name}! Время ухода за кожей</b> {Emoji.SPARKLES}\n\n"
                        f"{tips}\n\n"
                        f"{Emoji.DROPLET} Не забудь про уход!\n"
                        f"{Emoji.GIFT} +5 EXP за выполнение",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.error(f"{Emoji.ERROR} Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            logger.info(f"{Emoji.SUCCESS} Уведомления {time_name} отправлены {len(users)} пользователям")
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка отправки уведомлений: {e}")
    
    def get_skin_care_tips(self, time_of_day: str) -> str:
        """
        Возвращает советы по уходу за кожей.
        
        Args:
            time_of_day: 'morning' или 'evening'
            
        Returns:
            str: Советы по уходу
        """
        morning_tips = [
            f"{Emoji.DROPLET} Умойся прохладной водой для тонуса",
            f"{Emoji.LEAF} Нанеси легкий увлажняющий крем",
            f"{Emoji.SPARKLES} Используй сыворотку с витамином С",
            f"{Emoji.SUN} Обязательно нанеси солнцезащитный крем SPF 30+",
            f"{Emoji.DROPLET} Выпей стакан воды для гидратации",
        ]
        
        evening_tips = [
            f"{Emoji.MOON} Двухфазное очищение: масло + пенка",
            f"{Emoji.LEAF} Нанеси успокаивающий тонер",
            f"{Emoji.SPARKLES} Используй сыворотку (ретинол/пептиды)",
            f"{Emoji.DROPLET} Нанеси питательный ночной крем",
            f"{Emoji.MOON} Постарайся лечь до 23:00 для регенерации",
        ]
        
        import random
        tips = morning_tips if time_of_day == "morning" else evening_tips
        selected = random.sample(tips, min(3, len(tips)))
        return "\n".join(f"• {tip}" for tip in selected)

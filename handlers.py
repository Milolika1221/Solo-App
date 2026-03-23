"""
HANDLERS LAYER - Слой обработчиков
==================================

Этот модуль содержит обработчики команд и сообщений.
Все обработчики работают через экземпляр RaidSystemBot.

Обработчики разделены на группы:
- Command handlers: /start, /help, /stats
- Message handlers: главное меню (Квесты, Тренировки, и т.д.)
- Callback handlers: inline кнопки
"""

import logging
from datetime import date
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from constants import Emoji, MESSAGES, ANIME_UNIVERSES

logger = logging.getLogger(__name__)


class BotHandlers:
    """
    Класс для регистрации и управления обработчиками бота.
    
    Инициализируется с экземпляром RaidSystemBot для доступа к сервисам.
    """
    
    def __init__(self, bot_instance):
        """
        Инициализация обработчиков.
        
        Args:
            bot_instance: Экземпляр RaidSystemBot
        """
        self.bot = bot_instance
        self.dp = bot_instance.dp
        self.register_handlers()
    
    def register_handlers(self):
        """
        Регистрация всех обработчиков в диспетчере.
        
        Вызывается автоматически при инициализации.
        """
        # Обработчики команд
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.cmd_restart_db, Command("restart_db"))
        
        # Обработчики главного меню (Reply клавиатура)
        self.dp.message.register(
            self.handle_quests,
            F.text == "📋 Квесты"
        )
        self.dp.message.register(
            self.handle_workouts,
            F.text == "⚔️ Тренировки"
        )
        self.dp.message.register(
            self.handle_english,
            F.text == "📚 Английский"
        )
        self.dp.message.register(
            self.handle_stats,
            F.text.in_(["📊 Статус", "Статус"])
        )
        self.dp.message.register(
            self.handle_nutrition,
            F.text == "🍽️ Питание"
        )
        
        # Обработчик ввода веса (числовое сообщение)
        self.dp.message.register(
            self.handle_weight_input,
            F.text.regexp(r"^\d+(\.\d+)?$"),
            self.is_waiting_weight_input
        )
        
        # Обработчик callback запросов (inline кнопки)
        self.dp.callback_query.register(self.handle_callback)
        
        logger.info(f"{Emoji.GEAR} Обработчики зарегистрированы")
    
    # ========================================
    # COMMAND HANDLERS
    # ========================================
    
    async def cmd_start(self, message: types.Message):
        """
        Обработчик команды /start.
        
        Проверяет регистрацию пользователя:
        - Если зарегистрирован - показывает главное меню
        - Если нет - начинает процесс регистрации
        """
        try:
            user_id = message.from_user.id
            
            # Проверяем регистрацию
            if self.bot.user_service.is_registered(user_id):
                await self.bot.show_main_menu(message)
                return
            
            # Создаем пользователя
            self.bot.user_service.create_user(user_id)
            
            # Приветственное сообщение
            welcome_text = f"""
{Emoji.SWORD} <b>Добро пожаловать в RAID SYSTEM!</b>

Ты становишься Охотником в мире, где каждый день - это квест на прокачку себя.

<b>Что тебя ждет:</b>
{Emoji.TARGET} Ежедневные квесты для прокачки
{Emoji.BOOK} Английский язык (уровни A0 → C2)
{Emoji.POWER} Тренировки во вселенных аниме
{Emoji.CHART} Отслеживание прогресса

Начнем регистрацию?
            """
            
            from keyboards import KeyboardManager
            keyboard = KeyboardManager.get_registration_start_keyboard()
            
            await message.answer(welcome_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в cmd_start: {e}")
            await message.answer(MESSAGES["error_generic"])
    
    async def cmd_help(self, message: types.Message):
        """
        Обработчик команды /help.
        Показывает справку по использованию бота.
        Для админов показывает дополнительные команды.
        """
        user_id = message.from_user.id
        
        help_text = f"""
{Emoji.ROBOT} <b>RAID SYSTEM - Помощь</b>

<b>Основные команды:</b>
{Emoji.TARGET} /start - Начать работу с ботом
{Emoji.CHART} /stats - Твоя статистика
{Emoji.INFO} /help - Это сообщение

<b>Разделы меню:</b>
{Emoji.CLIPBOARD} <b>Квесты</b> - Ежедневные задания
{Emoji.SWORD} <b>Тренировки</b> - Тренировки во вселенных аниме
{Emoji.BOOK} <b>Английский</b> - Прогресс изучения языка
{Emoji.CHART} <b>Статус</b> - Твои характеристики

<b>Система прогресса:</b>
• Выполняй квесты и получай EXP
{Emoji.STAR} Повышай уровень и характеристики
{Emoji.FIRE} Поддерживай streak (последовательные дни)
{Emoji.TROPHY} Повышай уровень английского A0 → C2

<b>Система рангов:</b>
E → D → C → B → A → S
        """
        
        # Показываем админские команды только для админов
        if self.bot.db.is_admin(user_id):
            help_text += f"""

{Emoji.CROWN} <b>Админские команды:</b>
{Emoji.WARNING} /restart_db - Пересоздать базу данных (опасно!)
            """
        
        help_text += "\n\nУдачи в рейде, Охотник!"
        
        await message.answer(help_text)
    
    async def cmd_stats(self, message: types.Message):
        """Обработчик команды /stats - алиас для handle_stats"""
        await self.handle_stats(message)
    
    async def cmd_restart_db(self, message: types.Message):
        """
        Обработчик команды /restart_db (только для администратора).
        Пересоздает все таблицы базы данных.
        """
        user_id = message.from_user.id
        
        # Проверяем права администратора
        if not self.bot.db.is_admin(user_id):
            await message.answer(f"{Emoji.WARNING} У тебя нет прав для этой команды.")
            return
        
        try:
            # Запрашиваем подтверждение
            from keyboards import KeyboardManager
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{Emoji.WARNING} Да, пересоздать БД",
                            callback_data="admin_restart_db_confirm"
                        ),
                        InlineKeyboardButton(
                            text=f"{Emoji.CROSS} Отмена",
                            callback_data="admin_restart_db_cancel"
                        )
                    ]
                ]
            )
            
            await message.answer(
                f"{Emoji.WARNING} <b>ВНИМАНИЕ!</b>\n\n"
                f"Это действие удалит ВСЕ данные и пересоздаст базу данных.\n"
                f"Ты уверен?",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в cmd_restart_db: {e}")
            await message.answer(f"{Emoji.ERROR} Произошла ошибка.")
    
    async def handle_admin_callback(self, callback: types.CallbackQuery, action: str, user_id: int):
        """Обработчик админских callback-команд."""
        if action == "admin_restart_db_confirm":
            try:
                # Закрываем текущее соединение
                self.bot.db.conn.close()
                
                # Удаляем файл базы данных
                import os
                db_path = "bot_data.db"
                if os.path.exists(db_path):
                    os.remove(db_path)
                
                # Пересоздаем подключение и таблицы
                from database import DatabaseManager
                self.bot.db = DatabaseManager()
                
                # Пользователь остается админом (INSERT OR IGNORE на случай если уже существует)
                self.bot.db.execute(
                    "INSERT OR IGNORE INTO users (user_id, is_admin, registration_completed) VALUES (?, 1, 1)",
                    (user_id,)
                )
                self.bot.db.commit()
                
                await callback.message.edit_text(
                    f"{Emoji.SUCCESS} <b>База данных пересоздана!</b>\n\n"
                    f"Все таблицы созданы заново.\n"
                    f"Ты назначен администратором."
                )
                await callback.answer("БД пересоздана")
                
            except Exception as e:
                logger.error(f"{Emoji.ERROR} Ошибка пересоздания БД: {e}")
                await callback.message.edit_text(f"{Emoji.ERROR} Ошибка: {e}")
                await callback.answer("Ошибка")
                
        elif action == "admin_restart_db_cancel":
            await callback.message.edit_text(f"{Emoji.CROSS} Операция отменена.")
            await callback.answer("Отменено")
    
    # ========================================
    # MESSAGE HANDLERS (Главное меню)
    # ========================================
    
    async def handle_stats(self, message: types.Message):
        """
        Обработчик кнопки 'Статус'.
        Показывает полную статистику пользователя.
        """
        try:
            user_id = message.from_user.id
            stats = self.bot.user_service.get_user_stats(user_id)
            
            if not stats:
                await message.answer(MESSAGES["user_not_found"])
                return
            
            # Получаем название ранга английского
            english_rank = self.bot.english_service.get_english_rank_title(
                stats["english_level"]
            )
            
            # Формируем текст статистики
            stats_text = f"""
{Emoji.CHART} <b>Статус рейда Охотника</b>

{Emoji.TARGET} <b>Уровень: {stats['level']}</b>
{Emoji.STAR} Опыт: {stats['exp']}/{stats['exp_to_next']}

💪 <b>Характеристики:</b>
{Emoji.POWER} Боевая мощь: {stats['power']:.1f}
{Emoji.BRAIN} Анализ: {stats['analysis']:.1f}
{Emoji.SHIELD} Выносливость: {stats['endurance']:.1f}
{Emoji.FLASH} Скорость: {stats['speed']:.1f}

{Emoji.SPARKLES} <b>Прогресс:</b>
{Emoji.RUNNER} Streak: {stats['streak']} дней
{Emoji.BROOM} Чистота кожи: {stats['skin_health']}/100
{Emoji.BOOK} Английский: {stats['english_progress']}/1000

{Emoji.BOOK} <b>Английский язык:</b>
{english_rank}
{Emoji.TARGET} Уровень: {stats['english_level']} ({stats['english_exp']} EXP)

{Emoji.SCALE} <b>Вес:</b>
{stats['weight'] if stats['weight'] else "Не указан"} кг
            """
            
            from keyboards import KeyboardManager
            keyboard = KeyboardManager.get_weight_log_keyboard()
            
            await message.answer(stats_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_stats: {e}")
            await message.answer(MESSAGES["error_stats"])
    
    async def handle_quests(self, message: types.Message):
        """
        Обработчик кнопки 'Квесты'.
        Показывает категории ежедневных квестов.
        """
        try:
            from constants import DAILY_QUESTS, Emoji
            
            quest_text = f"{Emoji.CLIPBOARD} <b>Ежедневные квесты</b>\n\n"
            quest_text += "Выбери категорию заданий:\n\n"
            
            # Добавляем описание категорий
            for category_key, category_data in DAILY_QUESTS.items():
                quest_count = len(category_data.get("quests", []))
                quest_text += f"{category_data['title']} - {quest_count} квестов\n"
                quest_text += f"<i>{category_data['description']}</i>\n\n"
            
            from keyboards import KeyboardManager
            keyboard = KeyboardManager.get_quest_categories_keyboard()
            
            await message.answer(quest_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_quests: {e}")
            await message.answer(MESSAGES["error_generic"])
    
    async def handle_workouts(self, message: types.Message):
        """
        Обработчик кнопки 'Тренировки'.
        Сразу показывает ранги для вселенной пользователя (выбранной при регистрации).
        """
        try:
            user_id = message.from_user.id
            
            # Получаем данные пользователя
            cursor = self.bot.db.execute(
                "SELECT level, anime_universe FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            if not result:
                await message.answer(MESSAGES["user_not_found"])
                return
            
            user_level, universe = result
            universe = universe or "solo_leveling"
            
            # Преобразуем название вселенной в ключ
            universe_key = None
            for key, name in ANIME_UNIVERSES.items():
                if name == universe:
                    universe_key = key
                    break
            if not universe_key:
                universe_key = "solo_leveling"
            
            # Показываем сразу ранги для выбранной вселенной
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            from constants import WORKOUT_LIBRARY
            
            available_ranks = self.bot.quest_service.get_available_ranks(user_level)
            universe_name = ANIME_UNIVERSES.get(universe_key, universe_key)
            
            # Получаем тренировки для этой вселенной
            universe_workouts = WORKOUT_LIBRARY.get(universe_key, {})
            available_universe_ranks = [r for r in available_ranks if r in universe_workouts]
            
            if not available_universe_ranks:
                available_universe_ranks = ["E"]
            
            text = f"{Emoji.SWORD} <b>{universe_name}</b>\n\n"
            text += f"{Emoji.TARGET} <b>Доступные ранги:</b>\n"
            
            for rank in available_universe_ranks:
                workout = universe_workouts.get(rank, {})
                desc = workout.get("description", "Тренировка")
                exp = workout.get("exp", 20)
                text += f"{Emoji.FIRE} <b>Ранг {rank}</b> - {desc} (+{exp} EXP)\n"
            
            text += f"\n{Emoji.INFO} Выбери ранг для просмотра деталей:"
            
            # Создаем клавиатуру с рангами
            keyboard_buttons = []
            for rank in available_universe_ranks:
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{Emoji.SWORD} Ранг {rank}",
                    callback_data=f"workout_rank_{universe_key}_{rank}"
                )])
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{Emoji.CHART} Главное меню",
                callback_data="return_main_menu"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await message.answer(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_workouts: {e}")
            await message.answer(MESSAGES["error_generic"])
    
    async def handle_english(self, message: types.Message):
        """
        Обработчик кнопки 'Английский'.
        Показывает прогресс и ежедневные задания по английскому языку.
        Каждый день нужно прокачивать все 5 навыков.
        """
        try:
            user_id = message.from_user.id
            
            # Получаем данные пользователя
            stats = self.bot.user_service.get_user_stats(user_id)
            if not stats:
                await message.answer(MESSAGES["user_not_found"])
                return
            
            english_level = stats["english_level"]
            english_exp = stats["english_exp"]
            
            # Генерируем ежедневные задания для этого уровня
            daily_tasks = self.bot.english_service.get_daily_tasks(english_level)
            
            # Получаем требования для следующего уровня
            next_level = self.bot.english_service.get_next_english_level(english_level)
            exp_progress = 0
            
            if next_level:
                next_req = self.bot.english_service.get_english_level_requirements(next_level)
                if next_req:
                    exp_progress = int((english_exp / next_req["exp_required"]) * 100)
            
            # Формируем текст с заданиями
            english_text = self.bot.english_service.format_daily_tasks_text(
                daily_tasks, english_level, english_exp
            )
            
            # Добавляем информацию о прогрессе до следующего уровня
            if next_level:
                english_text += f"\n\n{Emoji.CHART} <b>Прогресс до {next_level}:</b> {exp_progress}%"
            
            # Создаем клавиатуру с заданиями и ссылками
            keyboard_buttons = []
            for i, task_key in enumerate(daily_tasks, 1):
                task_info = self.bot.english_service.get_task_info(task_key)
                icon = task_info.get("icon", "📝")
                name = task_info.get("name", "Задание")
                exp = task_info.get("exp", 15)
                urls = task_info.get("urls", [])
                
                # Кнопка выполнения задания
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{icon} {i}. {name} (+{exp} EXP)",
                    callback_data=f"english_task_{task_key}_{i}"
                )])
                
                # Кнопки с URL (если есть)
                if urls:
                    url_buttons = []
                    for url_item in urls[:2]:  # Максимум 2 ссылки в ряд
                        url_buttons.append(InlineKeyboardButton(
                            text=url_item.get("name", "🔗 Ссылка"),
                            url=url_item.get("url", "https://google.com")
                        ))
                    if url_buttons:
                        keyboard_buttons.append(url_buttons)
            
            # Добавляем кнопку теста
            if next_level:
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{Emoji.TARGET} Тест на уровень {next_level}",
                    callback_data=f"english_test_{next_level}"
                )])
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{Emoji.CHART} Главное меню",
                callback_data="return_main_menu"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await message.answer(english_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_english: {e}")
            await message.answer(MESSAGES["error_english"])
    
    async def handle_nutrition(self, message: types.Message):
        """
        Обработчик кнопки 'Питание'.
        Показывает раздел питания.
        """
        try:
            nutrition_text = f"""
{Emoji.FORK_KNIFE} <b>Питание</b>

Раздел в разработке...

Здесь будет:
• Планы питания
• Подсчет калорий
• Отслеживание воды
            """
            await message.answer(nutrition_text)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_nutrition: {e}")
            await message.answer(MESSAGES["error_generic"])
    
    # Словарь для отслеживания пользователей, ожидающих ввода веса
    _waiting_weight_input = {}
    
    async def is_waiting_weight_input(self, message: types.Message) -> bool:
        """Проверяет, ожидается ли ввод веса от пользователя."""
        user_id = message.from_user.id
        return self._waiting_weight_input.get(user_id, False)
    
    async def handle_weight_input(self, message: types.Message):
        """
        Обработчик ввода веса.
        Сохраняет вес пользователя в базу данных.
        """
        try:
            user_id = message.from_user.id
            weight_text = message.text.strip()
            
            # Парсим вес
            try:
                weight = float(weight_text)
                if weight < 30 or weight > 300:
                    await message.answer(f"{Emoji.WARNING} Введи реалистичный вес (30-300 кг)")
                    return
            except ValueError:
                await message.answer(f"{Emoji.WARNING} Введи число, например: 65.5")
                return
            
            # Сохраняем вес
            self.bot.db.execute(
                "UPDATE users SET weight = ? WHERE user_id = ?",
                (weight, user_id)
            )
            self.bot.db.commit()
            
            # Сбрасываем флаг ожидания
            self._waiting_weight_input[user_id] = False
            
            from keyboards import KeyboardManager
            await message.answer(
                f"{Emoji.SUCCESS} <b>Вес записан!</b>\n\n"
                f"{Emoji.SCALE} Текущий вес: {weight} кг",
                reply_markup=KeyboardManager.get_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка при сохранении веса: {e}")
            await message.answer(f"{Emoji.ERROR} Произошла ошибка. Попробуй позже.")
    
    # ========================================
    # CALLBACK HANDLER
    # ========================================
    
    async def handle_callback(self, callback: types.CallbackQuery):
        """
        Главный обработчик callback-запросов от inline кнопок.
        
        Распределяет запросы по специализированным обработчикам:
        - reg_* - регистрация
        - quest_* - квесты
        - workout_* - тренировки
        - english_* - английский язык
        """
        action = callback.data
        user_id = callback.from_user.id
        
        try:
            # Возврат в главное меню
            if action == "return_main_menu":
                if self.bot.user_service.is_registered(user_id):
                    await self.bot.show_main_menu(callback.message)
                else:
                    await callback.message.answer(MESSAGES["registration_incomplete"])
                await callback.answer()
                return
            
            # Регистрация
            if action.startswith("reg_"):
                await self.handle_registration(callback, action, user_id)
                return
            
            # Квесты
            if action == "quest_menu":
                await self.handle_quests(callback.message)
                await callback.answer()
                return
            
            if action.startswith("quest_category_"):
                category = action.replace("quest_category_", "")
                await self.show_quest_category(callback, user_id, category)
                return
            
            if action.startswith("complete_quest_"):
                quest_id = action.replace("complete_quest_", "")
                await self.complete_quest(callback, user_id, quest_id)
                return
            
            # Тренировки
            if action == "workout_menu":
                await self.handle_workouts(callback.message)
                await callback.answer()
                return
            
            if action.startswith("workout_universe_"):
                universe = action.split("_")[2]
                await self.show_workout_ranks(callback, universe)
                return
            
            if action.startswith("workout_rank_"):
                parts = action.split("_")
                universe = parts[2]
                rank = parts[3]
                await self.show_workout_details(callback, universe, rank)
                return
            
            if action.startswith("complete_workout_"):
                parts = action.split("_")
                universe = parts[2]
                rank = parts[3]
                await self.complete_workout(callback, universe, rank)
                return
            
            # Английский
            if action.startswith("english_task_"):
                parts = action.split("_")
                task_key = parts[2]
                task_number = parts[3] if len(parts) > 3 else "1"
                await self.complete_english_task(callback, user_id, task_key, task_number)
                return
            
            if action.startswith("english_test_"):
                # Получаем уровень теста из callback_data
                test_level = action.replace("english_test_", "")
                await self.start_english_test(callback, user_id, test_level)
                return
            
            # Обработка тестов - начало и ответы
            if action.startswith("test_start_"):
                test_level = action.replace("test_start_", "")
                # Показываем первый вопрос
                await self.show_test_question(callback, user_id)
                await callback.answer()
                return
            
            if action.startswith("test_answer_"):
                # Формат: test_answer_{level}_{question_idx}_{answer_idx}
                parts = action.split("_")
                if len(parts) >= 5:
                    level = parts[2]
                    question_idx = int(parts[3])
                    answer_idx = int(parts[4])
                    await self.handle_test_answer(callback, user_id, level, question_idx, answer_idx)
                return
            
            # Меню английского языка
            if action == "english_menu":
                await self.handle_english(callback.message)
                await callback.answer()
                return
            
            # Запись веса
            if action == "weight_log":
                # Устанавливаем флаг ожидания ввода веса
                self._waiting_weight_input[user_id] = True
                await callback.message.answer(
                    f"{Emoji.SCALE} Введи свой текущий вес в кг (например: 65.5):"
                )
                await callback.answer()
                return
            
            # Уход за кожей
            if action == "skin_care_morning":
                await self.handle_skin_care(callback, user_id, "morning")
                return
            
            if action == "skin_care_evening":
                await self.handle_skin_care(callback, user_id, "evening")
                return
            
            # Админские команды
            if action.startswith("admin_"):
                await self.handle_admin_callback(callback, action, user_id)
                return
            
            # Неизвестное действие
            await callback.answer(f"{Emoji.WARNING} Функция в разработке")
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_callback: {e}")
            await callback.answer(f"{Emoji.ERROR} Произошла ошибка")
    
    async def handle_registration(
        self,
        callback: types.CallbackQuery,
        action: str,
        user_id: int
    ):
        """
        Обработчик этапов регистрации.
        
        Args:
            callback: Объект callback запроса
            action: Действие (reg_continue, reg_skip, reg_universe_*, reg_gender_*)
            user_id: ID пользователя Telegram
        """
        from keyboards import KeyboardManager
        from constants import ANIME_UNIVERSES, QUEST_REWARDS
        
        # Продолжить регистрацию - выбор вселенной
        if action == "reg_continue":
            keyboard = KeyboardManager.get_universe_keyboard()
            await callback.message.answer(
                f"{Emoji.SWORD} <b>Выбери свою вселенную:</b>",
                reply_markup=keyboard
            )
            await callback.answer()
            return
        
        # Быстрая регистрация
        if action == "reg_skip":
            self.bot.db.execute("""
                UPDATE users 
                SET registration_completed = 1,
                    gender = 'женский',
                    skin_type = 'нормальная',
                    english_level = 'B1',
                    anime_universe = 'Solo Leveling'
                WHERE user_id = ?
            """, (user_id,))
            self.bot.db.commit()
            
            # Начисляем бонус
            self.bot.user_service.add_exp(user_id, QUEST_REWARDS.get("registration", 30))
            
            await callback.message.answer(
                f"{Emoji.PARTY} <b>Профиль создан!</b>\n\n"
                f"{Emoji.GIFT} Бонус: +30 EXP\n"
                f"Настройки по умолчанию применены.",
                reply_markup=KeyboardManager.get_main_keyboard()
            )
            await callback.answer()
            return
        
        # Выбор вселенной
        if action.startswith("reg_universe_"):
            universe_key = action.split("_")[2]
            universe_name = ANIME_UNIVERSES.get(universe_key, "Solo Leveling")
            
            self.bot.db.execute(
                "UPDATE users SET anime_universe = ? WHERE user_id = ?",
                (universe_name, user_id)
            )
            self.bot.db.commit()
            
            keyboard = KeyboardManager.get_gender_keyboard()
            await callback.message.answer(
                f"{Emoji.SUCCESS} <b>Вселенная выбрана: {universe_name}</b>\n\n"
                f"Теперь выбери пол:",
                reply_markup=keyboard
            )
            await callback.answer()
            return
        
        # Выбор пола
        if action.startswith("reg_gender_"):
            gender_map = {
                "female": "женский",
                "male": "мужской",
                "none": None
            }
            gender = gender_map.get(action.split("_")[2])
            
            self.bot.db.execute(
                "UPDATE users SET gender = ? WHERE user_id = ?",
                (gender, user_id)
            )
            
            # Завершаем регистрацию
            self.bot.db.execute("""
                UPDATE users 
                SET english_level = 'A0',
                    registration_completed = 1
                WHERE user_id = ?
            """, (user_id,))
            
            self.bot.db.commit()
            
            # Начисляем бонус
            self.bot.user_service.add_exp(user_id, QUEST_REWARDS.get("registration", 50))
            
            await callback.message.answer(
                f"{Emoji.PARTY} <b>Поздравляем, регистрация завершена!</b>\n\n"
                f"{Emoji.BOOK} Английский: A0\n"
                f"{Emoji.SWORD} Вселенная: Solo Leveling\n"
                f"{Emoji.GIFT} Бонус: +50 EXP",
                reply_markup=KeyboardManager.get_main_keyboard()
            )
            await callback.answer()
            return
    
    # ========================================
    # КВЕСТЫ
    # ========================================
    
    async def show_quest_category(self, callback: types.CallbackQuery, user_id: int, category: str):
        """
        Показывает квесты выбранной категории.
        """
        try:
            from constants import DAILY_QUESTS, Emoji
            
            category_data = DAILY_QUESTS.get(category)
            if not category_data:
                await callback.message.answer(f"{Emoji.ERROR} Категория не найдена")
                await callback.answer()
                return
            
            # Формируем текст с квестами
            text = f"{category_data['title']}\n\n"
            text += f"<i>{category_data['description']}</i>\n\n"
            text += f"{Emoji.CLIPBOARD} <b>Доступные квесты:</b>\n\n"
            
            keyboard_buttons = []
            for quest in category_data.get("quests", []):
                icon = quest.get("icon", "📝")
                name = quest.get("name", "Квест")
                description = quest.get("description", "")
                exp = quest.get("exp", 15)
                quest_id = quest.get("id", "")
                
                text += f"{icon} <b>{name}</b> (+{exp} EXP)\n"
                text += f"<i>{description}</i>\n\n"
                
                # Добавляем кнопку для выполнения квеста
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{Emoji.SUCCESS} {name}",
                    callback_data=f"complete_quest_{quest_id}"
                )])
            
            # Добавляем кнопку назад
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{Emoji.BACK} К категориям",
                callback_data="quest_menu"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в show_quest_category: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def complete_quest(self, callback: types.CallbackQuery, user_id: int, quest_id: str):
        """
        Обрабатывает выполнение квеста.
        """
        try:
            from constants import DAILY_QUESTS, QUEST_REWARDS, Emoji
            
            # Находим квест по ID
            quest_info = None
            category_name = ""
            for cat_key, cat_data in DAILY_QUESTS.items():
                for quest in cat_data.get("quests", []):
                    if quest.get("id") == quest_id:
                        quest_info = quest
                        category_name = cat_data.get("title", "")
                        break
                if quest_info:
                    break
            
            if not quest_info:
                await callback.answer(f"{Emoji.ERROR} Квест не найден")
                return
            
            # Получаем награду
            exp_reward = quest_info.get("exp", QUEST_REWARDS.get(quest_id, 20))
            quest_name = quest_info.get("name", "Квест")
            icon = quest_info.get("icon", "📝")
            
            # Начисляем опыт
            new_level, level_up = self.bot.user_service.add_exp(
                user_id, exp_reward, f"Квест: {quest_name}"
            )
            
            # Формируем текст
            text = f"{Emoji.SUCCESS} <b>Квест выполнен!</b>\n\n"
            text += f"{icon} {quest_name}\n"
            text += f"{Emoji.STAR} +{exp_reward} EXP\n\n"
            
            if level_up:
                text += f"{Emoji.TROPHY} <b>Поздравляем! Новый уровень: {new_level}!</b>\n\n"
            
            text += f"{Emoji.FIRE} Отличная работа, Охотник!"
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.CLIPBOARD} К квестам",
                        callback_data="quest_menu"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.CHART} Главное меню",
                        callback_data="return_main_menu"
                    )],
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer(f"+{exp_reward} EXP")
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в complete_quest: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    # ========================================
    # МЕТОДЫ ТРЕНИРОВОК
    # ========================================
    
    async def show_workout_ranks(self, callback: types.CallbackQuery, universe: str):
        """
        Показывает доступные ранги тренировок для выбранной вселенной.
        """
        try:
            user_id = callback.from_user.id
            stats = self.bot.user_service.get_user_stats(user_id)
            
            if not stats:
                await callback.message.answer(MESSAGES["user_not_found"])
                await callback.answer()
                return
            
            from constants import WORKOUT_LIBRARY
            
            available_ranks = self.bot.quest_service.get_available_ranks(stats["level"])
            universe_name = ANIME_UNIVERSES.get(universe, universe)
            
            # Получаем тренировки для этой вселенной
            universe_workouts = WORKOUT_LIBRARY.get(universe, {})
            available_universe_ranks = [r for r in available_ranks if r in universe_workouts]
            
            if not available_universe_ranks:
                available_universe_ranks = ["E"]
            
            text = f"{Emoji.SWORD} <b>{universe_name}</b>\n\n"
            text += f"{Emoji.TARGET} <b>Доступные ранги:</b>\n"
            
            for rank in available_universe_ranks:
                workout = universe_workouts.get(rank, {})
                desc = workout.get("description", "Тренировка")
                exp = workout.get("exp", 20)
                text += f"{Emoji.FIRE} <b>Ранг {rank}</b> - {desc} (+{exp} EXP)\n"
            
            text += f"\n{Emoji.INFO} Выбери ранг для просмотра деталей:"
            
            # Создаем клавиатуру с рангами
            keyboard_buttons = []
            for rank in available_universe_ranks:
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{Emoji.SWORD} Ранг {rank}",
                    callback_data=f"workout_rank_{universe}_{rank}"
                )])
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{Emoji.BACK} К вселенным",
                callback_data="workout_menu"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в show_workout_ranks: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def show_workout_details(self, callback: types.CallbackQuery, universe: str, rank: str):
        """
        Показывает детали выбранной тренировки.
        """
        try:
            workout = self.bot.quest_service.get_workout(universe, rank)
            
            if not workout:
                await callback.message.answer(
                    f"{Emoji.ERROR} Тренировка не найдена. Попробуй другой ранг."
                )
                await callback.answer()
                return
            
            text = self.bot.quest_service.format_workout_text(workout)
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.SUCCESS} Тренировка выполнена",
                        callback_data=f"complete_workout_{universe}_{rank}"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.BACK} К рангам",
                        callback_data=f"workout_universe_{universe}"
                    )],
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в show_workout_details: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def complete_workout(self, callback: types.CallbackQuery, universe: str, rank: str):
        """
        Завершает тренировку и начисляет награду.
        """
        try:
            user_id = callback.from_user.id
            
            # Проверяем, не выполнена ли тренировка сегодня
            workout_key = f"{universe}_{rank}"
            cursor = self.bot.db.execute(
                """
                SELECT COUNT(*) FROM daily_quests 
                WHERE user_id = ? AND title = ? AND date = ? AND type = 'workout'
                """,
                (user_id, workout_key, date.today())
            )
            already_completed = cursor.fetchone()[0] > 0
            
            if already_completed:
                await callback.answer(f"{Emoji.COMPLETED} Эта тренировка уже выполнена сегодня!")
                return
            
            workout = self.bot.quest_service.get_workout(universe, rank)
            exp_reward = workout.get("exp", 20) if workout else 20
            universe_name = ANIME_UNIVERSES.get(universe, universe)
            
            # Начисляем опыт
            new_level, level_up = self.bot.user_service.add_exp(
                user_id, exp_reward, f"Тренировка {universe_name} {rank}-rank"
            )
            
            # Записываем выполнение тренировки в daily_quests
            self.bot.db.execute(
                """
                INSERT INTO daily_quests (user_id, date, title, description, type, exp_reward, completed)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (user_id, date.today(), workout_key, f"Тренировка {universe_name} {rank}-rank", "workout", exp_reward)
            )
            self.bot.db.commit()
            
            text = f"{Emoji.PARTY} <b>Тренировка завершена!</b>\n\n"
            text += f"{Emoji.SWORD} Вселенная: {universe_name}\n"
            text += f"{Emoji.TARGET} Ранг: {rank.upper()}\n"
            text += f"{Emoji.STAR} Награда: +{exp_reward} EXP\n\n"
            
            if level_up:
                text += f"{Emoji.TROPHY} <b>Поздравляем! Новый уровень: {new_level}!</b>\n\n"
            
            text += f"{Emoji.FIRE} Отличная работа, Охотник!"
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.SWORD} Еще тренировка",
                        callback_data=f"workout_universe_{universe}"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.BACK} К тренировкам",
                        callback_data="workout_menu"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.CHART} Главное меню",
                        callback_data="return_main_menu"
                    )],
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer(f"+{exp_reward} EXP")
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в complete_workout: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    # ========================================
    # УХОД ЗА КОЖЕЙ
    # ========================================
    
    async def handle_skin_care(self, callback: types.CallbackQuery, user_id: int, time_of_day: str):
        """
        Обработчик ухода за кожей (утро/вечер).
        """
        try:
            user_id = callback.from_user.id
            
            # Проверяем, не выполнен ли уход за кожей сегодня
            cursor = self.bot.db.execute(
                """
                SELECT COUNT(*) FROM daily_quests 
                WHERE user_id = ? AND title = ? AND date = ? AND type = 'skincare'
                """,
                (user_id, f"skincare_{time_of_day}", date.today())
            )
            already_completed = cursor.fetchone()[0] > 0
            
            if already_completed:
                await callback.answer(f"{Emoji.COMPLETED} Уход за кожей уже выполнен сегодня!")
                return
            
            # Начисляем EXP
            self.bot.user_service.add_exp(user_id, 5, f"Уход за кожей ({time_of_day})")
            
            # Записываем выполнение ухода за кожей в daily_quests
            self.bot.db.execute(
                """
                INSERT INTO daily_quests (user_id, date, title, description, type, exp_reward, completed)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (user_id, date.today(), f"skincare_{time_of_day}", f"Уход за кожей ({time_of_day})", "skincare", 5)
            )
            self.bot.db.commit()
            
            if time_of_day == "morning":
                text = (
                    f"{Emoji.SUCCESS} <b>Утренний уход выполнен!</b> +5 EXP\n\n"
                    f"{Emoji.SUN} Отличное начало дня!\n"
                    f"{Emoji.SPARKLES} Твоя кожа скажет тебе спасибо!"
                )
            else:
                text = (
                    f"{Emoji.SUCCESS} <b>Вечерний уход выполнен!</b> +5 EXP\n\n"
                    f"{Emoji.MOON} Сладких снов!\n"
                    f"{Emoji.SPARKLES} Кожа регенерируется во время сна!"
                )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.CHART} Статус",
                        callback_data="return_main_menu"
                    )]
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_skin_care: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    # ========================================
    # АНГЛИЙСКИЙ ЯЗЫК - ВЫПОЛНЕНИЕ ЗАДАНИЙ
    # ========================================
    
    async def complete_english_task(
        self, 
        callback: types.CallbackQuery, 
        user_id: int, 
        task_key: str, 
        task_number: str
    ):
        """
        Обрабатывает выполнение задания по английскому языку.
        
        Args:
            callback: Объект callback запроса
            user_id: ID пользователя
            task_key: Ключ задания (vocabulary, listening_video и т.д.)
            task_number: Номер задания для отображения
        """
        try:
            # Проверяем, не выполнено ли задание сегодня
            cursor = self.bot.db.execute(
                """
                SELECT COUNT(*) FROM english_progress 
                WHERE user_id = ? AND activity_type = ? AND date = ?
                """,
                (user_id, task_key, date.today())
            )
            already_completed = cursor.fetchone()[0] > 0
            
            if already_completed:
                await callback.answer(f"{Emoji.COMPLETED} Это задание уже выполнено сегодня!")
                return
            
            # Получаем информацию о задании
            task_info = self.bot.english_service.get_task_info(task_key)
            exp_reward = task_info.get("exp", 15)
            task_name = task_info.get("name", "Задание")
            icon = task_info.get("icon", "📝")
            skills = task_info.get("skills", [])
            
            # Начисляем опыт общий
            new_level, level_up = self.bot.user_service.add_exp(
                user_id, exp_reward, f"Английский: {task_name}"
            )
            
            # Начисляем опыт по английскому
            self.bot.english_service.add_english_exp(user_id, exp_reward)
            
            # Записываем прогресс в базу данных
            self.bot.db.execute(
                """
                INSERT INTO english_progress (user_id, activity_type, amount, exp_gained, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, task_key, 1, exp_reward, date.today())
            )
            self.bot.db.commit()
            
            # Формируем текст подтверждения
            text = f"{Emoji.SUCCESS} <b>Задание выполнено!</b>\n\n"
            text += f"{icon} {task_name}\n"
            text += f"{Emoji.STAR} +{exp_reward} EXP\n"
            text += f"{Emoji.BOOK} Навыки: {', '.join(skills)}\n\n"
            
            if level_up:
                text += f"{Emoji.TROPHY} <b>Поздравляем! Новый уровень: {new_level}!</b>\n\n"
            
            text += f"{Emoji.FIRE} Отличная работа! Продолжай в том же духе!"
            
            # Добавляем ссылки на ресурсы
            keyboard_buttons = [
                [InlineKeyboardButton(
                    text=f"{Emoji.BOOK} К английскому",
                    callback_data="english_menu"
                )],
            ]
            
            # Добавляем ссылки на ресурсы задания
            urls = task_info.get("urls", [])
            if urls:
                for url_item in urls[:2]:
                    keyboard_buttons.append([InlineKeyboardButton(
                        text=f"🔗 {url_item.get('name', 'Ссылка')}",
                        url=url_item.get("url", "https://google.com")
                    )])
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{Emoji.CHART} Главное меню",
                callback_data="return_main_menu"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer(f"+{exp_reward} EXP")
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в complete_english_task: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    # ========================================
    # АНГЛИЙСКИЙ ЯЗЫК - ТЕСТЫ НА УРОВЕНЬ
    # ========================================
    
    # Хранение состояния тестов для пользователей
    _test_sessions = {}
    
    async def start_english_test(self, callback: types.CallbackQuery, user_id: int, test_level: str):
        """
        Начинает тест на повышение уровня английского.
        
        Args:
            callback: Объект callback запроса
            user_id: ID пользователя
            test_level: Уровень теста (A1, A2, B1 и т.д.)
        """
        try:
            from constants import ENGLISH_TESTS
            
            # Получаем данные теста
            test_data = ENGLISH_TESTS.get(test_level)
            if not test_data:
                await callback.message.answer(f"{Emoji.ERROR} Тест для уровня {test_level} не найден")
                await callback.answer()
                return
            
            # Проверяем, достаточно ли EXP для прохождения теста
            stats = self.bot.user_service.get_user_stats(user_id)
            current_level = stats.get("english_level", "A0")
            current_exp = stats.get("english_exp", 0)
            
            # Получаем требования для следующего уровня
            next_level_data = self.bot.english_service.get_english_level_requirements(test_level)
            if not next_level_data:
                await callback.message.answer(f"{Emoji.ERROR} Ошибка получения требований уровня")
                await callback.answer()
                return
            
            required_exp = next_level_data.get("exp_required", 100)
            
            if current_exp < required_exp:
                await callback.message.answer(
                    f"{Emoji.WARNING} <b>Недостаточно опыта!</b>\n\n"
                    f"Для теста на уровень {test_level} нужно {required_exp} EXP\n"
                    f"У тебя сейчас: {current_exp} EXP\n\n"
                    f"{Emoji.BOOK} Продолжай выполнять задания по английскому!"
                )
                await callback.answer()
                return
            
            # Инициализируем сессию теста
            self._test_sessions[user_id] = {
                "level": test_level,
                "current_question": 0,
                "correct_answers": 0,
                "questions": test_data["questions"],
                "test_data": test_data
            }
            
            # Отправляем информацию о тесте
            text = f"{Emoji.BOOK} <b>{test_data['title']}</b>\n\n"
            text += f"{test_data['description']}\n\n"
            text += f"{Emoji.INFO} <b>Всего вопросов:</b> {len(test_data['questions'])}\n"
            text += f"{Emoji.TARGET} <b>Проходной балл:</b> {test_data['pass_score']}/{len(test_data['questions'])}\n\n"
            text += f"{Emoji.WARNING} Внимательно читай вопросы и выбирай правильные ответы!"
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.TARGET} Начать тест",
                        callback_data=f"test_start_{test_level}"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.BACK} Отмена",
                        callback_data="english_menu"
                    )]
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в start_english_test: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def show_test_question(self, callback: types.CallbackQuery, user_id: int):
        """
        Показывает текущий вопрос теста.
        """
        try:
            session = self._test_sessions.get(user_id)
            if not session:
                await callback.message.answer(f"{Emoji.ERROR} Сессия теста не найдена")
                return
            
            current_idx = session["current_question"]
            questions = session["questions"]
            test_level = session["level"]
            
            # Проверяем, закончились ли вопросы
            if current_idx >= len(questions):
                await self.finish_english_test(callback, user_id)
                return
            
            question = questions[current_idx]
            question_text = question["question"]
            options = question["options"]
            
            # Формируем текст вопроса
            text = f"{Emoji.BOOK} <b>Вопрос {current_idx + 1}/{len(questions)}</b>\n\n"
            text += f"{question_text}\n\n"
            
            # Создаем клавиатуру с вариантами ответов
            keyboard_buttons = []
            for i, option in enumerate(options):
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{i+1}. {option}",
                    callback_data=f"test_answer_{test_level}_{current_idx}_{i}"
                )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в show_test_question: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def handle_test_answer(self, callback: types.CallbackQuery, user_id: int, level: str, question_idx: int, answer_idx: int):
        """
        Обрабатывает ответ на вопрос теста.
        """
        try:
            session = self._test_sessions.get(user_id)
            if not session:
                await callback.message.answer(f"{Emoji.ERROR} Сессия теста не найдена")
                await callback.answer()
                return
            
            # Проверяем соответствие индекса вопроса
            if question_idx != session["current_question"]:
                await callback.answer(f"{Emoji.WARNING} Этот вопрос уже пройден")
                return
            
            questions = session["questions"]
            question = questions[question_idx]
            correct_answer = question["correct"]
            
            # Проверяем правильность ответа
            if answer_idx == correct_answer:
                session["correct_answers"] += 1
                await callback.answer(f"{Emoji.SUCCESS} Правильно!")
            else:
                correct_option = question["options"][correct_answer]
                await callback.answer(f"{Emoji.ERROR} Неправильно! Ответ: {correct_option}")
            
            # Переходим к следующему вопросу
            session["current_question"] += 1
            
            # Показываем следующий вопрос или завершаем тест
            if session["current_question"] >= len(questions):
                await self.finish_english_test(callback, user_id)
            else:
                await self.show_test_question(callback, user_id)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_test_answer: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")
    
    async def finish_english_test(self, callback: types.CallbackQuery, user_id: int):
        """
        Завершает тест и показывает результаты.
        """
        try:
            session = self._test_sessions.get(user_id)
            if not session:
                await callback.message.answer(f"{Emoji.ERROR} Сессия теста не найдена")
                return
            
            test_level = session["level"]
            correct = session["correct_answers"]
            total = len(session["questions"])
            test_data = session["test_data"]
            pass_score = test_data["pass_score"]
            
            # Определяем результат
            passed = correct >= pass_score
            
            # Формируем текст результатов
            if passed:
                # Обновляем уровень в базе данных
                self.bot.db.execute(
                    "UPDATE users SET english_level = ?, english_exp = 0 WHERE user_id = ?",
                    (test_level, user_id)
                )
                self.bot.db.commit()
                
                level_name = self.bot.english_service.get_english_rank_title(test_level)
                
                text = f"{Emoji.PARTY} <b>Тест пройден!</b>\n\n"
                text += f"{Emoji.TARGET} Результат: {correct}/{total} правильных ответов\n"
                text += f"{Emoji.TROPHY} <b>Новый уровень: {test_level}!</b>\n"
                text += f"{level_name}\n\n"
                text += f"{Emoji.STAR} Поздравляем с повышением, Охотник!"
                
                # Начисляем бонусный опыт
                bonus_exp = 50
                self.bot.user_service.add_exp(user_id, bonus_exp, f"Повышение уровня английского до {test_level}")
                text += f"\n\n{Emoji.GIFT} Бонус: +{bonus_exp} EXP"
            else:
                text = f"{Emoji.ERROR} <b>Тест не пройден</b>\n\n"
                text += f"{Emoji.TARGET} Результат: {correct}/{total} правильных ответов\n"
                text += f"{Emoji.WARNING} Нужно набрать минимум {pass_score} баллов\n\n"
                text += f"{Emoji.BOOK} Не расстраивайся! Продолжай тренироваться и попробуй снова позже."
            
            # Записываем результат теста в базу
            self.bot.db.execute(
                """
                INSERT INTO english_test_results (user_id, test_date, from_level, to_level, score, passed)
                VALUES (?, date('now'), ?, ?, ?, ?)
                """,
                (user_id, session["level"], test_level, correct, passed)
            )
            self.bot.db.commit()
            
            # Очищаем сессию
            del self._test_sessions[user_id]
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.BOOK} К английскому",
                        callback_data="english_menu"
                    )],
                    [InlineKeyboardButton(
                        text=f"{Emoji.CHART} Главное меню",
                        callback_data="return_main_menu"
                    )]
                ]
            )
            
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в finish_english_test: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")

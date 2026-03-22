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
        """
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

Удачи в рейде, Охотник!
        """
        await message.answer(help_text)
    
    async def cmd_stats(self, message: types.Message):
        """Обработчик команды /stats - алиас для handle_stats"""
        await self.handle_stats(message)
    
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
            quest_text = f"{Emoji.CLIPBOARD} <b>Ежедневные квесты</b>\n\n"
            quest_text += "Выбери категорию заданий:\n\n"
            
            from keyboards import KeyboardManager
            keyboard = KeyboardManager.get_quest_categories_keyboard()
            
            await message.answer(quest_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка в handle_quests: {e}")
            await message.answer(MESSAGES["error_generic"])
    
    async def handle_workouts(self, message: types.Message):
        """
        Обработчик кнопки 'Тренировки'.
        Показывает доступные вселенные для тренировок.
        """
        try:
            user_id = message.from_user.id
            
            # Получаем уровень пользователя
            stats = self.bot.user_service.get_user_stats(user_id)
            if not stats:
                await message.answer(MESSAGES["user_not_found"])
                return
            
            from keyboards import KeyboardManager
            available_ranks = self.bot.quest_service.get_available_ranks(stats["level"])
            
            workout_text = f"""
{Emoji.SWORD} <b>Тренировки</b>

Выбери вселенную для тренировки:

<b>Доступные ранги:</b> {', '.join(available_ranks)}
            """
            
            keyboard = KeyboardManager.get_workout_universes_keyboard()
            
            await message.answer(workout_text, reply_markup=keyboard)
            
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
            
            # Создаем клавиатуру с заданиями
            keyboard_buttons = []
            for i, task_key in enumerate(daily_tasks, 1):
                task_info = self.bot.english_service.get_task_info(task_key)
                icon = task_info.get("icon", "📝")
                name = task_info.get("name", "Задание")
                exp = task_info.get("exp", 15)
                
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"{icon} {i}. {name} (+{exp} EXP)",
                    callback_data=f"english_task_{task_key}_{i}"
                )])
            
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
            if action.startswith("quest_"):
                await callback.answer(f"{Emoji.SUCCESS} Квест в разработке")
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
                await callback.answer(f"{Emoji.SUCCESS} Тест в разработке")
                return
            
            # Запись веса
            if action == "weight_log":
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
            
            workout = self.bot.quest_service.get_workout(universe, rank)
            exp_reward = workout.get("exp", 20) if workout else 20
            universe_name = ANIME_UNIVERSES.get(universe, universe)
            
            # Начисляем опыт
            new_level, level_up = self.bot.user_service.add_exp(
                user_id, exp_reward, f"Тренировка {universe_name} {rank}-rank"
            )
            
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
            # Начисляем EXP
            self.bot.user_service.add_exp(user_id, 5, f"Уход за кожей ({time_of_day})")
            
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
                (user_id, skills[0] if skills else "other", 1, exp_reward, date.today())
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
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{Emoji.BOOK} К английскому",
                        callback_data="english_menu"
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
            logger.error(f"{Emoji.ERROR} Ошибка в complete_english_task: {e}")
            await callback.answer(f"{Emoji.ERROR} Ошибка")

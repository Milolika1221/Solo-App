import asyncio
import logging
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import sqlite3
import os
from dotenv import load_dotenv
import json
import random
from health_check import start_health_check

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-abcdef1234567890abcdef1234567890abcdef12")  # API ключ для ИИ-интеграции

if not TOKEN:
    print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    print("🔧 Добавьте токен в .env файл или Environment Variables на Render")
    exit(1)


class SimpleRaidBot:
    def __init__(self, token):
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
        self.dp = Dispatcher()
        self.setup_handlers()
        self.init_database()

    def init_database(self):
        """Инициализация базы данных со всеми необходимыми таблицами"""
        self.conn = sqlite3.connect("raid_system.db")
        cursor = self.conn.cursor()

        # Очищаем старые данные о питании, если таблица существует
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nutrition_plans'"
        )
        if cursor.fetchone():
            cursor.execute("DELETE FROM nutrition_plans")

        # Таблица пользователей (расширенная согласно ТЗ)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                exp_to_next INTEGER DEFAULT 100,
                power REAL DEFAULT 10.0,
                analysis REAL DEFAULT 10.0,
                endurance REAL DEFAULT 10.0,
                speed REAL DEFAULT 10.0,
                skin_health INTEGER DEFAULT 50,
                english_progress INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                last_activity DATE,
                weight REAL,
                height REAL,
                target_weight REAL,
                gender TEXT,
                skin_type TEXT,
                english_level TEXT DEFAULT 'A0',
                english_exp INTEGER DEFAULT 0,
                english_level_progress INTEGER DEFAULT 0,
                english_test_attempts INTEGER DEFAULT 0,
                last_english_test_date DATE,
                                anime_universe TEXT DEFAULT 'Solo Leveling',
                registration_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица ежедневных квестов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_quests (
                quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                title TEXT,
                description TEXT,
                type TEXT,
                exp_reward INTEGER,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица прогресса по английскому
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS english_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                amount INTEGER,
                exp_gained INTEGER,
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица инвентаря
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_name TEXT,
                item_type TEXT,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица достижений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_name TEXT,
                unlocked_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица планов питания
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                breakfast TEXT,
                lunch TEXT,
                dinner TEXT,
                snack TEXT,
                water_goal INTEGER DEFAULT 8,
                water_consumed INTEGER DEFAULT 0,
                total_calories INTEGER,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица отслеживания веса
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_tracking (
                tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                weight REAL,
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица ежедневных заданий по английскому
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_english_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                task_type TEXT,
                task_content TEXT,
                task_link TEXT,
                completed BOOLEAN DEFAULT 0,
                exp_reward INTEGER DEFAULT 5,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица требований к уровням английского
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS english_level_requirements (
                level TEXT PRIMARY KEY,
                exp_required INTEGER,
                min_tasks_completed INTEGER,
                grammar_topics TEXT,
                vocabulary_topics TEXT,
                speaking_requirements TEXT,
                listening_requirements TEXT,
                reading_requirements TEXT,
                writing_requirements TEXT
            )
        """)

        # Таблица результатов тестов по английскому
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS english_test_results (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_date DATE,
                level_tested TEXT,
                grammar_score INTEGER,
                vocabulary_score INTEGER,
                speaking_score INTEGER,
                listening_score INTEGER,
                reading_score INTEGER,
                writing_score INTEGER,
                total_score INTEGER,
                passed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Инициализация требований к уровням
        cursor.execute("""
            INSERT OR IGNORE INTO english_level_requirements VALUES
            ('A0', 0, 0, 'Basic alphabet, greetings', 'Numbers 1-100, colors', 'Basic introductions', 'Simple instructions', 'Very short texts', 'Basic phrases'),
            ('A1', 100, 10, 'Present Simple, articles, basic prepositions', 'Family, food, daily routine', 'Ask/answer basic questions', 'Slow clear speech', 'Short simple texts', 'Fill forms, short messages'),
            ('A2', 300, 25, 'Past Simple, Present Continuous, comparatives', 'Travel, hobbies, weather, shopping', 'Describe experiences', 'Main points in familiar topics', 'Simple articles, stories', 'Simple letters, emails'),
            ('B1', 600, 50, 'Perfect tenses, conditionals, passive voice', 'Work, education, relationships, technology', 'Express opinions, plans', 'TV shows, movies, presentations', 'Articles, reports, fiction', 'Essays, detailed emails'),
            ('B2', 1200, 100, 'Complex conditionals, inversion, advanced modals', 'Business, science, culture, current events', 'Debates, negotiations, presentations', 'Lectures, debates, complex audio', 'Academic texts, literature', 'Reports, research papers'),
            ('C1', 2500, 200, 'Advanced grammar nuances, idiomatic expressions', 'Academic subjects, specialized topics', 'Academic discussions, teaching', 'Complex academic content', 'Specialized literature', 'Academic papers, theses'),
            ('C2', 5000, 400, 'Mastery of all grammar, stylistic devices', 'All topics including highly specialized', 'Teaching, public speaking, diplomacy', 'All types including native speech', 'All types including archaic texts', 'Creative writing, professional documents')
        """)

        self.conn.commit()

    def setup_handlers(self):
        # Command handlers
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.stats_command, Command("stats"))

        # Message handlers
        self.dp.message.register(self.daily_quests, F.text == "Квесты")
        self.dp.message.register(self.workout_menu, F.text == "Тренировки")
        self.dp.message.register(self.english_menu, F.text == "Английский")
        self.dp.message.register(
            self.stats_command, F.text.in_(["Статус", "📊 Статус"])
        )

        # Handle weight input
        self.dp.message.register(self.handle_weight_input, self._weight_filter)

        # Callback handlers
        self.dp.callback_query.register(self.callback_handler)

    async def start_command(self, message: types.Message):
        user_id = message.from_user.id

        # Check if user exists
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id, registration_completed FROM users WHERE user_id = ?",
            (user_id,),
        )
        user_data = cursor.fetchone()

        if user_data is None:
            # Create new user with basic info
            cursor.execute(
                """
                INSERT INTO users (user_id, last_activity)
                VALUES (?, ?)
            """,
                (user_id, date.today()),
            )
            self.conn.commit()

            await message.answer(
                "🎉 <b>Добро пожаловать в RAID SYSTEM!</b>\n\n"
                "⚔️ Ты новый Охотник!\n"
                "Давай создадим твой профиль для геймификации прогресса.\n\n"
                "📝 <b>Регистрация Охотника</b>\n\n"
                "Для начала, определим твою вселенную:\n\n"
                "<b>Выбери свою вселенную:</b>",
                reply_markup=self.get_anime_universe_keyboard(),
            )
        elif user_data[1] == 0:
            # User exists but registration not completed
            await message.answer(
                "📋 <b>Продолжение регистрации</b>\n\n"
                "Твой профиль не завершен. Давай закончим настройку!",
                reply_markup=self.get_registration_keyboard(),
            )
        else:
            await self.main_menu(message)


    def get_registration_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Продолжить регистрацию", callback_data="reg_continue"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Пропустить (использовать настройки по умолчанию)",
                        callback_data="reg_skip",
                    )
                ],
            ]
        )

    def get_gender_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👩 Девушка", callback_data="reg_gender_female"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👨 Парень", callback_data="reg_gender_male"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🚫 Не указывать", callback_data="reg_gender_none"
                    )
                ],
            ]
        )

    def get_skin_type_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌸 Сухая", callback_data="reg_skin_dry")],
                [InlineKeyboardButton(text="💧 Жирная", callback_data="reg_skin_oily")],
                [
                    InlineKeyboardButton(
                        text="🌿 Комбинированная", callback_data="reg_skin_combination"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✨ Нормальная", callback_data="reg_skin_normal"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🚫 Не указывать", callback_data="reg_skin_none"
                    )
                ],
            ]
        )

    def get_anime_universe_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⚔️ Solo Leveling", callback_data="reg_universe_solo"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🗼 Tower of God", callback_data="reg_universe_tower"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🌪️ Wind Breaker", callback_data="reg_universe_wind"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🥊 Kengan Ashura", callback_data="reg_universe_kengan"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💪 Lookism", callback_data="reg_universe_lookism"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏐 Haikyuu", callback_data="reg_universe_haikyuu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏃 Run with the Wind", callback_data="reg_universe_run"
                    )
                ],
            ]
        )

    def get_workout_ranks(self):
        """Получить доступные ранги тренировок"""
        return {
            "E": {
                "name": "E-rank",
                "description": "Легкий (для плохих дней)",
                "exp": 20,
            },
            "D": {
                "name": "D-rank",
                "description": "Средний (нормальные дни)",
                "exp": 30,
            },
            "C": {"name": "C-rank", "description": "Активный (хорошие дни)", "exp": 40},
            "B": {
                "name": "B-rank",
                "description": "Интенсивный (отличные дни)",
                "exp": 50,
            },
            "A": {
                "name": "A-rank",
                "description": "Сложный (только при отличном самочувствии)",
                "exp": 60,
            },
            "S": {"name": "S-rank", "description": "Особые испытания", "exp": 100},
        }

    def get_available_ranks(self, user_level: int):
        """Get available ranks based on user level"""
        if user_level <= 2:
            return ["E"]
        elif user_level <= 4:
            return ["E", "D"]
        elif user_level <= 6:
            return ["E", "D", "C"]
        elif user_level <= 9:
            return ["E", "D", "C", "B"]
        else:
            return ["E", "D", "C", "B", "A", "S"]

    def get_workout_library(self):
        """Complete workout library with all universes and ranks"""
        return {
            "solo": {
                "E": {
                    "title": "⚔️ Квест: Охотник День открытых врат",
                    "description": "Базовая тренировка для плохих дней",
                    "exercises": [
                        {
                            "name": "🧘 Медитация охотника",
                            "duration": "5 минут",
                            "quote": "Мана течет через дыхание - Сон Джин-Ву",
                        },
                        {
                            "name": "🤸 Призыв тени",
                            "duration": "10 минут",
                            "quote": "Тени всегда следуют за хозяином",
                        },
                        {
                            "name": "🚶 Сбор ингредиентов",
                            "duration": "10 минут",
                            "quote": "Каждый ингредиент имеет свою силу",
                        },
                    ],
                    "warnings": ["⚠️ Без наклонов головы вниз", "🌬️ Дыхание 4-2-6"],
                    "exp": 20,
                },
                "D": {
                    "title": "⚔️ Квест: Охотник Подъем на ранг D",
                    "description": "Усиленная базовая тренировка",
                    "exercises": [
                        {
                            "name": "🧘 Утренняя медитация",
                            "duration": "10 минут",
                            "quote": "Сила начинается с ума",
                        },
                        {
                            "name": "🤸 Динамическая растяжка",
                            "duration": "15 минут",
                            "quote": "Гибкость - ключ к выживанию",
                        },
                        {
                            "name": "🚶 Быстрая ходьба",
                            "duration": "15 минут",
                            "quote": "Скорость определяет победителя",
                        },
                    ],
                    "warnings": ["⚠️ Контролируй пульс", "🌬️ Отдых между упражнениями"],
                    "exp": 30,
                },
                "C": {
                    "title": "⚔️ Квест: Охотник Испытание ранга C",
                    "description": "Активная тренировка",
                    "exercises": [
                        {
                            "name": "🧘 Силовая медитация",
                            "duration": "5 минут",
                            "quote": "Сила духа преодолевает все",
                        },
                        {
                            "name": "🤸 Акробатическая растяжка",
                            "duration": "20 минут",
                            "quote": "Тело должно быть гибким как тень",
                        },
                        {
                            "name": "🏃 Легкий бег",
                            "duration": "20 минут",
                            "quote": "Бег формирует выносливость",
                        },
                        {
                            "name": "💪 Базовые упражнения",
                            "duration": "10 минут",
                            "quote": "Сила растет через преодоление",
                        },
                    ],
                    "warnings": ["⚠️ Следи за дыханием", "🌬️ Не перенапрягайся"],
                    "exp": 40,
                },
            },
            "tower": {
                "E": {
                    "title": "🗼 Квест: Регулярный Первый этаж",
                    "description": "Начальное испытание башни",
                    "exercises": [
                        {
                            "name": "⚖ Разминка регулярного",
                            "duration": "5 минут",
                            "quote": "Каждое путешествие начинается с первого шага",
                        },
                        {
                            "name": "🦘 Легкие прыжки",
                            "duration": "10 минут",
                            "quote": "Прыжки - это полет на мгновение",
                        },
                        {
                            "name": "🧘 Восстановление маны",
                            "duration": "10 минут",
                            "quote": "Мана восстанавливается через покой",
                        },
                    ],
                    "warnings": ["⚠️ Плавные движения", "🌬️ Глубокое дыхание"],
                    "exp": 20,
                }
            },
            "wind": {
                "E": {
                    "title": "🌪️ Квест: Уличный новичок",
                    "description": "Основы уличных боев",
                    "exercises": [
                        {
                            "name": "👊 Разминка бойца",
                            "duration": "5 минут",
                            "quote": "Уличный бой начинается с подготовки",
                        },
                        {
                            "name": "👊 Теневые удары",
                            "duration": "10 минут",
                            "quote": "Скорость важнее силы",
                        },
                        {
                            "name": "🤸 Базовая акробатика",
                            "duration": "10 минут",
                            "quote": "Гибкость - оружие уличного бойца",
                        },
                    ],
                    "warnings": ["⚠️ Без резких движений", "🌬️ Контроль дыхания"],
                    "exp": 20,
                }
            },
            "kengan": {
                "E": {
                    "title": "🥊 Квест: Боец новичок",
                    "description": "Основы единоборств",
                    "exercises": [
                        {
                            "name": "🥊 Боевая стойка",
                            "duration": "5 минут",
                            "quote": "Стойка - основа боя",
                        },
                        {
                            "name": "💪 Теневые удары",
                            "duration": "10 минут",
                            "quote": "Техника побеждает силу",
                        },
                        {
                            "name": "🧘 Боевая медитация",
                            "duration": "10 минут",
                            "quote": "Дух воина непоколебим",
                        },
                    ],
                    "warnings": ["⚠️ Без контактов", "🌬️ Ритмичное дыхание"],
                    "exp": 20,
                }
            },
            "lookism": {
                "E": {
                    "title": "💪 Квест: Трансформация начало",
                    "description": "Основы изменения тела",
                    "exercises": [
                        {
                            "name": "🧘 Осознанность тела",
                            "duration": "5 минут",
                            "quote": "Понимание тела - первый шаг к трансформации",
                        },
                        {
                            "name": "🤸 Утренняя растяжка",
                            "duration": "15 минут",
                            "quote": "Гибкость открывает потенциал",
                        },
                        {
                            "name": "🚶 Ходьба с осанкой",
                            "duration": "10 минут",
                            "quote": "Осанка - отражение духа",
                        },
                    ],
                    "warnings": ["⚠️ Плавные движения", "🌬️ Контроль спины"],
                    "exp": 20,
                },
                "A": {
                    "title": "💪 Квест: Титановое тело I",
                    "description": "Продвинутая трансформация",
                    "exercises": [
                        {
                            "name": "💪 Силовые упражнения",
                            "duration": "20 минут",
                            "quote": "Сила куется в огне усилий",
                        },
                        {
                            "name": "🏃 Высокоинтенсивный кардио",
                            "duration": "15 минут",
                            "quote": "Сердце титана бьется ровно",
                        },
                        {
                            "name": "🧘 Восстановительная медитация",
                            "duration": "10 минут",
                            "quote": "Покой укрепляет сталь",
                        },
                        {
                            "name": "🤸 Гибкость позвоночника",
                            "duration": "10 минут",
                            "quote": "Гибкое тело - несокрушимое",
                        },
                    ],
                    "warnings": ["⚠️ Контролируй нагрузку", "💧 Пей достаточно воды", "🌬️ Правильное дыхание"],
                    "exp": 50,
                },
                "S": {
                    "title": "💪 Квест: Титановое тело II",
                    "description": "Максимальная трансформация тела",
                    "exercises": [
                        {
                            "name": "🔥 Плиометрическая тренировка",
                            "duration": "25 минут",
                            "quote": "Взрывная сила титана",
                        },
                        {
                            "name": "💪 Функциональный тренинг",
                            "duration": "20 минут",
                            "quote": "Тело работает как единый механизм",
                        },
                        {
                            "name": "🏃 Интервальный спринт",
                            "duration": "15 минут",
                            "quote": "Скорость решает всё",
                        },
                        {
                            "name": "🧘 Статическая растяжка",
                            "duration": "15 минут",
                            "quote": "Растяжка укрепляет мышцы",
                        },
                        {
                            "name": "💆 Массаж и восстановление",
                            "duration": "10 минут",
                            "quote": "Восстановление - часть тренировки",
                        },
                    ],
                    "warnings": ["⚠️ Максимальная концентрация", "💧 Обязательное увлажнение", "🌬️ Дыхание по схеме 4-7-8", "⚡ Следи за пульсом"],
                    "exp": 100,
                }
            },
            "haikyuu": {
                "E": {
                    "title": "🏐 Квест: Волейбольный новичок",
                    "description": "Основы для хороших дней",
                    "exercises": [
                        {
                            "name": "🏐 Разминка волейболиста",
                            "duration": "5 минут",
                            "quote": "Разминка - ключ к прыжку",
                        },
                        {
                            "name": "🦘 Легкие прыжки",
                            "duration": "10 минут",
                            "quote": "Каждый прыжок - это полет",
                        },
                        {
                            "name": "🤸 Растяжка ног",
                            "duration": "15 минут",
                            "quote": "Гибкие ноги - высокие прыжки",
                        },
                    ],
                    "warnings": ["⚠️ Мягкие приземления", "🌬️ Дыхание при прыжках"],
                    "exp": 20,
                }
            },
            "run": {
                "E": {
                    "title": "🏃 Квест: Начало пробежки",
                    "description": "Адаптивный бег для контроля пульса",
                    "exercises": [
                        {
                            "name": "🏃 Разминка бегуна",
                            "duration": "5 минут",
                            "quote": "Бег начинается с подготовки",
                        },
                        {
                            "name": "🚶 Быстрая ходьба",
                            "duration": "15 минут",
                            "quote": "Ходьба - основа выносливости",
                        },
                        {
                            "name": "🧘 Восстановительное дыхание",
                            "duration": "10 минут",
                            "quote": "Дыхание - топливо для бега",
                        },
                    ],
                    "warnings": ["⚠️ Контроль пульса 100-120", "🌬️ Ритмичное дыхание"],
                    "exp": 20,
                }
            },
        }

    def get_main_keyboard(self):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Квесты"), KeyboardButton(text="Тренировки")],
                [KeyboardButton(text="Английский"), KeyboardButton(text="Статус")],
            ],
            resize_keyboard=True,
        )

    async def main_menu(self, message: types.Message):
        try:
            user_id = message.from_user.id
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT level, exp, exp_to_next, power, analysis, endurance, speed, streak
                FROM users WHERE user_id = ?
            """,
                (user_id,),
            )

            user_data = cursor.fetchone()
            if user_data:
                # Handle different database versions
                if len(user_data) >= 7:
                    level, exp, exp_to_next, power, analysis, endurance, speed = (
                        user_data[:7]
                    )
                    streak = user_data[7] if len(user_data) > 7 else 0
                else:
                    # Old database format
                    level, exp, exp_to_next, power, analysis, endurance = user_data[:6]
                    speed = 10.0
                    streak = 0

                text = f"""
⚔️ <b>RAID SYSTEM</b>

🎯 Уровень Охотника: {level}
⭐ Опыт: {exp}/{exp_to_next}

💪 Характеристики:
🥊 Боевая мощь: {power:.1f}
🧠 Анализ: {analysis:.1f}
🛡️ Выносливость: {endurance:.1f}
⚡ Скорость: {speed:.1f}

🏃 Стрик: {streak} дней
"""
            else:
                text = "❌ Пользователь не найден. Пожалуйста, пройдите регистрацию заново с /start"

            await message.answer(text, reply_markup=self.get_main_keyboard())
        except Exception as e:
            print(f"Error in main_menu: {e}")
            await message.answer(
                "❌ Произошла ошибка. Попробуйте /start",
                reply_markup=self.get_main_keyboard(),
            )

    async def help_command(self, message: types.Message):
        help_text = """
📖 <b>Справка Охотника</b>

🎯 <b>Команды:</b>
/start - Главное меню
/help - Эта справка
/stats - Статистика

🎮 <b>Меню:</b>
📋 Квесты - Ежедневные задания
⚔️ Тренировки - Аниме-тренировки
📊 Статус - Твой прогресс
📚 Английский - Изучение языка

⚔️ <b>Система рангов:</b>
E → D → C → B → A → S

🎯 Удачи в рейде, Охотник!
        """

        await message.answer(help_text)

    async def stats_command(self, message: types.Message):
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT level, exp, exp_to_next, power, analysis, endurance, speed, 
                   skin_health, english_progress, streak, weight, target_weight,
                   english_level, english_exp
            FROM users WHERE user_id = ?
        """,
            (user_id,),
        )

        user_data = cursor.fetchone()
        if user_data:
            level, exp, exp_to_next, power, analysis, endurance, speed = user_data[:7]
            skin_health = user_data[7] if len(user_data) > 7 else 50
            english_progress = user_data[8] if len(user_data) > 8 else 0
            streak = user_data[9] if len(user_data) > 9 else 0
            weight = user_data[10] if len(user_data) > 10 else None
            target_weight = user_data[11] if len(user_data) > 11 else None
            english_level = user_data[12] if len(user_data) > 12 else "A0"
            english_exp = user_data[13] if len(user_data) > 13 else 0
            english_rank = self.get_english_rank_title(english_level)

            stats_text = f"""
📊 <b>Статус рейда Охотника</b>

🎯 <b>Уровень: {level}</b>
⭐ Опыт: {exp}/{exp_to_next}

💪 <b>Характеристики:</b>
🥊 Боевая мощь: {power:.1f}
🧠 Анализ: {analysis:.1f}
🛡️ Выносливость: {endurance:.1f}
⚡ Скорость: {speed:.1f}

🌟 <b>Прогресс:</b>
🏃️ Streak: {streak} дней
🧹 Чистота кожи: {skin_health}/100
📚 Английский: {english_progress}/1000

📚 <b>Английский язык:</b>
{english_rank}
🎯 Уровень: {english_level} ({english_exp} EXP)

⚖️ <b>Вес:</b>
{weight if weight else "Не указан"} кг
            """

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⚖️ Записать вес", callback_data="weight_log"
                        )
                    ],
                ]
            )

            await message.answer(stats_text, reply_markup=keyboard)

    async def daily_quests(self, message: types.Message):
        user_id = message.from_user.id

        quest_text = "📋 <b>Ежедневные квесты</b>\n\n"
        quest_text += "Выбери категорию заданий:\n\n"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💪 Фитнес и здоровье",
                        callback_data="quest_category_fitness",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🧠 Обучение и развитие",
                        callback_data="quest_category_learning",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🌸 Уход за собой", callback_data="quest_category_selfcare"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎯 Личные привычки", callback_data="quest_category_habits"
                    )
                ],
            ]
        )

        await message.answer(quest_text, reply_markup=keyboard)

    async def show_fitness_quests(self, message):
        """Show fitness and health related quests"""
        quest_text = "💪 <b>Фитнес и здоровье</b>\n\n"
        quest_text += "Выбери задание:\n\n"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏃 15-минутная зарядка (+30 EXP)",
                        callback_data="quest_morning_workout",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🧘 10 минут растяжки (+20 EXP)",
                        callback_data="quest_stretching",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💧 Выпить 8 стаканов воды (+15 EXP)",
                        callback_data="quest_water",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🚶 5000 шагов (+25 EXP)", callback_data="quest_steps"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 К категориям", callback_data="refresh_quests"
                    )
                ],
            ]
        )

        await message.answer(quest_text, reply_markup=keyboard)

    async def show_learning_quests(self, message):
        """Show learning and development quests"""
        quest_text = "🧠 <b>Обучение и развитие</b>\n\n"
        quest_text += "Выбери задание:\n\n"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📚 30 минут английского (+40 EXP)",
                        callback_data="quest_english",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📖 Прочитать 10 страниц книги (+25 EXP)",
                        callback_data="quest_reading",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎧 Смотреть образовательное видео (+20 EXP)",
                        callback_data="quest_video",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✍️ Написать дневниковую запись (+15 EXP)",
                        callback_data="quest_journal",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 К категориям", callback_data="refresh_quests"
                    )
                ],
            ]
        )

        await message.answer(quest_text, reply_markup=keyboard)

    async def show_selfcare_quests(self, message):
        """Show self-care and grooming quests"""
        quest_text = "🌸 <b>Уход за собой</b>\n\n"
        quest_text += "Выбери задание:\n\n"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🧴 Утренний уход за кожей (+15 EXP)",
                        callback_data="skin_care_morning",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🌙 Вечерний уход за кожей (+15 EXP)",
                        callback_data="skin_care_evening",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💇 Уход за волосами (+20 EXP)",
                        callback_data="quest_hair_care",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🧼 Принять душ/ванну (+10 EXP)",
                        callback_data="quest_shower",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 К категориям", callback_data="refresh_quests"
                    )
                ],
            ]
        )

        await message.answer(quest_text, reply_markup=keyboard)

    async def show_habits_quests(self, message):
        """Show personal habit quests"""
        quest_text = "🎯 <b>Личные привычки</b>\n\n"
        quest_text += "Выбери задание:\n\n"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="😴 Лечь спать до 23:00 (+20 EXP)",
                        callback_data="quest_early_sleep",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📱 Без телефона за час до сна (+15 EXP)",
                        callback_data="quest_no_phone",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🧹 Убраться в комнате (+25 EXP)",
                        callback_data="quest_cleaning",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🍏 Съесть фрукт/овощ (+10 EXP)",
                        callback_data="quest_healthy_food",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 К категориям", callback_data="refresh_quests"
                    )
                ],
            ]
        )

        await message.answer(quest_text, reply_markup=keyboard)

    async def workout_menu(self, message: types.Message):
        user_id = message.from_user.id

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT level, anime_universe FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()

        user_level = result[0] if result else 1
        user_universe = result[1] if result else "Solo Leveling"

        # Get available ranks based on user level
        available_ranks = self.get_available_ranks(user_level)
        ranks_info = self.get_workout_ranks()

        workout_text = f"""
⚔️ <b>Тренировки</b>

🎯 Твой уровень: {user_level}

📊 <b>Доступные ранги:</b>
"""

        for rank in available_ranks:
            rank_info = ranks_info[rank]
            workout_text += f"🔹 {rank_info['name']} - {rank_info['description']}\n"

        workout_text += f"""
⚔️ <b>Твоя вселенная:</b> {user_universe}

🎮 <b>Доступные вселенные:</b>

🗡️ <b>Solo Leveling</b> - Система рангов E → S
🗼 <b>Tower of God</b> - Этажи и испытания
🌪️ <b>Wind Breaker</b> - Уличные бои
🥊 <b>Kengan Ashura</b> - Чистые единоборства
💪 <b>Lookism</b> - Трансформация тела
🏐 <b>Haikyuu</b> - Прыжки и реакция
🏃 <b>Run with the Wind</b> - Адаптивный бег

⚠️ <b>Важно:</b>
Слушай свое тело и не перенапрягайся!
        """

        # Create universe buttons
        universe_buttons = []
        universes = ["solo", "tower", "wind", "kengan", "lookism", "haikyuu", "run"]
        universe_names = [
            "⚔️ Solo Leveling",
            "🗼 Tower of God",
            "🌪️ Wind Breaker",
            "🥊 Kengan Ashura",
            "💪 Lookism",
            "🏐 Haikyuu",
            "🏃 Run with the Wind",
        ]

        for i, (universe, name) in enumerate(zip(universes, universe_names)):
            if i % 2 == 0:
                universe_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=name, callback_data=f"workout_universe_{universe}"
                        )
                    ]
                )
            else:
                universe_buttons[-1].append(
                    InlineKeyboardButton(
                        text=name, callback_data=f"workout_universe_{universe}"
                    )
                )

        keyboard = InlineKeyboardMarkup(inline_keyboard=universe_buttons)

        await message.answer(workout_text, reply_markup=keyboard)


    def get_nutrition_info(
        self, user_weight: float = None, target_weight: float = None
    ):
        """Get nutrition recommendations for weight loss"""
        if user_weight and target_weight and user_weight > target_weight:
            weight_to_lose = user_weight - target_weight
            calories_to_deficit = weight_to_lose * 7700  # 1kg = 7700 calories
            daily_deficit = 500  # Safe daily deficit
            days_to_goal = calories_to_deficit / daily_deficit

            return {
                "daily_deficit": daily_deficit,
                "days_to_goal": int(days_to_goal),
                "target_weight": target_weight,
            }
        else:
            return {
                "daily_deficit": 300,
                "days_to_goal": 30,
                "target_weight": target_weight or user_weight,
            }

    def get_low_calorie_foods(self):
        """Get list of low calorie foods"""
        return {
            "Белки": [
                "Куриная грудка (165 ккал/100г)",
                "Яичный белок (52 ккал/100г)",
                "Творог 2% (80 ккал/100г)",
                "Рыба (треска, минтай) (70-90 ккал/100г)",
            ],
            "Овощи": [
                "Огурцы (15 ккал/100г)",
                "Помидоры (18 ккал/100г)",
                "Капуста (25 ккал/100г)",
                "Брокколи (34 ккал/100г)",
                "Морковь (41 ккал/100г)",
            ],
            "Фрукты": [
                "Яблоки (52 ккал/100г)",
                "Грейпфрут (35 ккал/100г)",
                "Клубника (32 ккал/100г)",
                "Апельсины (47 ккал/100г)",
            ],
            "Углеводы": [
                "Овсянка (68 ккал/100г)",
                "Гречка (110 ккал/100г)",
                "Бурый рис (111 ккал/100г)",
                "Цельнозерновой хлеб (247 ккал/100г)",
            ],
        }

    def generate_english_tasks(self, english_level: str, user_id: int):
        """Генерирует уникальные ежедневные задания по английскому с помощью ИИ"""
        try:
            # Получаем прогресс пользователя для персонализации
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT english_exp, last_english_test_date, english_test_attempts
                FROM users WHERE user_id = ?
            """, (user_id,))
            user_data = cursor.fetchone()
            english_exp = user_data[0] if user_data else 0
            last_test = user_data[1] if len(user_data) > 1 else None
            test_attempts = user_data[2] if len(user_data) > 2 else 0

            # Получаем последние выполненные задания для анализа
            cursor.execute("""
                SELECT task_type, task_content, completed 
                FROM daily_english_tasks 
                WHERE user_id = ? AND date >= date('now', '-7 days')
                ORDER BY date DESC LIMIT 5
            """, (user_id,))
            recent_tasks = cursor.fetchall()
            
            # Формируем текст последних заданий для ИИ
            recent_tasks_text = ", ".join([f"{task[0]}: {task[1]}" for task in recent_tasks if task[2]]) if recent_tasks else "Нет заданий"
            
            # Промпт для ИИ с учетом прогресса пользователя
            prompt = f"""
            Создай 3 уникальных ежедневных задания по английскому языку для уровня {english_level}.
            
            Учитывай прогресс пользователя:
            - Текущий опыт: {english_exp} EXP
            - Последний тест: {last_test if last_test else 'Не сдавал'}
            - Попытки теста: {test_attempts}
            - Последние выполненные задания: {recent_tasks_text if recent_tasks_text else 'Нет заданий'}
            
            Требования:
            1. Каждое задание должно быть уникальным и интересным
            2. Адаптировано под уровень {english_level}
            3. Включай практические упражнения
            4. Добавляй актуальные ссылки на образовательные ресурсы
            5. Учитывай слабые места пользователя
            6. Чередуй типы заданий (лексика, аудирование, грамматика, говорение)
            
            Формат ответа (строго JSON):
            {{
                "tasks": [
                    {{
                        "type": "vocabulary|listening|grammar|speaking|reading|writing",
                        "content": "текст задания",
                        "link": "ссылка на ресурс",
                        "exp": 5-15,
                        "ai_generated": true
                    }}
                ]
            }}
            """

            # Настройка OpenAI
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Запрос к ИИ
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - помощник по изучению английского языка. Создавай интересные и разнообразные задания."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            # Обработка ответа ИИ
            ai_response = json.loads(response.choices[0].message.content)
            ai_tasks = ai_response.get("tasks", [])
            
            # Валидация и сохранение заданий
            valid_tasks = []
            for task in ai_tasks:
                if all(key in task for key in ["type", "content", "exp"]) and task["exp"] >= 5:
                    valid_tasks.append(task)
            
            # Сохранение в базу данных
            for task in valid_tasks[:3]:  # Берем максимум 3 задания
                cursor.execute("""
                    INSERT INTO daily_english_tasks 
                    (user_id, date, task_type, task_content, task_link, completed, exp_reward)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, date.today(), task["type"], task["content"], task.get("link", ""), False, task["exp"]))
            
            self.conn.commit()
            return valid_tasks[:3]
            
        except Exception as e:
            logging.error(f"Error generating AI tasks: {e}")
            # Fallback на статические шаблоны при ошибке ИИ
            return self.get_fallback_english_tasks(english_level)
    
    def get_fallback_english_tasks(self, english_level: str):
        """Запасные статические задания на случай ошибки ИИ"""
        fallback_tasks = {
            "A0": [
                {"type": "vocabulary", "content": "Выучи 5 английских слов", "link": "https://quizlet.com", "exp": 5},
                {"type": "listening", "content": "Прослушай английскую песню", "link": "https://youtube.com", "exp": 8},
                {"type": "grammar", "content": "Изучи Present Simple", "link": "https://learnenglish.britishcouncil.org", "exp": 6},
            ],
            "A1": [
                {"type": "vocabulary", "content": "Выучи 10 слов на тему 'Еда'", "link": "https://quizlet.com", "exp": 8},
                {"type": "listening", "content": "Посмотри 15 минут мультфильма", "link": "https://www.youtube.com", "exp": 10},
                {"type": "grammar", "content": "Сделай 15 упражнений на Past Simple", "link": "https://learnenglish.britishcouncil.org", "exp": 12},
            ],
            "B1": [
                {"type": "vocabulary", "content": "Выучи 15 фразовых глаголов", "link": "https://www.phrasalverbdemon.com/", "exp": 12},
                {"type": "reading", "content": "Прочитай новость на BBC Learning", "link": "https://www.bbc.co.uk/learningenglish", "exp": 15},
                {"type": "writing", "content": "Напиши эссе на 100 слов", "link": "https://www.grammarly.com/", "exp": 18},
            ],
        }
        return fallback_tasks.get(english_level, fallback_tasks["A1"])

    def get_english_level_requirements(self, level: str):
        """Get requirements for English level"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT exp_required, min_tasks_completed, grammar_topics, vocabulary_topics,
                   speaking_requirements, listening_requirements, reading_requirements, writing_requirements
            FROM english_level_requirements WHERE level = ?
        """,
            (level,),
        )
        result = cursor.fetchone()

        if result:
            return {
                "exp_required": result[0],
                "min_tasks_completed": result[1],
                "grammar_topics": result[2],
                "vocabulary_topics": result[3],
                "speaking_requirements": result[4],
                "listening_requirements": result[5],
                "reading_requirements": result[6],
                "writing_requirements": result[7],
            }
        return None

    def get_next_english_level(self, current_level: str):
        """Get next English level in CEFR progression"""
        levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        return None

    def can_take_english_test(self, user_id: int, target_level: str):
        """Check if user can take English level test"""
        cursor = self.conn.cursor()

        # Get user's current English stats
        cursor.execute(
            """
            SELECT english_level, english_exp, last_english_test_date, english_test_attempts
            FROM users WHERE user_id = ?
        """,
            (user_id,),
        )
        user_data = cursor.fetchone()

        if not user_data:
            return False, "User not found"

        current_level, english_exp, last_test_date, test_attempts = user_data

        # Check if target level is higher than current
        next_level = self.get_next_english_level(current_level)
        if next_level != target_level:
            return (
                False,
                f"Can only test for {next_level} from current level {current_level}",
            )

        # Get requirements for target level
        requirements = self.get_english_level_requirements(target_level)
        if not requirements:
            return False, "Level requirements not found"

        # Check EXP requirement
        if english_exp < requirements["exp_required"]:
            return False, f"Need {requirements['exp_required']} EXP, have {english_exp}"

        # Check completed tasks count
        cursor.execute(
            """
            SELECT COUNT(*) FROM daily_english_tasks 
            WHERE user_id = ? AND completed = 1
        """,
            (user_id,),
        )
        completed_tasks = cursor.fetchone()[0]

        if completed_tasks < requirements["min_tasks_completed"]:
            return (
                False,
                f"Need {requirements['min_tasks_completed']} completed tasks, have {completed_tasks}",
            )

        # NEW: Check if user has studied all required topics for current level
        current_requirements = self.get_english_level_requirements(current_level)
        if not current_requirements:
            return False, "Current level requirements not found"

        # Check if user has completed tasks covering all required topics
        cursor.execute(
            """
            SELECT DISTINCT task_type FROM daily_english_tasks 
            WHERE user_id = ? AND completed = 1 AND date >= date('now', '-30 days')
        """,
            (user_id,),
        )
        completed_task_types = {row[0] for row in cursor.fetchall()}

        required_task_types = {
            "vocabulary",
            "listening",
            "speaking",
            "reading",
            "writing",
        }

        # For A0-A1 levels, grammar is also required
        if current_level in ["A0", "A1"]:
            required_task_types.add("grammar")

        missing_types = required_task_types - completed_task_types
        if missing_types:
            return False, f"Need to practice: {', '.join(missing_types)}"

        # Check test cooldown (1 day between attempts)
        if last_test_date:
            from datetime import datetime, timedelta

            last_test = datetime.strptime(last_test_date, "%Y-%m-%d").date()
            if date.today() - last_test < timedelta(days=1):
                return False, "Can only test once per day"

        return True, "Ready for test"

    async def start_english_test_section(
        self, message, target_level: str, section: str
    ):
        """Start a specific section of English test"""
        user_id = message.from_user.id

        # Store test session data (in real implementation, you'd use a proper session management)
        test_session = {
            "user_id": user_id,
            "target_level": target_level,
            "current_section": section,
            "scores": {},
            "start_time": date.today(),
        }

        # Simple test questions based on level and section
        questions = self.get_test_questions(target_level, section)

        question_text = f"""
🎯 <b>Тест на {target_level} - {section.title()}</b>

❓ <b>Вопрос 1/{len(questions)}:</b>

{questions[0]["question"]}

💡 <b>Варианты ответа:</b>
"""

        keyboard_buttons = []
        for i, option in enumerate(questions[0]["options"], 1):
            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{i}. {option}",
                        callback_data=f"test_answer_{section}_{questions[0]['correct'] - 1}_{i - 1}",
                    )
                ]
            )

        keyboard_buttons.append(
            [InlineKeyboardButton(text="❌ Прервать тест", callback_data="cancel_test")]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(question_text, reply_markup=keyboard)

    def get_test_questions(self, level: str, section: str):
        """Get test questions for specific level and section"""
        # Simplified test questions - in real implementation, you'd use a proper test database
        questions = {
            "grammar": {
                "A1": [
                    {
                        "question": "Choose the correct form: I ___ a student.",
                        "options": ["am", "is", "are", "be"],
                        "correct": 1,
                    },
                    {
                        "question": "What is the past tense of 'go'?",
                        "options": ["goes", "went", "gone", "going"],
                        "correct": 2,
                    },
                ],
                "A2": [
                    {
                        "question": "Choose the correct form: She ___ to London yesterday.",
                        "options": ["go", "goes", "went", "going"],
                        "correct": 3,
                    }
                ],
                "B1": [
                    {
                        "question": "Choose the correct form: If I ___ rich, I would travel the world.",
                        "options": ["am", "was", "were", "will be"],
                        "correct": 3,
                    }
                ],
            },
            "vocabulary": {
                "A1": [
                    {
                        "question": "What is 'apple' in Russian?",
                        "options": ["апельсин", "яблоко", "банан", "груша"],
                        "correct": 2,
                    }
                ],
                "A2": [
                    {
                        "question": "What does 'delicious' mean?",
                        "options": ["bad", "tasty", "expensive", "cheap"],
                        "correct": 2,
                    }
                ],
            },
            "reading": {
                "A1": [
                    {
                        "question": "Read: 'My name is Tom. I am 10 years old.' How old is Tom?",
                        "options": ["5", "8", "10", "12"],
                        "correct": 3,
                    }
                ]
            },
            "listening": {
                "A1": [
                    {
                        "question": "Listen to the audio: 'Hello, how are you?' What is the greeting?",
                        "options": ["Goodbye", "Hello", "Thanks", "Sorry"],
                        "correct": 2,
                    }
                ]
            },
            "writing": {
                "A1": [
                    {
                        "question": "Write about your favorite food. What would you write about?",
                        "options": ["Pizza", "Rules", "Math", "Cars"],
                        "correct": 1,
                    }
                ]
            },
        }

        return questions.get(section, {}).get(level, questions["grammar"]["A1"])

    def get_english_rank_title(self, level: str):
        """Get game-style rank title for English level"""
        rank_titles = {
            "A0": "🌱 Новичок Охотника",
            "A1": "⚔️ Юный Охотник",
            "A2": "🛡️ Опытный Охотник",
            "B1": "🗡️ Мастер Охотник",
            "B2": "🏆 Элитный Охотник",
            "C1": "👑 Легендарный Охотник",
            "C2": "⚡ Божественный Охотник",
        }
        return rank_titles.get(level, "🌱 Новичок Охотника")

    async def check_rank_up(self, message, user_id: int):
        """Check if user should rank up and send Solo Leveling style notification"""
        cursor = self.conn.cursor()

        # Get user's current level and exp
        cursor.execute(
            "SELECT level, exp, exp_to_next FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()

        if not result:
            return

        current_level, exp, exp_to_next = result

        # Check if ready for rank up
        if exp >= exp_to_next:
            # Level up!
            new_level = current_level + 1
            new_exp_to_next = exp_to_next + 50  # Increase requirement for next level

            # Update user level
            cursor.execute(
                """
                UPDATE users SET 
                    level = ?, 
                    exp_to_next = ?,
                    exp = exp - ?  # Reset exp but keep overflow
                WHERE user_id = ?
            """,
                (new_level, new_exp_to_next, exp_to_next, user_id),
            )
            self.conn.commit()

            # Send Solo Leveling style notification
            rank_up_text = f"""
⚡️ <b>【LEVEL UP ALERT】</b> ⚡️

🎯 <b>НОВЫЙ РАНГ ДОСТИГНУТ!</b>

🏆 <b>Твой новый уровень: {new_level}</b>
🔥 <b>Остаток EXP: {exp - exp_to_next}</b>
⚔️ <b>Следующий порог: {new_exp_to_next} EXP</>

💫 <b>【AWAKENING COMPLETE】</b>
Ты стал сильнее, Охотник!

🎮 <b>【NEW ABILITIES UNLOCKED】</b>
• Разблокированы новые тренировки
• Повышенная выносливость
• Новый доступ к рангам

🌟 <b>【SOLO LEVELING SYSTEM】</b>
"Сила не дается, она зарабатывается кровью и потом"

🚀 <b>Продолжай свой путь к вершине!</b>
"""

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⚔️ Новые тренировки", callback_data="workout_menu"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📊 Проверить статус", callback_data="refresh_stats"
                        )
                    ],
                ]
            )

            await message.answer(rank_up_text, reply_markup=keyboard)

    async def check_english_level_up(self, message, user_id: int):
        """Check if user is ready for English level up and send Solo Leveling style notification"""
        cursor = self.conn.cursor()

        # Get user's current English level
        cursor.execute(
            "SELECT english_level, english_exp FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()

        if not result:
            return

        current_level, english_exp = result
        next_level = self.get_next_english_level(current_level)

        if not next_level:
            return  # Already at max level

        # Check if ready for test
        can_test, test_reason = self.can_take_english_test(user_id, next_level)

        if can_test:
            # Send Solo Leveling style notification
            upgrade_text = f"""
⚡️ <b>【SYSTEM ALERT】</b> ⚡️

🎯 <b>ОХОТНИК ГОТОВ К НОВОЙ СИЛЕ!</b>

📊 <b>Твой текущий уровень:</b> {current_level}
🔥 <b>Твой текущий EXP:</b> {english_exp}
⚔️ <b>Следующий ранг:</b> {next_level}

💫 <b>【QUEST UNLOCKED】</b>
Ты изучил все необходимые темы и накопил достаточно опыта!

🎮 <b>【NEW SKILL AWAKENING】</b>
Тест на {next_level} теперь доступен!

🌟 <b>【SOLO LEVELING SYSTEM】</b>
"Сила приходит к тем, кто достаточно упорен, чтобы ее заслужить"

🚀 <b>Готов доказать свою силу?</b>
"""

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"⚔️ Пройти испытание на {next_level}",
                            callback_data=f"english_test_{next_level}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📚 Проверить статус", callback_data="english_menu"
                        )
                    ],
                ]
            )

            await message.answer(upgrade_text, reply_markup=keyboard)

    async def nutrition_menu(self, message: types.Message):
        user_id = message.from_user.id

        cursor = self.conn.cursor()
        cursor.execute("SELECT weight FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        weight = result[0] if result and result[0] else None

        low_cal_foods = self.get_low_calorie_foods()

        # Get water data
        today = date.today()
        cursor.execute(
            """
            SELECT water_goal, water_consumed FROM nutrition_plans 
            WHERE user_id = ? AND date = ?
        """,
            (user_id, today),
        )

        water_data = cursor.fetchone()
        if not water_data:
            water_goal, water_consumed = 8, 0
            cursor.execute(
                """
                INSERT INTO nutrition_plans (user_id, date, water_goal, water_consumed)
                VALUES (?, ?, ?, ?)
            """,
                (user_id, today, water_goal, water_consumed),
            )
            self.conn.commit()
        else:
            water_goal, water_consumed = water_data

        water_percentage = (
            int((water_consumed / water_goal) * 100) if water_goal > 0 else 0
        )

        nutrition_text = f"""
План питания

💧 Водный баланс: {water_consumed}/{water_goal} стаканов ({water_percentage}%)

🥗 Рекомендуемые продукты:
"""

        for category, foods in low_cal_foods.items():
            nutrition_text += f"\n{category}:\n"
            for food in foods:
                nutrition_text += f"• {food}\n"

        nutrition_text += f"""
💡 Советы:
• Пей воду перед едой
• Ешь овощи в большом количестве
• Белок в каждом приеме пищи
• Углеводы до 14:00
• Никаких перекусов после 19:00
        """

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💧 Выпить стакан воды", callback_data="water_add"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⚖️ Записать вес", callback_data="weight_log"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Продукты для похудения", callback_data="food_list"
                    )
                ],
            ]
        )

        await message.answer(nutrition_text, reply_markup=keyboard)

    async def english_menu(self, message: types.Message):
        user_id = message.from_user.id

        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            await message.answer(
                "❌ Пользователь не найден. Пожалуйста, пройдите регистрацию заново с /start"
            )
            return

        cursor.execute(
            "SELECT english_level, english_exp FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()
        english_level = result[0] if result else "A0"
        english_exp = result[1] if result else 0

        # Get level requirements
        requirements = self.get_english_level_requirements(english_level)
        next_level = self.get_next_english_level(english_level)

        # Calculate progress to next level
        exp_progress = 0
        if requirements and next_level:
            next_requirements = self.get_english_level_requirements(next_level)
            if next_requirements:
                exp_progress = int(
                    (english_exp / next_requirements["exp_required"]) * 100
                )

        # Check if can take test
        can_test, test_reason = (
            self.can_take_english_test(user_id, next_level)
            if next_level
            else (False, "Already at max level")
        )

        # Check if daily tasks exist for today
        today = date.today()
        cursor.execute(
            """
            SELECT task_type, task_content, task_link, completed, exp_reward 
            FROM daily_english_tasks 
            WHERE user_id = ? AND date = ?
            ORDER BY task_id
        """,
            (user_id, today),
        )

        existing_tasks = cursor.fetchall()

        # If no tasks for today, generate new ones
        if not existing_tasks:
            daily_tasks = self.generate_english_tasks(english_level, user_id)

            for task in daily_tasks:
                cursor.execute(
                    """
                    INSERT INTO daily_english_tasks 
                    (user_id, date, task_type, task_content, task_link, exp_reward)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        today,
                        task["type"],
                        task["content"],
                        task["link"],
                        task["exp"],
                    ),
                )

            self.conn.commit()

            # Fetch the newly created tasks
            cursor.execute(
                """
                SELECT task_type, task_content, task_link, completed, exp_reward 
                FROM daily_english_tasks 
                WHERE user_id = ? AND date = ?
                ORDER BY task_id
            """,
                (user_id, today),
            )
            existing_tasks = cursor.fetchall()

        # Calculate progress
        completed_tasks = sum(1 for task in existing_tasks if task[3])
        total_tasks = len(existing_tasks)
        progress_percentage = (
            int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        )

        # Get total completed tasks
        cursor.execute(
            """
            SELECT COUNT(*) FROM daily_english_tasks 
            WHERE user_id = ? AND completed = 1
        """,
            (user_id,),
        )
        total_completed_tasks = cursor.fetchone()[0]

        # Check topic completion for current level
        cursor.execute(
            """
            SELECT DISTINCT task_type FROM daily_english_tasks 
            WHERE user_id = ? AND completed = 1 AND date >= date('now', '-30 days')
        """,
            (user_id,),
        )
        completed_task_types = {row[0] for row in cursor.fetchall()}

        required_task_types = {
            "vocabulary",
            "listening",
            "speaking",
            "reading",
            "writing",
        }
        if english_level in ["A0", "A1"]:
            required_task_types.add("grammar")

        studied_types = completed_task_types & required_task_types
        missing_types = required_task_types - completed_task_types

        topic_progress = int((len(studied_types) / len(required_task_types)) * 100)

        english_text = f"""
📚 <b>Английский язык</b>

🎯 Твой уровень: {english_level} ({english_exp} EXP)
📊 Прогресс до {next_level}: {exp_progress}% (если доступен)
📖 Изученные темы: {len(studied_types)}/{len(required_task_types)} ({topic_progress}%)
🏆 Всего выполнено заданий: {total_completed_tasks}
📅 Задания на сегодня: {completed_tasks}/{total_tasks} ({progress_percentage}%)

📋 <b>Прогресс по темам:</b>
"""

        task_emojis = {
            "vocabulary": "📚",
            "listening": "🎧",
            "speaking": "🗣",
            "grammar": "📖",
            "reading": "📄",
            "writing": "✍️",
        }

        # Show topic progress
        for task_type in required_task_types:
            emoji = task_emojis.get(task_type, "📝")
            status = "✅" if task_type in studied_types else "⭕"
            task_names = {
                "vocabulary": "Лексика",
                "listening": "Аудирование",
                "speaking": "Говорение",
                "grammar": "Грамматика",
                "reading": "Чтение",
                "writing": "Письмо",
            }
            task_name = task_names.get(task_type, task_type)

            english_text += f"{status} {emoji} {task_name}\n"

        english_text += f"\n📋 <b>Сегодняшние задания:</b>\n"

        keyboard_buttons = []

        for i, task in enumerate(existing_tasks, 1):
            task_type, task_content, task_link, completed, exp_reward = task
            emoji = task_emojis.get(task_type, "📝")
            status = "✅" if completed else "⭕"

            english_text += f"""
{status} {emoji} <b>Задание {i}:</b> {task_content}
💰 +{exp_reward} EXP
"""

            if not completed:
                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"📖 Открыть задание {i}", url=task_link
                        ),
                        InlineKeyboardButton(
                            text=f"✅ Выполнено {i}",
                            callback_data=f"eng_task_complete_{task[0]}_{i}",
                        ),
                    ]
                )

        # Add test button if available
        if next_level and can_test:
            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🎯 Тест на {next_level}",
                        callback_data=f"english_test_{next_level}",
                    )
                ]
            )
        elif next_level:
            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🚫 Тест на {next_level} ({test_reason})",
                        callback_data="test_info",
                    )
                ]
            )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(english_text, reply_markup=keyboard)

    def is_weight_input(self, text: str) -> bool:
        """Check if text is a valid weight input"""
        try:
            weight = float(text)
            return 30.0 <= weight <= 200.0  # Reasonable weight range
        except (ValueError, TypeError):
            return False

    async def _weight_filter(self, message: types.Message) -> bool:
        """Async filter for weight input messages"""
        return bool(message.text) and self.is_weight_input(message.text)

    async def handle_weight_input(self, message: types.Message):
        user_id = message.from_user.id
        try:
            weight = float(message.text)

            cursor = self.conn.cursor()
            # Save weight to tracking table
            cursor.execute(
                """
                INSERT INTO weight_tracking (user_id, weight, date)
                VALUES (?, ?, ?)
            """,
                (user_id, weight, date.today()),
            )

            # Update user's current weight
            cursor.execute(
                """
                UPDATE users SET weight = ? WHERE user_id = ?
            """,
                (weight, user_id),
            )

            self.conn.commit()

            # Get weight history for progress
            cursor.execute(
                """
                SELECT weight, date FROM weight_tracking 
                WHERE user_id = ? ORDER BY date DESC LIMIT 5
            """,
                (user_id,),
            )

            weight_history = cursor.fetchall()

            progress_text = f"⚖️ <b>Вес записан!</b>\n\n"
            progress_text += f"📊 Текущий вес: {weight} кг\n"
            progress_text += f"📅 Дата: {date.today().strftime('%d.%m.%Y')}\n\n"

            if len(weight_history) > 1:
                prev_weight = weight_history[1][0]
                change = weight - prev_weight
                if change > 0:
                    progress_text += f"📈 +{change:.1f} кг с последнего замера\n"
                elif change < 0:
                    progress_text += f"📉 {change:.1f} кг с последнего замера\n"
                else:
                    progress_text += f"➡️ Вес не изменился\n"

            progress_text += f"\n🎯 Отлично продолжай! +10 EXP"

            await self.add_exp(user_id, 10, "Запись веса")

            await message.answer(progress_text, reply_markup=self.get_main_keyboard())

        except ValueError:
            await message.answer(
                "❌ Неверный формат веса!\n\nВведи вес в килограммах (например: 65.5)",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="🍽️ Питание")]], resize_keyboard=True
                ),
            )

    async def callback_handler(self, callback: types.CallbackQuery):
        action = callback.data
        user_id = callback.from_user.id

        # Main menu handler (moved to top)
        if action == "return_main_menu":
            print(f"DEBUG: return_main_menu callback received from user {user_id}")

            # Check if user exists at all
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            user_exists = cursor.fetchone()

            if not user_exists:
                await callback.message.answer(
                    "❌ Пользователь не найден. Пожалуйста, пройдите регистрацию заново с /start"
                )
                await callback.answer()
                return

            # Check if user is registered
            cursor.execute(
                "SELECT registration_completed FROM users WHERE user_id = ?", (user_id,)
            )
            result = cursor.fetchone()

            if not result or not result[0]:
                await callback.message.answer(
                    "❌ Сначала завершите регистрацию! Нажмите /start"
                )
                await callback.answer()
                return

            await self.main_menu(callback.message)
            await callback.answer()
            return

        # Registration handlers

        elif action.startswith("reg_gender_"):
            gender_map = {"female": "женский", "male": "мужской", "none": None}
            gender = gender_map.get(action.split("_")[2])

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id)
            )
            self.conn.commit()

            await callback.message.answer(
                "✅ <b>Пол определен!</b>\n\n"
                "Теперь выбери тип кожи (это поможет с рекомендациями по уходу):",
                reply_markup=self.get_skin_type_keyboard(),
            )

        elif action.startswith("reg_skin_"):
            skin_map = {
                "dry": "сухая",
                "oily": "жирная",
                "combination": "комбинированная",
                "normal": "нормальная",
                "none": None,
            }
            skin_type = skin_map.get(action.split("_")[2])

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET skin_type = ? WHERE user_id = ?", (skin_type, user_id)
            )
            self.conn.commit()

            # Complete registration with default universe and English level A0
            cursor.execute(
                """
                UPDATE users SET 
                    anime_universe = 'Solo Leveling',
                    english_level = 'A0',
                    registration_completed = 1
                WHERE user_id = ?
            """,
                (user_id,),
            )
            self.conn.commit()

            # Give welcome bonus
            await self.add_exp(user_id, 50, "Завершение регистрации")

            await callback.message.answer(
                f"🎉 <b>Поздравляем, регистрация завершена!</b>\n\n"
                f"📋 <b>Твой профиль:</b>\n"
                f"📚 Английский: A0 (🌱 Новичок Охотника)\n"
                f"⚔️ Вселенная: Solo Leveling (по умолчанию)\n\n"
                f"🎁 Бонус за регистрацию: +50 EXP\n\n"
                f"Теперь можешь начать свой рейд!",
                reply_markup=self.get_main_keyboard(),
            )

        elif action == "reg_continue":
            await callback.message.answer(
                "📝 <b>Продолжаем регистрацию...</b>\n\n"
                "Выбери свою вселенную:",
                reply_markup=self.get_anime_universe_keyboard(),
            )

        elif action == "reg_skip":
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE users 
                SET registration_completed = 1, 
                    gender = 'женский',
                    skin_type = 'нормальная',
                    english_level = 'B1',
                    anime_universe = 'Solo Leveling'
                WHERE user_id = ?
            """,
                (user_id,),
            )
            self.conn.commit()

            await self.add_exp(user_id, 30, "Быстрая регистрация")

            await callback.message.answer(
                "🎉 <b>Профиль создан с настройками по умолчанию!</b>\n\n"
                "⚔️ Добро пожаловать в RAID SYSTEM!\n\n"
                "🎁 Бонус за регистрацию: +30 EXP\n\n"
                "Твой профиль готов к использованию!",
                reply_markup=self.get_main_keyboard(),
            )

        elif action == "refresh_stats":
            await self.stats_command(callback.message)
        elif action == "refresh_quests":
            await self.daily_quests(callback.message)

        # Quest category handlers
        elif action == "quest_category_fitness":
            await self.show_fitness_quests(callback.message)
        elif action == "quest_category_learning":
            await self.show_learning_quests(callback.message)
        elif action == "quest_category_selfcare":
            await self.show_selfcare_quests(callback.message)
        elif action == "quest_category_habits":
            await self.show_habits_quests(callback.message)

        # Enhanced workout handlers
        elif action.startswith("workout_universe_"):
            universe = action.split("_")[2]
            user_id = callback.from_user.id

            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT level FROM users WHERE user_id = ?", (user_id,)
            )
            result = cursor.fetchone()
            user_level = result[0] if result else 1

            available_ranks = self.get_available_ranks(user_level)
            workout_library = self.get_workout_library()

            # Get the highest available rank
            highest_rank = available_ranks[-1] if available_ranks else "E"

            # Get workout for this universe and rank
            universe_workouts = workout_library.get(universe, {})

            # Special handling for Solo Leveling with ranks
            if universe == "solo":
                # Try to get the highest available rank, fallback to lower ranks
                workout = {}
                selected_rank = "E"
                for rank in reversed(available_ranks):
                    workout = universe_workouts.get(rank, {})
                    if workout:
                        selected_rank = rank
                        break
            else:
                # For other universes, only use E-rank
                workout = universe_workouts.get("E", {})
                selected_rank = "E"

            # If still no workout found, use fallback
            if not workout:
                # Fallback to basic workout if specific universe not available
                fallback_workout = {
                    "title": f"⚔️ Квест: {universe.title()} Базовая тренировка",
                    "description": "Адаптированная тренировка",
                    "exp": 20,
                    "exercises": [
                        {
                            "name": "🧘 Разминка",
                            "duration": "5 минут",
                            "quote": "Начало - половина успеха",
                        },
                        {
                            "name": "🤸 Основная часть",
                            "duration": "15 минут",
                            "quote": "Сила растет через преодоление",
                        },
                        {
                            "name": "🧘 Заминка",
                            "duration": "5 минут",
                            "quote": "Восстановление важно",
                        },
                    ],
                    "warnings": ["⚠️ Контролируй дыхание", "🌬️ Не перенапрягайся"],
                }

                text = f"{fallback_workout['title']}\n\n"
                text += f"📝 <b>Ранг:</b> {fallback_workout['description']}\n"
                text += f"⭐ <b>Награда:</b> {fallback_workout['exp']} EXP\n\n"
                text += "📋 <b>План тренировки:</b>\n"

                for i, exercise in enumerate(fallback_workout["exercises"], 1):
                    text += f"{i}. {exercise['name']} ({exercise['duration']})\n"
                    text += f'   💬 "{exercise["quote"]}"\n'

                text += "\n⚠️ <b>Важно для астматиков:</b>\n"
                for warning in fallback_workout["warnings"]:
                    text += f"{warning}\n"

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Тренировка выполнена",
                                callback_data=f"complete_workout_{universe}_E",
                            )
                        ]
                    ]
                )

                await callback.message.answer(text, reply_markup=keyboard)
                return

            # Display the found workout
            text = f"{workout['title']}\n\n"
            text += f"📝 <b>Ранг:</b> {workout.get('description', '')}\n"
            text += f"⭐ <b>Награда:</b> {workout.get('exp', 20)} EXP\n\n"
            text += "📋 <b>План тренировки:</b>\n"

            for i, exercise in enumerate(workout["exercises"], 1):
                text += f"{i}. {exercise['name']} ({exercise['duration']})\n"
                text += f'   💬 "{exercise["quote"]}"\n'

            text += "\n⚠️ <b>Важно для астматиков:</b>\n"
            for warning in workout.get("warnings", []):
                text += f"{warning}\n"

            text += "\n🌬️ <b>Дыхательные техники:</b>\n"
            text += "• Вдох 4 сек - задержка 2 сек - выдох 6 сек\n"
            text += "• Дышать через нос при нагрузке\n"
            text += "• Отдыхать при дискомфорте\n"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Тренировка выполнена",
                            callback_data=f"complete_workout_{universe}_{selected_rank}",
                        )
                    ],
                ]
            )

            await callback.message.answer(text, reply_markup=keyboard)

        elif action.startswith("workout_specific_"):
            parts = action.split("_")
            universe = parts[2]
            rank = parts[3]

            workout_library = self.get_workout_library()
            workout = workout_library.get(universe, {}).get(rank, {})

            if workout:
                text = f"{workout['title']}\n\n"
                text += f"📝 <b>Ранг:</b> {workout.get('description', '')}\n"
                text += f"⭐ <b>Награда:</b> {workout.get('exp', 20)} EXP\n\n"
                text += "📋 <b>План тренировки:</b>\n"

                for i, exercise in enumerate(workout["exercises"], 1):
                    text += f"{i}. {exercise['name']} ({exercise['duration']})\n"
                    text += f'   💬 "{exercise["quote"]}"\n'

                text += "\n⚠️ <b>Важно для астматиков:</b>\n"
                for warning in workout.get("warnings", []):
                    text += f"{warning}\n"

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Тренировка выполнена",
                                callback_data=f"complete_workout_{universe}_{rank}",
                            )
                        ]
                    ]
                )

                await callback.message.answer(text, reply_markup=keyboard)

        elif action.startswith("complete_workout_"):
            parts = action.split("_")
            universe = parts[2]
            rank = parts[3] if len(parts) > 3 else "E"

            workout_library = self.get_workout_library()
            workout = workout_library.get(universe, {}).get(rank, {})

            exp_reward = workout.get("exp", 20)

            await self.add_exp(
                user_id, exp_reward, f"Тренировка: {universe} {rank}-rank"
            )

            # Check for rank up
            await self.check_rank_up(callback.message, user_id)

            await callback.message.answer(
                f"🎉 <b>Тренировка завершена!</b>\n\n"
                f"⚔️ Вселенная: {universe.title()}\n"
                f"🎯 Ранг: {rank.upper()}\n"
                f"⭐ Награда: +{exp_reward} EXP\n\n"
                f"🔥 Отличная работа, Охотник!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⚔️ Еще тренировка", callback_data="workout_menu"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="🔙 К тренировкам", callback_data="workout_menu"
                            )
                        ],
                    ]
                ),
            )

        elif action == "workout_menu":
            await self.workout_menu(callback.message)

        # Nutrition handlers
        elif action == "water_add":
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE nutrition_plans 
                SET water_consumed = water_consumed + 1
                WHERE user_id = ? AND date = ?
            """,
                (user_id, date.today()),
            )
            self.conn.commit()

            await self.add_exp(user_id, 5, "Выпит стакан воды")
            await self.nutrition_menu(callback.message)

        elif action == "skin_care_morning":
            await self.add_exp(user_id, 5, "Утренний уход за кожей")
            # Mark skin care quest as completed
            await self.complete_daily_quest(user_id, "🧹 Уход за кожей")
            await callback.message.answer(
                "✅ <b>Утренний уход выполнен!</b> +5 EXP\n\n"
                "🌟 Отличное начало дня!\n"
                "Твоя кожа скажет тебе спасибо ✨",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "skin_care_evening":
            await self.add_exp(user_id, 5, "Вечерний уход за кожей")
            # Mark skin care quest as completed
            await self.complete_daily_quest(user_id, "🧹 Уход за кожей")
            await callback.message.answer(
                "✅ <b>Вечерний уход выполнен!</b> +5 EXP\n\n"
                "🌙 Сладких снов!\n"
                "Кожа регенерируется во время сна 💫",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        # Quest completion handlers
        elif action == "quest_morning_workout":
            await self.add_exp(callback.from_user.id, 30, "Утренняя зарядка")
            await callback.message.answer(
                "✅ <b>Зарядка выполнена!</b> +30 EXP\n\n"
                "🌅 Отличное начало дня!\n"
                "💪 Ты стал сильнее!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_stretching":
            await self.add_exp(callback.from_user.id, 20, "Растяжка")
            await callback.message.answer(
                "✅ <b>Растяжка выполнена!</b> +20 EXP\n\n"
                "🧘 Тело стало более гибким!\n"
                "🌿 Отлично для здоровья позвоночника!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_steps":
            await self.add_exp(callback.from_user.id, 25, "5000 шагов")
            await callback.message.answer(
                "✅ <b>5000 шагов пройдено!</b> +25 EXP\n\n"
                "🚶 Отличная активность!\n"
                "💔 Сердце скажет спасибо!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_english":
            await self.add_exp(callback.from_user.id, 40, "Английский язык")
            await callback.message.answer(
                "✅ <b>Английский изучен!</b> +40 EXP\n\n"
                "📚 Knowledge is power!\n"
                "🌍 Ты стал ближе к миру!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📚 Английский", callback_data="english_menu"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_reading":
            await self.add_exp(callback.from_user.id, 25, "Чтение книги")
            await callback.message.answer(
                "✅ <b>10 страниц прочитано!</b> +25 EXP\n\n"
                "📖 Книга - лучший друг!\n"
                "🧠 Мозг стал острее!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_video":
            await self.add_exp(callback.from_user.id, 20, "Образовательное видео")
            await callback.message.answer(
                "✅ <b>Видео просмотрено!</b> +20 EXP\n\n"
                "🎧 Новые знания получены!\n"
                "💡 Продолжай развиваться!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_journal":
            await self.add_exp(callback.from_user.id, 15, "Дневниковая запись")
            await callback.message.answer(
                "✅ <b>Запись в дневнике сделана!</b> +15 EXP\n\n"
                "✍️ Мысли выражены!\n"
                "🧘 Психологическое здоровье важно!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_hair_care":
            await self.add_exp(callback.from_user.id, 20, "Уход за волосами")
            await callback.message.answer(
                "✅ <b>Уход за волосами выполнен!</b> +20 EXP\n\n"
                "💇 Волосы скажут спасибо!\n"
                "✨ Ты прекрасен/прекрасна!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_shower":
            await self.add_exp(callback.from_user.id, 10, "Душ/ванна")
            await callback.message.answer(
                "✅ <b>Гигиена выполнена!</b> +10 EXP\n\n"
                "🧼 Чистота - залог здоровья!\n"
                "💦 Свежесть и бодрость!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_early_sleep":
            await self.add_exp(callback.from_user.id, 20, "Ранний сон")
            await callback.message.answer(
                "✅ <b>Ранний сон!</b> +20 EXP\n\n"
                "😴 Сладких снов!\n"
                "🌙 Восстановление началось!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_no_phone":
            await self.add_exp(callback.from_user.id, 15, "Без телефона перед сном")
            await callback.message.answer(
                "✅ <b>Цифровой детокс!</b> +15 EXP\n\n"
                "📱 Глаза отдохнули!\n"
                "🧘 Мозг готов ко сну!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_cleaning":
            await self.add_exp(callback.from_user.id, 25, "Уборка")
            await callback.message.answer(
                "✅ <b>Комната убрана!</b> +25 EXP\n\n"
                "🧹 Чистота и порядок!\n"
                "🏠 Дом - крепость!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "quest_healthy_food":
            await self.add_exp(callback.from_user.id, 10, "Здоровая пища")
            await callback.message.answer(
                "✅ <b>Полезная еда съедена!</b> +10 EXP\n\n"
                "🍏 Витамины получены!\n"
                "💪 Энергия на весь день!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Статус", callback_data="refresh_stats"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action.startswith("meal_"):
            meal_type = action.split("_")[1]
            meal_names = {"breakfast": "завтрак", "lunch": "обед", "dinner": "ужин"}
            meal_name = meal_names.get(meal_type, "прием пищи")

            await self.add_exp(user_id, 15, f"Выполнен {meal_name}")
            await callback.message.answer(
                f"✅ {meal_name.capitalize()} выполнен! +15 EXP",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🍽️ Питание", callback_data="nutrition_menu"
                            )
                        ]
                    ]
                ),
            )

        elif action == "food_list":
            low_cal_foods = self.get_low_calorie_foods()

            food_text = "🥗 Продукты для похудения\n\n"

            for category, foods in low_cal_foods.items():
                food_text += f"📋 {category}:\n"
                for food in foods:
                    food_text += f"• {food}\n"
                food_text += "\n"

            food_text += """
💡 Как использовать:
• Составляй рацион из этих продуктов
• Белки + овощи = идеальное сочетание
• Углеводы только на завтрак и обед
• Фрукты как перекусы до 16:00
• Овощи можно есть в неограниченном количестве
            """

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🍽️ Питание", callback_data="nutrition_menu"
                        )
                    ]
                ]
            )

            await callback.message.answer(food_text, reply_markup=keyboard)

        elif action == "menu_week":
            weekly_menu = self.generate_weekly_menu()

            week_text = "Меню на неделю\n\n"

            for day, meals in weekly_menu.items():
                week_text += f"{day}:\n"
                week_text += f"Завтрак: {meals['breakfast']}\n"
                week_text += f"Обед: {meals['lunch']}\n"
                week_text += f"Ужин: {meals['dinner']}\n"
                week_text += f"Перекус: {meals['snack']}\n\n"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Сегодняшнее меню", callback_data="nutrition_menu"
                        )
                    ]
                ]
            )

            await callback.message.answer(week_text, reply_markup=keyboard)

        elif action == "weight_log":
            await callback.message.answer(
                "⚖️ <b>Запись веса</b>\n\n"
                "Введи свой вес в килограммах (например: 65.5)\n"
                "Это поможет отслеживать прогресс похудения!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
            )

        elif action == "nutrition_menu":
            await self.nutrition_menu(callback.message)

        # English handlers
        elif action == "english_menu":
            await self.english_menu(callback.message)
        elif action.startswith("eng_task_complete_"):
            parts = action.split("_")
            task_type = parts[3]
            task_number = parts[4]

            cursor = self.conn.cursor()

            # Update task as completed
            cursor.execute(
                """
                UPDATE daily_english_tasks 
                SET completed = 1 
                WHERE user_id = ? AND date = ? AND task_type = ?
            """,
                (user_id, date.today(), task_type),
            )

            # Get exp reward
            cursor.execute(
                """
                SELECT exp_reward FROM daily_english_tasks 
                WHERE user_id = ? AND date = ? AND task_type = ?
            """,
                (user_id, date.today(), task_type),
            )
            result = cursor.fetchone()
            exp_reward = result[0] if result else 5

            self.conn.commit()

            # Add experience
            await self.add_exp(
                user_id, exp_reward, f"Английское задание #{task_number}"
            )

            # Check for rank up
            await self.check_rank_up(callback.message, user_id)

            # Add English specific EXP
            cursor.execute(
                """
                UPDATE users SET english_exp = english_exp + ? WHERE user_id = ?
            """,
                (exp_reward, user_id),
            )
            self.conn.commit()

            # Check if user is ready for level up
            await self.check_english_level_up(callback.message, user_id)

            await callback.message.answer(
                f"🎉 <b>Задание #{task_number} выполнено!</b>\n\n"
                f"💰 Награда: +{exp_reward} EXP\n"
                f"🔥 Отличная работа!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📚 К заданиям", callback_data="english_menu"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action.startswith("english_test_"):
            target_level = action.split("_")[2]

            can_test, test_reason = self.can_take_english_test(user_id, target_level)

            if not can_test:
                await callback.message.answer(
                    f"🚫 <b>Тест недоступен</b>\n\nПричина: {test_reason}",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="📚 К английскому",
                                    callback_data="english_menu",
                                )
                            ]
                        ]
                    ),
                )
                await callback.answer()
                return

            # Get level requirements for test info
            requirements = self.get_english_level_requirements(target_level)

            test_text = f"""
🎯 <b>Тест на уровень {target_level}</b>

📋 <b>Требования для прохождения:</b>
• Опыт: {requirements["exp_required"]} EXP
• Выполненных заданий: {requirements["min_tasks_completed"]}

📚 <b>Темы тестирования:</b>

📖 <b>Грамматика:</b>
{requirements["grammar_topics"]}

📝 <b>Лексика:</b>
{requirements["vocabulary_topics"]}

🗣 <b>Говорение:</b>
{requirements["speaking_requirements"]}

🎧 <b>Аудирование:</b>
{requirements["listening_requirements"]}

📄 <b>Чтение:</b>
{requirements["reading_requirements"]}

✍️ <b>Письмо:</b>
{requirements["writing_requirements"]}

⚠️ <b>Важно:</b>
• Тест можно сдавать раз в день
• Нужно набрать минимум 70% по каждому навыку
• В случае провала можно попробовать завтра

Готов начать тестирование?
"""

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🚀 Начать тест",
                            callback_data=f"start_english_test_{target_level}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📚 К английскому", callback_data="english_menu"
                        )
                    ],
                ]
            )

            await callback.message.answer(test_text, reply_markup=keyboard)
            await callback.answer()

        elif action.startswith("start_english_test_"):
            target_level = action.split("_")[3]

            # Update test attempts
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE users 
                SET last_english_test_date = ?, english_test_attempts = english_test_attempts + 1
                WHERE user_id = ?
            """,
                (date.today(), user_id),
            )
            self.conn.commit()

            # Start with grammar test
            await self.start_english_test_section(
                callback.message, target_level, "grammar"
            )
            await callback.answer()

        elif action == "test_info":
            await callback.message.answer(
                "ℹ️ <b>О тестах английского</b>\n\n"
                "Тесты становятся доступны когда:\n"
                "• Накоплено достаточно EXP для следующего уровня\n"
                "• Выполнено минимальное количество заданий\n"
                "• Прошло 24 часа с последней попытки\n\n"
                "Тест проверяет все 5 навыков языка!\n"
                "Нужно минимум 70% по каждому для перехода.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📚 К английскому", callback_data="english_menu"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action.startswith("test_answer_"):
            parts = action.split("_")
            section = parts[2]
            correct_answer = int(parts[3])
            user_answer = int(parts[4])

            is_correct = correct_answer == user_answer

            if is_correct:
                await callback.message.answer(
                    "✅ <b>Правильно!</b>\n\n"
                    "Отличная работа! Переходим к следующему вопросу...",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="➡️ Следующий вопрос",
                                    callback_data=f"next_question_{section}",
                                )
                            ]
                        ]
                    ),
                )
            else:
                await callback.message.answer(
                    "❌ <b>Неправильно!</b>\n\n"
                    "Не волнуйся, это часть обучения. Продолжаем...",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="➡️ Следующий вопрос",
                                    callback_data=f"next_question_{section}",
                                )
                            ]
                        ]
                    ),
                )
            await callback.answer()

        elif action.startswith("next_question_"):
            section = action.split("_")[2]

            # For simplicity, end test after one question per section
            await callback.message.answer(
                f"✅ <b>Секция {section.title()} завершена!</b>\n\n"
                "Переходим к следующему навыку...",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="➡️ Следующий навык",
                                callback_data="next_test_section",
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "next_test_section":
            # Simplified - just complete the test
            await callback.message.answer(
                "🎉 <b>Тест завершен!</b>\n\n"
                "Твои результаты сохранены. Проверяем ответы...\n\n"
                "⏳ Пожалуйста, подожди немного...",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📊 Посмотреть результаты",
                                callback_data="show_test_results",
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action == "show_test_results":
            # Simulate test results (in real implementation, calculate from actual answers)
            scores = {
                "grammar": 85,
                "vocabulary": 90,
                "reading": 80,
                "listening": 75,
                "writing": 88,
            }

            passed = all(score >= 70 for score in scores.values())

            if passed:
                # Update user level
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT english_level FROM users WHERE user_id = ?", (user_id,)
                )
                current_level = cursor.fetchone()[0]
                next_level = self.get_next_english_level(current_level)

                if next_level:
                    cursor.execute(
                        """
                        UPDATE users SET english_level = ? WHERE user_id = ?
                    """,
                        (next_level, user_id),
                    )
                    self.conn.commit()

                result_text = f"""
🎉 <b>Поздравляем! Тест пройден!</b>

🏆 <b>Твой новый уровень: {next_level}</>

📊 <b>Результаты:</b>
📖 Грамматика: {scores["grammar"]}%
📝 Лексика: {scores["vocabulary"]}%
📄 Чтение: {scores["reading"]}%
🎧 Аудирование: {scores["listening"]}%
✍️ Письмо: {scores["writing"]}%

🎁 <b>Награда:</b>
• Новый уровень английского
• +100 EXP
• Разблокированы новые задания

🔥 Отличная работа, продолжай в том же духе!
"""
            else:
                result_text = f"""
😔 <b>Тест не пройден</b>

📊 <b>Результаты:</b>
📖 Грамматика: {scores["grammar"]}%
📝 Лексика: {scores["vocabulary"]}%
📄 Чтение: {scores["reading"]}%
🎧 Аудирование: {scores["listening"]}%
✍️ Письмо: {scores["writing"]}%

⚠️ <b>Требования:</b>
• Минимум 70% по каждому навыку
• Можно попробовать завтра снова

💡 <b>Рекомендации:</b>
• Выполняй больше ежедневных заданий
• Практикуй слабые навыки
• Не сдавайся!

🔄 Попробуй снова завтра!
"""

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📚 К английскому", callback_data="english_menu"
                        )
                    ]
                ]
            )

            await callback.message.answer(result_text, reply_markup=keyboard)
            await callback.answer()

        elif action == "cancel_test":
            await callback.message.answer(
                "❌ <b>Тест прерван</b>\n\n"
                "Ты можешь начать тест заново завтра.\n"
                "Продолжай выполнять ежедневные задания!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📚 К английскому", callback_data="english_menu"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

        elif action.startswith("eng_"):
            activity_type = action.split("_")[1]
            activity_map = {
                "memrise": ("Memrise", "слов", 5),
                "listening": ("Listening", "минут аудирования", 2),
                "speaking": ("Speaking", "минут разговора", 3),
                "grammar": ("Grammar", "урок грамматики", 50),
                "immersion": ("Immersion", "минут погружения", 1),
                "reading": ("Reading", "глав манги", 30),
                "gaming": ("Gaming", "минут игры", 1),
            }

            activity_name, unit, exp_rate = activity_map.get(
                activity_type, ("Activity", "единиц", 1)
            )

            await callback.message.answer(
                f"📚 <b>{activity_name}</b>\n\n"
                f"Сколько {unit} ты выполнил(а)?\n"
                f"🎁 {exp_rate} EXP за каждую {unit.rstrip('ы')}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"10 {unit}",
                                callback_data=f"log_{activity_type}_10",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=f"20 {unit}",
                                callback_data=f"log_{activity_type}_20",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=f"30 {unit}",
                                callback_data=f"log_{activity_type}_30",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=f"50 {unit}",
                                callback_data=f"log_{activity_type}_50",
                            )
                        ],
                    ]
                ),
            )

        elif action.startswith("log_"):
            parts = action.split("_")
            activity_type = parts[1]
            amount = int(parts[2])

            activity_map = {
                "memrise": 5,
                "listening": 2,
                "speaking": 3,
                "grammar": 50,
                "immersion": 1,
                "reading": 30,
                "gaming": 1,
            }

            exp_rate = activity_map.get(activity_type, 1)
            total_exp = amount * exp_rate

            await self.add_exp(user_id, total_exp, f"Английский: {activity_type}")

            await callback.message.answer(
                f"✅ Отлично! +{total_exp} EXP за {amount} единиц!\n"
                f"🎯 Продолжай в том же духе!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📚 Английский", callback_data="english_menu"
                            )
                        ]
                    ]
                ),
            )
            await callback.answer()

    async def complete_daily_quest(self, user_id: int, quest_title: str):
        """Mark a daily quest as completed"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE daily_quests 
            SET completed = 1 
            WHERE user_id = ? AND title = ? AND date = ?
        """,
            (user_id, quest_title, date.today()),
        )
        self.conn.commit()

    async def add_exp(self, user_id: int, exp_amount: int, reason: str = ""):
        """Add experience to user and handle level up"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT level, exp, exp_to_next FROM users WHERE user_id = ?", (user_id,)
        )
        user_data = cursor.fetchone()

        if user_data:
            level, current_exp, exp_to_next = user_data
            new_exp = current_exp + exp_amount

            # Check for level up
            while new_exp >= exp_to_next:
                new_exp -= exp_to_next
                level += 1
                exp_to_next = int(exp_to_next * 1.5)

                # Increase stats on level up
                cursor.execute(
                    """
                    UPDATE users 
                    SET level = ?, exp_to_next = ?, 
                        power = power + 1,
                        analysis = analysis + 1, 
                        endurance = endurance + 1,
                        speed = speed + 1
                    WHERE user_id = ?
                """,
                    (level, exp_to_next, user_id),
                )

            # Update experience
            cursor.execute(
                """
                UPDATE users 
                SET exp = ?, last_activity = ?
                WHERE user_id = ?
            """,
                (new_exp, date.today(), user_id),
            )

            self.conn.commit()

            # Log progress
            cursor.execute(
                """
                INSERT INTO english_progress (user_id, activity_type, amount, exp_gained, date)
                VALUES (?, ?, ?, ?, ?)
            """,
                (user_id, reason, 1, exp_amount, date.today()),
            )
            self.conn.commit()

    async def send_skin_care_reminders(self):
        """Send daily skin care reminders to all users"""
        while True:
            try:
                # Check current time
                now = datetime.now()

                # Early morning reminder at 6:00 AM for students
                if now.hour == 6 and now.minute == 0:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT user_id FROM users")
                    users = cursor.fetchall()

                    for user in users:
                        user_id = user[0]
                        try:
                            morning_tips = self.get_skin_care_tips("morning")
                            await self.bot.send_message(
                                user_id,
                                f"🌅 <b>Раннее утро! Время ухода за кожей 📚</b>\n\n"
                                f"{morning_tips}\n\n"
                                f"💧 Идеальное время для ухода перед учебой!\n"
                                f"🎁 +5 EXP за утренний уход",
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text="✅ Уход выполнен",
                                                callback_data="skin_care_morning",
                                            )
                                        ]
                                    ]
                                ),
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to send early morning reminder to user {user_id}: {e}"
                            )

                # Morning reminder at 9:00 AM
                if now.hour == 9 and now.minute == 0:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT user_id FROM users")
                    users = cursor.fetchall()

                    for user in users:
                        user_id = user[0]
                        try:
                            morning_tips = self.get_skin_care_tips("morning")
                            await self.bot.send_message(
                                user_id,
                                f"🌅 <b>Доброе утро! Время ухода за кожей ☀️</b>\n\n"
                                f"{morning_tips}\n\n"
                                f"💧 Не забудь умыться и нанести увлажняющий крем!\n"
                                f"🎁 +5 EXP за утренний уход",
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text="✅ Уход выполнен",
                                                callback_data="skin_care_morning",
                                            )
                                        ]
                                    ]
                                ),
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to send morning reminder to user {user_id}: {e}"
                            )

                # Evening reminder at 9:00 PM
                if now.hour == 21 and now.minute == 0:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT user_id FROM users")
                    users = cursor.fetchall()

                    for user in users:
                        user_id = user[0]
                        try:
                            evening_tips = self.get_skin_care_tips("evening")
                            await self.bot.send_message(
                                user_id,
                                f"🌙 <b>Добрый вечер! Время вечернего ухода за кожей 🌜</b>\n\n"
                                f"{evening_tips}\n\n"
                                f"🧼 Очисти кожу от макияжа и загрязнений!\n"
                                f"🎁 +5 EXP за вечерний уход",
                                reply_markup=InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text="✅ Уход выполнен",
                                                callback_data="skin_care_evening",
                                            )
                                        ]
                                    ]
                                ),
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to send evening reminder to user {user_id}: {e}"
                            )

                # Sleep for 1 minute to check time
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in skin care reminders: {e}")
                await asyncio.sleep(60)

    def get_skin_care_tips(self, time_of_day):
        """Get skin care tips based on time of day"""
        morning_tips = [
            "🧊 Умойся прохладной водой для тонуса кожи",
            "💧 Нанеси легкий увлажняющий крем",
            "🌱 Используй сыворотку с витамином С",
            "☀️ Обязательно нанеси солнцезащитный крем",
            "🥤 Выпей стакан воды для гидратации изнутри",
        ]

        evening_tips = [
            "🧪 Используй мицеллярную воду или гель для умывания",
            "🌿 Нанеси успокаивающий тонер",
            "💊 Примени сыворотку с ретинолом или гиалуроновой кислотой",
            "🧴 Используй питательный ночной крем",
            "😴 Постарайся лечь спать до 23:00 для регенерации кожи",
        ]

        tips = morning_tips if time_of_day == "morning" else evening_tips
        return "\n".join(f"• {tip}" for tip in random.sample(tips, 3))

    async def run(self):
        try:
            # Запускаем health check сервер для UptimeRobot
            start_health_check()
            
            # Запускаем напоминания
            asyncio.create_task(self.send_skin_care_reminders())

            logging.info("🤖 Bot started polling...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logging.error(f"❌ Ошибка запуска бота: {e}")
            raise

def main():
    if not TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не найден в .env файле")
        return

    print("🚀 Запуск бота...")
    
    # Запускаем бота
    bot = SimpleRaidBot(TOKEN)
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()

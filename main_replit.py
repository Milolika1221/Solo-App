import asyncio
import logging
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os
from dotenv import load_dotenv
import json
import random
from flask import Flask, request
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
try:
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
except:
    TOKEN = "8680731216:AAF384UUlQlvmsrEQ2hm2VxLaaxE9YyUjfI"

# Flask app для Replit (чтобы бот не засыпал)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Для будущей интеграции с webhook
    return "ok"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Запуск Flask в отдельном потоке
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

class SimpleRaidBot:
    def __init__(self, token):
        self.bot = Bot(token=token, parse_mode="HTML")
        self.dp = Dispatcher(self.bot)
        self.setup_handlers()
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        self.conn = sqlite3.connect('raid_system.db')
        cursor = self.conn.cursor()
        
        # Clear old nutrition data if exists (only if table exists)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nutrition_plans'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM nutrition_plans")
        
        # Users table (expanded according to TZ)
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
                has_asthma BOOLEAN DEFAULT 1,
                asthma_control INTEGER DEFAULT 3,
                anime_universe TEXT DEFAULT 'Solo Leveling',
                registration_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily quests table
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
        
        # English progress table
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
        
        # Nutrition plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                meals_completed INTEGER DEFAULT 0,
                water_consumed INTEGER DEFAULT 0,
                calories_consumed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        self.conn.commit()
    
    def setup_handlers(self):
        # Command handlers
        self.dp.message_handler(Command("start"))(self.start_command)
        self.dp.message_handler(Command("help"))(self.help_command)
        self.dp.message_handler(Command("stats"))(self.stats_command)
        
        # Message handlers
        self.dp.message_handler(lambda msg: msg.text == "Квесты")(self.daily_quests)
        self.dp.message_handler(lambda msg: msg.text == "Тренировки")(self.workout_menu)
        self.dp.message_handler(lambda msg: msg.text == "Английский")(self.english_menu)
        self.dp.message_handler(lambda msg: msg.text in ["Статус", "📊 Статус"])(self.stats_command)
        self.dp.message_handler(lambda msg: msg.text == "🍽️ Питание")(self.nutrition_menu)
        self.dp.message_handler(lambda msg: msg.text == "🏠 Главное меню")(self.main_menu)
        
        # Registration handlers
        self.dp.message_handler(lambda msg: msg.text in ["Мужской", "👨 Мужской"])(self.set_gender_male)
        self.dp.message_handler(lambda msg: msg.text in ["Женский", "👩 Женский"])(self.set_gender_female)
        
        # Skin type handlers
        self.dp.message_handler(lambda msg: msg.text in ["Сухая", "🏜️ Сухая"])(self.set_skin_dry)
        self.dp.message_handler(lambda msg: msg.text in ["Жирная", "🫧 Жирная"])(self.set_skin_oily)
        self.dp.message_handler(lambda msg: msg.text in ["Нормальная", "⚖️ Нормальная"])(self.set_skin_normal)
        self.dp.message_handler(lambda msg: msg.text in ["Комбинированная", "🌈 Комбинированная"])(self.set_skin_combination)
        self.dp.message_handler(lambda msg: msg.text in ["Чувствительная", "🌸 Чувствительная"])(self.set_skin_sensitive)
        
        # Weight input handler
        self.dp.message_handler(self.is_weight_input)(self.handle_weight_input)
        
        # Callback handlers
        self.dp.callback_query_handler()(self.callback_handler)
    
    def get_main_keyboard(self):
        """Get main menu keyboard"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                ["📊 Статус", "Квесты"],
                ["Тренировки", "Английский"],
                ["🍽️ Питание", "🏠 Главное меню"]
            ],
            resize_keyboard=True
        )
        return keyboard
    
    def get_gender_keyboard(self):
        """Get gender selection keyboard"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                ["👨 Мужской", "👩 Женский"]
            ],
            resize_keyboard=True
        )
        return keyboard
    
    def get_skin_type_keyboard(self):
        """Get skin type selection keyboard"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                ["🏜️ Сухая", "🫧 Жирная"],
                ["⚖️ Нормальная", "🌈 Комбинированная"],
                ["🌸 Чувствительная"]
            ],
            resize_keyboard=True
        )
        return keyboard
    
    async def start_command(self, message: types.Message):
        """Handle /start command"""
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            # Create new user
            cursor.execute("""
                INSERT INTO users (user_id, created_at, last_activity)
                VALUES (?, ?, ?)
            """, (user_id, datetime.now(), date.today()))
            self.conn.commit()
            
            await message.answer(
                "🎮 <b>Добро пожаловать в SOLO RAID SYSTEM!</b>\n\n"
                "Ты готов начать свой путь к силе?\n\n"
                "Давай проведем быструю регистрацию!",
                reply_markup=self.get_gender_keyboard()
            )
        else:
            await self.main_menu(message)
    
    async def help_command(self, message: types.Message):
        """Handle /help command"""
        help_text = """
🤖 <b>SOLO RAID SYSTEM - Помощь</b>

🎮 <b>Основные команды:</b>
• /start - Начать игру
• /stats - Посмотреть статистику
• /help - Эта помощь

📋 <b>Меню:</b>
• 📊 Статус - Твой прогресс
• Квесты - Ежедневные задания
• Тренировки - Физические упражнения
• Английский - Изучение языка
• 🍽️ Питание - План питания

💪 <b>Как играть:</b>
1. Выполняй ежедневные квесты
2. Получай EXP за задания
3. Повышай свой уровень
4. Открывай новые тренировки

🌟 <b>Совет:</b> Регулярность - ключ к успеху!
        """
        await message.answer(help_text, reply_markup=self.get_main_keyboard())
    
    async def main_menu(self, message: types.Message):
        """Show main menu"""
        await message.answer(
            "🏠 <b>Главное меню</b>\n\n"
            "Выбери действие:",
            reply_markup=self.get_main_keyboard()
        )
    
    async def set_gender_male(self, message: types.Message):
        """Set male gender"""
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET gender = 'мужской' WHERE user_id = ?", (user_id,))
        self.conn.commit()
        
        await message.answer(
            "👨 Пол установлен: Мужской\n\n"
            "Теперь выбери тип кожи:",
            reply_markup=self.get_skin_type_keyboard()
        )
    
    async def set_gender_female(self, message: types.Message):
        """Set female gender"""
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET gender = 'женский' WHERE user_id = ?", (user_id,))
        self.conn.commit()
        
        await message.answer(
            "👩 Пол установлен: Женский\n\n"
            "Теперь выбери тип кожи:",
            reply_markup=self.get_skin_type_keyboard()
        )
    
    async def set_skin_dry(self, message: types.Message):
        """Set dry skin type"""
        await self.set_skin_type(message, "сухая")
    
    async def set_skin_oily(self, message: types.Message):
        """Set oily skin type"""
        await self.set_skin_type(message, "жирная")
    
    async def set_skin_normal(self, message: types.Message):
        """Set normal skin type"""
        await self.set_skin_type(message, "нормальная")
    
    async def set_skin_combination(self, message: types.Message):
        """Set combination skin type"""
        await self.set_skin_type(message, "комбинированная")
    
    async def set_skin_sensitive(self, message: types.Message):
        """Set sensitive skin type"""
        await self.set_skin_type(message, "чувствительная")
    
    async def set_skin_type(self, message: types.Message, skin_type: str):
        """Set skin type and complete registration"""
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET skin_type = ?, registration_completed = 1 WHERE user_id = ?", (skin_type, user_id))
        self.conn.commit()
        
        # Add registration bonus
        await self.add_exp(user_id, 30, "Регистрация")
        
        await message.answer(
            "🌸 Тип кожи установлен: " + skin_type.capitalize() + "\n\n"
            "🎉 <b>Регистрация завершена!</b>\n\n"
            "🎁 Бонус за регистрацию: +30 EXP\n\n"
            "🚀 Твой путь к силе начинается сейчас!",
            reply_markup=self.get_main_keyboard()
        )
    
    def is_weight_input(self, message: types.Message) -> bool:
        """Check if message is valid weight input"""
        try:
            weight = float(message.text)
            return 30.0 <= weight <= 200.0
        except ValueError:
            return False
    
    async def handle_weight_input(self, message: types.Message):
        """Handle weight input"""
        user_id = message.from_user.id
        weight = float(message.text)
        
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET weight = ?, last_activity = ? WHERE user_id = ?", (weight, date.today(), user_id))
        self.conn.commit()
        
        await self.add_exp(user_id, 10, "Запись веса")
        
        progress_text = f"""
⚖️ <b>Вес записан!</b>

📊 Текущий вес: {weight} кг
🎁 Получено: +10 EXP

💪 Отличная работа! Продолжай в том же духе!
        """
        
        await message.answer(progress_text, reply_markup=self.get_main_keyboard())
    
    async def stats_command(self, message: types.Message):
        """Show user statistics"""
        user_id = message.from_user.id
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT level, exp, exp_to_next, power, analysis, endurance, speed, 
                   skin_health, english_progress, streak, last_activity, weight,
                   gender, skin_type, english_level, english_exp, has_asthma, asthma_control
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            await message.answer("Сначала зарегистрируйся! /start")
            return
        
        (level, exp, exp_to_next, power, analysis, endurance, speed,
         skin_health, english_progress, streak, last_activity, weight,
         gender, skin_type, english_level, english_exp, has_asthma, asthma_control) = result
        
        # Calculate progress percentage
        progress_percentage = (exp / exp_to_next) * 100 if exp_to_next > 0 else 0
        
        # Create status bar
        status_bar = "█" * int(progress_percentage // 10) + "░" * (10 - int(progress_percentage // 10))
        
        # Get anime universe based on level
        universe = self.get_anime_universe(level)
        
        # Asthma emoji based on control level
        asthma_emoji = self.get_asthma_emoji(asthma_control)
        
        stats_text = f"""
🏮 <b>【SOLO LEVELING SYSTEM】</b> 🏮

🎯 <b>Уровень: {level}</b> ({universe})
⭐ EXP: {exp}/{exp_to_next} [{status_bar}] ({progress_percentage:.1f}%)

💪 <b>Статы:</b>
• Сила: {power:.1f}
• Анализ: {analysis:.1f}
• Выносливость: {endurance:.1f}
• Скорость: {speed:.1f}

🌸 <b>Здоровье:</b>
{asthma_emoji} Контроль астмы: {asthma_control}/5
🧹 Здоровье кожи: {skin_health}/100

📚 <b>Английский:</b>
🏆 Уровень: {english_level}
⭐ EXP: {english_exp}

📊 <b>Прогресс:</b>
🔥 Серия дней: {streak}
⚖️ Вес: {weight if weight else "Не указан"} кг
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_stats")],
            [InlineKeyboardButton(text="⚖️ Записать вес", callback_data="weight_log")]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
    
    def get_anime_universe(self, level: int) -> str:
        """Get anime universe based on level"""
        if level <= 5:
            return "Solo Leveling"
        elif level <= 10:
            return "Tower of God"
        elif level <= 15:
            return "Wind Breaker"
        elif level <= 20:
            return "Kengan Ashura"
        elif level <= 25:
            return "Lookism"
        elif level <= 30:
            return "Haikyuu"
        else:
            return "Run with the Wind"
    
    def get_asthma_emoji(self, control_level: int) -> str:
        """Get asthma emoji based on control level"""
        if control_level >= 4:
            return "😊"
        elif control_level == 3:
            return "😐"
        else:
            return "😷"
    
    async def daily_quests(self, message: types.Message):
        user_id = message.from_user.id
        
        quest_text = "📋 <b>Ежедневные квесты</b>\n\n"
        quest_text += "Выбери категорию заданий:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💪 Фитнес и здоровье", callback_data="quest_category_fitness")],
            [InlineKeyboardButton(text="🧠 Обучение и развитие", callback_data="quest_category_learning")],
            [InlineKeyboardButton(text="🌸 Уход за собой", callback_data="quest_category_selfcare")],
            [InlineKeyboardButton(text="🎯 Личные привычки", callback_data="quest_category_habits")]
        ])
        
        await message.answer(quest_text, reply_markup=keyboard)
    
    async def show_fitness_quests(self, message):
        """Show fitness and health related quests"""
        quest_text = "💪 <b>Фитнес и здоровье</b>\n\n"
        quest_text += "Выбери задание:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏃 15-минутная зарядка (+30 EXP)", callback_data="quest_morning_workout")],
            [InlineKeyboardButton(text="🧘 10 минут растяжки (+20 EXP)", callback_data="quest_stretching")],
            [InlineKeyboardButton(text="💧 Выпить 8 стаканов воды (+15 EXP)", callback_data="quest_water")],
            [InlineKeyboardButton(text="🚶 5000 шагов (+25 EXP)", callback_data="quest_steps")],
            [InlineKeyboardButton(text="🔙 К категориям", callback_data="refresh_quests")]
        ])
        
        await message.answer(quest_text, reply_markup=keyboard)
    
    async def show_learning_quests(self, message):
        """Show learning and development quests"""
        quest_text = "🧠 <b>Обучение и развитие</b>\n\n"
        quest_text += "Выбери задание:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 30 минут английского (+40 EXP)", callback_data="quest_english")],
            [InlineKeyboardButton(text="📖 Прочитать 10 страниц книги (+25 EXP)", callback_data="quest_reading")],
            [InlineKeyboardButton(text="🎧 Смотреть образовательное видео (+20 EXP)", callback_data="quest_video")],
            [InlineKeyboardButton(text="✍️ Написать дневниковую запись (+15 EXP)", callback_data="quest_journal")],
            [InlineKeyboardButton(text="🔙 К категориям", callback_data="refresh_quests")]
        ])
        
        await message.answer(quest_text, reply_markup=keyboard)
    
    async def show_selfcare_quests(self, message):
        """Show self-care and grooming quests"""
        quest_text = "🌸 <b>Уход за собой</b>\n\n"
        quest_text += "Выбери задание:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧴 Утренний уход за кожей (+15 EXP)", callback_data="skin_care_morning")],
            [InlineKeyboardButton(text="🌙 Вечерний уход за кожей (+15 EXP)", callback_data="skin_care_evening")],
            [InlineKeyboardButton(text="💇 Уход за волосами (+20 EXP)", callback_data="quest_hair_care")],
            [InlineKeyboardButton(text="🧼 Принять душ/ванну (+10 EXP)", callback_data="quest_shower")],
            [InlineKeyboardButton(text="🔙 К категориям", callback_data="refresh_quests")]
        ])
        
        await message.answer(quest_text, reply_markup=keyboard)
    
    async def show_habits_quests(self, message):
        """Show personal habit quests"""
        quest_text = "🎯 <b>Личные привычки</b>\n\n"
        quest_text += "Выбери задание:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😴 Лечь спать до 23:00 (+20 EXP)", callback_data="quest_early_sleep")],
            [InlineKeyboardButton(text="📱 Без телефона за час до сна (+15 EXP)", callback_data="quest_no_phone")],
            [InlineKeyboardButton(text="🧹 Убраться в комнате (+25 EXP)", callback_data="quest_cleaning")],
            [InlineKeyboardButton(text="🍏 Съесть фрукт/овощ (+10 EXP)", callback_data="quest_healthy_food")],
            [InlineKeyboardButton(text="🔙 К категориям", callback_data="refresh_quests")]
        ])
        
        await message.answer(quest_text, reply_markup=keyboard)
    
    async def workout_menu(self, message: types.Message):
        """Show workout menu"""
        user_id = message.from_user.id
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT level, anime_universe FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        user_level = result[0] if result else 1
        user_universe = result[1] if result else "Solo Leveling"
        
        workout_text = f"""
⚔️ <b>Меню тренировок</b>

🎯 <b>Твой уровень:</b> {user_level}
🌌 <b>Вселенная:</b> {user_universe}

💪 <b>Доступные ранги:</b>
E-rank: Новички
D-rank: Любители
C-rank: Опытные
B-rank: Эксперты

Выбери вселенную для тренировок:
        """
        
        universe_buttons = []
        universes = ["solo", "tower", "wind", "kengan", "lookism", "haikyuu", "run"]
        universe_names = ["⚔️ Solo Leveling", "🗼 Tower of God", "🌪️ Wind Breaker", 
                         "🥊 Kengan Ashura", "💪 Lookism", "🏐 Haikyuu", "🏃 Run with the Wind"]
        
        for i, (universe, name) in enumerate(zip(universes, universe_names)):
            if i % 2 == 0:
                universe_buttons.append([InlineKeyboardButton(text=name, callback_data=f"workout_universe_{universe}")])
            else:
                universe_buttons[-1].append(InlineKeyboardButton(text=name, callback_data=f"workout_universe_{universe}"))
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=universe_buttons)
        
        await message.answer(workout_text, reply_markup=keyboard)
    
    async def asthma_control(self, message: types.Message):
        """Show asthma control menu"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="😊 Отлично (5/5)", callback_data="asthma_5")],
            [InlineKeyboardButton(text="🙂 Хорошо (4/5)", callback_data="asthma_4")],
            [InlineKeyboardButton(text="😐 Нормально (3/5)", callback_data="asthma_3")],
            [InlineKeyboardButton(text="😕 Плохо (2/5)", callback_data="asthma_2")],
            [InlineKeyboardButton(text="😢 Очень плохо (1/5)", callback_data="asthma_1")]
        ])
        
        asthma_text = """
💨 <b>Контроль астмы</b>

Оцени свое самочувствие:

😊 Отлично - нет симптомов
🙂 Хорошо - легкие симптомы
😐 Нормально - умеренные симптомы
😕 Плохо - сильные симптомы
😢 Очень плохо - очень сильные симптомы

Выбери свой текущий статус:
        """
        
        await message.answer(asthma_text, reply_markup=keyboard)
    
    async def nutrition_menu(self, message: types.Message):
        """Show nutrition menu"""
        user_id = message.from_user.id
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT weight FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        weight = result[0] if result else None
        
        nutrition_text = f"""
🍽️ <b>План питания</b>

⚖️ <b>Твой вес:</b> {weight if weight else "Не указан"} кг

📋 <b>Рекомендации:</b>
• Пей воду перед едой
• Ешь овощи в большом количестве
• Белок в каждом приеме пищи
• Углеводы до 14:00
• Никаких перекусов после 19:00
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💧 Выпить стакан воды", callback_data="water_add")],
            [InlineKeyboardButton(text="⚖️ Записать вес", callback_data="weight_log")],
            [InlineKeyboardButton(text="📊 Продукты для похудения", callback_data="food_list")]
        ])
        
        await message.answer(nutrition_text, reply_markup=keyboard)
    
    async def english_menu(self, message: types.Message):
        """Show English learning menu"""
        user_id = message.from_user.id
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            await message.answer("Сначала зарегистрируйся! /start")
            return
        
        cursor.execute("""
            SELECT english_level, english_exp, english_level_progress 
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        current_level = result[0] if result else "A0"
        current_exp = result[1] if result else 0
        level_progress = result[2] if result else 0
        
        # Get level requirements
        requirements = self.get_english_level_requirements(current_level)
        exp_needed = requirements.get("exp_needed", 100)
        
        # Calculate progress
        progress_percentage = (current_exp / exp_needed) * 100 if exp_needed > 0 else 0
        progress_bar = "█" * int(progress_percentage // 10) + "░" * (10 - int(progress_percentage // 10))
        
        english_text = f"""
📚 <b>Изучение английского</b>

🏆 <b>Текущий уровень:</b> {current_level}
⭐ EXP: {current_exp}/{exp_needed} [{progress_bar}] ({progress_percentage:.1f}%)

📝 <b>Требования для {current_level}:</b>
{requirements.get('description', '')}

🎯 <b>Доступные задания:</b>
        """
        
        # Add activity buttons
        keyboard_buttons = []
        
        # Memrise
        keyboard_buttons.append([
            InlineKeyboardButton(text="📱 Memrise", callback_data="eng_memrise")
        ])
        
        # Listening
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎧 Listening", callback_data="eng_listening")
        ])
        
        # Speaking
        keyboard_buttons.append([
            InlineKeyboardButton(text="🗣️ Speaking", callback_data="eng_speaking")
        ])
        
        # Reading
        keyboard_buttons.append([
            InlineKeyboardButton(text="📖 Reading", callback_data="eng_reading")
        ])
        
        # Writing
        keyboard_buttons.append([
            InlineKeyboardButton(text="✍️ Writing", callback_data="eng_writing")
        ])
        
        # Test button if available
        next_level = self.get_next_english_level(current_level)
        can_test, test_reason = self.can_take_english_test(user_id, next_level)
        
        if next_level and can_test:
            keyboard_buttons.append([
                InlineKeyboardButton(text=f"🎯 Тест на {next_level}", callback_data=f"english_test_{next_level}")
            ])
        elif next_level:
            keyboard_buttons.append([
                InlineKeyboardButton(text=f"🚫 Тест на {next_level} ({test_reason})", callback_data="test_info")
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(english_text, reply_markup=keyboard)
    
    def get_english_level_requirements(self, level: str) -> dict:
        """Get requirements for English level"""
        requirements = {
            "A0": {
                "exp_needed": 100,
                "description": "Базовые фразы, алфавит, цифры"
            },
            "A1": {
                "exp_needed": 200,
                "description": "Простые предложения, повседневные ситуации"
            },
            "A2": {
                "exp_needed": 300,
                "description": "Базовая грамматика, разговорные темы"
            },
            "B1": {
                "exp_needed": 400,
                "description": "Сложные конструкции, абстрактные темы"
            },
            "B2": {
                "exp_needed": 500,
                "description": "Свободное общение, профессиональные темы"
            },
            "C1": {
                "exp_needed": 600,
                "description": "Продвинутая грамматика, академический английский"
            },
            "C2": {
                "exp_needed": 800,
                "description": "Уровень носителя, сложная лексика"
            }
        }
        return requirements.get(level, requirements["A0"])
    
    def get_next_english_level(self, current_level: str) -> str:
        """Get next English level"""
        levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
        try:
            index = levels.index(current_level)
            return levels[index + 1] if index < len(levels) - 1 else None
        except ValueError:
            return "A1"
    
    def can_take_english_test(self, user_id: int, target_level: str) -> tuple:
        """Check if user can take English test"""
        if not target_level:
            return False, "Нет следующего уровня"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT english_level, english_exp, last_english_test_date, english_test_attempts
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return False, "Пройдите начальный уровень"
        
        current_level, english_exp, last_test_date, test_attempts = result
        
        # Check if user has enough experience
        requirements = self.get_english_level_requirements(current_level)
        if english_exp < requirements["exp_needed"]:
            return False, f"Нужно {requirements['exp_needed']} EXP"
        
        # Check if 24 hours passed since last test
        if last_test_date:
            last_test = datetime.strptime(last_test_date, "%Y-%m-%d").date()
            if (date.today() - last_test).days < 1:
                return False, "Можно сдавать раз в день"
        
        return True, "Можно сдавать тест"
    
    async def callback_handler(self, callback: types.CallbackQuery):
        """Handle callback queries"""
        action = callback.data
        user_id = callback.from_user.id
        
        # Main menu handler (moved to top)
        if action == "return_main_menu":
            await self.main_menu(callback.message)
            await callback.answer()
        
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
        elif action.startswith("asthma_"):
            rating = int(action.split("_")[1])
            user_id = callback.from_user.id
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET asthma_control = ?, last_activity = ?
                WHERE user_id = ?
            """, (rating, date.today(), user_id))
            self.conn.commit()
            
            # Add EXP for asthma tracking
            await self.add_exp(user_id, 5, "Контроль астмы")
            
            # Provide recommendations based on rating
            if rating <= 2:
                text = "😷 <b>Рекомендации:</b>\n"
                text += "• Проконсультируйся с врачом\n"
                text += "• Используй ингалятор при необходимости\n"
                text += "• Избегай триггеров\n"
                text += "• Легкие тренировки только\n"
            elif rating == 3:
                text = "🟡 <b>Рекомендации:</b>\n"
                text += "• Тренировки до D-rank\n"
                text += "• Контролируй дыхание\n"
            else:
                text = "✅ <b>Отличное самочувствие!</b>\n"
                text += "• Можно все ранги тренировок\n"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            
            await callback.message.answer(text, reply_markup=keyboard)
        
        # Quest completion handlers
        elif action == "quest_morning_workout":
            await self.add_exp(callback.from_user.id, 30, "Утренняя зарядка")
            await callback.message.answer(
                "✅ <b>Зарядка выполнена!</b> +30 EXP\n\n"
                "🌅 Отличное начало дня!\n"
                "💪 Ты стал сильнее!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_stretching":
            await self.add_exp(callback.from_user.id, 20, "Растяжка")
            await callback.message.answer(
                "✅ <b>Растяжка выполнена!</b> +20 EXP\n\n"
                "🧘 Тело стало более гибким!\n"
                "🌿 Отлично для здоровья позвоночника!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_steps":
            await self.add_exp(callback.from_user.id, 25, "5000 шагов")
            await callback.message.answer(
                "✅ <b>5000 шагов пройдено!</b> +25 EXP\n\n"
                "🚶 Отличная активность!\n"
                "💔 Сердце скажет спасибо!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_english":
            await self.add_exp(callback.from_user.id, 40, "Английский язык")
            await callback.message.answer(
                "✅ <b>Английский изучен!</b> +40 EXP\n\n"
                "📚 Knowledge is power!\n"
                "🌍 Ты стал ближе к миру!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📚 Английский", callback_data="english_menu")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_reading":
            await self.add_exp(callback.from_user.id, 25, "Чтение книги")
            await callback.message.answer(
                "✅ <b>10 страниц прочитано!</b> +25 EXP\n\n"
                "📖 Книга - лучший друг!\n"
                "🧠 Мозг стал острее!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_video":
            await self.add_exp(callback.from_user.id, 20, "Образовательное видео")
            await callback.message.answer(
                "✅ <b>Видео просмотрено!</b> +20 EXP\n\n"
                "🎧 Новые знания получены!\n"
                "💡 Продолжай развиваться!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_journal":
            await self.add_exp(callback.from_user.id, 15, "Дневниковая запись")
            await callback.message.answer(
                "✅ <b>Запись в дневнике сделана!</b> +15 EXP\n\n"
                "✍️ Мысли выражены!\n"
                "🧘 Психологическое здоровье важно!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_hair_care":
            await self.add_exp(callback.from_user.id, 20, "Уход за волосами")
            await callback.message.answer(
                "✅ <b>Уход за волосами выполнен!</b> +20 EXP\n\n"
                "💇 Волосы скажут спасибо!\n"
                "✨ Ты прекрасен/прекрасна!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_shower":
            await self.add_exp(callback.from_user.id, 10, "Душ/ванна")
            await callback.message.answer(
                "✅ <b>Гигиена выполнена!</b> +10 EXP\n\n"
                "🧼 Чистота - залог здоровья!\n"
                "💦 Свежесть и бодрость!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_early_sleep":
            await self.add_exp(callback.from_user.id, 20, "Ранний сон")
            await callback.message.answer(
                "✅ <b>Ранний сон!</b> +20 EXP\n\n"
                "😴 Сладких снов!\n"
                "🌙 Восстановление началось!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_no_phone":
            await self.add_exp(callback.from_user.id, 15, "Без телефона перед сном")
            await callback.message.answer(
                "✅ <b>Цифровой детокс!</b> +15 EXP\n\n"
                "📱 Глаза отдохнули!\n"
                "🧘 Мозг готов ко сну!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_cleaning":
            await self.add_exp(callback.from_user.id, 25, "Уборка")
            await callback.message.answer(
                "✅ <b>Комната убрана!</b> +25 EXP\n\n"
                "🧹 Чистота и порядок!\n"
                "🏠 Дом - крепость!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action == "quest_healthy_food":
            await self.add_exp(callback.from_user.id, 10, "Здоровая пища")
            await callback.message.answer(
                "✅ <b>Полезная еда съедена!</b> +10 EXP\n\n"
                "🍏 Витамины получены!\n"
                "💪 Энергия на весь день!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
            
        elif action.startswith("meal_"):
            meal_type = action.split("_")[1]
            meal_names = {"breakfast": "завтрак", "lunch": "обед", "dinner": "ужин"}
            meal_name = meal_names.get(meal_type, "прием пищи")
            
            await self.add_exp(user_id, 15, f"Выполнен {meal_name}")
            await callback.message.answer(
                f"✅ {meal_name.capitalize()} выполнен! +15 EXP",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🍽️ Питание", callback_data="nutrition_menu")]
                ])
            )
        
        elif action == "food_list":
            low_cal_foods = self.get_low_calorie_foods()
            
            food_text = "🥗 Продукты для похудения\n\n"
            
            for category, foods in low_cal_foods.items():
                food_text += f"📋 {category}:\n"
                for food in foods:
                    food_text += f"  • {food}\n"
                food_text += "\n"
            
            food_text += """
💡 Как использовать:
• Составляй рацион из этих продуктов
• Белки + овощи = идеальное сочетание
• Углеводы только на завтрак и обед
• Фрукты как перекусы до 16:00
• Овощи можно есть в неограниченном количестве
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Питание", callback_data="nutrition_menu")]
            ])
            
            await callback.message.answer(food_text, reply_markup=keyboard)
        
        elif action == "menu_week":
            weekly_menu = self.generate_weekly_menu()
            
            week_text = "Меню на неделю\n\n"
            
            for day, meals in weekly_menu.items():
                week_text += f"📅 {day}:\n"
                week_text += f"Завтрак: {meals['breakfast']}\n"
                week_text += f"Обед: {meals['lunch']}\n"
                week_text += f"Ужин: {meals['dinner']}\n"
                week_text += f"Перекус: {meals['snack']}\n\n"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Сегодняшнее меню", callback_data="nutrition_menu")]
            ])
            
            await callback.message.answer(week_text, reply_markup=keyboard)
            
        elif action == "weight_log":
            await callback.message.answer(
                "⚖️ <b>Запись веса</b>\n\n"
                "Введи свой вес в килограммах (например: 65.5)\n"
                "Это поможет отслеживать прогресс похудения!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
            )
        
        elif action == "nutrition_menu":
            await self.nutrition_menu(callback.message)
        
        # English handlers
        elif action == "english_menu":
            await self.english_menu(callback.message)
        
        elif action.startswith("eng_"):
            activity_type = action.split("_")[1]
            activity_map = {
                "memrise": ("Memrise", "слов", 5),
                "listening": ("Listening", "минут аудирования", 2),
                "speaking": ("Speaking", "минут разговора", 3),
                "reading": ("Reading", "страниц чтения", 1),
                "writing": ("Writing", "минут письма", 2)
            }
            
            activity_name, unit, exp_rate = activity_map.get(activity_type, ("Activity", "единиц", 1))
            
            await callback.message.answer(
                f"📚 <b>{activity_name}</b>\n\n"
                f"Сколько {unit} ты выполнил(а)?\n"
                f"🎁 {exp_rate} EXP за каждую {unit.rstrip('ы')}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"10 {unit}", callback_data=f"log_{activity_type}_10")],
                    [InlineKeyboardButton(text=f"20 {unit}", callback_data=f"log_{activity_type}_20")],
                    [InlineKeyboardButton(text=f"30 {unit}", callback_data=f"log_{activity_type}_30")],
                    [InlineKeyboardButton(text=f"50 {unit}", callback_data=f"log_{activity_type}_50")]
                ])
            )
            
        elif action.startswith("log_"):
            parts = action.split("_")
            activity_type = parts[1]
            amount = int(parts[2])
            
            activity_map = {
                "memrise": 5, "listening": 2, "speaking": 3,
                "reading": 1, "writing": 2
            }
            
            exp_rate = activity_map.get(activity_type, 1)
            total_exp = amount * exp_rate
            
            await self.add_exp(user_id, total_exp, f"Английский: {activity_type}")
            
            await callback.message.answer(
                f"✅ Отлично! +{total_exp} EXP за {amount} единиц!\n"
                f"🎯 Продолжай в том же духе!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📚 Английский", callback_data="english_menu")]
                ])
            )
            await callback.answer()
        
        elif action == "water_add":
            cursor = self.conn.cursor()
            
            # Check if nutrition plan exists for today
            cursor.execute("""
                SELECT id FROM nutrition_plans 
                WHERE user_id = ? AND date = ?
            """, (user_id, date.today()))
            
            plan_exists = cursor.fetchone()
            
            if not plan_exists:
                # Create new nutrition plan for today
                cursor.execute("""
                    INSERT INTO nutrition_plans (user_id, date, water_consumed)
                    VALUES (?, ?, 1)
                """, (user_id, date.today()))
            else:
                # Update water consumption
                cursor.execute("""
                    UPDATE nutrition_plans 
                    SET water_consumed = water_consumed + 1
                    WHERE user_id = ? AND date = ?
                """, (user_id, date.today()))
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
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
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
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Статус", callback_data="refresh_stats")]
                ])
            )
            await callback.answer()
        
        await callback.answer()
    
    async def complete_daily_quest(self, user_id: int, quest_title: str):
        """Mark a daily quest as completed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE daily_quests 
            SET completed = 1 
            WHERE user_id = ? AND title = ? AND date = ?
        """, (user_id, quest_title, date.today()))
        self.conn.commit()

    async def add_exp(self, user_id: int, exp_amount: int, reason: str = ""):
        """Add experience to user and handle level up"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT level, exp, exp_to_next FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            level, current_exp, exp_to_next = user_data
            new_exp = current_exp + exp_amount
            
            # Check for level up
            if new_exp >= exp_to_next:
                new_level = level + 1
                new_exp_to_next = exp_to_next + (50 * new_level)  # Increase EXP requirement
                
                # Update user level and stats
                cursor.execute("""
                    UPDATE users 
                    SET level = ?, exp = ?, exp_to_next = ?, last_activity = ?
                    WHERE user_id = ?
                """, (new_level, new_exp, new_exp_to_next, date.today(), user_id))
                
                # Increase stats
                power_increase = random.uniform(1.0, 3.0)
                analysis_increase = random.uniform(1.0, 3.0)
                endurance_increase = random.uniform(1.0, 3.0)
                speed_increase = random.uniform(1.0, 3.0)
                
                cursor.execute("""
                    UPDATE users 
                    SET power = power + ?, analysis = analysis + ?, 
                       endurance = endurance + ?, speed = speed + ?
                    WHERE user_id = ?
                """, (power_increase, analysis_increase, endurance_increase, speed_increase, user_id))
                
                self.conn.commit()
                
                # Send level up notification
                await self.send_level_up_notification(user_id, new_level, new_exp_to_next)
            else:
                # Just update EXP
                cursor.execute("""
                    UPDATE users 
                    SET exp = ?, last_activity = ?
                    WHERE user_id = ?
                """, (new_exp, date.today(), user_id))
                
                self.conn.commit()
            
            # Log progress
            cursor.execute("""
                INSERT INTO english_progress (user_id, activity_type, amount, exp_gained, date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, reason, 1, exp_amount, date.today()))
            self.conn.commit()
    
    async def send_level_up_notification(self, user_id: int, new_level: int, exp_to_next: int):
        """Send level up notification"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT anime_universe FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        universe = result[0] if result else "Solo Leveling"
        
        rank_up_text = f"""
⚡️ <b>【LEVEL UP!】</b> ⚡️

🎯 <b>Новый уровень: {new_level}</b>
🌌 <b>Вселенная: {universe}</b>

📈 <b>Статы увеличены:</b>
• Сила +{random.uniform(1.0, 3.0):.1f}
• Анализ +{random.uniform(1.0, 3.0):.1f}
• Выносливость +{random.uniform(1.0, 3.0):.1f}
• Скорость +{random.uniform(1.0, 3.0):.1f}

⚔️ <b>【NEW ABILITIES UNLOCKED】</b>
• Доступ к новым тренировкам
• Увеличенная награда EXP
• Новый доступ к рангам

🌟 <b>【SOLO LEVELING SYSTEM】</b>
"Сила не дается, она зарабатывается кровью и потом"

🚀 <b>Продолжай свой путь к вершине!</b>
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Новые тренировки", callback_data="workout_menu")],
            [InlineKeyboardButton(text="📊 Проверить статус", callback_data="refresh_stats")]
        ])
        
        try:
            await self.bot.send_message(user_id, rank_up_text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Failed to send level up notification: {e}")
    
    def get_low_calorie_foods(self) -> dict:
        """Get list of low-calorie foods for weight loss"""
        return {
            "🥗 Белки": {
                "Куриная грудка (100г) - 165 ккал",
                "Индейка (100г) - 145 ккал", 
                "Яйца (2шт) - 140 ккал",
                "Творог 2% (100г) - 98 ккал",
                "Рыба (100г) - 120 ккал"
            },
            "🥬 Овощи": {
                "Огурцы (100г) - 15 ккал",
                "Помидоры (100г) - 18 ккал",
                "Брокколи (100г) - 34 ккал",
                "Шпинат (100г) - 23 ккал",
                "Морковь (100г) - 41 ккал"
            },
            "🍎 Фрукты": {
                "Яблоки (100г) - 52 ккал",
                "Апельсины (100г) - 47 ккал",
                "Киви (100г) - 61 ккал",
                "Грейпфрут (100г) - 42 ккал",
                "Ягоды (100г) - 32 ккал"
            },
            "🌾 Углеводы": {
                "Овсянка (100г) - 68 ккал",
                "Гречка (100г) - 132 ккал",
                "Бурый рис (100г) - 111 ккал",
                "Цельнозерновой хлеб (1шт) - 75 ккал"
            }
        }
    
    def generate_weekly_menu(self) -> dict:
        """Generate weekly menu plan"""
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        
        breakfast_options = [
            "Овсянка с ягодами и орехами",
            "Яичница с овощами",
            "Творог с фруктами",
            "Гречка с молоком"
        ]
        
        lunch_options = [
            "Куриная грудка с рисом и салатом",
            "Суп с овощами и цельнозерновым хлебом",
            "Запеченная рыба с овощами",
            "Индейка с гречкой и огурцами"
        ]
        
        dinner_options = [
            "Запеченная курица с овощами",
            "Творог с зеленью",
            "Омлет с шпинатом",
            "Рыба на гриле с салатом"
        ]
        
        snack_options = [
            "Яблоко или грейпфрут",
            "Горсть орехов (30г)",
            "Стакан кефира",
            "Морковь с хумусом"
        ]
        
        weekly_menu = {}
        
        for i, day in enumerate(days):
            weekly_menu[day] = {
                "breakfast": breakfast_options[i % len(breakfast_options)],
                "lunch": lunch_options[i % len(lunch_options)],
                "dinner": dinner_options[i % len(dinner_options)],
                "snack": snack_options[i % len(snack_options)]
            }
        
        return weekly_menu
    
    def get_available_ranks(self, asthma_level: int) -> list:
        """Get available workout ranks based on asthma level"""
        if asthma_level >= 4:
            return ["E", "D", "C", "B", "A", "S"]
        elif asthma_level == 3:
            return ["E", "D", "C"]
        else:
            return ["E", "D"]
    
    def get_workout_library(self) -> dict:
        """Get workout library with different exercises"""
        return {
            "solo": {
                "E": {
                    "title": "E-rank: Новичок Sung Jinwoo",
                    "description": "Начальный уровень для самых слабых охотников",
                    "exp": 20,
                    "exercises": [
                        {"name": "Отжимания от стены", "duration": "3 подхода по 10 раз", "quote": "Даже самый слабый может стать сильным"},
                        {"name": "Приседания без веса", "duration": "3 подхода по 15 раз", "quote": "Каждое повторение делает тебя сильнее"},
                        {"name": "Планка", "duration": "3 подхода по 20 секунд", "quote": "Стойкость - ключ к силе"}
                    ],
                    "warnings": [
                        "🌬️ Дыши ровно и глубоко",
                        "⚠️ При затруднении дыхания немедленно остановись",
                        "💧 Пей достаточно воды"
                    ]
                },
                "D": {
                    "title": "D-rank: Опытный боец",
                    "description": "Средний уровень для регулярных тренировок",
                    "exp": 30,
                    "exercises": [
                        {"name": "Отжимания от пола", "duration": "3 подхода по 8 раз", "quote": "Тело помнит каждое усилие"},
                        {"name": "Выпады", "duration": "3 подхода по 10 раз на ногу", "quote": "Шаг за шагом к силе"},
                        {"name": "Подтягивания (если есть турник)", "duration": "3 подхода по макс", "quote": "Поднимай себя выше"}
                    ],
                    "warnings": [
                        "🌬️ Контролируй дыхание между подходами",
                        "⚠️ Не делай резких движений",
                        "💧 Отдыхай 60 секунд между подходами"
                    ]
                }
            }
        }
    
    async def run(self):
        """Start the bot"""
        try:
            await self.dp.start_polling()
        except Exception as e:
            logger.error(f"Bot error: {e}")

# Запуск бота
if __name__ == "__main__":
    if not TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не найден")
    else:
        bot = SimpleRaidBot(TOKEN)
        print("🚀 Solo Raid Bot запускается...")
        asyncio.run(bot.run())

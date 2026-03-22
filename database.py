"""
DATABASE LAYER - Слой работы с базой данных
============================================

Этот модуль отвечает за:
- Подключение к SQLite
- Создание и обновление таблиц
- Выполнение SQL запросов

Все остальные слои работают с базой данных через этот модуль.
"""

import sqlite3
import logging
from constants import Config, Emoji

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Класс для управления базой данных SQLite.
    
    Отвечает за создание таблиц, подключение и выполнение запросов.
    Используется сервисным слоем для работы с данными.
    """
    
    def __init__(self, db_name: str = Config.DATABASE_NAME):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_name: Имя файла базы данных (по умолчанию из Config)
        """
        self.conn = sqlite3.connect(db_name)
        self.init_tables()
        logger.info(f"{Emoji.SUCCESS} Подключение к базе данных установлено")
        
    def init_tables(self):
        """
        Создание всех необходимых таблиц базы данных.
        
        Вызывается при инициализации. Если таблицы уже существуют,
        они не будут пересозданы (CREATE TABLE IF NOT EXISTS).
        """
        cursor = self.conn.cursor()
        
        # Таблица пользователей - основная таблица с прогрессом
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
                is_admin BOOLEAN DEFAULT 0,
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
        
        # Таблица прогресса по английскому языку
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
        
        # Таблица инвентаря пользователя
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
                from_level TEXT,
                to_level TEXT,
                score INTEGER,
                passed BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        self.conn.commit()
        logger.info(f"{Emoji.SUCCESS} Таблицы базы данных инициализированы")
    
    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором."""
        try:
            cursor = self.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else False
        except Exception:
            return False
    
    def set_admin(self, user_id: int, is_admin: bool = True):
        """Назначить или снять права администратора."""
        self.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (1 if is_admin else 0, user_id))
        self.commit()
    
    def execute(self, query: str, params: tuple = ()):
        """
        Выполнить SQL запрос с параметрами.
        
        Args:
            query: SQL запрос
            params: Параметры для запроса
            
        Returns:
            sqlite3.Cursor: Курсор для получения результатов
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def commit(self):
        """Подтвердить изменения в базе данных."""
        self.conn.commit()

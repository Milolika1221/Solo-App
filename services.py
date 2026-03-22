"""
SERVICE LAYER - Слой бизнес-логики
==================================

Этот модуль содержит бизнес-логику приложения:
- Управление пользователями и опытом
- Уровни английского языка
- Квесты и тренировки
- Расчет наград и прогресса

Сервисы работают с базой данных через DatabaseManager.
"""

import logging
from datetime import date
from database import DatabaseManager
from constants import (
    Emoji, Config, QUEST_REWARDS,
    ENGLISH_LEVELS, ENGLISH_LEVEL_ORDER,
    RANK_REQUIREMENTS, WORKOUT_LIBRARY,
    ENGLISH_DAILY_TASKS, ENGLISH_DAILY_SETS, ENGLISH_LEVEL_TO_SET
)

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для работы с пользователями.
    
    Управляет:
    - Опытом и уровнями
    - Характеристиками (сила, анализ, выносливость, скорость)
    - Профилем пользователя
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Инициализация сервиса.
        
        Args:
            db: Экземпляр DatabaseManager для работы с базой
        """
        self.db = db
    
    def add_exp(self, user_id: int, amount: int, reason: str = "") -> tuple:
        """
        Добавляет опыт пользователю и проверяет повышение уровня.
        
        При повышении уровня автоматически увеличивает характеристики:
        - Боевая мощь: +2.0
        - Анализ: +1.5
        - Выносливость: +2.5
        - Скорость: +1.0
        
        Args:
            user_id: ID пользователя Telegram
            amount: Количество опыта для добавления
            reason: Причина начисления (для логирования)
            
        Returns:
            tuple: (новый_уровень, повышение_уровня_было)
        """
        cursor = self.db.execute(
            "SELECT level, exp, exp_to_next, power, analysis, endurance, speed FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None, False
        
        level, exp, exp_to_next, power, analysis, endurance, speed = result
        new_exp = exp + amount
        level_up = False
        
        # Проверяем повышение уровня
        while new_exp >= exp_to_next and level < Config.MAX_LEVEL:
            new_exp -= exp_to_next
            level += 1
            exp_to_next = int(exp_to_next * Config.EXP_MULTIPLIER)
            level_up = True
            
            # Увеличиваем характеристики при повышении уровня
            power += 2.0
            analysis += 1.5
            endurance += 2.5
            speed += 1.0
        
        # Обновляем данные пользователя
        self.db.execute("""
            UPDATE users 
            SET level = ?, exp = ?, exp_to_next = ?, 
                power = ?, analysis = ?, endurance = ?, speed = ?
            WHERE user_id = ?
        """, (level, new_exp, exp_to_next, power, analysis, endurance, speed, user_id))
        
        self.db.commit()
        
        if level_up:
            logger.info(f"{Emoji.TROPHY} Пользователь {user_id} повысил уровень до {level}!")
        
        return level, level_up
    
    def get_user_stats(self, user_id: int) -> dict:
        """
        Получает полную статистику пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Словарь со всеми характеристиками пользователя или None
        """
        cursor = self.db.execute("""
            SELECT level, exp, exp_to_next, power, analysis, endurance, speed,
                   skin_health, english_progress, streak, weight, target_weight,
                   english_level, english_exp
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        return {
            "level": result[0],
            "exp": result[1],
            "exp_to_next": result[2],
            "power": result[3],
            "analysis": result[4],
            "endurance": result[5],
            "speed": result[6],
            "skin_health": result[7] if len(result) > 7 else Config.DEFAULT_SKIN_HEALTH,
            "english_progress": result[8] if len(result) > 8 else 0,
            "streak": result[9] if len(result) > 9 else 0,
            "weight": result[10] if len(result) > 10 else None,
            "target_weight": result[11] if len(result) > 11 else None,
            "english_level": result[12] if len(result) > 12 else Config.DEFAULT_ENGLISH_LEVEL,
            "english_exp": result[13] if len(result) > 13 else Config.DEFAULT_ENGLISH_EXP
        }
    
    def create_user(self, user_id: int) -> bool:
        """
        Создает нового пользователя в базе данных.
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            bool: True если пользователь создан или уже существует
        """
        try:
            self.db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка создания пользователя: {e}")
            return False
    
    def is_registered(self, user_id: int) -> bool:
        """
        Проверяет, завершил ли пользователь регистрацию.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если регистрация завершена
        """
        cursor = self.db.execute(
            "SELECT registration_completed FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result is not None and result[0] == 1


class EnglishService:
    """
    Сервис для работы с английским языком.
    
    Управляет:
    - Уровнями английского (A0 → C2)
    - Требованиями для повышения уровня
    - Тестами и заданиями
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Инициализация сервиса.
        
        Args:
            db: Экземпляр DatabaseManager
        """
        self.db = db
    
    def get_english_rank_title(self, level: str) -> str:
        """
        Возвращает название ранга для уровня английского.
        
        Args:
            level: Уровень английского (A0-C2)
            
        Returns:
            str: Название ранга с эмодзи
        """
        level_data = ENGLISH_LEVELS.get(level, ENGLISH_LEVELS["A0"])
        return level_data["name"]
    
    def get_next_english_level(self, current_level: str) -> str:
        """
        Возвращает следующий уровень английского.
        
        Args:
            current_level: Текущий уровень (A0, A1 и т.д.)
            
        Returns:
            str: Следующий уровень или None если максимальный
        """
        try:
            idx = ENGLISH_LEVEL_ORDER.index(current_level)
            if idx < len(ENGLISH_LEVEL_ORDER) - 1:
                return ENGLISH_LEVEL_ORDER[idx + 1]
        except ValueError:
            pass
        return None
    
    def get_english_level_requirements(self, level: str) -> dict:
        """
        Возвращает требования для уровня английского.
        
        Args:
            level: Уровень английского
            
        Returns:
            dict: Требования для получения уровня
        """
        level_data = ENGLISH_LEVELS.get(level)
        if level_data:
            return {
                "exp_required": level_data["exp_required"],
                "name": level_data["name"],
                "description": level_data["description"]
            }
        return None
    
    def add_english_exp(self, user_id: int, amount: int) -> bool:
        """
        Добавляет опыт по английскому языку.
        
        Args:
            user_id: ID пользователя
            amount: Количество опыта
            
        Returns:
            bool: True если успешно
        """
        try:
            self.db.execute(
                "UPDATE users SET english_exp = english_exp + ? WHERE user_id = ?",
                (amount, user_id)
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка добавления EXP английского: {e}")
            return False
    
    def get_daily_tasks(self, english_level: str) -> list:
        """
        Генерирует ежедневные задания для пользователя.
        
        Выбирает набор заданий в зависимости от уровня.
        Каждый набор покрывает все 5 навыков.
        
        Args:
            english_level: Уровень английского (A0, A1, B1 и т.д.)
            
        Returns:
            list: Список заданий для сегодня
        """
        import random
        
        # Получаем категорию наборов для уровня
        set_category = ENGLISH_LEVEL_TO_SET.get(english_level, "beginner")
        available_sets = ENGLISH_DAILY_SETS.get(set_category, [])
        
        if not available_sets:
            # Если нет наборов, возвращаем базовые задания
            return ["vocabulary", "listening_video", "writing_journal"]
        
        # Выбираем случайный набор заданий
        selected_tasks = random.choice(available_sets)
        
        return selected_tasks
    
    def get_task_info(self, task_key: str) -> dict:
        """
        Возвращает информацию о задании.
        
        Args:
            task_key: Ключ задания (vocabulary, listening_video и т.д.)
            
        Returns:
            dict: Информация о задании
        """
        return ENGLISH_DAILY_TASKS.get(task_key, {})
    
    def format_daily_tasks_text(self, tasks: list, english_level: str, english_exp: int) -> str:
        """
        Форматирует текст с ежедневными заданиями.
        
        Args:
            tasks: Список ключей заданий
            english_level: Уровень английского
            english_exp: Текущий опыт
            
        Returns:
            str: Отформатированный текст
        """
        # Собираем все прокачиваемые навыки
        all_skills = set()
        for task_key in tasks:
            task_info = self.get_task_info(task_key)
            skills = task_info.get("skills", [])
            all_skills.update(skills)
        
        # Формируем текст
        text = f"{Emoji.BOOK} <b>Английский язык</b>\n\n"
        text += f"{Emoji.TARGET} Уровень: {english_level} ({english_exp} EXP)\n\n"
        
        text += f"{Emoji.CLIPBOARD} <b>Задания на сегодня:</b>\n\n"
        
        for i, task_key in enumerate(tasks, 1):
            task_info = self.get_task_info(task_key)
            icon = task_info.get("icon", "📝")
            name = task_info.get("name", "Задание")
            description = task_info.get("description", "")
            exp = task_info.get("exp", 15)
            skills = task_info.get("skills", [])
            
            # Формируем строку навыков
            skills_text = ", ".join(skills) if skills else ""
            
            text += f"{i}. {icon} <b>{name}</b> (+{exp} EXP)\n"
            text += f"   {description}\n"
            text += f"   <i>Навыки: {skills_text}</i>\n\n"
        
        text += f"{Emoji.STAR} <b>Прокачиваемые навыки:</b> {', '.join(sorted(all_skills))}\n"
        text += f"\n{Emoji.INFO} Нажми на задание для отметки выполнения"
        
        return text
    
    def get_skills_progress(self, user_id: int) -> dict:
        """
        Получает прогресс по каждому навыку.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Прогресс по навыкам
        """
        # Получаем данные из таблицы english_progress
        cursor = self.db.execute(
            """
            SELECT activity_type, SUM(amount) as total 
            FROM english_progress 
            WHERE user_id = ? AND date >= date('now', '-30 days')
            GROUP BY activity_type
            """,
            (user_id,)
        )
        
        results = cursor.fetchall()
        
        skills = {
            "vocabulary": 0,
            "listening": 0,
            "speaking": 0,
            "reading": 0,
            "writing": 0,
            "grammar": 0
        }
        
        for activity_type, total in results:
            if activity_type in skills:
                skills[activity_type] = total
        
        return skills


class QuestService:
    """
    Сервис для работы с квестами и тренировками.
    
    Управляет:
    - Системой квестов и наград
    - Тренировками и рангами
    - Доступностью контента по уровню
    """
    
    def __init__(self, db: DatabaseManager):
        """
        Инициализация сервиса.
        
        Args:
            db: Экземпляр DatabaseManager
        """
        self.db = db
    
    def get_quest_reward(self, quest_name: str) -> int:
        """
        Возвращает награду за квест.
        
        Args:
            quest_name: Название квеста
            
        Returns:
            int: Количество EXP (по умолчанию 10)
        """
        quest_key = quest_name.lower().replace(" ", "_")
        return QUEST_REWARDS.get(quest_key, 10)
    
    def get_available_ranks(self, user_level: int) -> list:
        """
        Возвращает доступные ранги тренировок для уровня пользователя.
        
        Ранги открываются по достижении определенного уровня:
        E - 1, D - 10, C - 25, B - 50, A - 75, S - 100
        
        Args:
            user_level: Уровень пользователя
            
        Returns:
            list: Список доступных рангов (например ['E', 'D', 'C'])
        """
        available = []
        for rank, min_level in RANK_REQUIREMENTS.items():
            if user_level >= min_level:
                available.append(rank)
        return available if available else ["E"]
    
    def complete_daily_quest(self, user_id: int, quest_id: int) -> bool:
        """
        Отмечает ежедневный квест как выполненный.
        
        Args:
            user_id: ID пользователя
            quest_id: ID квеста
            
        Returns:
            bool: True если успешно
        """
        try:
            self.db.execute(
                "UPDATE daily_quests SET completed = 1 WHERE quest_id = ? AND user_id = ?",
                (quest_id, user_id)
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"{Emoji.ERROR} Ошибка завершения квеста: {e}")
            return False
    
    def get_workout(self, universe: str, rank: str) -> dict:
        """
        Получает тренировку по вселенной и рангу.
        
        Args:
            universe: Код вселенной (solo, tower, wind, etc.)
            rank: Ранг тренировки (E, D, C, B, A, S)
            
        Returns:
            dict: Данные тренировки или None
        """
        return WORKOUT_LIBRARY.get(universe, {}).get(rank)
    
    def format_workout_text(self, workout: dict) -> str:
        """
        Форматирует текст тренировки для отображения.
        
        Args:
            workout: Данные тренировки
            
        Returns:
            str: Отформатированный текст
        """
        if not workout:
            return f"{Emoji.ERROR} Тренировка не найдена"
        
        text = f"{workout['title']}\n\n"
        text += f"📝 <b>Описание:</b> {workout['description']}\n"
        text += f"⭐ <b>Награда:</b> {workout.get('exp', 20)} EXP\n\n"
        text += f"{Emoji.CLIPBOARD} <b>План тренировки:</b>\n\n"
        
        for i, exercise in enumerate(workout.get("exercises", []), 1):
            text += f"<b>{i}. {exercise['name']}</b> ({exercise['duration']})\n"
            text += f"{exercise.get('details', '')}\n"
            text += f"💬 <i>{exercise.get('quote', '')}</i>\n\n"
        
        warnings = workout.get("warnings", [])
        if warnings:
            text += f"\n{Emoji.WARNING} <b>Важно:</b>\n"
            for warning in warnings:
                text += f"{warning}\n"
        
        text += f"\n{Emoji.INFO} <b>Дыхательная техника:</b> Вдох 4сек - Задержка 2сек - Выдох 6сек\n"
        
        return text

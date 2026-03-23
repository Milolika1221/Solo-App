"""
KEYBOARD LAYER - Слой клавиатур
================================

Этот модуль отвечает за создание всех клавиатур бота:
- ReplyKeyboardMarkup (главное меню)
- InlineKeyboardMarkup (inline кнопки)

Все клавиатуры создаются через статические методы класса KeyboardManager.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from constants import Emoji, KEYBOARD_BUTTONS, ANIME_UNIVERSES


class KeyboardManager:
    """
    Класс для создания и управления клавиатурами бота.
    
    Все методы статические - не требуют создания экземпляра.
    Используют константы из constants.py для текстов и callback_data.
    """
    
    @staticmethod
    def get_main_keyboard() -> ReplyKeyboardMarkup:
        """
        Создает главную клавиатуру бота (ReplyKeyboard).
        
        Структура:
        [Квесты] [Тренировки]
        [Английский] [Статус]
        [Питание]
        
        Returns:
            ReplyKeyboardMarkup: Главная клавиатура
        """
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=KEYBOARD_BUTTONS["quests"]),
                    KeyboardButton(text=KEYBOARD_BUTTONS["workouts"]),
                ],
                [
                    KeyboardButton(text=KEYBOARD_BUTTONS["english"]),
                    KeyboardButton(text=KEYBOARD_BUTTONS["status"]),
                ],
                [
                    KeyboardButton(text=KEYBOARD_BUTTONS["nutrition"]),
                ],
            ],
            resize_keyboard=True
        )
        return keyboard
    
    @staticmethod
    def get_universe_keyboard() -> InlineKeyboardMarkup:
        """
        Создает клавиатуру выбора вселенной аниме (Inline).
        
        Доступные вселенные:
        - Solo Leveling
        - Tower of God
        - Wind Breaker
        - Kengan Ashura
        - Lookism
        - Haikyuu
        - Run with the Wind
        
        Returns:
            InlineKeyboardMarkup: Клавиатура выбора вселенной
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.SWORD} Solo Leveling",
                        callback_data="reg_universe_solo"
                    ),
                    InlineKeyboardButton(
                        text=f"{Emoji.TARGET} Tower of God",
                        callback_data="reg_universe_tower"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.RUNNER} Wind Breaker",
                        callback_data="reg_universe_wind"
                    ),
                    InlineKeyboardButton(
                        text=f"{Emoji.POWER} Kengan Ashura",
                        callback_data="reg_universe_kengan"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.BOOK} Lookism",
                        callback_data="reg_universe_lookism"
                    ),
                    InlineKeyboardButton(
                        text=f"{Emoji.FLASH} Haikyuu",
                        callback_data="reg_universe_haikyuu"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.RUNNER} Run with the Wind",
                        callback_data="reg_universe_run"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_gender_keyboard() -> InlineKeyboardMarkup:
        """
        Создает клавиатуру выбора пола (Inline).
        
        Варианты:
        - Женский
        - Мужской
        - Не указывать
        
        Returns:
            InlineKeyboardMarkup: Клавиатура выбора пола
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="♀️ Женский",
                        callback_data="reg_gender_female"
                    ),
                    InlineKeyboardButton(
                        text="♂️ Мужской",
                        callback_data="reg_gender_male"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="⚪ Не указывать",
                        callback_data="reg_gender_none"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_registration_start_keyboard() -> InlineKeyboardMarkup:
        """
        Клавиатура начала регистрации.
        
        Returns:
            InlineKeyboardMarkup: Кнопки начала регистрации
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.FORWARD} Начать регистрацию",
                        callback_data="reg_continue"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"⚡ Пропустить (базовые настройки)",
                        callback_data="reg_skip"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_skin_type_keyboard() -> InlineKeyboardMarkup:
        """
        Создает клавиатуру выбора типа кожи (Inline).
        
        Варианты:
        - Жирная
        - Сухая
        - Комбинированная
        - Нормальная
        - Проблемная (акне)
        
        Returns:
            InlineKeyboardMarkup: Клавиатура выбора типа кожи
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💧 Жирная",
                        callback_data="reg_skin_oily"
                    ),
                    InlineKeyboardButton(
                        text="🏜️ Сухая",
                        callback_data="reg_skin_dry"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="⚖️ Комбинированная",
                        callback_data="reg_skin_combination"
                    ),
                    InlineKeyboardButton(
                        text="✨ Нормальная",
                        callback_data="reg_skin_normal"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="⚠️ Проблемная (акне)",
                        callback_data="reg_skin_acne"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_quest_categories_keyboard() -> InlineKeyboardMarkup:
        """
        Клавиатура категорий квестов.
        
        Returns:
            InlineKeyboardMarkup: Кнопки категорий
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.POWER} Фитнес",
                        callback_data="quest_category_fitness"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.BOOK} Обучение",
                        callback_data="quest_category_learning"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.SPARKLES} Уход за собой",
                        callback_data="quest_category_selfcare"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_workout_universes_keyboard() -> InlineKeyboardMarkup:
        """
        Клавиатура выбора вселенной для тренировки.
        
        Returns:
            InlineKeyboardMarkup: Кнопки вселенных
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.SWORD} Solo Leveling",
                        callback_data="workout_universe_solo"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.TARGET} Tower of God",
                        callback_data="workout_universe_tower"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.RUNNER} Wind Breaker",
                        callback_data="workout_universe_wind"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_english_level_keyboard() -> InlineKeyboardMarkup:
        """
        Создает клавиатуру выбора уровня английского (Inline).
        
        Варианты:
        - A0 (Beginner)
        - A1 (Elementary) 
        - A2 (Pre-Intermediate)
        - B1 (Intermediate)
        - B2 (Upper-Intermediate)
        - C1 (Advanced)
        - C2 (Proficient)
        
        Returns:
            InlineKeyboardMarkup: Клавиатура выбора уровня английского
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌱 A0 (Beginner)",
                        callback_data="reg_english_a0"
                    ),
                    InlineKeyboardButton(
                        text="🌿 A1 (Elementary)",
                        callback_data="reg_english_a1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🌳 A2 (Pre-Intermediate)",
                        callback_data="reg_english_a2"
                    ),
                    InlineKeyboardButton(
                        text="🌲 B1 (Intermediate)",
                        callback_data="reg_english_b1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🏔️ B2 (Upper-Intermediate)",
                        callback_data="reg_english_b2"
                    ),
                    InlineKeyboardButton(
                        text="🏔️ C1 (Advanced)",
                        callback_data="reg_english_c1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🏔️ C2 (Proficient)",
                        callback_data="reg_english_c2"
                    ),
                ],
            ]
        )
        return keyboard
    
    @staticmethod
    def get_weight_log_keyboard() -> InlineKeyboardMarkup:
        """
        Клавиатура для записи веса.
        
        Returns:
            InlineKeyboardMarkup: Кнопка записи веса
        """
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.SCALE} Записать вес",
                        callback_data="weight_log"
                    )
                ],
            ]
        )
        return keyboard

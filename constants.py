"""
Константы и эмодзи для RAID SYSTEM бота
======================================

Этот файл содержит все константы, эмодзи и настройки бота.
Вынесено в отдельный файл для удобства поддержки и локализации.
"""

# ============================================
# БАЗОВЫЕ ЭМОДЗИ
# ============================================

class Emoji:
    """Класс с эмодзи для использования в боте"""
    
    # Статусы
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    QUESTION = "❓"
    LOCK = "🔒"
    UNLOCK = "🔓"
    CROSS = "❌"
    
    # Прогресс
    COMPLETED = "✅"
    PENDING = "⭕"
    STAR = "⭐"
    FIRE = "🔥"
    TROPHY = "🏆"
    TARGET = "🎯"
    CHART = "📊"
    CROWN = "👑"
    
    # Характеристики
    POWER = "🥊"  # Боевая мощь
    BRAIN = "🧠"  # Анализ
    SHIELD = "🛡️"  # Выносливость
    FLASH = "⚡"  # Скорость
    
    # Активности
    RUNNER = "🏃"
    BROOM = "🧹"
    BOOK = "📚"
    CALENDAR = "📅"
    CLIPBOARD = "📋"
    DIAMOND = "💎"
    
    # Английский язык
    VOCABULARY = "📚"
    LISTENING = "🎧"
    SPEAKING = "🗣"
    GRAMMAR = "📖"
    READING = "📄"
    WRITING = "✍️"
    DEFAULT_TASK = "📝"
    
    # Тренировки и здоровье
    SWORD = "⚔️"
    MEDITATION = "🧘"
    LEAF = "🌿"
    MOON = "🌙"
    SPARKLES = "✨"
    DROPLET = "💧"
    
    # Питание
    FORK_KNIFE = "🍽️"
    SCALE = "⚖️"
    
    # Награды и события
    GIFT = "🎁"
    PARTY = "🎉"
    MONEY = "💰"
    PLUS = "📈"
    MINUS = "📉"
    ARROW_RIGHT = "➡️"
    
    # Время
    SUN = "🌅"
    SUNRISE = "🌅"
    HEART = "💔"  # Здоровье сердца
    
    # Технические
    ROBOT = "🤖"
    GLOBE = "🌐"
    GEAR = "⚙️"
    
    # Стрелки и навигация
    BACK = "🔙"
    RETURN = "🔙"
    FORWARD = "▶️"
    NEXT = "➡️"
    PREV = "⬅️"
    UP = "⬆️"
    DOWN = "⬇️"


# ============================================
# УРОВНИ АНГЛИЙСКОГО ЯЗЫКА
# ============================================

ENGLISH_LEVELS = {
    "A0": {
        "name": "🌱 Новичок Охотника",
        "exp_required": 0,
        "description": "Только начинаешь путь"
    },
    "A1": {
        "name": "🌿 Охотник E-ранга",
        "exp_required": 100,
        "description": "Базовые навыки"
    },
    "A2": {
        "name": "🌱 Охотник D-ранга",
        "exp_required": 250,
        "description": "Уверенное общение"
    },
    "B1": {
        "name": "⚔️ Охотник C-ранга",
        "exp_required": 500,
        "description": "Средний уровень"
    },
    "B2": {
        "name": "💫 Охотник B-ранга",
        "exp_required": 1000,
        "description": "Хороший уровень"
    },
    "C1": {
        "name": "🌟 Охотник A-ранга",
        "exp_required": 2000,
        "description": "Продвинутый"
    },
    "C2": {
        "name": "👑 Охотник S-ранга",
        "exp_required": 3500,
        "description": "Владение языком"
    }
}

# Порядок уровней
ENGLISH_LEVEL_ORDER = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]

# ============================================
# ВСЕЛЕННЫЕ АНИМЕ
# ============================================

ANIME_UNIVERSES = {
    "solo": "Solo Leveling",
    "tower": "Tower of God", 
    "wind": "Wind Breaker",
    "kengan": "Kengan Ashura",
    "lookism": "Lookism",
    "haikyuu": "Haikyuu",
    "run": "Run with the Wind"
}

# ============================================
# НАГРАДЫ ЗА КВЕСТЫ (EXP)
# ============================================

QUEST_REWARDS = {
    "morning_workout": 30,
    "stretching": 20,
    "steps": 25,
    "english": 40,
    "reading": 35,
    "video": 25,
    "journal": 20,
    "hair_care": 15,
    "shower": 10,
    "early_sleep": 30,
    "no_phone": 25,
    "cleaning": 20,
    "healthy_food": 30,
    "water": 5,
    "skin_care": 5,
    "weight_log": 10,
}


# ============================================
# ЕЖЕДНЕВНЫЕ КВЕСТЫ ПО КАТЕГОРИЯМ
# ============================================

DAILY_QUESTS = {
    "fitness": {
        "title": f"{Emoji.POWER} Фитнес-квесты",
        "description": "Тренируй тело как настоящий охотник",
        "quests": [
            {
                "id": "morning_workout",
                "name": "Утренняя тренировка",
                "description": "Сделай разминку или тренировку утром (15-30 мин)",
                "exp": 30,
                "icon": Emoji.POWER,
            },
            {
                "id": "stretching",
                "name": "Растяжка",
                "description": "Сделай растяжку для всего тела (10-15 мин)",
                "exp": 20,
                "icon": "🤸",
            },
            {
                "id": "steps",
                "name": "Шаги",
                "description": "Пройди 8000+ шагов за день",
                "exp": 25,
                "icon": "👟",
            },
        ]
    },
    "learning": {
        "title": f"{Emoji.BOOK} Квесты обучения",
        "description": "Прокачивай разум и навыки",
        "quests": [
            {
                "id": "english",
                "name": "Английский язык",
                "description": "Выполни все задания по английскому на сегодня",
                "exp": 40,
                "icon": Emoji.BOOK,
            },
            {
                "id": "reading",
                "name": "Чтение",
                "description": "Прочитай 20+ страниц книги",
                "exp": 35,
                "icon": "📖",
            },
            {
                "id": "video",
                "name": "Обучающее видео",
                "description": "Посмотри обучающее видео (20+ мин)",
                "exp": 25,
                "icon": "🎓",
            },
            {
                "id": "journal",
                "name": "Дневник",
                "description": "Запиши свои мысли/цели в дневник",
                "exp": 20,
                "icon": "📓",
            },
        ]
    },
    "selfcare": {
        "title": f"{Emoji.SPARKLES} Уход за собой",
        "description": "Заботься о себе как о будущем S-ранге",
        "quests": [
            {
                "id": "hair_care",
                "name": "Уход за волосами",
                "description": "Маска/масло/уход за волосами",
                "exp": 15,
                "icon": "💆",
            },
            {
                "id": "shower",
                "name": "Контрастный душ",
                "description": "Примай контрастный душ",
                "exp": 10,
                "icon": "🚿",
            },
            {
                "id": "early_sleep",
                "name": "Ранний сон",
                "description": "Ложись спать до 23:00",
                "exp": 30,
                "icon": "😴",
            },
            {
                "id": "no_phone",
                "name": "Цифровой детокс",
                "description": "Не используй телефон 1 час после пробуждения",
                "exp": 25,
                "icon": "📵",
            },
            {
                "id": "cleaning",
                "name": "Уборка",
                "description": "Убери свое пространство (15+ мин)",
                "exp": 20,
                "icon": "🧹",
            },
            {
                "id": "healthy_food",
                "name": "Здоровое питание",
                "description": "Ешь здоровую еду весь день",
                "exp": 30,
                "icon": "🥗",
            },
            {
                "id": "water",
                "name": "Вода",
                "description": "Выпей 8 стаканов воды",
                "exp": 5,
                "icon": "💧",
            },
            {
                "id": "skin_care",
                "name": "Уход за кожей",
                "description": "Утренний и вечерний уход за кожей",
                "exp": 5,
                "icon": Emoji.SPARKLES,
            },
        ]
    }
}


# ============================================
# НАСТРОЙКИ БОТА
# ============================================

class Config:
    """Конфигурационные параметры бота"""
    
    # База данных
    DATABASE_NAME = "raid_system.db"
    
    # Порт для health check (Render)
    DEFAULT_PORT = 8080
    
    # Параметры уровней
    MAX_LEVEL = 100
    BASE_EXP = 100
    EXP_MULTIPLIER = 1.2
    
    # Параметры здоровья кожи
    MAX_SKIN_HEALTH = 100
    MIN_SKIN_HEALTH = 0
    DEFAULT_SKIN_HEALTH = 50
    
    # Параметры веса
    MIN_WEIGHT = 30.0
    MAX_WEIGHT = 200.0
    
    # Английский язык
    DEFAULT_ENGLISH_LEVEL = "A0"
    DEFAULT_ENGLISH_EXP = 0
    DAILY_TASKS_COUNT = 3
    
    # Требования к тестам
    MIN_DAYS_BEFORE_TEST = 7
    MIN_TASKS_FOR_TEST = 10
    
    # Напоминания
    MORNING_REMINDER_HOUR = 8
    EVENING_REMINDER_HOUR = 20
    
    # Питание
    DEFAULT_WATER_GOAL = 8


# ============================================
# ТЕКСТЫ СООБЩЕНИЙ
# ============================================

MESSAGES = {
    # Ошибки
    "user_not_found": "❌ Пользователь не найден. Пожалуйста, пройдите регистрацию заново с /start",
    "error_generic": "❌ Произошла ошибка. Попробуйте позже или используйте /start",
    "error_stats": "❌ Произошла ошибка при получении статуса. Попробуйте позже или используйте /start",
    "error_english": "❌ Произошла ошибка при загрузке раздела Английский. Попробуйте позже или используйте /start",
    "registration_incomplete": "❌ Сначала завершите регистрацию! Нажмите /start",
    
    # Успех
    "registration_complete": "🎉 Поздравляем, регистрация завершена!",
    "quest_complete": "✅ Задание выполнено!",
    "weight_logged": "⚖️ Вес записан!",
    
    # Приветствие
    "welcome": "⚔️ Добро пожаловать в RAID SYSTEM!",
    "welcome_bonus": "🎁 Бонус за регистрацию",
}


# ============================================
# КЛАВИАТУРЫ
# ============================================

KEYBOARD_BUTTONS = {
    # Главное меню
    "quests": "📋 Квесты",
    "workouts": "⚔️ Тренировки",
    "english": "📚 Английский",
    "status": "📊 Статус",
    "nutrition": "🍽️ Питание",
    
    # Действия
    "complete": "✅ Выполнено",
    "open_task": "📖 Открыть задание",
    "log_weight": "⚖️ Записать вес",
    "refresh": "🔄 Обновить",
    "back": "🔙 Назад",
}


# ============================================
# ТИПЫ ЗАДАНИЙ ПО АНГЛИЙСКОМУ
# ============================================

ENGLISH_TASK_TYPES = {
    "vocabulary": "Лексика",
    "listening": "Аудирование",
    "speaking": "Говорение",
    "grammar": "Грамматика",
    "reading": "Чтение",
    "writing": "Письмо"
}

REQUIRED_TASK_TYPES = {
    "vocabulary",
    "listening",
    "speaking",
    "reading",
    "writing"
}

# Для уровней A0, A1 добавляется грамматика
GRAMMAR_LEVELS = {"A0", "A1"}


# ============================================
# ЕЖЕДНЕВНЫЕ ЗАДАНИЯ ПО АНГЛИЙСКОМУ (5 НАВЫКОВ)
# ============================================

# Каждый день нужно прокачивать все 5 навыков:
# 1. Vocabulary (Лексика) - через Memrise или карточки
# 2. Listening (Аудирование) - видео, подкасты
# 3. Speaking (Говорение) - разговорная практика
# 4. Reading (Чтение) - книги, статьи, манга
# 5. Writing (Письмо) - дневник, упражнения

ENGLISH_DAILY_TASKS = {
    "vocabulary": {
        "icon": "📚",
        "name": "Лексика (Memrise)",
        "description": "Выучи 10-15 новых слов в Memrise или с помощью карточек",
        "exp": 15,
        "skills": ["vocabulary"],
        "tools": ["Memrise", "Anki", "Quizlet"],
        "urls": [
            {"name": "📱 Memrise", "url": "https://www.memrise.com/app/"},
            {"name": "🗂️ Anki", "url": "https://apps.ankiweb.net/"},
            {"name": "📝 Quizlet", "url": "https://quizlet.com/"}
        ],
        "tips": [
            "Составь карточки с контекстом",
            "Повторяй слова вслух",
            "Используй в предложениях"
        ]
    },
    "listening_video": {
        "icon": "🎧",
        "name": "Аудирование - Видео",
        "description": "Посмотри обучающее видео на английском (10-15 мин)",
        "exp": 20,
        "skills": ["listening"],
        "sources": ["YouTube", "English with Lucy", "BBC Learning"],
        "urls": [
            {"name": "📺 BBC Learning", "url": "https://www.youtube.com/@bbclearningenglish"},
            {"name": "👩‍🏫 English with Lucy", "url": "https://www.youtube.com/@EnglishwithLucy"},
            {"name": "🎓 EngVid", "url": "https://www.youtube.com/@engvidAdam"}
        ],
        "tips": [
            "Сначала смотри без субтитров",
            "Затем с английскими субтитрами",
            "Записывай незнакомые слова"
        ]
    },
    "listening_podcast": {
        "icon": "🎙️",
        "name": "Аудирование - Подкаст",
        "description": "Послушай подкаст на английском (10-15 мин)",
        "exp": 20,
        "skills": ["listening"],
        "sources": ["6 Minute English", "TED Talks Daily", "Luke's English Podcast"],
        "urls": [
            {"name": "🎧 BBC 6 Min English", "url": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"},
            {"name": "💡 TED Talks", "url": "https://www.ted.com/talks"},
            {"name": "🎙️ Luke's Podcast", "url": "https://teacherluke.co.uk/"}
        ],
        "tips": [
            "Слушай в дороге",
            "Повторяй вслед за диктором",
            "Отмечай интересные фразы"
        ]
    },
    "speaking_shadowing": {
        "icon": "🗣️",
        "name": "Говорение - Shadowing",
        "description": "Повторяй вслед за диктором видео (5-10 мин)",
        "exp": 20,
        "skills": ["speaking", "listening"],
        "urls": [
            {"name": "📺 YouTube", "url": "https://www.youtube.com/results?search_query=english+shadowing+practice"}
        ],
        "tips": [
            "Копируй интонацию и ритм",
            "Записывай свой голос",
            "Сравнивай с оригиналом"
        ]
    },
    "speaking_self": {
        "icon": "💬",
        "name": "Говорение - Монолог",
        "description": "Опиши свой день или расскажи о планах вслух (3-5 мин)",
        "exp": 15,
        "skills": ["speaking"],
        "urls": [
            {"name": "🎯 Темы для разговора", "url": "https://www.thoughtco.com/esl-conversation-questions-1212839"}
        ],
        "topics": [
            "Что ты сделал сегодня",
            "Твои планы на завтра",
            "Описание твоей комнаты",
            "Рассказ о твоем хобби"
        ],
        "tips": [
            "Говори перед зеркалом",
            "Используй новые слова",
            "Не бойся ошибок"
        ]
    },
    "reading_book": {
        "icon": "📖",
        "name": "Чтение - Книга",
        "description": "Прочитай 5-10 страниц книги на английском",
        "exp": 20,
        "skills": ["reading"],
        "levels": {
            "A0": "Graded Readers Level 1",
            "A1": "Graded Readers Level 2",
            "A2": "Harry Potter (упрощенный)",
            "B1": "Harry Potter, short stories",
            "B2": "Novels, news articles",
            "C1": "Literature, academic texts",
            "C2": "Classics, professional docs"
        },
        "urls": [
            {"name": "📚 Oxford Bookworms", "url": "https://elt.oup.com/catalogue/items/global/graded_readers/"},
            {"name": "📖 Penguin Readers", "url": "https://www.penguinreaders.com/"},
            {"name": "🌐 Project Gutenberg", "url": "https://www.gutenberg.org/"}
        ],
        "tips": [
            "Не переводи каждое слово",
            "Догадывайся по контексту",
            "Записывай полезные фразы"
        ]
    },
    "reading_manga": {
        "icon": "📱",
        "name": "Чтение - Манга/Комикс",
        "description": "Прочитай главу манги или комикса на английском",
        "exp": 15,
        "skills": ["reading", "vocabulary"],
        "sources": ["MangaPlus", "Webtoon", "Crunchyroll Manga"],
        "urls": [
            {"name": "📱 MangaPlus", "url": "https://mangaplus.shueisha.co.jp/"},
            {"name": "🎨 Webtoon", "url": "https://www.webtoons.com/en/"},
            {"name": "🍥 Crunchyroll Manga", "url": "https://www.crunchyroll.com/comics/manga"}
        ],
        "tips": [
            "Начни с знакомых историй",
            "Обрати внимание на диалоги",
            "Записывай разговорные фразы"
        ]
    },
    "writing_journal": {
        "icon": "✍️",
        "name": "Письмо - Дневник",
        "description": "Напиши 3-5 предложений о своем дне",
        "exp": 15,
        "skills": ["writing"],
        "urls": [
            {"name": "📝 Grammarly (проверка)", "url": "https://www.grammarly.com/"},
            {"name": "📚 Reverso", "url": "https://www.reverso.net/"}
        ],
        "prompts": [
            "Today I...",
            "I feel... because...",
            "My plans for tomorrow...",
            "Something interesting happened..."
        ],
        "tips": [
            "Используй простые предложения",
            "Проверь грамматику после",
            "Повторяй новые слова"
        ]
    },
    "writing_exercise": {
        "icon": "📝",
        "name": "Письмо - Грамматика",
        "description": "Выполни грамматическое упражнение (10 заданий)",
        "exp": 20,
        "skills": ["writing", "grammar"],
        "sources": ["English Grammar in Use", "Perfect English Grammar", "Cambridge"],
        "urls": [
            {"name": "📘 Perfect English Grammar", "url": "https://www.perfect-english-grammar.com/"},
            {"name": "🎯 English Grammar", "url": "https://www.english-grammar.at/"},
            {"name": "📚 Cambridge Grammar", "url": "https://www.cambridge.org/gb/cambridgeenglish/catalog/grammar-vocabulary-and-pronunciation"}
        ],
        "tips": [
            "Повторяй правило перед упражнением",
            "Проверь ответы",
            "Запиши свои ошибки"
        ]
    },
    "memrise_extra": {
        "icon": "🧠",
        "name": "Memrise - Дополнительно",
        "description": "Пройди дополнительный урок в Memrise",
        "exp": 10,
        "skills": ["vocabulary"],
        "urls": [
            {"name": "📱 Memrise App", "url": "https://www.memrise.com/app/"}
        ],
        "tips": [
            "Повторяй сложные слова",
            "Используй Speed Review",
            "Не пропускай дни"
        ]
    },
    "immersion": {
        "icon": "🌐",
        "name": "Погружение в язык",
        "description": "Измени язык интерфейса телефона/приложений на английский на 1 час",
        "exp": 10,
        "skills": ["vocabulary", "reading"],
        "tips": [
            "Используй английский интерфейс",
            "Смотри англоязычный контент",
            "Думай на английском"
        ]
    }
}

# Наборы заданий по уровням - 3 задания покрывают 5 навыков
ENGLISH_DAILY_SETS = {
    "beginner": [
        ["vocabulary", "listening_video", "writing_journal"],  # A0: vocab, listen, write
        ["vocabulary", "speaking_self", "reading_manga"],      # A0: vocab, speak, read
        ["listening_podcast", "writing_exercise", "memrise_extra"],  # listen, write, vocab
    ],
    "elementary": [
        ["vocabulary", "listening_video", "writing_journal", "speaking_self"],  # A1: all skills
        ["vocabulary", "reading_book", "writing_exercise"],    # vocab, read, write
        ["listening_podcast", "speaking_shadowing", "reading_manga"],  # listen, speak, read
    ],
    "intermediate": [
        ["vocabulary", "listening_video", "writing_journal", "speaking_self", "reading_book"],  # B1: all
        ["listening_podcast", "speaking_shadowing", "writing_exercise", "reading_manga"],  # B1
        ["memrise_extra", "immersion", "speaking_self", "reading_book", "listening_video"],  # B1
    ],
    "advanced": [
        ["vocabulary", "listening_podcast", "speaking_shadowing", "reading_book", "writing_journal"],  # B2+
        ["immersion", "listening_video", "speaking_self", "writing_exercise", "reading_manga"],  # B2+
        ["memrise_extra", "listening_podcast", "speaking_shadowing", "reading_book", "writing_journal"],  # B2+
    ]
}

# Маппинг уровней к наборам
ENGLISH_LEVEL_TO_SET = {
    "A0": "beginner",
    "A1": "elementary", 
    "A2": "elementary",
    "B1": "intermediate",
    "B2": "advanced",
    "C1": "advanced",
    "C2": "advanced"
}


# ============================================
# ТЕСТЫ ДЛЯ ПОВЫШЕНИЯ УРОВНЯ АНГЛИЙСКОГО
# ============================================

ENGLISH_TESTS = {
    "A1": {
        "title": "🌿 Тест на уровень A1 (E-ранг)",
        "description": "Проверка базовых знаний английского",
        "pass_score": 7,
        "questions": [
            {
                "question": "Как переводится 'I am a hunter'?",
                "options": ["Я охотник", "Ты охотник", "Он охотник", "Мы охотники"],
                "correct": 0
            },
            {
                "question": "Выберите правильную форму: 'She _____ to school every day'",
                "options": ["go", "goes", "going", "gone"],
                "correct": 1
            },
            {
                "question": "Какое слово означает 'система'?",
                "options": ["shadow", "system", "power", "level"],
                "correct": 1
            },
            {
                "question": "Переведите 'I wake up at 7 AM'",
                "options": ["Я ложусь спать в 7 утра", "Я просыпаюсь в 7 утра", "Я иду в школу в 7 утра", "Я ем завтрак в 7 утра"],
                "correct": 1
            },
            {
                "question": "Выберите правильный артикль: 'I have _____ cat'",
                "options": ["a", "an", "the", "-"],
                "correct": 0
            },
            {
                "question": "Какое слово НЕ относится к цветам?",
                "options": ["red", "blue", "run", "green"],
                "correct": 2
            },
            {
                "question": "Выберите правильное множественное число: 'one child - two _____'",
                "options": ["childs", "children", "childes", "child"],
                "correct": 1
            },
            {
                "question": "Переведите 'The dungeon is dangerous'",
                "options": ["Подземелье безопасно", "Подземелье опасно", "Подземелье большое", "Подземелье старое"],
                "correct": 1
            },
            {
                "question": "Выберите правильный вопрос: '_____ you like anime?'",
                "options": ["Do", "Does", "Is", "Are"],
                "correct": 0
            },
            {
                "question": "Какое число следует за 'six'?",
                "options": ["five", "seven", "eight", "nine"],
                "correct": 1
            }
        ]
    },
    "A2": {
        "title": "🌱 Тест на уровень A2 (D-ранг)",
        "description": "Проверка базового общения",
        "pass_score": 7,
        "questions": [
            {
                "question": "Выберите правильное время: 'Yesterday I _____ a new skill'",
                "options": ["learn", "learned", "have learned", "learning"],
                "correct": 1
            },
            {
                "question": "Как переводится 'I have been waiting for 2 hours'?",
                "options": ["Я ждал 2 часа", "Я жду 2 часа", "Я буду ждать 2 часа", "Я ждал вчера 2 часа"],
                "correct": 0
            },
            {
                "question": "Выберите правильный предлог: 'I am interested _____ learning English'",
                "options": ["on", "in", "at", "for"],
                "correct": 1
            },
            {
                "question": "Какое слово является синонимом к 'strong'?",
                "options": ["weak", "powerful", "slow", "small"],
                "correct": 1
            },
            {
                "question": "Выберите правильную форму: 'If I _____ enough money, I will buy a new sword'",
                "options": ["have", "had", "will have", "would have"],
                "correct": 0
            },
            {
                "question": "Переведите 'The monster was defeated by the hunter'",
                "options": ["Охотник победил монстра", "Монстр победил охотника", "Охотник и монстр сражались", "Монстр был побежден охотником"],
                "correct": 3
            },
            {
                "question": "Выберите правильное слово: 'This dungeon is _____ than the last one'",
                "options": ["more dangerous", "dangerouser", "most dangerous", "dangerous"],
                "correct": 0
            },
            {
                "question": "Какое предложение построено правильно?",
                "options": ["I not understand", "I don't understand", "I no understand", "I understanding not"],
                "correct": 1
            },
            {
                "question": "Выберите правильный артикль: '_____ Sun gives us light'",
                "options": ["A", "An", "The", "-"],
                "correct": 2
            },
            {
                "question": "Переведите 'I need to level up quickly'",
                "options": ["Мне нужно быстро повысить уровень", "Мне нужно медленно повысить уровень", "Я хочу снизить уровень", "Я не хочу повышать уровень"],
                "correct": 0
            }
        ]
    },
    "B1": {
        "title": "⚔️ Тест на уровень B1 (C-ранг)",
        "description": "Проверка среднего уровня",
        "pass_score": 7,
        "questions": [
            {
                "question": "Выберите правильную форму: 'By the time we arrived, the boss _____'",
                "options": ["already defeated", "had already been defeated", "has already defeated", "was already defeating"],
                "correct": 1
            },
            {
                "question": "Какое слово НЕ является наречием?",
                "options": ["quickly", "carefully", "beautiful", "suddenly"],
                "correct": 2
            },
            {
                "question": "Выберите правильный фразовый глагол: 'The raid was called _____ due to bad weather'",
                "options": ["off", "on", "out", "up"],
                "correct": 0
            },
            {
                "question": "Переведите 'I would have leveled up if I had trained harder'",
                "options": ["Я повышу уровень, если буду тренироваться усерднее", "Я бы повысил уровень, если бы тренировался усерднее", "Я повысил уровень, потому что тренировался усерднее", "Я не повышу уровень, даже если буду тренироваться"],
                "correct": 1
            },
            {
                "question": "Выберите правильную конструкцию: 'Not only _____ strong, but also fast'",
                "options": ["he is", "is he", "he was", "was he"],
                "correct": 1
            },
            {
                "question": "Какой вариант использует правильный модальный глагол: 'You _____ train every day to get stronger'",
                "options": ["must", "can", "may", "might"],
                "correct": 0
            },
            {
                "question": "Выберите правильное слово: 'Despite _____ tired, he continued training'",
                "options": ["being", "be", "was", "been"],
                "correct": 0
            },
            {
                "question": "Переведите 'The system is said to be ancient'",
                "options": ["Говорят, что система древняя", "Система говорит, что она древняя", "Древняя система говорит", "Система древняя, как говорят"],
                "correct": 0
            },
            {
                "question": "Выберите правильную форму: 'I wish I _____ more EXP yesterday'",
                "options": ["got", "had got", "have got", "get"],
                "correct": 1
            },
            {
                "question": "Какое предложение содержит герундий?",
                "options": ["I train every day", "Training is important", "I trained yesterday", "I will train tomorrow"],
                "correct": 1
            }
        ]
    },
    "B2": {
        "title": "💫 Тест на уровень B2 (B-ранг)",
        "description": "Проверка хорошего уровня",
        "pass_score": 7,
        "questions": [
            {
                "question": "Выберите правильную конструкцию: 'Hardly _____ started when the alarm went off'",
                "options": ["had we", "we had", "have we", "we have"],
                "correct": 0
            },
            {
                "question": "Какое слово является причастием II от 'choose'?",
                "options": ["chose", "chosen", "choosing", "choosed"],
                "correct": 1
            },
            {
                "question": "Выберите правильный инверсионный вариант: 'Never before _____ such a powerful monster'",
                "options": ["I saw", "have I seen", "I have seen", "saw I"],
                "correct": 1
            },
            {
                "question": "Переведите 'Had I known about the trap, I wouldn't have entered the dungeon'",
                "options": ["Если бы я знал о ловушке, я бы не вошел в подземелье", "Если бы я знал о ловушке, я вошел бы в подземелье", "Когда я узнал о ловушке, я вошел в подземелье", "Я знал о ловушке и вошел в подземелье"],
                "correct": 0
            },
            {
                "question": "Выберите правильную форму: 'The weapon _____ is legendary'",
                "options": ["wielding", "wielded by him", "he wields it", "which he wields it"],
                "correct": 1
            },
            {
                "question": "Какое предложение использует сослагательное наклонение правильно?",
                "options": ["If I am stronger, I win", "If I were stronger, I would win", "If I was stronger, I win", "If I be stronger, I would win"],
                "correct": 1
            },
            {
                "question": "Выберите правильный вариант: 'It's high time we _____ to the boss'",
                "options": ["go", "went", "have gone", "going"],
                "correct": 1
            },
            {
                "question": "Переведите 'No sooner had he leveled up than he faced a new challenge'",
                "options": ["Как только он повысил уровень, он столкнулся с новым вызовом", "Он не повысил уровень и не столкнулся с вызовом", "Он повысил уровень, но не столкнулся с вызовом", "Прежде чем он повысил уровень, он столкнулся с вызовом"],
                "correct": 0
            },
            {
                "question": "Выберите правильную конструкцию с 'need': 'Your skills _____ checking'",
                "options": ["need", "need to", "need to be", "needs"],
                "correct": 2
            },
            {
                "question": "Какое предложение содержит эллипсис?",
                "options": ["I train every day and I eat well", "I train every day and eat well", "I train every day", "Training every day is good"],
                "correct": 1
            }
        ]
    },
    "C1": {
        "title": "🌟 Тест на уровень C1 (A-ранг)",
        "description": "Проверка продвинутого уровня",
        "pass_score": 7,
        "questions": [
            {
                "question": "Выберите правильную конструкцию: 'Were I in your position, I _____ the quest'",
                "options": ["accept", "would accept", "will accept", "accepted"],
                "correct": 1
            },
            {
                "question": "Какое слово НЕ является синонимом к 'ephemeral'?",
                "options": ["transient", "fleeting", "permanent", "evanescent"],
                "correct": 2
            },
            {
                "question": "Выберите правильный вариант: 'Not until the final battle _____ the true extent of his power'",
                "options": ["did we see", "we saw", "we did see", "saw we"],
                "correct": 0
            },
            {
                "question": "Переведите 'Little did they know what awaited them in the A-rank dungeon'",
                "options": ["Они мало знали, что их ждет", "Они почти не знали", "Они не знали, что их ждет в подземелье A-ранга", "Мало кто знал, что их ждет"],
                "correct": 2
            },
            {
                "question": "Выберите правильную форму: 'The dungeon, _____ for centuries, was finally conquered'",
                "options": ["to be unexplored", "having been unexplored", "being unexplored", "unexplored"],
                "correct": 1
            },
            {
                "question": "Какое предложение использует подчинительную клаузалу с 'were' правильно?",
                "options": ["I wish I were stronger", "If I were go", "Were I goes", "I were stronger yesterday"],
                "correct": 0
            },
            {
                "question": "Выберите правильный вариант с 'but for': '_____ his quick thinking, we would have failed'",
                "options": ["But for", "Except for", "Without for", "Unless for"],
                "correct": 0
            },
            {
                "question": "Переведите 'Should you encounter any difficulty, do not hesitate to ask'",
                "options": ["Если вы столкнетесь с трудностями, не стесняйтесь спросить", "Вы должны столкнуться с трудностями", "Когда вы столкнетесь с трудностями", "Не стесняйтесь спросить"],
                "correct": 0
            },
            {
                "question": "Выберите правильный порядок слов: 'Under no circumstances _____ give up'",
                "options": ["you should", "should you", "you would", "would you"],
                "correct": 1
            },
            {
                "question": "Какое предложение использует сложное подлежащее?",
                "options": ["I think he is right", "It is known that he is strong", "He is strong", "Being strong is good"],
                "correct": 1
            }
        ]
    },
    "C2": {
        "title": "👑 Тест на уровень C2 (S-ранг)",
        "description": "Проверка владения языком",
        "pass_score": 8,
        "questions": [
            {
                "question": "Выберите правильную конструкцию: '_____ the difficulty of the raid, the team pressed on'",
                "options": ["Regardless of", "Regardless", "Despite of", "Although"],
                "correct": 0
            },
            {
                "question": "Какое слово лучше всего подходит: 'His _____ to detail made him an excellent strategist'",
                "options": ["meticulousness", "carelessness", "indifference", "ignorance"],
                "correct": 0
            },
            {
                "question": "Выберите правильный вариант: 'Seldom _____ such a formidable opponent'",
                "options": ["have I faced", "I have faced", "faced I", "I faced have"],
                "correct": 0
            },
            {
                "question": "Переведите 'Had it not been for the healer's intervention, the tank would have perished'",
                "options": ["Если бы не вмешательство целителя, танк бы погиб", "Целитель вмешался, и танк погиб", "Танк погиб из-за целителя", "Целитель не вмешался, и танк выжил"],
                "correct": 0
            },
            {
                "question": "Выберите правильную конструкцию: 'So powerful _____ that he defeated the boss single-handedly'",
                "options": ["he was", "was he", "he is", "is he"],
                "correct": 1
            },
            {
                "question": "Какое предложение использует архаичную/литературную форму?",
                "options": ["He doesn't know", "He knows not", "He not knows", "He is not knowing"],
                "correct": 1
            },
            {
                "question": "Выберите правильный вариант с 'let alone': 'He can't defeat an E-rank monster, _____ an S-rank boss'",
                "options": ["let alone", "leave alone", "let along", "alone let"],
                "correct": 0
            },
            {
                "question": "Переведите 'Be that as it may, we must proceed with caution'",
                "options": ["Как бы то ни было, мы должны действовать осторожно", "Пусть будет так, мы должны остановиться", "Как это может быть, мы должны продолжить", "Будь это так, мы будем осторожны"],
                "correct": 0
            },
            {
                "question": "Выберите правильный вариант: 'Were it not for the system, he _____ an ordinary hunter'",
                "options": ["would be", "would have been", "will be", "is"],
                "correct": 1
            },
            {
                "question": "Какое предложение использует эмфатический 'do' правильно?",
                "options": ["I do train every day", "Do I train every day", "I do training every day", "I does train every day"],
                "correct": 0
            }
        ]
    }
}


# ============================================
# ПОЛЬЗОВАТЕЛЬСКИЕ ПАРАМЕТРЫ ПО УМОЛЧАНИЮ
# ============================================

DEFAULT_USER_STATS = {
    "level": 1,
    "exp": 0,
    "exp_to_next": 100,
    "power": 10.0,
    "analysis": 10.0,
    "endurance": 10.0,
    "speed": 10.0,
    "skin_health": 50,
    "english_progress": 0,
    "streak": 0,
    "weight": None,
    "height": None,
    "target_weight": None,
    "gender": None,
    "skin_type": None,
    "english_level": "A0",
    "english_exp": 0,
    "english_level_progress": 0,
    "english_test_attempts": 0,
    "anime_universe": "Solo Leveling",
    "registration_completed": False
}


# ============================================
# РАНГИ ТРЕНИРОВОК
# ============================================

WORKOUT_RANKS = ["E", "D", "C", "B", "A", "S"]

RANK_REQUIREMENTS = {
    "E": 1,
    "D": 10,
    "C": 25,
    "B": 50,
    "A": 75,
    "S": 100
}


# ============================================
# БИБЛИОТЕКА ТРЕНИРОВОК
# ============================================

WORKOUT_LIBRARY = {
    "solo": {
        "E": {
            "title": "⚔️ E-ранг: Пробуждение охотника",
            "description": "Ты только получил систему. Тело слабое, но дух горит. Цель: выжить и адаптироваться. (15-20 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "🧘 Медитация пробуждения",
                    "duration": "5 минут",
                    "details": "1. Сядь на пол, скрестив ноги или на стуле\n2. Закрой глаза, выпрями спину\n3. Дыши ровно: вдох 4 сек, задержка 2 сек, выдох 6 сек\n4. Представь, как система активируется в тебе\n5. Повтори цикл 10 раз\n\n⚠️ Если чувствуешь головокружение - отдохни",
                    "quote": "Система выбрала тебя. Не подведи."
                },
                {
                    "name": "🤸 Разминка тела охотника",
                    "duration": "10 минут",
                    "details": "1. Наклоны головы влево-вправо: медленно, 10 раз в каждую сторону (2 мин)\n2. Вращение плечами: 10 раз вперед, 10 назад (2 мин)\n3. Круговые махи руками: 15 раз в каждую сторону (2 мин)\n4. Наклоны корпуса: 10 раз влево, 10 вправо (2 мин)\n5. Приседания: 10 раз, без рук (2 мин)\n\n💡 Если больно - делай в полсилы",
                    "quote": "Тени следуют за сильным духом"
                },
                {
                    "name": "🚶 Первая охота (ходьба)",
                    "duration": "10 минут",
                    "details": "1. Иди по комнате или на месте\n2. Шаги уверенные, плечи расправлены\n3. Дыши ровно: вдох-выдох через нос\n4. Представь, что собираешь ингредиенты\n5. Можно смотреть аниме параллельно\n\n⚡ Цель: выработать привычку двигаться каждый день",
                    "quote": "Даже слабый охотник сильнее обычного человека"
                }
            ],
            "warnings": ["⚠️ Не перенапрягайся - E-ранг это начало", "🌬️ При боли в суставах - уменьши амплитуду", "💧 Пей воду во время тренировки", "🛌 Если чувствуешь усталость - сделай перерыв"]
        },
        "D": {
            "title": "⚔️ D-ранг: Пробуждение силы",
            "description": "Ты убил первых монстров. Система дает больше опыта. Цель: укрепить тело для больших подвигов. (25-30 мин)",
            "exp": 30,
            "exercises": [
                {
                    "name": "🧘 Силовая медитация D-ранга",
                    "duration": "10 минут",
                    "details": "1. Встань, ноги на ширине плеч\n2. Руки согнуты перед грудью (стойка охотника)\n3. Дыши: вдох 4сек, задержка 4сек, выдох 6сек\n4. Представь, как мана накапливается\n5. Держи позу, сохраняя ровное дыхание\n\n💡 Сосредоточься на напряжении в животе",
                    "quote": "Сила начинается с ума"
                },
                {
                    "name": "🤸 Динамическая растяжка",
                    "duration": "15 минут",
                    "details": "1. Махи ногами вперед: 15 раз каждой ногой (3 мин)\n2. Выпады на месте: 10 раз на каждую ногу (4 мин)\n3. Повороты корпуса стоя: 20 раз (3 мин)\n4. Мостик: держать 30 сек, 3 подхода с отдыхом (3 мин)\n5. Растяжка бедра в присяде: по 2 мин на каждую ногу (2 мин)\n\n⚡ Выпады - главное упражнение для ног охотника",
                    "quote": "Гибкость - ключ к выживанию в данжах"
                },
                {
                    "name": "🚶 Быстрая ходьба",
                    "duration": "15 минут",
                    "details": "1. 2 минуты обычным шагом (разминка)\n2. 1 минута ускоренная ходьба (как от монстра)\n3. Повторить 5 циклов\n4. Руки работают активно, дыши ровно\n5. В конце - 2 минуты медленной ходьбы (заминка)\n\n💡 Пульс должен быть 120-130 ударов в быстрой фазе",
                    "quote": "Скорость спасает жизнь в двойных данжах"
                }
            ],
            "warnings": ["⚠️ Контролируй пульс - не выше 140 ударов", "🌬️ Отдых 30 сек между подходами", "💧 Выпей стакан воды до начала", "⚡ Если головокружение - снизь темп"]
        },
        "C": {
            "title": "⚔️ C-ранг: Испытание в данже",
            "description": "Ты достаточно силен для C-ранга. Цель: развить выносливость и базовую силу для полноценных рейдов. (35-40 мин)",
            "exp": 40,
            "exercises": [
                {
                    "name": "🧘 Медитация перед рейдом",
                    "duration": "5 минут",
                    "details": "1. Стоя, ноги на ширине плеч, руки согнуты\n2. Концентрация на дыхании: вдох-задержка-выдох\n3. Представь, что готовишься к входу в данж\n4. Чувствуй напряжение в мышцах\n5. Дыши ровно, несмотря на пульс\n\n⚡ Эта медитация используется перед реальными боями",
                    "quote": "Сила духа преодолевает любого босса"
                },
                {
                    "name": "🤸 Акробатическая растяжка",
                    "duration": "20 минут",
                    "details": "1. Прыжки на месте - 2 минуты (разогрев)\n2. Шпагат в стороны - 5 минут растяжки (насколько получается)\n3. Мостик с опорой на руки - 5 минут\n4. Скручивания лежа: 3 подхода по 10 раз (3 мин)\n5. Растяжка ног стоя (коснуться носков) - 5 минут\n\n💡 C-ранг требует гибкости для уклонений",
                    "quote": "Тело должно быть гибким как тень"
                },
                {
                    "name": "🏃 Выносливость охотника",
                    "duration": "20 минут",
                    "details": "1. Бег на месте: 3 минуты, средний темп\n2. Ходьба: 2 минуты восстановление\n3. Повторить 4 цикла\n4. Держи ровное дыхание: вдох носом, выдох ртом\n5. В конце - заминка 2 минуты\n\n⚡ Это базовая выносливость для C-ранга",
                    "quote": "Бег формирует выносливость для длинных рейдов"
                },
                {
                    "name": "💪 Базовая сила охотника",
                    "duration": "10 минут",
                    "details": "1. Приседания: 2 подхода по 15 раз (3 мин)\n2. Отжимания от стены или стола: 2 подхода по 10 раз (3 мин)\n3. Планка: держать 30-45 секунд, 2 подхода (4 мин)\n\n💡 C-ранг требует минимальной силовой базы\n⚡ Отжимания от стены - если не хватает сил для пола",
                    "quote": "Сила растет через преодоление себя"
                }
            ],
            "warnings": ["⚠️ Следи за дыханием - не задерживай", "🌬️ Не перенапрягай суставы", "💧 Пей воду каждые 10 минут", "⚡ C-ранг - серьезная нагрузка, слушай тело"]
        },
        "B": {
            "title": "⚔️ B-ранг: Элитный охотник",
            "description": "Ты элита среди охотников. Цель: развить взрывную силу и скорость для А-ранга. (45-50 мин)",
            "exp": 60,
            "exercises": [
                {
                    "name": "🧘 Медитация элиты",
                    "duration": "5 минут",
                    "details": "1. Стоя, ноги на ширине плеч\n2. Руки перед грудью, мышцы напряжены\n3. Визуализируй бой с сильным противником\n4. Дыши: вдох 3сек, задержка 3сек, выдох 5сек\n5. Чувствуй силу, текущую через тело\n\n⚡ B-ранг требует психологической устойчивости",
                    "quote": "Элита не рождается - она куется в боях"
                },
                {
                    "name": "🔥 Плиометрика B-ранга",
                    "duration": "20 минут",
                    "details": "1. Прыжки на месте с поднятием колен: 3 минуты\n2. Выпрыгивания из приседа: 3 подхода по 12 раз\n3. Берпи (упрощенные): 2 подхода по 8 раз\n4. Прыжки в длину с места: 2 подхода по 10 раз\n5. Отдых между подходами: 1 минута\n\n💡 Взрывная сила - ключ к B-рангу",
                    "quote": "Взрывная сила разрушает любую защиту"
                },
                {
                    "name": "🏃 Интервальный бег",
                    "duration": "15 минут",
                    "details": "1. 30 секунд бег на месте с максимальной скоростью\n2. 30 секунд ходьба (восстановление)\n3. Повторить 10 циклов\n4. Держи форму: руки согнуты, плечи расправлены\n5. В конце - 5 минут заминки\n\n⚡ B-ранг требует выносливости и скорости",
                    "quote": "Скорость решает исход боя"
                },
                {
                    "name": "💪 Силовая база B-ранга",
                    "duration": "15 минут",
                    "details": "1. Приседания: 3 подхода по 20 раз\n2. Отжимания от пола (или с колен): 3 подхода по 12 раз\n3. Планка: 3 подхода по 45 секунд\n4. Выпады: 3 подхода по 15 раз на ногу\n5. Отдых между подходами: 45 секунд\n\n💡 B-ранг требует реальной силы",
                    "quote": "Сила телесная отражает силу воли"
                }
            ],
            "warnings": ["⚠️ B-ранг - высокая нагрузка", "💧 Пей воду каждые 5 минут", "🌬️ Контролируй пульс: не выше 160", "⚡ Если болит грудь - немедленно остановись"]
        },
        "A": {
            "title": "⚔️ A-ранг: Вершина силы",
            "description": "Ты среди сильнейших охотников. Цель: довести тело до предела человеческих возможностей. (55-60 мин)",
            "exp": 80,
            "exercises": [
                {
                    "name": "🧘 Медитация мастера",
                    "duration": "10 минут",
                    "details": "1. Сидя в полной тишине\n2. Дыши: вдох 4сек, задержка 7сек, выдох 8сек\n3. Визуализируй бой с монархом теней\n4. Почувствуй абсолютный контроль над телом\n5. Повтори цикл 10 раз\n\n⚡ A-ранг требует идеального контроля",
                    "quote": "Мастерство - это когда тело слушается без мысли"
                },
                {
                    "name": "🔥 Максимальная плиометрика",
                    "duration": "25 минут",
                    "details": "1. Берпи полные: 3 подхода по 12 раз\n2. Прыжки в длину: 3 подхода по 15 раз\n3. Выпрыгивания: 3 подхода по 15 раз\n4. Отжимания с хлопком (или максимально взрывные): 3 подхода по 10 раз\n5. Прыжки с разведением ног: 3 минуты без остановки\n6. Отдых между подходами: 1 минута\n\n💡 A-ранг требует взрывной силы на пределе",
                    "quote": "Взрыв - это сила, умноженная на скорость"
                },
                {
                    "name": "🏃 Спринтерская выносливость",
                    "duration": "15 минут",
                    "details": "1. 45 секунд максимальный бег на месте\n2. 15 секунд отдых\n3. Повторить 12 циклов\n4. Держи максимальную интенсивность\n5. В конце - 5 минут заминки\n\n⚡ Темп не падает даже на 12-м круге",
                    "quote": "Выносливость A-ранга - это спринт длиной в марафон"
                },
                {
                    "name": "💪 Максимальная сила",
                    "duration": "15 минут",
                    "details": "1. Приседания: 4 подхода по 25 раз\n2. Отжимания: 4 подхода по 20 раз\n3. Планка: 4 подхода по 60 секунд\n4. Выпады с прыжком: 3 подхода по 12 раз на ногу\n5. Отдых между подходами: 30 секунд\n\n💡 A-ранг = максимальные объемы",
                    "quote": "Сила A-ранга ломает горы"
                }
            ],
            "warnings": ["⚠️ A-ранг - экстремальная нагрузка", "💧 Минимум 500мл воды во время тренировки", "🌬️ Пульс контроль - не выше 180", "⚡ При любом дискомфорте - остановись", "🛌 После тренировки - обязательный отдых 1 час"]
        },
        "S": {
            "title": "⚔️ S-ранг: Монарх",
            "description": "Ты достиг пика. Тело - оружие массового поражения. Цель: поддерживать форму бога войны. (70-80 мин)",
            "exp": 120,
            "exercises": [
                {
                    "name": "🧘 Медитация Монарха",
                    "duration": "10 минут",
                    "details": "1. Сидя в абсолютной тишине, свет выключен\n2. Дыши: вдох 4сек, задержка 8сек, выдох 8сек\n3. Визуализируй себя как Армия Теней\n4. Почувствуй абсолютную власть над своим телом\n5. Каждый вдох - энергия, каждый выдох - сила\n\n⚡ S-ранг требует абсолютного контроля разума",
                    "quote": "Я - тень, я - монарх, я - бог"
                },
                {
                    "name": "🔥 Божественная плиометрика",
                    "duration": "30 минут",
                    "details": "1. Берпи с отжиманием: 4 подхода по 15 раз\n2. Прыжки в длину: 4 подхода по 20 раз\n3. Выпрыгивания с хлопком: 4 подхода по 15 раз\n4. Отжимания с хлопком: 4 подхода по 12 раз\n5. Прыжки на месте 5 минут без остановки\n6. Альпинист (в планке): 4 подхода по 30 раз\n7. Отдых между подходами: 45 секунд\n\n💡 S-ранг = тренировки на пределе человеческих возможностей",
                    "quote": "Тело монарха не знает усталости"
                },
                {
                    "name": "🏃 Безумная выносливость",
                    "duration": "20 минут",
                    "details": "1. 60 секунд максимальный бег\n2. 15 секунд отдых\n3. Повторить 15 циклов\n4. Каждый спринт - как будто от тигра бежишь\n5. Последние 5 циклов - еще быстрее\n\n⚡ S-ранг не знает пощады",
                    "quote": "Выносливость монарха - бесконечна"
                },
                {
                    "name": "� Сила бога",
                    "duration": "20 минут",
                    "details": "1. Приседания: 5 подхода по 30 раз\n2. Отжимания: 5 подходов по 25 раз\n3. Планка: 5 подходов по 90 секунд\n4. Выпады с прыжком: 4 подхода по 15 раз на ногу\n5. Берпи: 3 подхода по 10 раз (финиш)\n6. Отдых между подходами: 30 секунд\n\n💡 S-ранг = божественные объемы",
                    "quote": "Сила монарха уничтожает нации"
                }
            ],
            "warnings": ["⚠️ S-ранг - только для тех, кто прошел все остальное", "💧 Минимум 1 литр воды", "🌬️ Контролируй пульс, но не останавливайся", "⚡ Это тренировка для монстров", "🛌 После - отдых минимум 2 часа", "⚠️ Если не готов - вернись к A-рангу"]
        }
    },
    "tower": {
        "E": {
            "title": "🗼 Квест: Регулярный Первый этаж",
            "description": "Начальное испытание башни (15-20 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "⚖ Разминка регулярного",
                    "duration": "5 минут",
                    "details": "1. Повороты головы - медленно, по 10 раз в каждую сторону\n2. Разминка запястий - круговые движения\n3. Покачивания на носках - 20 раз\n4. Легкие прыжки на месте - 2 минуты",
                    "quote": "Каждое путешествие начинается с первого шага"
                },
                {
                    "name": "🦘 Легкие прыжки",
                    "duration": "10 минут",
                    "details": "1. Прыжки на месте с поднятием колен - 2 минуты\n2. Прыжки в стороны - 2 минуты\n3. Прыжки с разведением ног - 2 минуты\n4. Медленные приседания - 10 раз, 2 подхода\n5. Выпады на месте - по 5 раз на каждую ногу",
                    "quote": "Прыжки - это полет на мгновение"
                },
                {
                    "name": "🧘 Восстановление маны",
                    "duration": "10 минут",
                    "details": "Лежа на спине, руки вдоль тела. Глубокое диафрагмальное дыхание. Вдох - живот поднимается, выдох - опускается. 5 минут. Затем легкая растяжка ног и рук.",
                    "quote": "Мана восстанавливается через покой"
                }
            ],
            "warnings": ["⚠️ Плавные движения", "🌬️ Глубокое дыхание", "💧 Выпей воды после"]
        }
    },
    "wind": {
        "E": {
            "title": "🌪️ Квест: Уличный новичок",
            "description": "Основы уличных боев (15-20 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "👊 Разминка бойца",
                    "duration": "5 минут",
                    "details": "1. Легкий бег на месте - 2 минуты\n2. Разминка плеч - 20 кругов вперед, 20 назад\n3. Разминка таза - круговые движения 10 раз\n4. Прыжки с разведением рук - 20 раз",
                    "quote": "Уличный бой начинается с подготовки"
                },
                {
                    "name": "👊 Теневые удары",
                    "duration": "10 минут",
                    "details": "1. Стойка: ноги на ширине плеч, руки на уровне лица\n2. Прямые удары левой-правой - по 20 раз\n3. Боковые удары локтями - по 15 раз каждой рукой\n4. Защитные движения - уклоны в стороны по 10 раз\n5. Комбинация: удар-уклон-контрудар - 5 минут",
                    "quote": "Скорость важнее силы"
                },
                {
                    "name": "🤸 Базовая акробатика",
                    "duration": "10 минут",
                    "details": "1. Перекаты вперед-назад - 5 раз\n2. Колесо (если получается) или боковые наклоны - 5 минут\n3. Отжимания - 2 подхода по 10 раз\n4. Планка боковая - по 20 сек каждая сторона",
                    "quote": "Гибкость - оружие уличного бойца"
                }
            ],
            "warnings": ["⚠️ Без резких движений", "🌬️ Контроль дыхания", "⚠️ Не бей по стенам!"]
        }
    },
    "kengan": {
        "E": {
            "title": "🥊 Квест: Боец новичок",
            "description": "Основы единоборств (15-20 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "🥊 Боевая стойка",
                    "duration": "5 минут",
                    "details": "1. Ноги на ширине плеч, одна нога впереди\n2. Руки на уровне подбородка, локти прижаты\n3. Держи стойку 1 минуту, переключи ноги\n4. Легкие движения в стойке - вперед-назад\n5. Практикуй уклоны корпусом",
                    "quote": "Стойка - основа боя"
                },
                {
                    "name": "💪 Теневые удары",
                    "duration": "10 минут",
                    "details": "1. Джэбы (прямые) - 30 раз каждой рукой\n2. Хуки (боковые) - 20 раз каждой рукой\n3. Апперкоты - 15 раз\n4. Защитные движения - 5 минут\n5. Комбинация: джеб-кросс-хук - 5 минут",
                    "quote": "Техника побеждает силу"
                },
                {
                    "name": "🧘 Боевая медитация",
                    "duration": "10 минут",
                    "details": "Сидя в стойке (сейдза) или на стуле. Спина прямая. Дыши через нос, глубоко. Представь бой, но оставайся спокойным. Концентрация на дыхании.",
                    "quote": "Дух воина непоколебим"
                }
            ],
            "warnings": ["⚠️ Без контактов", "🌬️ Ритмичное дыхание", "⚠️ Не перенапрягай кисти"]
        }
    },
    "lookism": {
        "E": {
            "title": "💪 Квест: Трансформация начало",
            "description": "Основы изменения тела (20-25 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "🧘 Осознанность тела",
                    "duration": "5 минут",
                    "details": "Лежа на спине, закрой глаза. Просканируй тело от пальцев ног до макушки. Отметь напряженные места. Дыши в эти места, расслабляй их.",
                    "quote": "Понимание тела - первый шаг к трансформации"
                },
                {
                    "name": "🤸 Утренняя растяжка",
                    "duration": "15 минут",
                    "details": "1. Растяжка задней поверхности ног - 3 минуты\n2. Бабочка (растяжка паха) - 3 минуты\n3. Кошка-корова (спина) - 20 повторений\n4. Повороты корпуса лежа - 20 раз\n5. Растяжка плеч - 3 минуты",
                    "quote": "Гибкость открывает потенциал"
                },
                {
                    "name": "🚶 Ходьба с осанкой",
                    "duration": "10 минут",
                    "details": "Ходи по комнате с книгой на голове или просто следи за осанкой. Плечи назад, подбородок вверх, живот втянут. Дыши ровно. Представь что ты модель.",
                    "quote": "Осанка - отражение духа"
                }
            ],
            "warnings": ["⚠️ Плавные движения", "🌬️ Контроль спины", "💧 Выпей воды"]
        },
        "A": {
            "title": "💪 Квест: Титановое тело I",
            "description": "Продвинутая трансформация (45-50 мин)",
            "exp": 50,
            "exercises": [
                {
                    "name": "💪 Силовые упражнения",
                    "duration": "20 минут",
                    "details": "1. Приседания с собственным весом - 3 подхода по 20 раз\n2. Отжимания - 3 подхода по 15 раз\n3. Выпады - 3 подхода по 12 раз на каждую ногу\n4. Планка - 3 подхода по 45 секунд\n5. Берпи (упрощенные) - 2 подхода по 8 раз",
                    "quote": "Сила куется в огне усилий"
                },
                {
                    "name": "🏃 Высокоинтенсивный кардио",
                    "duration": "15 минут",
                    "details": "Интервальная тренировка:\n1. 30 сек бег на месте с высокими коленями\n2. 30 сек отдых (ходьба)\n3. 30 сек прыжки с разведением\n4. 30 сек отдых\n5. Повторить 5 кругов",
                    "quote": "Сердце титана бьется ровно"
                },
                {
                    "name": "🧘 Восстановительная медитация",
                    "duration": "10 минут",
                    "details": "Лежа на спине. Прогрессивная релаксация: напрягай и расслабляй каждую группу мышц. Начни с ног, закончи лицом. Глубокое дыхание.",
                    "quote": "Покой укрепляет сталь"
                },
                {
                    "name": "🤸 Гибкость позвоночника",
                    "duration": "10 минут",
                    "details": "1. Кошка-корова - 30 повторений\n2. Повороты корпуса сидя - 20 раз\n3. Мостик - держать 30 сек, 3 раза\n4. Скручивания лежа - 15 раз каждая сторона\n5. Поза ребенка - отдых 2 минуты",
                    "quote": "Гибкое тело - несокрушимое"
                }
            ],
            "warnings": ["⚠️ Контролируй нагрузку", "💧 Пей достаточно воды", "🌬️ Правильное дыхание"]
        },
        "S": {
            "title": "💪 Квест: Титановое тело II",
            "description": "Максимальная трансформация тела (60+ мин)",
            "exp": 100,
            "exercises": [
                {
                    "name": "🔥 Плиометрическая тренировка",
                    "duration": "25 минут",
                    "details": "1. Прыжки на месте с поднятием колен - 3 минуты\n2. Прыжки в длину с места - 2 подхода по 10 раз\n3. Выпрыгивания (присяд-прыжок) - 3 подхода по 12 раз\n4. Боковые прыжки - 3 минуты\n5. Отжимания с хлопком (или без) - 3 подхода по 8 раз\n6. Отдых между подходами - 1 минута",
                    "quote": "Взрывная сила титана"
                },
                {
                    "name": "💪 Функциональный тренинг",
                    "duration": "20 минут",
                    "details": "1. Берпи - 3 подхода по 10 раз\n2. Горка (планка + прыжок к рукам) - 3 подхода по 12 раз\n3. Альпинист (колени к груди в планке) - 3 подхода по 20 раз\n4. Обратные выпады с поворотом - 3 подхода по 10 раз\n5. Планка с отжиманием - 3 подхода по 8 раз",
                    "quote": "Тело работает как единый механизм"
                },
                {
                    "name": "🏃 Интервальный спринт",
                    "duration": "15 минут",
                    "details": "На месте или на улице:\n1. 20 сек максимально быстро\n2. 40 сек медленно\n3. Повторить 10 раз\nДержи темп, не сбавляй!",
                    "quote": "Скорость решает всё"
                },
                {
                    "name": "🧘 Статическая растяжка",
                    "duration": "15 минут",
                    "details": "1. Шпагат продольный - по 3 мин каждая нога\n2. Шпагат поперечный - 3 минуты\n3. Наклон к ногам - 3 минуты\n4. Растяжка плеч с полотенцем - 3 минуты\n5. Поза ребенка - 3 минуты отдыха",
                    "quote": "Растяжка укрепляет мышцы"
                },
                {
                    "name": "💆 Массаж и восстановление",
                    "duration": "10 минут",
                    "details": "1. Растирание мышц руками\n2. Простукивание ног\n3. Поглаживание рук к плечам\n4. Вращение стоп\n5. Глубокое дыхание лежа - 5 минут",
                    "quote": "Восстановление - часть тренировки"
                }
            ],
            "warnings": ["⚠️ Максимальная концентрация", "💧 Обязательное увлажнение", "🌬️ Дыхание 4-7-8", "⚡ Следи за пульсом"]
        }
    },
    "haikyuu": {
        "E": {
            "title": "🏐 Квест: Волейбольный новичок",
            "description": "Основы для хороших дней (20-25 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "🏐 Разминка волейболиста",
                    "duration": "5 минут",
                    "details": "1. Легкий бег с высокими коленями - 2 минуты\n2. Разминка плеч - круговые движения 20 раз\n3. Разминка запястий - вращения 10 раз каждое\n4. Приседания без веса - 15 раз\n5. Махи руками - 20 раз вперед-назад",
                    "quote": "Разминка - ключ к прыжку"
                },
                {
                    "name": "🦘 Легкие прыжки",
                    "duration": "10 минут",
                    "details": "1. Прыжки на месте с поднятием рук - 2 минуты\n2. Прыжки вверх с вытягиванием - 20 раз\n3. Прыжки в длину с места - 15 раз\n4. Присяд-прыжок - 15 раз\n5. Отдых и растяжка икр - 2 минуты",
                    "quote": "Каждый прыжок - это полет"
                },
                {
                    "name": "🤸 Растяжка ног",
                    "duration": "15 минут",
                    "details": "1. Наклоны к ногам стоя - 3 минуты\n2. Шпагат поперечный (насколько получается) - 5 минут\n3. Растяжка икр у стены - по 2 минуты каждая\n4. Бабочка (сидя, стопы вместе) - 3 минуты\n5. Поза ребенка - 2 минуты",
                    "quote": "Гибкие ноги - высокие прыжки"
                }
            ],
            "warnings": ["⚠️ Мягкие приземления", "🌬️ Дыхание при прыжках", "💧 Пей воду"]
        }
    },
    "run": {
        "E": {
            "title": "🏃 Квест: Начало пробежки",
            "description": "Адаптивный бег для контроля пульса (20-25 мин)",
            "exp": 20,
            "exercises": [
                {
                    "name": "🏃 Разминка бегуна",
                    "duration": "5 минут",
                    "details": "1. Ходьба на месте с высокими коленями - 2 минуты\n2. Вращения бедрами - 10 раз каждую сторону\n3. Махи ногами вперед - по 10 раз каждой\n4. Легкие приседания - 10 раз\n5. Разминка лодыжек - круговые движения",
                    "quote": "Бег начинается с подготовки"
                },
                {
                    "name": "🚶 Быстрая ходьба",
                    "duration": "15 минут",
                    "details": "Ходьба в умеренном темпе. Пульс должен быть 100-120 ударов. Дыши ровно. Руки согнуты в локтях, двигаются в такт ногам. Спина прямая, взгляд вперед.",
                    "quote": "Ходьба - основа выносливости"
                },
                {
                    "name": "🧘 Восстановительное дыхание",
                    "duration": "10 минут",
                    "details": "Лежа на спине. Руки на животе. Дыши диафрагмально - живот поднимается на вдохе, опускается на выдохе. 4-7-8: вдох 4, задержка 7, выдох 8. Повторять 10 раз.",
                    "quote": "Дыхание - топливо для бега"
                }
            ],
            "warnings": ["⚠️ Контроль пульса 100-120", "🌬️ Ритмичное дыхание", "⚠️ При боли - остановись"]
        }
    }
}

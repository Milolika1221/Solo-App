## Описание слоёв

### 1. Database Layer (`DatabaseManager`)
**Файл:** `main.py` (class `DatabaseManager`)

**Ответственность:**
- Управление подключением к SQLite
- Создание и обновление таблиц
- Выполнение SQL запросов

**Таблицы:**
- `users` - пользователи и их прогресс
- `daily_quests` - ежедневные квесты
- `english_progress` - прогресс по английскому
- `daily_english_tasks` - задания по английскому
- `weight_tracking` - отслеживание веса
- `nutrition_plans` - планы питания
- `inventory` - инвентарь
- `achievements` - достижения

---

### 2. Service Layer (`UserService`, `EnglishService`, `QuestService`)
**Файл:** `main.py` (classes с окончанием `Service`)

**Ответственность:**
- Бизнес-логика приложения
- Расчёт опыта и повышение уровней
- Управление прогрессом

**Классы:**
- `UserService` - управление пользователями, опытом, характеристиками
- `EnglishService` - уровни английского (A0-C2), требования, тесты
- `QuestService` - квесты, тренировки, награды

---

### 3. Keyboard Layer (`KeyboardManager`)
**Файл:** `main.py` (class `KeyboardManager`)

**Ответственность:**
- Создание Reply и Inline клавиатур
- Унифицированные методы для всех клавиатур

**Методы:**
- `get_main_keyboard()` - главное меню
- `get_universe_keyboard()` - выбор вселенной
- `get_gender_keyboard()` - выбор пола

---

### 4. Bot Layer (`RaidSystemBot`)
**Файл:** `main.py` (class `RaidSystemBot`)

**Ответственность:**
- Инициализация aiogram Bot и Dispatcher
- Регистрация всех обработчиков
- Запуск health check сервера
- Запуск polling

**Обработчики:**
- Команды: `/start`, `/help`, `/stats`
- Сообщения: "Квесты", "Тренировки", "Английский", "Статус"
- Callback: `reg_*`, `quest_*`, `workout_*`, `english_*`

---

### 5. Constants Layer (`constants.py`)
**Файл:** `constants.py`

**Ответственность:**
- Все константы в одном месте
- Эмодзи для использования в боте
- Конфигурационные параметры

**Содержимое:**
- `Emoji` - класс с эмодзи
- `ENGLISH_LEVELS` - уровни английского A0-C2
- `ANIME_UNIVERSES` - вселенные аниме
- `QUEST_REWARDS` - награды за квесты
- `Config` - настройки бота
- `MESSAGES` - тексты сообщений
- `KEYBOARD_BUTTONS` - тексты кнопок

---

### 6. Health Check (`health_check.py`)
**Файл:** `health_check.py`

**Ответственность:**
- HTTP сервер для Render.com
- Поддержание бота в активном состоянии 24/7
- Эндпоинты: `/`, `/health`

**Запуск:**
```python
from health_check import start_health_check
start_health_check()  # В отдельном потоке
```

---

## Запуск

```bash
# Локально
python main.py
```

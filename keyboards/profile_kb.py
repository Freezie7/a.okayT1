from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для выбора уровня образования
def get_education_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Среднее")],
            [KeyboardButton(text="Среднее специальное")],
            [KeyboardButton(text="Высшее")],
            [KeyboardButton(text="Неоконченное высшее")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери вариант ↓"
    )

# Клавиатура для пропуска шага (будет полезно в будущем)
def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить шаг")]
        ],
        resize_keyboard=True
    )

def get_skills_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌍 Иностранные языки")],
            [KeyboardButton(text="💻 Языки программирования")],
            [KeyboardButton(text="🔧 Другие навыки")],
            [KeyboardButton(text="✅ Завершить добавление")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери тип навыка ↓"
    )

# Клавиатура для выбора уровня владения
def get_level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начальный"), KeyboardButton(text="Средний")],
            [KeyboardButton(text="Продвинутый"), KeyboardButton(text="Эксперт")]
        ],
        resize_keyboard=True
    )

# Инлайн-клавиатура для популярных языков
def get_popular_languages_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="lang_english"),
             InlineKeyboardButton(text="Deutsch", callback_data="lang_german"),
             InlineKeyboardButton(text="Français", callback_data="lang_french")],
            [InlineKeyboardButton(text="Español", callback_data="lang_spanish"),
             InlineKeyboardButton(text="Italiano", callback_data="lang_italian"),
             InlineKeyboardButton(text="Português", callback_data="lang_portuguese")],
            [InlineKeyboardButton(text="中文", callback_data="lang_chinese"),
             InlineKeyboardButton(text="日本語", callback_data="lang_japanese"),
             InlineKeyboardButton(text="한국어", callback_data="lang_korean")],
            [InlineKeyboardButton(text="Русский", callback_data="lang_russian"),
             InlineKeyboardButton(text="العربية", callback_data="lang_arabic"),
             InlineKeyboardButton(text="हिन्दी", callback_data="lang_hindi")],
            [InlineKeyboardButton(text="Другой язык", callback_data="lang_other")]
        ]
    )

# Инлайн-клавиатура для популярных языков программирования
def get_popular_programming_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Python", callback_data="prog_python"),
             InlineKeyboardButton(text="JavaScript", callback_data="prog_js"),
             InlineKeyboardButton(text="Java", callback_data="prog_java")],
            [InlineKeyboardButton(text="C++", callback_data="prog_cpp"),
             InlineKeyboardButton(text="C#", callback_data="prog_csharp"),
             InlineKeyboardButton(text="PHP", callback_data="prog_php")],
            [InlineKeyboardButton(text="Go", callback_data="prog_go"),
             InlineKeyboardButton(text="Ruby", callback_data="prog_ruby"),
             InlineKeyboardButton(text="Swift", callback_data="prog_swift")],
            [InlineKeyboardButton(text="Kotlin", callback_data="prog_kotlin"),
             InlineKeyboardButton(text="TypeScript", callback_data="prog_ts"),
             InlineKeyboardButton(text="Rust", callback_data="prog_rust")],
            [InlineKeyboardButton(text="SQL", callback_data="prog_sql"),
             InlineKeyboardButton(text="HTML/CSS", callback_data="prog_html"),
             InlineKeyboardButton(text="Dart", callback_data="prog_dart")],
            [InlineKeyboardButton(text="Другой язык", callback_data="prog_other")]
        ]
    )
def get_popular_skills_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Лидерство", callback_data="skill_leadership"),
             InlineKeyboardButton(text="Коммуникация", callback_data="skill_communication")],
            [InlineKeyboardButton(text="Дизайн", callback_data="skill_design"),
             InlineKeyboardButton(text="Аналитика", callback_data="skill_analysis")],
            [InlineKeyboardButton(text="Управление проектами", callback_data="skill_management"),
             InlineKeyboardButton(text="Маркетинг", callback_data="skill_marketing")],
            [InlineKeyboardButton(text="Продажи", callback_data="skill_sales"),
             InlineKeyboardButton(text="Креативность", callback_data="skill_creativity")],
            [InlineKeyboardButton(text="Командная работа", callback_data="skill_teamwork"),
             InlineKeyboardButton(text="Решение проблем", callback_data="skill_problem_solving")],
            [InlineKeyboardButton(text="Другой навык", callback_data="skill_other")]
        ]
    )
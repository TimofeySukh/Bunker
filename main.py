import os
import logging
import re
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gemini import Gemini
from prompt import SYSTEM_PROMPT, START_PROMPT

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Проверка загрузки токенов
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения")
    raise ValueError("Пожалуйста, установите TELEGRAM_TOKEN в .env файле")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY не найден в переменных окружения")
    raise ValueError("Пожалуйста, установите GEMINI_API_KEY в .env файле")

logger.info("Токены загружены успешно")

# Инициализация клиента Gemini
gemini = Gemini(API_KEY=GEMINI_API_KEY, system_instruction=SYSTEM_PROMPT, temperature=0.9)

def extract_card_details(response: str):
    """
    Извлекает все ключевые параметры из карточки
    """
    patterns = {
        'profession': r"Профессия:\s*([^\n]+)",
        'age': r"Возраст:\s*(\d+)",
        'health': r"Состояние здоровья:\s*([^\n]+)",
        'hobby': r"Хобби:\s*([^\n]+)",
        'phobia': r"Фобия:\s*([^\n]+)",
        'fact': r"Смешной факт:\s*([^\n]+)",
        'gender': r"Пол:\s*([^\n]+)",
        'card': r"Карта:\s*([^\n]+)"
    }
    
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response)
        if match:
            results[key] = match.group(1).strip()
    return results

# Глобальные множества для отслеживания всех использованных значений
used_values = {
    'professions': set(),
    'ages': set(),
    'health': set(),
    'hobbies': set(),
    'phobias': set(),
    'facts': set(),
    'cards': set()
}

def generate_random_card():
    """
    Генерирует карточку с случайными параметрами и учетом всех ранее использованных значений
    """
    # Генерируем случайный возраст от 9 до 70 лет
    random_age = str(random.randint(9, 70))
    while random_age in used_values['ages']:
        random_age = str(random.randint(9, 70))
    used_values['ages'].add(random_age)
    
    # Генерируем случайный пол и фертильность
    genders = ["Мужской", "Женский"]
    random_gender = random.choice(genders)
    is_fertile = random.choice(["плоден", "бесплоден"])
    
    extra_instructions = f"\nИспользуй следующие параметры:\n"
    extra_instructions += f"Возраст: {random_age} лет\n"
    extra_instructions += f"Пол: {random_gender}, {is_fertile}\n"
    extra_instructions += f"\nПожалуйста, не используйте следующие значения:\n"
    
    for category, values in used_values.items():
        if values and category not in ['ages', 'gender']:  # Пропускаем возраст и пол
            extra_instructions += f"\n{category}: {', '.join(values)}"
    
    prompt = SYSTEM_PROMPT + extra_instructions
    logger.info(f"Запрос для генерации карточки с возрастом {random_age} и полом {random_gender}")
    
    response = gemini.send_message(prompt)
    
    # Извлекаем все параметры из ответа
    details = extract_card_details(response)
    
    # Сохраняем новые значения (кроме возраста и пола, которые мы уже задали)
    for key, value in details.items():
        if key in used_values and value and key not in ['age', 'gender']:
            used_values[key].add(value)
    
    return response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Генерация начальной карточки")
    try:
        response = generate_random_card()
        logger.info(f"Получен ответ от Gemini: {response}")
        await update.message.reply_text(response)
        logger.info("Начальная карточка успешно отправлена пользователю")
    except Exception as e:
        logger.error(f"Ошибка при генерации карточки: {e}")
        await update.message.reply_text(
            "Произошла ошибка при генерации карточки. Пожалуйста, попробуйте снова."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    logger.info(f"Получено сообщение: {message}")
    
    if "/start" in message:
        logger.info("Запрос на генерацию карточки получен")
        try:
            response = generate_random_card()
            logger.info(f"Получен ответ от Gemini: {response}")
            await update.message.reply_text(response)
            logger.info("Карточка успешно отправлена пользователю")
        except Exception as e:
            logger.error(f"Ошибка при генерации карточки: {e}")
            await update.message.reply_text(
                "Произошла ошибка при генерации карточки. Пожалуйста, попробуйте снова."
            )
    elif "начать" in message:
        logger.info("Запрос на генерацию начального состояния игры получен")
        try:
            response = gemini.send_message(START_PROMPT)
            logger.info(f"Получен ответ от Gemini: {response}")
            await update.message.reply_text(response)
            logger.info("Начальное состояние игры успешно отправлено пользователю")
        except Exception as e:
            logger.error(f"Ошибка при генерации начального состояния: {e}")
            await update.message.reply_text(
                "Произошла ошибка при генерации начального состояния. Пожалуйста, попробуйте снова."
            )
    else:
        await update.message.reply_text(
            "Доступные команды:\n"
            "- '[имя] карточку' - получить карточку персонажа\n"
            "- 'начать' - получить описание начального состояния игры"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Ошибка: {context.error}')
    await update.message.reply_text(
        "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова."
    )

def main():
    # Создание приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Запуск бота
    logger.info("Бот запущен и работает...")
    application.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()

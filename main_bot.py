"""Содержит методы для работы с операционной системой"""
import os
import sys
import datetime
import tempfile
from logging import info, fatal, error, basicConfig, INFO
import telebot
from telebot.types import User
from dotenv import load_dotenv
from tools_bot import remove_file, docx2pdf
from db_main import save_info_db
from db_main import intermediate_status

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

token = os.getenv("BOT_TOKEN")

if token is None:
    fatal("Токен не установлена.")
    sys.exit(1)

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message: any) -> None:
    """Ответ на команду start"""
    bot.reply_to(message, "Привет! Отправь мне .docx файл — я сделаю из него PDF.")

tmp = tempfile.mkdtemp(prefix="telegram_bot_")
info(f"Создана временная директория: {tmp}")

@bot.message_handler(content_types=['document'])
def handle_document(message: any) -> None:
    """Конвертирует документ"""
    try:
        doc = message.document

        if not doc.file_name.lower().endswith('.docx'):
            bot.reply_to(message, "Пожалуйста, отправь файл с расширением .docx")
            return
        
        user: User = message.from_user
        user_id = user.id
        username = user.username
        original_file_id = doc.file_id 
        
        file_info = bot.get_file(doc.file_id)
        intermediate_status(user_id, original_file_id, "pending", datetime.datetime.now)
        file_content = bot.download_file(file_info.file_path)

        docx_path = os.path.join(tmp, doc.file_name)
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

        with open(docx_path, 'wb') as f:
            f.write(file_content)

        bot.send_message(message.chat.id, "Конвертирую...")


        intermediate_status(user_id, original_file_id, "processing", datetime.datetime.now)

        if docx2pdf(docx_path, pdf_path):
            with open(pdf_path, 'rb') as f:
                sent_message=bot.send_document(message.chat.id, f)
            pdf_file_id = sent_message.document.file_id 
            save_info_db(
            user_id=user_id,
            username=username,
            original_file_id=original_file_id,
            pdf_file_id=pdf_file_id,
            timestamp=datetime.datetime.now(),
            status_name="completed")
        else:
            bot.send_message(message.chat.id, "Не удалось конвертировать файл.")
            save_info_db(
                user_id=user_id,
                username=username,
                original_file_id=original_file_id,
                pdf_file_id=None,
                timestamp=datetime.datetime.now(),
                status_name="failed"
            )
        remove_file(docx_path)
        remove_file(pdf_path)

    except Exception as e:
        error('Ошибка при обработке документа: %s', e)
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке файла: {e}")
        raise

if __name__ == "__main__":
    info("Бот запущен")
    bot.polling(none_stop=True, interval=0, timeout=20)

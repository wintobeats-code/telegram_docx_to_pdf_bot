"""Содержит методы для работы с операционной системой"""
import os
import sys
import tempfile
from logging import info, fatal, error, basicConfig, INFO
import telebot
from dotenv import load_dotenv
from tools import remove_file, docx2pdf

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

token = os.getenv("BOT_TOKEN")

if token is None:
    fatal("Токен не установлена.")
    sys.exit(1)

with tempfile.TemporaryDirectory() as tmp:
    info(f'Создана директория для временных файлов: {tmp}')

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message: any) -> None:
    """Ответ на команду start"""
    bot.reply_to(message, "Привет! Отправь мне .docx файл — я сделаю из него PDF.")

@bot.message_handler(content_types=['document'])
def handle_document(message: any) -> None:
    """Конвертирует документ"""
    try:
        doc = message.document

        if not doc.file_name.lower().endswith('.docx'):
            bot.reply_to(message, "Пожалуйста, отправь файл с расширением .docx")
            return

        file_info = bot.get_file(doc.file_id)
        file_content = bot.download_file(file_info.file_path)

        docx_path = os.path.join(tmp, doc.file_name)
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

        with open(docx_path, 'wb') as f:
            f.write(file_content)

        bot.send_message(message.chat.id, "Конвертирую...")

        if docx2pdf(docx_path, pdf_path):
            with open(pdf_path, 'rb') as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.send_message(message.chat.id, "Не удалось конвертировать файл.")

        remove_file(docx_path)
        remove_file(pdf_path)

    except Exception as e: 
        error('Ошибка при обработке документа: %s', e)
        bot.send_message(message.chat.id, "Произошла ошибка при обработке файла: %s", e)
        raise

if __name__ == "__main__":
    info("Бот запущен")
    bot.polling(none_stop=True, interval=0, timeout=20)
